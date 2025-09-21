kubectl apply -f ../deploy/k8s/namespace.yaml
kubectl apply -f ../deploy/k8s/configmap.yaml
kubectl apply -f ../deploy/k8s/secret-db.yaml
kubectl apply -f ../deploy/k8s/postgres-statefulset.yaml

kubectl apply -f ../deploy/k8s/cliente-deploy.yaml
kubectl apply -f ../deploy/k8s/cliente-svc.yaml
kubectl apply -f ../deploy/k8s/campanias-deploy.yaml
kubectl apply -f ../deploy/k8s/campanias-svc.yaml
kubectl apply -f ../deploy/k8s/pagos-deploy.yaml
kubectl apply -f ../deploy/k8s/pagos-svc.yaml
kubectl apply -f ../deploy/k8s/bff-deploy.yaml
kubectl apply -f ../deploy/k8s/bff-svc.yaml