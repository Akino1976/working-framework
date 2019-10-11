PROJECT := work-assignment
SERVICE_NAME := $(PROJECT)

VERSION ?= commit_$(shell git rev-parse --short HEAD)
ENVIRONMENT ?= test
AWS_REGION ?= eu-west-1

export VERSION
export ENVIRONMENT
export AWS_REGION
export PACKAGE_NAME

COMPOSE_DEFAULT_FLAGS := -f docker-compose.yaml
COMPOSE_TEST_FLAGS := $(COMPOSE_DEFAULT_FLAGS) -f docker-compose.test.yaml

validate-templates:
	aws --profile serdar cloudformation validate-template --template-body file://infrastructure/cfn-$(SERVICE_NAME)-persistence.yml --region eu-west-1


%-persistence:
	aws --region $(REGION) cloudformation $*-stack \
		--stack-name $(SERVICE_NAME)-persistence-$(ENVIRONMENT) \
		--template-body file://infrastructure/cfn-$(SERVICE_NAME)-persistence.yml \
		--parameters \
			ParameterKey=Environment,ParameterValue=$(ENVIRONMENT) \
		--tags \
			Key=Component,Value=$(SERVICE_NAME) \
			Key=Environment,Value=dev \
			Key=BusinessArea,Value=BusinessIntelligence \
			Key=Access,Value=Internal \
			Key=InfrastructureType,Value=Storage \
			Key=Name,Value=$(SERVICE_NAME)-persistence \
		--profile serdar
	aws --region $(REGION) cloudformation wait stack-$*-complete \
		--stack-name $(SERVICE_NAME)-persistence-$(ENVIRONMENT)


run-%:
	docker-compose $(COMPOSE_DEFAULT_FLAGS) run --rm $*

build-%:
	docker-compose $(COMPOSE_TEST_FLAGS) build $*

run-migrator:
	docker-compose $(COMPOSE_DEFAULT_FLAGS) run --rm db-migrator

setup-local-environment: provision

build-app: run-migrator
	docker-compose $(COMPOSE_TEST_FLAGS) build app

run-detached: build-app
	docker-compose $(COMPOSE_FLAGS) run -d app

build-systemtests:
	docker-compose $(COMPOSE_TEST_FLAGS) build systemtests-base

systemtests: run-detached build-systemtests setup-local-environment
	docker-compose $(COMPOSE_TEST_FLAGS) run --rm systemtests

systemtests-watch: run-detached build-systemtests setup-local-environment
	docker-compose $(COMPOSE_TEST_FLAGS) run --rm systemtests-watch

provision:
	docker-compose run --rm provisioner

stop-all-containers:
	docker ps -q | xargs -I@ docker kill @

clear-all-containers: stop-all-containers
	docker ps -aq | xargs -I@ docker rm @

clear-volumes: clear-all-containers
	docker volume ls -q | xargs -I@ docker volume rm @

clear-images: clear-volumes
	docker images -q | uniq | xargs -I@ docker rmi -f @

test:
	docker run  --rm -it \
		-e AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id --profile serdar) \
		-e AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key --profile serdar) \
		-e AWS_SESSION_TOKEN=$(aws configure get aws_session_token --profile serdar) \
		-e DSN='storage' \
			work-framework:commit_2d9a116
