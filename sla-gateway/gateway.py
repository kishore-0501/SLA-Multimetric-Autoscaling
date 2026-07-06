from fastapi import FastAPI
import requests
import boto3
import json
import time

app = FastAPI()

# ----------------------------
# Configuration
# ----------------------------

PODINFO_URL = "http://podinfo.sla-demo.svc.cluster.local:9898"

PROMETHEUS_URL = (
    "http://prometheus-kube-prometheus-prometheus.monitoring:9090"
)

SQS_QUEUE_URL = (
    "https://sqs.eu-west-1.amazonaws.com/238679625965/sla-fallback-queue"
)

REQUEST_RATE_LIMIT = 50

sqs = boto3.client(
    "sqs",
    region_name="eu-west-1"
)

# ----------------------------
# Send to SQS
# ----------------------------

def send_to_sqs(message):

    sqs.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=json.dumps(message)
    )

# ----------------------------
# Read request rate
# ----------------------------

def get_request_rate():

    query = 'sum(rate(http_requests_total{service="podinfo"}[1m]))'

    try:

        response = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": query},
            timeout=2
        )

        result = response.json()

        value = float(
            result["data"]["result"][0]["value"][1]
        )

        return value

    except Exception as e:

        print("Prometheus error:", e)

        return 0

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
            PODINFO_URL,
            timeout=2
        )

        latency = time.time() - start

        return {
            "backend": "Kubernetes",
            "latency": round(latency, 4),
            "response": response.json()
        }

    except Exception:

        send_to_sqs({
            "reason": "Podinfo Unreachable"
        })

        return {
            "status": "fallback -> SQS"
        }