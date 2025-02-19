'''
An application that return the Request Latency and CPU usage
'''

# To log errors
import logging
from flask import Flask, g, Response, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics
import psutil  # To track CPU usage
import time  # For request latency
from prometheus_client import CollectorRegistry, Histogram, Gauge, generate_latest # For creating a custome webpage that only returns selected response
import requests
from flask_cors import CORS

# For automating response notification
# from apscheduler.schedulers.background import BackgroundScheduler
# import atexit

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)

# Enable CORS for cross-origin resource sharing
CORS(app)

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
        # Obaserve the latency for this request
        latency = time.time() - g.start_time
        latency_metric.observe(latency)
    
        # Update CPU usage metric
        cpu_metric.set(psutil.cpu_percent(interval=1))  # Track CPU usage every second
    except Exception as e:
        logger.error(f"Error logging request metrics: {e}")
    return response

#  Home Route
@app.route('/')
def home():
    return '<h1>Welcome to simply_metric home page!</h1>'

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
    
    # Get the metrics data by calling the return_metrics function
    metrics_response = return_metrics_data()
    
    # Build the payload with the metrics data as the message
    payload = {
        "event_name": "Simply-app latency and cpu_usage",
        "message": metrics_response,
        "status": "accepted",
        "username": "Omobolanle"     
    }
    
    # Telex webhook URL (replace with your actual URL)
    url = "https://ping.telex.im/v1/webhooks/01951965-f6ad-7ff0-9468-aba9ddc3bbf0"
    
    try:
        # Send the POST request with the payload
        response = requests.post(
            url,
            json=payload,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
    
    except requests.exceptions.RequestException as e:
        # If there's an error sending the notification, return an error message
        logger.error(f"Request error: {e}")
        return {"message":"unable to send request", "error":str(e)}, 500
    
    except requests.exceptions.ConnectionError as e:
        # If there's an error connecting to the webhook, return an error message
        return {"error": "Unable to connect to the webhook", "message": e}, 500
    
    # Return a response indicating that the notification was sent
    return response.json()

@app.route('/tick')
def notify():
    try:
        result = send_notification()
        return {"result": result}, 202
    except Exception as e:
        # If there's an error connecting to the webhook, return an error message
        logger.error(f"Error sending notification: {e}")
        return {"error": "Internal Server Error", "message": str(e)}, 500


@app.get("/integration.json")
def get_integration_json():
    base_url = request.url_root.rstrip("/")
    return {
        "data": {
            "descriptions": {
                "app_name": "simply_metrics",
                "app_description": "Check for latency threshold and CPU usage of a flask web app",
                "app_url": base_url,
                "app_logo": "https://i.imgur.com/lZqvffp.png",
                "background_color": "#fff"
            },
            "integration_category": "Monitoring & Logging",
            "integration_type": "interval",
            "key_features": [
                "Check for latency request in seconds in the app, and return the metrics",
                "Check for CPU usage percentage in the app, and return the metrics"
            ],
            "settings": [
                {"label": "interval", "type": "text", "required": True, "default": "* * * * *"}
            ],
            "tick_url": f"{base_url}/tick",
            "target_url": "https://ping.telex.im/v1/webhooks/01951965-f6ad-7ff0-9468-aba9ddc3bbf0"
        }
    }


''' APScheduler for sending metrics (latency and cpu usage) notifications '''
# scheduler = BackgroundScheduler()

# # Add the job to send metrics notifications at every 1 minute
# scheduler.add_job(func=send_notification, trigger="interval", minutes=3)
# scheduler.start()

# # To ensure the scheduler stops when app exits
# atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run()

        
