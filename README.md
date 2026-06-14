# 基于华为云 CCE 的云原生应用部署与 Spark 数据分析

本仓库为《云计算技术》课程设计项目代码。项目围绕华为云 CCE 和 Kubernetes 完成云原生应用部署，并在同一集群上运行 Spark 数据分析任务；同时补充 Prometheus + Grafana 监控系统和 GitHub Actions CI/CD 流水线。

## 项目信息

- 课程：云计算技术
- 题目：基于华为云 CCE 的云原生应用部署与 Spark 数据分析
- 学号：2023112411
- 姓名：刘彬彬
- 云平台：华为云
- Region：`cn-north-4`
- 镜像仓库：华为云 SWR，组织名 `cloud-course-2023112411`

## 完成内容

| 模块 | 内容 |
|---|---|
| 第一部分：云计算平台搭建 | Flask 后端、Nginx 前端、Redis、本地 Docker Compose、SWR 镜像推送、CCE 部署、ELB 暴露、PVC 持久化、ConfigMap Volume、HPA 弹性伸缩 |
| 第二部分：Spark 大数据分析 | Spark Operator、SparkApplication、豆瓣电影数据清洗、Spark SQL 统计分析、Pandas 与 PySpark 性能对比、Amdahl 分析 |
| 附加题 1：监控系统 | kube-prometheus-stack、Prometheus、Grafana、节点 CPU 利用率、Pod 内存使用情况 |
| 附加题 2：CI/CD 流水线 | GitHub Actions 自动构建 backend 镜像、推送 SWR、更新 CCE 中的 backend Deployment |

## 项目目录

```text
backend/                         Flask API 后端代码
frontend/                        Nginx 前端页面与本地反向代理配置
k8s/                             Kubernetes YAML 模板，镜像地址使用 __SWR__ 占位
spark/                           PySpark 分析脚本、Pandas 对比脚本和豆瓣电影数据集
scripts/                         Windows PowerShell 辅助脚本
docs/screenshot-checklist.md      实验报告截图清单
docs/prometheus-promql.md         监控实验使用的 PromQL 查询说明
docs/cicd-notes.md               CI/CD 流水线说明
monitoring/                      Prometheus + Grafana 附加题相关配置
.github/workflows/               GitHub Actions 工作流
```

## 一、本地联调

在 Windows PowerShell 中进入项目根目录：

```powershell
cd "D:\working\本学期学习\class\Cloud\courseDesign\cloud-course-design-complete"
```

启动本地服务：

```powershell
docker compose up --build
```

浏览器访问：

```text
http://localhost:8080
```

本地验证目标：

1. 页面能显示姓名、学号和应用说明。
2. 点击“测试 /api/ping”后返回 `{"status":"ok"}`。
3. 点击“测试 Redis 计数”后计数能够递增。
4. 后端日志出现 `Received request: /api/ping` 或 `/api/count` 相关记录。

本地联调用于先排除代码、Dockerfile 和容器网络问题。只有本地服务正常后，再进入 CCE 部署。

## 二、构建并推送 backend/frontend 镜像到 SWR

准备信息：

- Region：`cn-north-4`
- SWR 组织名：`cloud-course-2023112411`
- AK：华为云访问密钥中的 AK
- Token：SWR 登录指令中的临时登录 Token

执行：

```powershell
.\scripts\02-build-and-push-swr.ps1 `
  -Region cn-north-4 `
  -Org cloud-course-2023112411 `
  -Ak <YOUR_AK> `
  -Token "<YOUR_SWR_TEMP_TOKEN>"
```

脚本会完成：

1. 登录 SWR。
2. 构建 `backend:v1`。
3. 构建 `frontend:v1`。
4. 打 tag 到 SWR 地址。
5. 推送两个镜像到 SWR。

推送后在 SWR 控制台确认存在：

```text
backend:v1
frontend:v1
```

## 三、创建 CCE 集群

在华为云 CCE 控制台创建 Kubernetes 集群。

建议配置：

- Kubernetes 版本：`>= 1.27`，本实验使用 `v1.34`
- 网络插件：默认 Yangtse CNI
- Worker 节点：至少 2 个
- 节点规格：可先使用 2 vCPU / 4 GiB；运行 Spark 和监控组件时，可补充 2 vCPU / 8 GiB 节点

验证集群：

```powershell
kubectl get nodes -o wide
```

要求 Worker 节点处于 `Ready`，并且输出中包含 `VERSION` 列。

