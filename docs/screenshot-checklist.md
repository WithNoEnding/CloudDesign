# 实验截图清单

本文件用于记录课程设计报告中建议保留的截图。截图本身不建议全部提交到仓库，除非教师明确要求。报告中应保证截图清晰，能看到命令、资源名称、状态和关键返回值。

## 第一部分：云计算平台搭建

1. 本地前端页面，能看到姓名、学号和接口测试结果。
2. 本地 `docker compose up --build` 日志，后端出现 `/api/ping` 或 `/api/count` 请求记录。
3. SWR 控制台镜像列表，包含 `backend:v1` 和 `frontend:v1`。
4. `kubectl get nodes -o wide`，Worker 节点状态为 `Ready`，并显示 `VERSION` 列。
5. `kubectl get pods`，backend、Redis、frontend Pod 处于 `Running`。
6. `kubectl get svc`，backend-svc 获得 `EXTERNAL-IP`。
7. 浏览器或 curl 访问 `http://<ELB-IP>/api/ping`，返回 `{"status":"ok"}`。
8. `kubectl get pvc`，`redis-data-pvc` 状态为 `Bound`。
9. Redis 写入 `SET testkey hello` 并读取成功。
10. 删除 Redis Pod 后，Deployment 自动重建新 Pod。
11. Redis Pod 重建后再次执行 `GET testkey`，返回 `hello`。
12. `kubectl exec` 进入 frontend Pod，查看 `/etc/nginx/conf.d/default.conf`。
13. `kubectl top nodes` 或 `kubectl top pods` 返回指标。
14. `kubectl get hpa` 显示 `backend-hpa`。
15. 压测期间 backend Pod 数量增加。
16. 停止压测并等待后，backend Pod 数量缩回低负载状态。

## 第二部分：Spark 大数据分析

1. Spark Operator 和 SparkApplication CRD 部署成功。
2. Spark 作业权限配置成功。
3. SparkApplication 提交成功。
4. Driver 和 Executor Pod 正常运行。
5. Driver 日志中包含 Schema、前 5 行、缺失值统计和清洗前后行数。
6. 查询 1：按类型统计电影数量和平均评分。
7. 查询 2：评分人数大于 10000 的高评分电影 Top-N。
8. 查询 3：按年份统计电影数量和平均评分。
9. 查询 4：每个类型内评分排名 Top5。
10. SparkApplication 状态为 `COMPLETED`。
11. Pandas、PySpark 1 Executor、PySpark 2 Executors 的耗时对比图或表。
12. 加速比、并行效率和 Amdahl 分析结果。

## 附加题 1：Prometheus + Grafana

1. monitoring 命名空间中 Prometheus、Grafana、Alertmanager、node-exporter 等组件处于 `Running`。
2. Grafana 节点 CPU 利用率折线图。
3. Grafana 各 Pod 内存使用图。
4. PromQL 查询语句或 Dashboard 配置页面。

## 附加题 2：GitHub Actions CI/CD

1. GitHub Actions workflow 文件。
2. GitHub Secrets 页面，只展示 Secret 名称，不展示值。
3. Actions 流水线全部阶段 Passed。
4. CCE 中 backend Deployment 的镜像 Tag 已更新为 `ci-xxxxxxx`。
5. backend Pod 完成滚动更新并处于 `Running`。

## 截图整理建议

- 每张截图前后都应有文字说明，避免只放图片。
- 命令行截图应尽量放大，保证资源名称、状态、时间和返回值可读。
- 不要在截图中展示 kubeconfig、Token、AK/SK、SWR 密码或 GitHub Secret 值。
