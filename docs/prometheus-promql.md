# Prometheus Queries Used in the Report

## Node CPU utilization

```promql
100 * (1 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[1m])))
```

`node_cpu_seconds_total` records the cumulative CPU time of a node in different modes. The query calculates the non-idle part of CPU usage.

## Pod memory usage

```promql
sum by (pod) (container_memory_working_set_bytes{namespace="monitoring", container!="", image!=""}) / 1024 / 1024
```

`container_memory_working_set_bytes` represents the current working set memory of containers. The query aggregates memory usage by Pod and converts bytes to MiB.

## Target scrape status

```promql
up
```

`up=1` means the scrape target is reachable. `up=0` means Prometheus failed to scrape the target.
