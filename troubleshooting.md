# Harness CLI Troubleshooting Guide

## Exec format error

Error:
```
-bash: /home/ubuntu/harness: cannot execute binary file: Exec format error
```

OS: Ubuntu 22.04.2 LTS

CLI Version: harness-v0.0.15-Preview-linux-arm64.tar.gz

Issue:
- By downloading arm64 binary on amd64 arch OS throws this error

Resolution:
- Use amd64 binary.

## application 'gitops-application' in namespace 'default' is not allowed to use project '237d0516'

Error:
```
failed to create app in argo: failed to execute create app task: rpc error: code = Unknown desc = error while validating and normalizing app: error getting application's project: application 'gitops-application' in namespace 'default' is not allowed to use project '237d0516'
```

CLI Version: harness-v0.0.15-Preview-linux-arm64.tar.gz

Issue:
- GitOps Agent installed in XXX namespace on the Kubernetes setup.
- GitOps Application Metadata namespace in the YAML contains a different/target namespace where we want to sync the microservice app.

Resolution:
- GitOps Application Metadata namespace in the YAML should be the same namespace where GitOps Agent is installed.





