### simple social media app
#### fastapi
* just using this to learn about microservices, s3, terraform, kubernetes

* i should put all of these in seperate repos for them to have different cicd pipelines later

* there's currently 4 microservices (post, comment, user, analytics)

* `/shared` is used for code that can be used throughout the microservices such as auth, database usage, and rate limiting middleware

* i am using terraform to provision a public s3 bucket to store photos

#### future plans:

Services:
* frontend

K8s:
* making deployments and services
* helm charts

etc:
* bash script to post everything to aws ecr and deploy the application
