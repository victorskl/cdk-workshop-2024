#!/usr/bin/env python3
import aws_cdk as cdk

from app_cdk.app_cdk_stack import AppCdkStack
from app_cdk.pipeline_cdk_stack import PipelineCdkStack
from app_cdk.ecr_cdk_stack import EcrCdkStack

app = cdk.App()

# app_stack = AppCdkStack(
#     app,
#     'app-stack'
# )

ecr_stack = EcrCdkStack(
    app,
    'ecr-stack'
)

test_app_stack = AppCdkStack(
    app,
    'test-app-stack',
    ecr_repository=ecr_stack.ecr_data
)

prod_app_stack = AppCdkStack(
    app,
    'prod-app-stack',
    ecr_repository=ecr_stack.ecr_data
)

pipeline_stack = PipelineCdkStack(
    app,
    'pipeline-stack',
    ecr_repository=ecr_stack.ecr_data,
    test_app_fargate=test_app_stack.ecs_service_data,
    # prod_app_fargate=prod_app_stack.ecs_service_data,  # commented for blue-green deployment
)

app.synth()
