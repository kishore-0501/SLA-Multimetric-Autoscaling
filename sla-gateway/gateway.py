from fastapi import FastAPI
import requests
import boto3
import json
import time

app = FastAPI()

# ----------------------------
# Configuration
# ----------------------------

FARM_APP_URL = "http://farm-service.sla-demo.svc.cluster.local"

PROMETHEUS_URL = (
    "http://monitoring-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090"
)

SQS_QUEUE_URL = (
    "https://sqs.eu-west-1.amazonaws.com/562460196113/sla-fallback-queue"
)

REQUEST_RATE_LIMIT = 31

sqs = boto3.client(
    "sqs",
    region_name="eu-west-1"
)

# ----------------------------
# Send to SQS
# ----------------------------

def send_to_sqs(message):

    print("******** SENDING TO SQS ********")
    print(message)

    response = sqs.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=json.dumps(message)
    )
    print(response)

# ----------------------------
# Read request rate
# ----------------------------

def get_request_rate():

    query = '''sum(rate(django_http_requests_total_by_method_total{namespace="sla-demo"}[1m]))'''

    try:

        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": query},
            timeout=2
        )

        result = response.json()

        result = response.json()["data"]["result"]

        if not result:
            return 0

        return float(result[0]["value"][1])

        return value

    except Exception as e:

        print("Prometheus error:", e)

        return 0
    
request_rate = get_request_rate()

print("========================")
print("Current Request Rate:", request_rate)
print("========================")

# ----------------------------
# Gateway
# ----------------------------

@app.get("/")
def gateway():

    request_rate = get_request_rate()

    print("Current Request Rate =", request_rate)

    # -------------------------
    # Serverless Fallback
    # -------------------------

    if request_rate >= REQUEST_RATE_LIMIT:

        send_to_sqs({
            "reason": "High Request Rate",
            "request_rate": request_rate
        })

        return {
            "status": "fallback -> SQS",
            "request_rate": request_rate
        }

    # -------------------------
    # Normal Kubernetes Path
    # -------------------------

    try:

        start = time.time()

        response = requests.get(
            FARM_APP_URL,
            timeout=2
        )

        latency = time.time() - start

        return {
            "backend": "Kubernetes",
            "status_code": response.status_code,
            "latency": round(latency, 4),
            "message": "Request successfully served by Farm application"
}

    except Exception:

        send_to_sqs({
            "reason": "Farm App Unreachable"
        })

        return {
            "status": "fallback -> SQS"
        }