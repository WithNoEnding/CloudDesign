# CI/CD 流水线说明

本项目使用 GitHub Actions 完成附加题 2 的 CI/CD 流水线。流水线文件位于：

```text
.github/workflows/deploy-backend.yml
```

## 触发条件

当前 workflow 在以下情况触发：

```text
push 到 main 分支，并且 backend/ 或 .github/workflows/deploy-backend.yml 发生变化
```

这样可以避免每次修改文档都触发镜像构建和部署。

## 流水线流程

1. 拉取 GitHub 仓库代码。
2. 使用 Git commit hash 生成镜像 tag，格式为 `ci-xxxxxxx`。
3. 登录华为云 SWR。
4. 构建 backend Docker 镜像。
5. 推送 backend 镜像到 SWR。
6. 从 GitHub Secrets 解码 kubeconfig。
7. 执行 `kubectl set image` 更新 CCE 中的 backend Deployment。
8. 执行 `kubectl rollout status` 等待滚动更新完成。
9. 输出 Deployment、Pod 状态和当前镜像地址。

## GitHub Secrets

workflow 使用以下仓库 Secrets：

```text
SWR_USERNAME
SWR_PASSWORD
KUBE_CONFIG_B64
```

仓库中只能保存 Secret 名称引用，不能提交这些值本身。

## 验证命令

```bash
kubectl get deployment backend -o wide
kubectl get pods -l app=backend -o wide
kubectl get deployment backend -o jsonpath='{.spec.template.spec.containers[0].image}'; echo
```

期望镜像格式：

```text
swr.cn-north-4.myhuaweicloud.com/cloud-course-2023112411/backend:ci-xxxxxxx
```

## CI、CD 与 GitOps 区别

CI 表示持续集成，重点是代码提交后的自动构建和检查。本项目中，GitHub Actions 会在代码更新后自动构建 backend 镜像。

CD 表示持续部署，重点是将构建产物发布到运行环境。本项目中，流水线会把新镜像推送到 SWR，并更新 Kubernetes Deployment。

GitOps 通常要求由 Argo CD 或 Flux 这类集群控制器持续对比 Git 仓库中的声明式配置，并自动同步集群状态。本项目使用 GitHub Actions 直接执行 `kubectl set image`，属于自动化部署流程，不是完整 GitOps 实现。
