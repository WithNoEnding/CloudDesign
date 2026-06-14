# Prometheus 查询说明

本文件记录监控附加题中使用的 PromQL 查询语句。报告中主要展示节点 CPU 利用率和 Pod 内存使用情况。

## 节点 CPU 利用率

```promql
100 * (1 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[1m])))
```

说明：

- `node_cpu_seconds_total` 表示节点 CPU 在不同 mode 下的累计运行时间。
- `mode="idle"` 表示空闲时间。
- `rate(...[1m])` 计算 1 分钟窗口内的变化率。
- `1 - idle` 可以得到非空闲占比，即 CPU 使用率。

## Pod 内存使用量

```promql
sum by (pod) (container_memory_working_set_bytes{namespace="monitoring", container!="", image!=""}) / 1024 / 1024
```

说明：

- `container_memory_working_set_bytes` 表示容器当前工作集内存。
- `sum by (pod)` 将同一 Pod 内多个容器的内存使用量聚合。
- `/ 1024 / 1024` 将字节转换为 MiB。

## 采集目标状态

```promql
up
```

说明：

- `up = 1` 表示 Prometheus 能够正常抓取目标。
- `up = 0` 表示抓取失败。

## 实验说明

本实验中，节点 CPU 图主要依赖 node-exporter 指标，Pod 内存图依赖容器运行时相关指标。kube-state-metrics 用于补充 Kubernetes 对象状态信息，但本报告展示的两个核心图表不依赖 kube-state-metrics，因此在镜像不可用时关闭了该组件。
