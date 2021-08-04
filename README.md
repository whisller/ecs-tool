# ECS Tool
[![PyPI](https://img.shields.io/pypi/v/ecs-tool.svg)](https://pypi.org/project/ecs-tool/) ![](https://img.shields.io/pypi/pyversions/ecs-tool.svg) ![](https://img.shields.io/pypi/l/ecs-tool.svg)

[aws-ecs](https://docs.aws.amazon.com/cli/latest/reference/ecs/index.html) on steroids.

ecs-tool tries to eliminate common caveats for your day-to-day work with Elastic Container Service (ECS).

Dashboards with important information about your services, more intuitive CLI interface and more.

### New version (`0.10`) is still in Beta.

## Screenshots
<a href="https://user-images.githubusercontent.com/164009/127609861-145265c3-5b1a-4ed2-a55b-2d400f7b0975.png" title="Dashboard"><img width="150" alt="Dashboard" src="https://user-images.githubusercontent.com/164009/127609795-ac1a5684-a334-418b-932f-15880bfe7066.png"></a>
<a href="https://user-images.githubusercontent.com/164009/127610177-ca44d337-a2a3-469b-b413-8221e9c4598e.png" title="Cluster listing"><img width="150" alt="Cluster listing" src="https://user-images.githubusercontent.com/164009/127610175-c3ebd211-dc65-4770-8f69-360c1fb5bf89.png"></a>
<a href="https://user-images.githubusercontent.com/164009/127610437-3d2f153e-7554-4284-9454-cfed8e2a3ac8.png" title="Serices list"><img width="150" alt="Services list" src="https://user-images.githubusercontent.com/164009/127610439-e8d0b543-3062-47c8-918f-4edd30bdf6eb.png"></a>

## Summary of functionalities
### Cluster
* <a href="https://user-images.githubusercontent.com/164009/127610177-ca44d337-a2a3-469b-b413-8221e9c4598e.png">Listing of all clusters</a>
### Service
* <a href="https://user-images.githubusercontent.com/164009/127610437-3d2f153e-7554-4284-9454-cfed8e2a3ac8.png">Listing of all services</a>
* <a href="https://user-images.githubusercontent.com/164009/127609861-145265c3-5b1a-4ed2-a55b-2d400f7b0975.png">Dashboard</a>, which includes `CPUUtilization` and `MemoryUtilization` plots for service (refreshed automatically)
### Task
* Run task, returns information about ran task, e.g. logs output from it (refreshed automatically)
* Show list of running tasks
* Show single task, displays information about running task (refreshed automatically)
* Show tasks logs (refreshed automatically)

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

### Cluster
### List of available clusters
```shell
ecs cluster list
```

### Service
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

### Task
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

### List of running tasks
```shell
ecs task list [OPTIONS]

Options:
  --cluster TEXT
```

### Display information about ran task
```shell
ecs task show [OPTIONS] TASK_ID

Options:
  --cluster TEXT
```

### Display task logs
```shell
ecs task logs [OPTIONS] TASK_ID

Options:
  --cluster TEXT
```

## Can I use grep?
Yes! All commands results (but dashboards) can be filtered with `grep`
