kubectl get hpa -n sla-demo -w
kubectl get pods -n sla-demo -w
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090 -n monitoring