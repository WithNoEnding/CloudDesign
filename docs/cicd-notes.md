# Optional Task 2: CI/CD Notes

The CI/CD workflow is implemented with GitHub Actions.

## Pipeline flow

1. Checkout source code.
2. Generate image tag from the Git commit hash.
3. Log in to Huawei Cloud SWR.
4. Build the backend Docker image.
5. Push the backend image to SWR.
6. Configure kubeconfig from GitHub Secrets.
7. Run `kubectl set image` to update the backend Deployment.
8. Wait for `kubectl rollout status` to finish.
9. Print the Deployment image and Pod status.

## GitHub Secrets

The workflow uses the following repository secrets. Their values must not be committed to GitHub.

- `SWR_USERNAME`
- `SWR_PASSWORD`
- `KUBE_CONFIG_B64`

## Validation commands

```bash
kubectl get deployment backend -o wide
kubectl get pods -l app=backend -o wide
kubectl get deployment backend -o jsonpath='{.spec.template.spec.containers[0].image}'; echo
```

The expected image tag format is:

```text
swr.cn-north-4.myhuaweicloud.com/cloud-course-2023112411/backend:ci-xxxxxxx
```

## CI, CD and GitOps

Continuous Integration focuses on automatic build and verification after code changes. In this project, GitHub Actions builds the backend image and pushes it to SWR.

Continuous Deployment focuses on releasing the build artifact to the running environment. In this project, GitHub Actions updates the Kubernetes Deployment image and waits for the rollout result.

Strict GitOps usually uses a controller such as Argo CD or Flux to continuously reconcile the cluster state with declarative files in Git. This project uses Git-triggered CI/CD and `kubectl set image`, so it is an automated deployment workflow, not a complete GitOps implementation.
