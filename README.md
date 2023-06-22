# slowking

This is a proof of concept. It is an attempt to create a benchmarking app/tool with an event-driven architecture.

- [slowking](#slowking)
  - [Design Principles](#design-principles)
  - [Setup](#setup)
  - [Design Notes](#design-notes)
    - [Commands](#commands)
      - [`start_benchmark`](#start_benchmark)
    - [Events](#events)
    - [Database Tables](#database-tables)

## Design Principles

- Event driven architecture
- Can benchmark any target Eigen Platform
  - Local
  - Docker
  - k8s
- No infrastructure provisioning. It relies on a benchmarkable Platform to already be running
- Benchmark reports will be in CSV format

## Setup

```shell
docker-compose up --build
```

There are also various tasks in the Taskfile:

```shell
task --list
```


## Design Notes

### Commands

> Commands are sent by one actor to another specific actor with the expectation that a particular thing will happen as a result.

#### `start_benchmark`

This is the start point and requires a dedicated endpoint.

`/api/v1/benchmarks/start`

Payload (WIP):

```json
{
    "benchmark_name": "str",
    "benchmark_type": "str e.g. latency",
    "benchmark_url": "str e.g. localhost:3000",
    // creds to log into the above instance
    "username": "str",
    "password": "str"
}
```

### Events

> Events are broadcast by an actor to all interested listeners.
> We often use events to spread the knowledge about successful commands.
> Events capture facts about things that happened in the past.

- get artifacts (for POC, have them locally and just use them)
- login to instance? (mechanics, think is probably just part of creating a project)
- create project
- Upload documents
- Doc upload started (instrumented event sent by Eigen application)
- Doc upload completed (instrumented event sent by Eigen application)
- All docs uploaded (a check to see if all docs are uploaded)
- Create benchmark report (simply log or if time create a csv, maybe take the code from Geo?)

### Database Tables

- benchmark
  - id | uuid
  - name
  - type e.g. latency
  - infra e.g. docker, k8s or local
  - project (doc_type)
  - documents (ids) ?
  - username
  - password
- document
  - (used to measure upload latency)
  - fk to benchmark
  - (fk to project ?)
  - id
  - doc upload start timestamp (utc)
  - doc upload end timestamp (utc)
  - doc upload total time