## 四、生成 Kubernetes YAML

`k8s/` 目录中的 backend 和 frontend 镜像地址使用 `__SWR__` 占位。部署前需要渲染为实际 SWR 地址。

```powershell
.\scripts\03-render-k8s.ps1 -Region cn-north-4 -Org cloud-course-2023112411
```

生成结果在：

```text
k8s-rendered/
```

如果需要检查渲染结果，可以打开：

```text
k8s-rendered/04-backend-deployment.yaml
k8s-rendered/07-frontend-deployment.yaml
```

确认镜像地址类似：

```text
swr.cn-north-4.myhuaweicloud.com/cloud-course-2023112411/backend:v1
swr.cn-north-4.myhuaweicloud.com/cloud-course-2023112411/frontend:v1
```

## 五、部署应用到 CCE

按顺序部署基础配置、PVC、Redis、后端、Service、前端和 HPA。

```powershell
kubectl apply -f k8s-rendered\01-configmap-secret.yaml
kubectl apply -f k8s-rendered\02-pvc.yaml
kubectl apply -f k8s-rendered\03-redis-deployment.yaml
kubectl apply -f k8s-rendered\04-backend-deployment.yaml
kubectl apply -f k8s-rendered\05-services.yaml
kubectl apply -f k8s-rendered\06-frontend-nginx-configmap.yaml
kubectl apply -f k8s-rendered\07-frontend-deployment.yaml
```

查看状态：

```powershell
kubectl get pods
kubectl get svc
kubectl get pvc
```

等待 `backend-svc` 出现 `EXTERNAL-IP` 后访问：

```powershell
curl http://<ELB-IP>/api/ping
```

期望返回：

```json
{"status":"ok"}
```

## 六、Redis 持久化验证

查看 Redis Pod：

```powershell
kubectl get pods -l app=redis
```

写入测试数据：

```powershell
kubectl exec -it <redis-pod-name> -- redis-cli -a <REDIS_PASSWORD> SET testkey hello
kubectl exec -it <redis-pod-name> -- redis-cli -a <REDIS_PASSWORD> GET testkey
```

删除 Redis Pod：

```powershell
kubectl delete pod <redis-pod-name>
```

等待新 Pod 创建后再次查询：

```powershell
kubectl get pods -l app=redis
kubectl exec -it <new-redis-pod-name> -- redis-cli -a <REDIS_PASSWORD> GET testkey
```

如果返回 `hello`，说明 Redis 数据目录已经通过 PVC 持久化，数据没有随 Pod 删除而丢失。

## 七、ConfigMap Volume 挂载验证

查看 frontend Pod：

```powershell
kubectl get pods -l app=frontend
```

进入 Pod 查看 Nginx 配置文件：

```powershell
kubectl exec -it <frontend-pod-name> -- cat /etc/nginx/conf.d/default.conf
```

本项目的 frontend Deployment 使用 `subPath` 将 ConfigMap 中的 `default.conf` 挂载到 Nginx 配置路径。`subPath` 适合覆盖单个目标文件，但 ConfigMap 更新后通常不会自动同步到已有容器内。因此修改 ConfigMap 后，建议删除 frontend Pod，让 Deployment 自动重建：

```powershell
kubectl apply -f k8s-rendered\06-frontend-nginx-configmap.yaml
kubectl delete pod <frontend-pod-name>
```

重建后再次执行 `cat /etc/nginx/conf.d/default.conf`，确认配置已经更新。

## 八、HPA 弹性伸缩验证

确认 Metrics API 可用：

```powershell
kubectl top nodes
kubectl top pods
```

部署 HPA：

```powershell
kubectl apply -f k8s-rendered\08-hpa.yaml
kubectl get hpa
```

一个窗口监控 Pod 数量：

```powershell
kubectl get pods -w
```

另一个窗口压测 backend：

```powershell
ab -n 10000 -c 200 http://<ELB-IP>/api/ping
```

Windows 没有 `ab` 时，可以用 PowerShell 方式产生请求：

```powershell
1..2000 | ForEach-Object { Start-Job { Invoke-WebRequest -UseBasicParsing http://<ELB-IP>/api/ping | Out-Null } }
```

实验中 HPA 参数为：

```text
minReplicas = 1
maxReplicas = 4
targetCPUUtilizationPercentage = 60
```

期望现象：压测后 backend Pod 数量增加，停止压测并等待一段时间后，副本数缩回低负载状态。

