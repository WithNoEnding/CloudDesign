# Optional Task 1: Prometheus + Grafana Monitoring

This directory records the configuration used for the monitoring optional task. No credential is included.

## Install

```bash
helm upgrade --install monitoring ./kube-prometheus-stack-83.7.0.tgz \
  -n monitoring \
  --create-namespace \
  -f monitoring/monitoring-values-extra.yaml
```

Check pods:

```bash
kubectl get pods -n monitoring -o wide
kubectl get svc -n monitoring
```

## Temporary Grafana external access

```bash
kubectl apply -f monitoring/grafana-lb.yaml
kubectl get svc grafana-lb -n monitoring
```

After screenshots are collected, delete the temporary public LoadBalancer:

```bash
kubectl delete svc grafana-lb -n monitoring --ignore-not-found=true
```

## PromQL used in the report

Node CPU utilization:

```promql
100 * (1 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[1m])))
```

Pod memory usage in the monitoring namespace:

```promql
sum by (pod) (container_memory_working_set_bytes{namespace="monitoring", container!="", image!=""}) / 1024 / 1024
```

## Notes

The experiment used node-exporter metrics for node CPU and container metrics for Pod memory. These two charts do not depend on kube-state-metrics, so kube-state-metrics was disabled when its image was unavailable.
