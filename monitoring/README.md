# Prometheus + Grafana 监控附加题

本目录保存附加题 1 的监控系统配置文件。文件中不包含 kubeconfig、Token、AK/SK 或 GitHub Secret 值。

## 文件说明

```text
monitoring-values-extra.yaml    kube-prometheus-stack values 覆盖配置
grafana-lb.yaml                 临时暴露 Grafana 的 LoadBalancer Service
README.md                       本说明文件
```

## 部署方式

将课程提供的 kube-prometheus-stack 离线 Chart 放在本地或 CloudShell 中，然后执行：

```bash
helm upgrade --install monitoring <kube-prometheus-stack-chart-path> \
  -n monitoring \
  --create-namespace \
  -f monitoring/monitoring-values-extra.yaml
```

示例：

```bash
helm upgrade --install monitoring ./kube-prometheus-stack-83.7.0.tgz \
  -n monitoring \
  --create-namespace \
  -f monitoring/monitoring-values-extra.yaml
```

查看组件状态：

```bash
kubectl get pods -n monitoring -o wide
kubectl get svc -n monitoring
```

## 临时暴露 Grafana

```bash
kubectl apply -f monitoring/grafana-lb.yaml
kubectl get svc grafana-lb -n monitoring
```

通过 `grafana-lb` 的公网地址访问 Grafana，并在 Grafana 中配置 Prometheus 数据源或使用 Helm Chart 默认数据源。

截图完成后删除公网 LoadBalancer：

```bash
kubectl delete svc grafana-lb -n monitoring --ignore-not-found=true
```

## 报告使用的 PromQL

节点 CPU 利用率：

```promql
100 * (1 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[1m])))
```

Pod 内存使用量：

```promql
sum by (pod) (container_memory_working_set_bytes{namespace="monitoring", container!="", image!=""}) / 1024 / 1024
```

更多说明见：

```text
docs/prometheus-promql.md
```

## 注意事项

- `grafana-lb.yaml` 只用于临时截图，不建议长期保留公网访问。
- `monitoring-values-extra.yaml` 中的镜像地址使用本实验的 SWR 组织名。复用到其他账号时，需要替换为自己的 SWR 地址。
- 本实验关闭了 kube-state-metrics，因为报告中的节点 CPU 和 Pod 内存图不依赖该组件。
