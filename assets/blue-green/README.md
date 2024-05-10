# Lab 5: Blue/Green Deployments

## Objective

In this module you will:

* Update app stack to support blue/green deployments using AWS CodeDeploy in the production environment.
* Create a CodeDeploy application and deployment configuration.
* Update the pipeline stack to use CodeDeploy in the production stage.
* Add `appspec.yaml` and `taskdef.json` to the `cdk-workshop-2024` folder.

## Blue/Green Deployments

A blue/green deployment is a deployment strategy in which you create two separate, but identical environments. One environment (blue) is running the current application version and one environment (green) is running the new application version.

Using a blue/green deployment strategy increases application availability and reduces deployment risk by simplifying the rollback process if a deployment fails. Once testing has been completed on the green environment, live application traffic is directed to the green environment and the blue environment is deprecated.

#### Before deployment
![ecs-deployment-step-1.png](ecs-deployment-step-1.png)

#### During deployment
![ecs-deployment-step-2.png](ecs-deployment-step-2.png)

#### After deployment
![ecs-deployment-step-3.png](ecs-deployment-step-3.png)

## Update Prod Environment and the Code Pipeline

We already defined the infrastructure in the previous lab and we can re-use that code so all we need to do is update a production instance.

Before you do that, you will need to:

* Update and deploy the pipeline stack (remove the production stage).
* Update and deploy the prod app stack (add new Fargate service that supports CodeDeploy controller).
* Update and deploy the pipeline stack (add the production stage that deploys to the production application stack created in the above step).
* Add `appspec` and `taskdef` files.

## Add `taskdef.json` and `appspec.yaml` files

The artifacts `appspec.yaml` and `taskdef.json` are used by the CodeDeploy.

For Amazon ECS compute platform applications, the AppSpec file is used by CodeDeploy to determine your Amazon ECS task definition file. It also helps to determine the container and port in your replacement task set where your Application Load Balancer or Network Load Balancer reroutes traffic during a deployment. This is specified with the LoadBalancerInfo instruction in the AppSpec file.

REF:
* https://docs.aws.amazon.com/codepipeline/latest/userguide/tutorials-ecs-ecr-codedeploy.html
* https://docs.aws.amazon.com/codepipeline/latest/userguide/file-reference.html
* See also [artifact-size-limit-issue](../artifact-size-limit-issue)

### AppSpec

* In the AWS console, navigate to Elastic Container Service > Task definitions.
* Select the Task Definition of the prod cluster > select latest revision > copy the ARN of your Task Definition's revision (from the Overview section).
* Replace the value of `<Task_Definition>` in appspec with the ARN of your Task Definition.

### taskdef

* Copy the following (`taskdef.template.json`) to define our taskdef to deploy our container. Replace the values for `executionRoleArn`, `image`, and `family` with resources from your environment:
* In the AWS console, navigate to Elastic Container Service > Task definitions > select the Task Definition of the prod cluster > select latest revision.
* For executionRoleArn, select the Task execution role, which will take you to the IAM console. Copy the ARN and replace the executionRoleArn below.
* For image, scroll down to the Containers section, and copy the details below the Image column. Replace the image below.
* For family, switch to the JSON tab, and copy the family value from the task_definition.json file. Replace the family details below.

---

![blue-green-deployment1.png](blue-green-deployment1.png)
![blue-green-deployment2.png](blue-green-deployment2.png)
