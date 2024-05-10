import os

from constructs import Construct
from aws_cdk import (
    Stack,
    aws_codecommit as codecommit,
    CfnOutput,
    aws_codepipeline as codepipeline,
    aws_codebuild as codebuild,
    aws_codepipeline_actions as codepipeline_actions,
    aws_iam as iam,
    aws_ssm as ssm,
    aws_codedeploy as codedeploy,
)


class PipelineCdkStack(Stack):

    def __init__(self, scope: Construct, id: str, ecr_repository, test_app_fargate, prod_app_fargate,
                 green_target_group, green_load_balancer_listener, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Creates a CodeCommit repository called 'CICD_Workshop'
        repo = codecommit.Repository(
            self, 'CICD_Workshop',
            repository_name='CICD_Workshop',
            description='Repository for my application code and infrastructure'
        )

        CfnOutput(
            self, 'CodeCommitRepositoryUrl',
            value=repo.repository_clone_url_grc
        )

        # step 1
        pipeline = codepipeline.Pipeline(
            self, 'CICD_Pipeline',
            cross_account_keys=False
        )

        # step 2
        code_quality_build = codebuild.PipelineProject(
            self, 'CodeBuild',

            # externalise buildspec to buildspec_test.yml

            # Create the build specification for the code quality stage
            #
            # A buildspec is a collection of build commands and related settings, in YAML format, that CodeBuild uses
            # to run a build. You can include a buildspec as part of the source code, or you can define a buildspec
            # when you create a build project.
            #
            # By default, the Code Quality stage we defined using CodeBuild will look for a buildspec.yml file in
            # the current directory.
            #
            # However, in this workshop we will be using AWS CodeBuild in multiple stages so will require multiple
            # buildspecs to define each stage. The good news is that we can see from the CDK reference for CodeBuild
            # that there is a method fromSourceFilename that we can use if we want to use a file different from
            # buildspec.yml.

            # build_spec=codebuild.BuildSpec.from_object({
            #     'version': '0.2'
            # }),
            build_spec=codebuild.BuildSpec.from_source_filename('./buildspec_test.yml'),

            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
                compute_type=codebuild.ComputeType.LARGE,
            ),
        )

        # step 3
        source_output = codepipeline.Artifact()
        unit_test_output = codepipeline.Artifact()

        source_action = codepipeline_actions.CodeCommitSourceAction(
            action_name='CodeCommit',
            repository=repo,
            output=source_output,
            branch='main'
        )

        pipeline.add_stage(
            stage_name='Source',
            actions=[source_action]
        )

        build_action = codepipeline_actions.CodeBuildAction(
            action_name='Unit-Test',
            project=code_quality_build,
            input=source_output,  # The build action must use the CodeCommitSourceAction output as input.
            outputs=[unit_test_output]
        )

        pipeline.add_stage(
            stage_name='Code-Quality-Testing',
            actions=[build_action]
        )

        # add docker build and push artifact stage

        docker_build_project = codebuild.PipelineProject(
            self, 'Docker Build',
            build_spec=codebuild.BuildSpec.from_source_filename('./buildspec_docker.yml'),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
                compute_type=codebuild.ComputeType.LARGE,
                environment_variables={
                    'IMAGE_TAG': codebuild.BuildEnvironmentVariable(
                        type=codebuild.BuildEnvironmentVariableType.PLAINTEXT,
                        value='latest'
                    ),
                    'IMAGE_REPO_URI': codebuild.BuildEnvironmentVariable(
                        type=codebuild.BuildEnvironmentVariableType.PLAINTEXT,
                        value=ecr_repository.repository_uri
                    ),
                    'AWS_DEFAULT_REGION': codebuild.BuildEnvironmentVariable(
                        type=codebuild.BuildEnvironmentVariableType.PLAINTEXT,
                        value=os.environ['CDK_DEFAULT_REGION']
                    )
                }
            ),
        )

        docker_build_project.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'ecr:GetAuthorizationToken',
                'ecr:BatchCheckLayerAvailability',
                'ecr:GetDownloadUrlForLayer',
                'ecr:GetRepositoryPolicy',
                'ecr:DescribeRepositories',
                'ecr:ListImages',
                'ecr:DescribeImages',
                'ecr:BatchGetImage',
                'ecr:InitiateLayerUpload',
                'ecr:UploadLayerPart',
                'ecr:CompleteLayerUpload',
                'ecr:PutImage'
            ],
            resources=['*'],
        ))

        docker_build_output = codepipeline.Artifact()

        docker_build_action = codepipeline_actions.CodeBuildAction(
            action_name='Docker-Build',
            project=docker_build_project,
            input=source_output,
            outputs=[docker_build_output]
        )

        pipeline.add_stage(
            stage_name='Docker-Push-ECR',
            actions=[docker_build_action]
        )

        # DOCKER IMAGE SIGNER - SKIPPING THIS PART
        # See https://docs.aws.amazon.com/signer/latest/developerguide/Welcome.html

        ssmParameter = ssm.StringParameter(
            self, 'SignerProfileARN',
            parameter_name='signer-profile-arn',
            string_value='Signing Profile ARN',
        )

        docker_build_project.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'ssm:GetParametersByPath',
                'ssm:GetParameters',
            ],
            resources=['*'],
        ))

        # THE FOLLOWING ONLY AVAILABLE AS TYPESCRIPT CODE IN AWS TUTORIAL

        # Updating the CodeBuild service role's permissions to allow access to AWS Signer

        # We will be signing the container images via CodeBuild, hence we need to update the CodeBuild service
        # role so that during the builds CodeBuild can access AWS Signer and sign the container images.

        #     const signerPolicy = new iam.PolicyStatement({
        #       effect: iam.Effect.ALLOW,
        #       resources: ['*'],
        #       actions: [
        #         'signer:PutSigningProfile',
        #         'signer:SignPayload',
        #         'signer:GetRevocationStatus',
        #       ],
        #     });
        #
        #     dockerBuild.addToRolePolicy(signerPolicy);

        # THEN, OVERWRITE buildspec_docker.yml CONTENT FROM buildspec_docker.signer.yml
        # THEN, PUSH `cdk deploy pipeline-stack`

        # Continuous Delivery to Test Environment
        pipeline.add_stage(
            stage_name='Deploy-Test',
            actions=[
                codepipeline_actions.EcsDeployAction(
                    action_name='Deploy-Fargate-Test',
                    service=test_app_fargate.service,
                    input=docker_build_output
                )
            ]
        )

        # Gated Delivery to Production Environment
        #
        # (NOTE)
        # Need to push `pipeline-stack` once to create the stage into pipeline, after adding the following stage
        #   cd app-cdk
        #   npx cdk deploy pipeline-stack
        #
        # Afterward, making any commit to repo would go through the pipeline (gated-delivery-production1.png)
        # and pause at `Deploy-Production` stage and waiting for manual approval (gated-delivery-production2.png)
        # See complete pipeline transitions at `assets/gated-delivery-production/*.png`

        # pipeline.add_stage(
        #     stage_name='Deploy-Production',
        #     actions=[
        #         codepipeline_actions.ManualApprovalAction(
        #             action_name='Approve-Prod-Deploy',
        #             run_order=1,
        #         ),
        #         codepipeline_actions.EcsDeployAction(
        #             action_name='Deploy-Production',
        #             service=prod_app_fargate.service,
        #             input=docker_build_output,
        #             run_order=2,
        #         )
        #     ]
        # )

        ###
        # BLUE-GREEN DEPLOYMENT
        #

        # Add a CodeDeploy Elastic Container Service (ECS) application.
        ecs_code_deploy_app = codedeploy.EcsApplication(
            self, 'my-app',
            application_name='my-app'
        )

        # Add a CodeDeploy deployment group that shifts 10 percent of traffic every minute until all traffic is shifted.
        prod_ecs_deployment_group = codedeploy.EcsDeploymentGroup(
            self, 'my-app-dg',
            service=prod_app_fargate.service,
            blue_green_deployment_config=codedeploy.EcsBlueGreenDeploymentConfig(
                blue_target_group=prod_app_fargate.target_group,
                green_target_group=green_target_group,
                listener=prod_app_fargate.listener,
                test_listener=green_load_balancer_listener
            ),
            deployment_config=codedeploy.EcsDeploymentConfig.LINEAR_10_PERCENT_EVERY_1_MINUTES,
            application=ecs_code_deploy_app
        )

        # Add a Prod stage with action CodeDeployEcsDeployAction:
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
                    app_spec_template_file=source_output.at_path('appspec.yaml'),
                    task_definition_template_file=source_output.at_path('taskdef.json'),
                    run_order=2
                )
            ]
        )

        """
        NOTE:
        The `source_output` artifact (git clone checkout) could be big for CodeDeploy input, 3MB limit. It hits:
        
            Exception while trying to read the task definition artifact file from: Artifact_Source_CodeCommit.
        
        See assets/artifact-size-limit-issue/README.md
        """
