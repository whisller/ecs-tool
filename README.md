# ECS Tool
[![PyPI](https://img.shields.io/pypi/v/ecs-tool.svg)](https://pypi.org/project/ecs-tool/) ![](https://img.shields.io/pypi/pyversions/ecs-tool.svg) ![](https://img.shields.io/pypi/l/ecs-tool.svg)

[aws-ecs](https://docs.aws.amazon.com/cli/latest/reference/ecs/index.html) on steroids.

ecs-tool tries to eliminate common caveats for your day-to-day work with Elastic Container Service (ECS).

Dashboards with important information about your services, more intuitive CLI interface and more.

## Some screenshots
[ecs services](https://github.com/whisller/ecs-tool/blob/master/screenshots/ecs-services-1.png) | [ecs tasks](https://github.com/whisller/ecs-tool/blob/master/screenshots/ecs-tasks-1.png) | [ecs task-definitions](https://github.com/whisller/ecs-tool/blob/master/screenshots/ecs-task-definitions-1.png) | [ecs task-log](https://github.com/whisller/ecs-tool/blob/master/screenshots/ecs-task-log-1.png)

## Installation & usage

### As python package
```shell
pip install ecs-tool

ecs

# with aws-vault
aws-vault exec my-aws-profile -- ecs 
```

### With docker
```shell
# build image
docker build -t ecs-tool

docker run -it --rm --name ecs-tool ecs-tool ecs

# with aws-vault
docker run -it --rm --env-file <(aws-vault exec my-aws-profile -- env | grep "^AWS_") --name ecs-tool ecs-tool ecs
```

## What `ecs-tool` can do?
List services, tasks, task definitions and logs for those tasks. All of those can be filtered by several attributes.

You can run task definition, here either it will automatically select latest version or you can specify number manually. 
There is an option to wait for results of this execution.

`ecs-tool` is grep friendly.
