# About Project
Using flask APM (prometheus_flask_exporter).
Uses prometheus_flask_exporter to check the real time performance mtrics for request latency (the time it takes for the app to respond to request) and cpu_usage (measures the percentage of CPU resources used by the app)

# Purpose 

This metrics (latency and cpu_usage) will be sent as notification to telex channel me and my teams would be able to monitor it in real time, and act quickly if the latency time passes 100-500ms (For web application). A high latency threshold can lead to poor user experience, and decreased overall performance.
High CPU usage can lead to performance degradation, increased latency and might crashes.


# Project Setup
```
python -m venv venv

venv/Scripts/acyivate

pip install -r requirements.txt
```

# To start and test the app
```
flask run --debug
pytest test_app.py
```

# To view the metrics on the app and to also trigger the notification
```
# To view the metrics in real time
http://127.0.0.1:5000/metric

# To send a notification
http://127.0.0.1:5000/tick

# Integration.json endpoint
http://127.0.0.1:5000
```

get_integration_json function returns integration.json to integarte into telex app
setting this will automate telex to trigger the /tick endpoint at the time interval set.

```
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
                    "default": "* * * * *"
                }
            ],
            "target_url": "",
            "tick_url": f"{base_url}/tick"
        }

```
# Request Format

The /tick endpoint accepts a POST request, when triggered by telex it returns the following json.
```
{"result":
    {"message": "request received",
    "status":"success",
    "status_code":202,
    "task_id":"d180c65e-0f3e-491a-bcfd-2d57d2bd00a1"}
}
```
![cpu_usage](https://github.com/user-attachments/assets/1274f749-19e0-4c3f-b592-8245d566a578)
![channel_telex](https://github.com/user-attachments/assets/e368ea3a-31ed-4117-ab6e-56fdc5c695f7)

# To test the integration
curl -X GET "https://simply-metric.onrender.com/tick"  // To trigger notifigation

curl -X GET "https://simply-metric.onrender.com"  // To get the integration.json

