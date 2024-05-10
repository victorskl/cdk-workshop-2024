# AWS Modern DevOps Immersion Day - Victoria

`vic-cicd-24`

## Notes

* `git log` to trail each lab session and corresponding changes.
* `git tag --list` for major break away; such as `baseline`, `blue-green`.
* I use localised cdk.
* I use `Makefile` to record mnemonic CLI commands. Do observe those.
* I took lots of screen-mo in `assets` [folder](assets). Look around.
* Interesting topics:
  * [gated-delivery-deployment](assets/gated-delivery-production) (or `baseline`)
  * [artifact-size-limit-issue](assets/artifact-size-limit-issue)
  * [blue-green-deployment](assets/blue-green)

(TL;DR)
```
brew bundle
npm install
npx cdk --version

export AWS_PROFILE=aws-day

cd app-cdk
make cdk-list
make cdk-diff
make cdk-synth
make cdk-destroy
```

## CDK Workshop 2024

We will be using practices such as:

- Developing web applications using Docker containers.
- Setting up a source control service to manage source code changes.
- Continuous Integration to automate building and testing.
- Continuous Deployment to automatically deploy to our test environment.
- Continuous Delivery to approve deployments to our production environment.
- Infrastructure as Code to define all the steps we take in code.


### Technology stack

We will be writing our application and infrastructure code in either TypeScript or Python using the following AWS CI/CD pipeline components and services:

- Docker, Flask Python application
- AWS VPC (Virtual Private Cloud) and Subnets
- AWS EC2, Application Load Balancer (ALB)
- AWS Cloud Development Kit (CDK)
- AWS CloudFormation
- AWS CodeCommit
- AWS CodeBuild
- AWS CodePipeline
- Amazon Elastic Container Registry (ECR)
- Amazon Elastic Container Service (ECS), Fargate

### Additional

* CodeWhisperer // Amazon Q 
* CodeCatalyst
