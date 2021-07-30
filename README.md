# ECS Tool
[![PyPI](https://img.shields.io/pypi/v/ecs-tool.svg)](https://pypi.org/project/ecs-tool/) ![](https://img.shields.io/pypi/pyversions/ecs-tool.svg) ![](https://img.shields.io/pypi/l/ecs-tool.svg)

[aws-ecs](https://docs.aws.amazon.com/cli/latest/reference/ecs/index.html) on steroids.

ecs-tool tries to eliminate common caveats for your day-to-day work with Elastic Container Service (ECS).

Dashboards with important information about your services, more intuitive CLI interface and more.

## Screenshots
[[[https://github.com/whisller/ecs-tool/blob/docs/img/dashboard-small.png|alt=Dashboard]]](https://github.com/whisller/ecs-tool/blob/docs/img/dashboard-big.png)

## Summary of functionalities
### Cluster
* Listing of all clusters
### Service
* Listing of all services
* Dashboard, which includes `CPUUtilization` and `MemoryUtilization` plots for service (refreshed automatically)
### Task
* Run task, returns information about ran task, e.g. logs output from it (refreshed automatically)

More detailed information about available commands below.

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
  --network-configuration TEXT
  --capacity-provider-strategy TEXT
```

`TASK_DEFINITION` - you can either provide full definition e.g. `my-definition:123` or just name, `my-definition`. If no number is provided, latest version is assumed.

`[COMMAND]` - any command that should be executed on ECS task

Examples:

**Running with Fargate**
```shell
ecs task run epsy-dynks --capacity-provider-strategy '{"capacityProvider": "FARGATE"}' --network-configuration '{"awsvpcConfiguration":{"subnets":["subnet-1234567890"],"securityGroups":["sg-123456789"],"assignPublicIp":"DISABLED"}}' --  my_command subcommand --one-option --another-option="test"
```

## Can I use grep?
Yes! All commands results (but dashboards) can be filtered with `grep`
