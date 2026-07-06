from fastapi import FastAPI
import requests
import boto3
import json
import time

app = FastAPI()

PODINFO_URL = "http://podinfo.sla-demo.svc.cluster.local:9898"

SQS_QUEUE_URL = "https://sqs.eu-west-1.amazonaws.com/238679625965/sla-fallback-queue"

sqs = boto3.client("sqs", region_name="eu-west-1")

# SLA threshold (simple and realistic)
LATENCY_LIMIT = 0.9  # seconds


def send_to_sqs(reason: str):
    sqs.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=json.dumps({
            "reason": reason,
            "service": "podinfo"
        })
    )


@app.get("/")
def gateway():

    start = time.time()

    try:
        r = requests.get(PODINFO_URL, timeout=2)
        latency = time.time() - start

        # ❗ SLA FAILURE CONDITIONS
        if r.status_code >= 500:
            send_to_sqs("5xx error from podinfo")
            return {"status": "fallback -> SQS"}

        if latency > LATENCY_LIMIT:
            send_to_sqs("high latency breach")
            return {"status": "fallback -> SQS"}

        # normal flow (THIS triggers HPA naturally)
        return r.json()

    except Exception as e:
        send_to_sqs("timeout or connection failure")
        return {"status": "fallback -> SQS"}
