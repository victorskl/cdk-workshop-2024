from constructs import Construct
from aws_cdk import (
    Stack,
    aws_codecommit as codecommit,
    CfnOutput,
    aws_codepipeline as codepipeline,
    aws_codebuild as codebuild,
    aws_codepipeline_actions as codepipeline_actions,
)


class PipelineCdkStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
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
            build_spec=codebuild.BuildSpec.from_object({
                'version': '0.2'
            }),
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
