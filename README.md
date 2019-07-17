# ECS Tool
[![Build Status](https://travis-ci.org/whisller/ecs-tool.svg?branch=master)](https://travis-ci.org/whisller/ecs-tool) [![PyPI](https://img.shields.io/pypi/v/ecs-tool.svg)](https://pypi.org/project/ecs-tool/) ![](https://img.shields.io/pypi/pyversions/ecs-tool.svg) ![](https://img.shields.io/pypi/l/ecs-tool.svg)

CLI wrapper on top of "aws ecs" that tries to improve user experience and remove bottlenecks of work with AWS ECS.

AWS is great platform, you can manage your ECS by web console or ecs-cli. 
But both tools have their flaws, either speed or user interface.

That's why `ecs-tool` came to life, its aim is to be your day to day CLI tool for managing your ECS. 

It is in early stage of development though.

## Some screenshots
[ecs services](https://github.com/whisller/ecs-tool/blob/master/screenshots/ecs-services-1.png) | [ecs tasks](https://github.com/whisller/ecs-tool/blob/master/screenshots/ecs-tasks-1.png) | [ecs task-definitions](https://github.com/whisller/ecs-tool/blob/master/screenshots/ecs-task-definitions-1.png) | [ecs task-log](https://github.com/whisller/ecs-tool/blob/master/screenshots/ecs-task-log-1.png)

## Installation
```sh
pip install ecs-tool
```

## What `ecs-tool` can do?
List services, tasks, task definitions and logs for those tasks. All of those can be filtered by several attributes.

You can run task definition, here either it will automatically select latest version or you can specify number manually. 
There is an option to wait for results of this execution.

`ecs-tool` is grep friendly.
