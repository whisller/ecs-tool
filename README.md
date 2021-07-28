# ECS Tool
[![PyPI](https://img.shields.io/pypi/v/ecs-tool.svg)](https://pypi.org/project/ecs-tool/) ![](https://img.shields.io/pypi/pyversions/ecs-tool.svg) ![](https://img.shields.io/pypi/l/ecs-tool.svg)

[aws-ecs](https://docs.aws.amazon.com/cli/latest/reference/ecs/index.html) on steroids.

ecs-tool tries to eliminate common caveats for your day-to-day work with Elastic Container Service (ECS).

Dashboards with important information about your services, more intuitive CLI interface and more.

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

### List of available clusters
```shell
ecs cluster list
```

### List of available services
```shell
ecs service list [OPTIONS]

Options:
  --cluster TEXT
```

### Dashboard for service
```shell
ecs service dashboard [OPTIONS] SERVICE

Options:
  --cluster TEXT
```

### Run task
```shell
ecs task run [OPTIONS] TASK_DEFINITION [COMMAND]...

Options:
  --cluster TEXT
```

`TASK_DEFINITION` - you can either provide full definition e.g. `my-definition:123` or just name, `my-definition`. If no number is provided, latest version is assumed.

## Can I use grep?
Yes! All commands results (but dashboards) can be filtered with `grep`
