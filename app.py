'''
An application that return the Request Latency and CPU usage
'''

# To log errors
import logging
from flask import Flask, g, Response, jsonify, request, render_template
from prometheus_flask_exporter import PrometheusMetrics
import psutil  # To track CPU usage
import time  # For request latency
from prometheus_client import CollectorRegistry, Histogram, Gauge, generate_latest # For creating a custom webpage that only returns selected response
import requests
from flask_cors import CORS

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)

# Enable CORS for cross-origin resource sharing
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app, path=None) # Disable the default endpoint to create a custom endpoint

# static information as metric
metrics.info('app_info', 'Application info', version='1.0.0')

# Create a custom reqistry and define only the selected metrics needed
custom_registry = CollectorRegistry()

# Create a custom histogram for request latency and a gauge for CPU usage
latency_metric = Histogram('request_latency_seconds', 'Request latency in seconds', registry=custom_registry)

cpu_metric = Gauge('cpu_usage_percent', 'Current CPU usage percentage', registry=custom_registry)


@app.before_request
def start_timer():
    ''' Start the timer before processing a request '''
    g.start_time = time.time()


@app.after_request
def log_request_latency(response):
    ''' Calculate and log request latency after each request and also CPU usage.'''
    
    try:
        if hasattr(g, "start_time"):  # Check if g.start_time exists
            latency = time.time() - g.start_time
            latency_metric.observe(latency)

        # Update CPU usage metric
        cpu_metric.set(psutil.cpu_percent(interval=1))  # Track CPU usage every second

    except Exception as e:
        logger.error(f"Error logging request metrics: {e}")
    return response

#  Home Route
@app.route('/about')
def home():
    return render_template("about.html")

@app.route('/metric')
def return_metrics_data():
    ''' Return Latency and CPU usage when route is visited '''
    
    try:
        return generate_latest(custom_registry).decode('utf-8')
    except Exception as e:
        logger.error(f"Error generating latest metrics: {e}")
        return jsonify({"message": "Error generating latest metrics"}), 500


# Send a POST request to a webhook with the metrics data. 
def send_notification():

    """
    Call the metric endpoint, extract its data,
    and send it as a notification to the Telex webhook.
    """
    
    try:
        
        # Get the metrics data by calling the return_metrics function
        metrics_response = return_metrics_data()
    
        # Build the payload with the metrics data as the message
        

        url = "https://ping.telex.im/v1/webhooks/019533b3-05ef-7c62-85ff-e12a75a67875"
        payload = {
            "event_name": "Latency and CPU_Usage Performance monitoring",
            "message": metrics_response,
            "status": "success",
            "username": "Omobolanle"
        }

        response = requests.post(
                url,
                json=payload,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
        )
        
        # Log the full response for debugging
        # logger.info(f"Webhook response status: {response.status_code}")
        # logger.info(f"Webhook response body: {response.text}")
    
    except requests.exceptions.RequestException as e:
        # If there's an error sending the notification, return an error message
        logger.error(f"Request error: {e}")
        return {"message":"unable to send request", "error":str(e)}, 500
    
    # Return a response indicating that the notification was sent
    return response.json()

@app.route('/tick',  methods=['GET', 'POST'])
def notify():
    try:
        result = send_notification()
        logger.info(f"Notification result: {result}")
        return {"result": result}, 202
    
    except Exception as e:
        # If there's an error connecting to the webhook, return an error message
        logger.error(f"Error sending notification: {e}")
        return {"error": "Internal Server Error", "message": str(e)}, 500


@app.route("/")
def get_integration_json():
    base_url = request.url_root.rstrip("/")
    return {
        "data": {
            "date": {
                "created_at": "2025-02-20",
                "updated_at": "2025-02-20"
            },
            "descriptions": {
                "app_name": "simply_metrics",
                "app_description": "Check for latency threshold and CPU usage of a flask web app",
                "app_logo": "https://i.imgur.com/lZqvffp.png",
                "app_url": base_url,
                "background_color": "#fff"
            },
            "is_active": True,
            "integration_category": "Performance Monitoring",
            "integration_type": "interval",
            "key_features": [
                "Check for latency request in seconds and return the metrics",
                "Check for CPU usage percentage and return the metrics"
            ],
            "author": "Azeezat Omobolanle",
            "website": base_url,
            "settings": [
                {
                    "label": "interval",
                    "type": "text",
                    "required": True,
                    "default": "*/3 * * * *"
                }
            ],
            "target_url": "",
            "tick_url": f"{base_url}/tick"
        }
    }

if __name__ == '__main__':
    app.run()

        
