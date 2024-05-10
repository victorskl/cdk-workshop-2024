# CodePipeline CodeDeploy Artifact Size Limit

You will encounter CodePipeline failed with the following message:

> Exception while trying to read the task definition artifact file from: Artifact_Source_CodeCommit.

See screen-mo:
- [codepipeline-console-error1.png](codepipeline-console-error1.png)
- [codepipeline-console-error2.png](codepipeline-console-error2.png)
- [codepipeline-console-error3.png](codepipeline-console-error3.png)

## Q

I had chat with Q. See [convo](convo-with-Q.png) screen-mo. _(Well it is part of the workshop activity; advocate to deal with as such debugging issue. Right?)_

Q seems nice. But, Q couldn't pinpoint to anything concrete leading pointers. Perhaps, Q need to be trained better from SO topics and/or AWS doco _(:shrug: i don't know; next)_.

## Google & SO

So. Fallback to classic technique; [Google](https://www.google.com/search?q=Exception+while+trying+to+read+the+task+definition+artifact+file+from%3A+Artifact_Source_CodeCommit) #ftw.

2 top hits from page rank pointers artifact size limit 3 MB:

- https://stackoverflow.com/questions/57216053/invalid-action-configuration-exception-while-trying-to-read-the-task-definition
- https://docs.aws.amazon.com/codepipeline/latest/userguide/troubleshooting.html#troubleshooting-ecstocodedeploy-size

Obviously, this repo `assets` directory contains lots of screen-mo. So yeah.! Obviously. 

Let confirm that with latest pipeline execution artifact:

```
aws s3 ls --human-readable s3://pipeline-stack-cicdpipelineartifactsbucketf7b9aed3-hkrwu20hww4h/pipeline-stack-CICDP/Artifact_S/wQSUX8C
2024-05-10 11:16:15    5.4 MiB wQSUX8C
```

See screen-mo for completeness - [codepipeline-source-artifact-size.png](codepipeline-source-artifact-size.png)

## AWS

Quotas in AWS CodePipeline

https://docs.aws.amazon.com/codepipeline/latest/userguide/limits.html

> Maximum size of artifacts in a source stage
> 
> * Exception: If you are using AWS Elastic Beanstalk to deploy applications, the maximum artifact size is always 512 MB.
> * Exception: If you are using AWS CloudFormation to deploy applications, the maximum artifact size is always 256 MB.
> * Exception: If you are using the **CodeDeployToECS** action to deploy applications, the maximum artifact size is always 3 MB.

## Fix

This leads to [`CodeDeployToECS`](https://docs.aws.amazon.com/codepipeline/latest/userguide/action-reference-ECSbluegreen.html) action of CodePipeline Blue/Green deployment. In CDK v2 API, the construct class is called [`CodeDeployEcsDeployAction`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_codepipeline_actions.CodeDeployEcsDeployAction.html).

I am with Python. So.

- https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_codepipeline_actions/CodeDeployEcsDeployAction.html
- https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_codepipeline/ArtifactPath.html#aws_cdk.aws_codepipeline.ArtifactPath

However. Source artifact location (git clone) is still >3MB. We switch to leverage Docker build output artifact location.

See [codepipeline-docker-artifact-size1.png](codepipeline-docker-artifact-size1.png)

TL;DR

```
        pipeline.add_stage(
            stage_name='Deploy-Production',
            actions=[
                codepipeline_actions.ManualApprovalAction(
                    action_name='Approve-Prod-Deploy',
                    run_order=1
                ),
                codepipeline_actions.CodeDeployEcsDeployAction(
                    action_name='ABlueGreen-deployECS',
                    deployment_group=prod_ecs_deployment_group,
                    # app_spec_template_input=source_output,
                    # task_definition_template_input=source_output,
                    app_spec_template_file=docker_build_output.at_path('appspec.yaml'),
                    task_definition_template_file=docker_build_output.at_path('taskdef.json'),
                    run_order=2
                )
            ]
        )
```
