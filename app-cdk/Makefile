cdk-bootstrap:
	@export AWS_PROFILE=aws-day
	@npx cdk bootstrap

cdk-list:
	@npx cdk list

cdk-diff:
	@npx cdk diff

cdk-diff-app:
	@npx cdk diff -e app-stack

cdk-diff-pipeline:
	@npx cdk diff -e pipeline-stack

cdk-synth:
	@npx cdk synth pipeline-stack

cdk-synth-template:
	@mkdir -p .local/
	@npx cdk synth pipeline-stack > .local/template.yml && code .local/template.yml

cdk-deploy-pipeline:
	@npx cdk deploy pipeline-stack

cdk-deploy-ecr:
	@npx cdk deploy ecr-stack

cdk-deploy-test:
	@npx cdk deploy test-app-stack

cdk-deploy-prod:
	@npx cdk deploy prod-app-stack
