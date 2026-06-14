# 云计算课程设计项目

姓名：刘彬彬  
学号：2023112411

本项目包含第一部分云计算平台搭建所需的 Flask 后端、Nginx 前端、Redis、本地 docker compose、K8s YAML；也包含第二部分 Spark 数据分析脚本。

## 目录说明

```text
backend/                 Flask API 后端
frontend/                Nginx 前端页面
k8s/                     Kubernetes YAML 模板，镜像地址使用 __SWR__ 占位
spark/                   Spark 数据分析代码和豆瓣电影数据
scripts/                 PowerShell 脚本
docs/截图清单.md         报告需要的截图清单
report/screenshots/      建议保存截图的位置
```

## 第一步：本地联调

在 Windows PowerShell 中进入项目根目录：

```powershell
cd D:\你的路径\cloud-course-design-complete
```

启动本地服务：

```powershell
docker compose up --build
```

浏览器访问：

```text
http://localhost:8080
```

需要截图：

1. 页面显示姓名、学号，并且 `/api/ping` 返回 `{"status":"ok"}`。
2. PowerShell 后端日志出现 `Received request: /api/ping`。

## 第二步：构建并推送 backend/frontend 镜像到 SWR

进入华为云 SWR 控制台，先创建组织，记下：

- Region，例如 `cn-east-3`
- 组织名，例如 `cloud-course-2023112411`
- AK
- SWR 登录指令里的临时 Token。注意不是 IAM 永久 SK。

执行：

```powershell
.\scripts\02-build-and-push-swr.ps1 -Region cn-east-3 -Org 你的组织名 -Ak 你的AK -Token "你的SWR临时Token"
```

推送完成后，在 SWR 控制台截图，要求能看到：

- `backend:v1`
- `frontend:v1`

## 第三步：创建 CCE 集群

在华为云 CCE 控制台创建 Kubernetes 集群：

- Kubernetes 版本：>= 1.27
- 网络插件：默认 Yangtse CNI
- Worker 节点：至少2个
- 节点规格：建议先 2vCPU / 4GB，不够再加 2vCPU / 8GB

创建完成后，在 CCE 控制台下载 kubeconfig，配置 kubectl。

验证：

```powershell
kubectl get nodes -o wide
```

截图要求：节点 Ready，并显示 VERSION 列。

## 第四步：生成 K8s YAML

把 `k8s/` 里的 `__SWR__` 替换为你的 SWR 地址：

```powershell
.\scripts\03-render-k8s.ps1 -Region cn-east-3 -Org 你的组织名
```

生成结果在：

```text
k8s-rendered/
```

## 第五步：部署到 CCE

先部署配置、PVC、Redis、后端、Service、前端：

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

应返回：

```json
{"status":"ok"}
```

## 第六步：Redis 持久化验证

查看 Redis Pod 名称：

```powershell
kubectl get pods
```

进入 Redis：

```powershell
kubectl exec -it <redis-pod-name> -- redis-cli -a redis123456
```

写入：

```redis
SET testkey hello
GET testkey
```

删除 Redis Pod：

```powershell
kubectl delete pod <redis-pod-name>
```

等待重建后再次查询：

```powershell
kubectl exec -it <new-redis-pod-name> -- redis-cli -a redis123456 GET testkey
```

返回 `hello` 即可截图。

## 第七步：ConfigMap Volume 挂载验证

查看前端 Pod 名称：

```powershell
kubectl get pods
```

进入前端 Pod 查看 Nginx 配置：

```powershell
kubectl exec -it <frontend-pod-name> -- cat /etc/nginx/conf.d/default.conf
```

如果修改了 `06-frontend-nginx-configmap.yaml`，由于本项目使用 subPath 挂载，修改后建议删除 frontend Pod 让 Deployment 重建：

```powershell
kubectl apply -f k8s-rendered\06-frontend-nginx-configmap.yaml
kubectl delete pod <frontend-pod-name>
```

## 第八步：HPA 弹性伸缩

确认指标可用：

```powershell
kubectl top nodes
kubectl top pods
```

部署 HPA：

```powershell
kubectl apply -f k8s-rendered\08-hpa.yaml
kubectl get hpa
```

一个窗口监控：

```powershell
kubectl get pods -w
```

另一个窗口压测：

```powershell
ab -n 10000 -c 200 http://<ELB-IP>/api/ping
```

Windows 没有 ab 时，可以使用下面的 PowerShell 简易压测：

```powershell
1..2000 | ForEach-Object { Start-Job { Invoke-WebRequest -UseBasicParsing http://<ELB-IP>/api/ping | Out-Null } }
```

## 第二部分 Spark 简要说明

README 中的离线资源包需要先 `docker load`，重新打 tag 到自己的 SWR，再 push 到 SWR。Spark 分析脚本在 `spark/analysis.py`，数据在 `spark/data/douban_movies.csv`。

构建 Spark 分析镜像前，需保证你已经把 `pyspark:v9` 推送到了自己的 SWR。

```powershell
.\scripts\04-build-spark-analysis.ps1 -Region cn-east-3 -Org 你的组织名 -Ak 你的AK -Token "你的SWR临时Token"
```

然后把 `spark/sparkapplication-analysis.yaml` 里的 `__SWR__` 替换为自己的 SWR 地址，提交：

```powershell
kubectl apply -f spark\sparkapplication-analysis.yaml
kubectl get pods
kubectl logs <driver-pod-name>
```