## 九、Spark 大数据分析

Spark 分析代码位于：

```text
spark/analysis.py
```

数据集位于：

```text
spark/data/douban_movies.csv
```

Pandas 对比脚本位于：

```text
spark/performance_pandas.py
```

构建 Spark 分析镜像前，需要先将课程提供的 PySpark 基础镜像重新 tag 并推送到自己的 SWR，使其地址为：

```text
swr.cn-north-4.myhuaweicloud.com/cloud-course-2023112411/pyspark:v9
```

然后构建并推送分析镜像：

```powershell
.\scripts\04-build-spark-analysis.ps1 `
  -Region cn-north-4 `
  -Org cloud-course-2023112411 `
  -Ak <YOUR_AK> `
  -Token "<YOUR_SWR_TEMP_TOKEN>"
```

提交 SparkApplication 前，将 `spark/sparkapplication-analysis.yaml` 中的 `__SWR__` 替换为实际 SWR 地址。可以手动替换，也可以复制到临时文件后替换。

提交作业：

```powershell
kubectl apply -f spark\sparkapplication-analysis.yaml
kubectl get pods
kubectl logs <driver-pod-name>
```

`analysis.py` 完成以下工作：

1. 读取豆瓣电影 CSV。
2. 输出 Schema、前 5 行和缺失值统计。
3. 对关键字段执行 `dropna`，对文本字段执行 `fillna`。
4. 输出清洗前后行数。
5. 完成类型聚合、高分电影 Top-N、年份趋势和类型内 Top5 查询。
6. 输出 PySpark 类型聚合耗时。

## 十、Prometheus + Grafana 监控附加题

监控相关文件位于：

```text
monitoring/
```

配置文件：

```text
monitoring/monitoring-values-extra.yaml
monitoring/grafana-lb.yaml
monitoring/README.md
```

部署示例：

```powershell
helm upgrade --install monitoring <kube-prometheus-stack-chart-path> `
  -n monitoring `
  --create-namespace `
  -f monitoring/monitoring-values-extra.yaml
```

查看组件：

```powershell
kubectl get pods -n monitoring -o wide
kubectl get svc -n monitoring
```

临时暴露 Grafana：

```powershell
kubectl apply -f monitoring\grafana-lb.yaml
kubectl get svc grafana-lb -n monitoring
```

截图完成后删除临时公网 LoadBalancer：

```powershell
kubectl delete svc grafana-lb -n monitoring --ignore-not-found=true
```

PromQL 说明见：

```text
docs/prometheus-promql.md
```

## 十一、GitHub Actions CI/CD 附加题

流水线文件位于：

```text
.github/workflows/deploy-backend.yml
```

该流水线在 `main` 分支中 backend 代码或 workflow 文件变化时触发，流程为：

```text
checkout -> docker login -> docker build -> docker push -> kubectl set image -> rollout status
```

需要在 GitHub 仓库中配置以下 Secrets：

```text
SWR_USERNAME
SWR_PASSWORD
KUBE_CONFIG_B64
```

这些值不能提交到仓库中。仓库中只保留 Secret 名称引用。

CI/CD 说明见：

```text
docs/cicd-notes.md
```

## 十二、安全说明

仓库中不应提交以下内容：

```text
kubeconfig
KUBE_CONFIG_B64
SWR Token
AK/SK
GitHub Token
.env
任何真实生产密码
```

本项目中的 Kubernetes Secret 仅用于课程演示。实际项目中应使用更安全的密钥管理方式，并避免在公开仓库中保存可直接访问云资源的凭证。

## 十三、资源清理

课程验收完成后，建议清理公网入口和计费资源。

删除 Grafana 临时公网 Service：

```powershell
kubectl delete svc grafana-lb -n monitoring --ignore-not-found=true
```

查看 LoadBalancer Service：

```powershell
kubectl get svc -A
```

确认不再需要后，可在 CCE 控制台释放不使用的节点、ELB 和相关云硬盘，避免继续产生资源费用。

## 十四、文档说明

- `README.md`：项目总体说明和复现实验步骤。
- `docs/screenshot-checklist.md`：实验截图清单。
- `docs/prometheus-promql.md`：Prometheus 查询语句说明。
- `docs/cicd-notes.md`：CI/CD 流水线说明。
- `monitoring/README.md`：监控附加题部署说明。

最终提交时，建议同时提交实验报告 PDF 和 GitHub 仓库链接。
