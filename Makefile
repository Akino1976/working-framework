PROJECT := work-assignment
SERVICE_NAME := $(PROJECT)

VERSION ?= commit_$(shell git rev-parse --short HEAD)
ENVIRONMENT ?= dev
AWS_REGION ?= eu-west-1

export VERSION
export ENVIRONMENT
export AWS_REGION
export PACKAGE_NAME


COMPOSE_DEFAULT_FLAGS := -f docker-compose.yaml
COMPOSE_TEST_FLAGS := $(COMPOSE_DEFAULT_FLAGS) -f docker-compose.test.yaml

run-%:
	docker-compose $(COMPOSE_DEFAULT_FLAGS) run --rm $*

run-migrator:
	docker-compose $(COMPOSE_DEFAULT_FLAGS) run --rm db-migrator

run-mock:
	docker-compose $(COMPOSE_DEFAULT_FLAGS) run --rm aws-mock

setup-local-environment: provision

build-systemtests:
	docker-compose $(COMPOSE_TEST_FLAGS) build systemtests-base

systemtests: build-systemtests setup-local-environment
	docker-compose $(COMPOSE_TEST_FLAGS) run --rm systemtests

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
