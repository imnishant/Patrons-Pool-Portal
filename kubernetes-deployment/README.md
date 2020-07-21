This project can be deployed directly on to the kubernetes cluster by deploying "patrons-pool.yaml" and "mongodb.yaml" files in your k8s cluster that runs on the cloud.

### Use the below commands to deploy the application

```
kubectl apply -f patrons-pool.yaml
```
```
kubectl apply -f mongodb.yaml
```

If you running k8s cluster on the local vagrant machines the patrons-pool-service will show <pending> in the EXTERNAL-IP as the service is of type LoadBalancer and the Vagrant does not have an internal load balancer to balance the requests, wherein if you deploy the application in the k8s cluster running ithe cloud you will get an external-ip which you can share with the users and users can start using the application which will be running inside the kubernetes pods :)
