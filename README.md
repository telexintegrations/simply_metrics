Setup, testing, and deployment instructions
Integration purpose and functionality
Screenshots of it working in Telex

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
http://127.0.0.1:5000/metric
http://127.0.0.1:5000/notify
```
