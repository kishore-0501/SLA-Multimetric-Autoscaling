import subprocess

output = subprocess.check_output(
    [
        "kubectl",
        "get",
        "hpa",
        "-n",
        "sla-demo",
        "-o",
        "jsonpath={.items[0].status.currentReplicas}"
    ]
)

current = int(output.decode())

if current >= 30:
    print("FALLBACK_ENABLED")
else:
    print("NORMAL_MODE")