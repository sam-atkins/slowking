# slowking

This is a proof of concept benchmarking app/tool with an event-driven architecture.

- [slowking](#slowking)
  - [What is slowking?](#what-is-slowking)
  - [Design Principles](#design-principles)
  - [Local Dev](#local-dev)
  - [Database Migrations](#database-migrations)
  - [Design Notes](#design-notes)
    - [Commands](#commands)
    - [Events](#events)
    - [Domain Models](#domain-models)
    - [Database Tables](#database-tables)
    - [Unit of Work](#unit-of-work)
  - [Open Issues](#open-issues)
  - [Closed Issues](#closed-issues)
    - [Concurrent DB connection issues](#concurrent-db-connection-issues)
      - [Solution 1](#solution-1)
      - [Solution 2](#solution-2)

## What is slowking?

At [Eigen](https://eigentech.com/), we have a benchmarking tool called `slowbro`. This tool benchmarks latency of document upload amongst other things.

In the process of learning about event driven architecture, I had the idea of adding instrumentation to an Eigen application which would send events via HTTP to a new tool that would process the events and provided a benchmark report. From `slowbro` to `slowking` 😀.

In this POC repo, the slowking application is the majority of the code and in order for it to be standalone and work as a demo, the Eigen application is mocked out with a few simple endpoints for document upload.

## Design Principles

- Event driven architecture
- Can benchmark any target Eigen Platform
  - Local
  - Docker
  - k8s
- No infrastructure provisioning. It relies on a benchmarkable Platform to already be running
- Benchmark reports in CSV format

## Local Dev

```shell
task build && task up
```

Following are available:

- Swagger Docs for the Slowking API: http://0.0.0.0:8091/docs
- MailHog UI: http://0.0.0.0:18025/

There are also various tasks in the Taskfile:

```shell
task --list
```

## Database Migrations

Alembic is used for migrations. To create a migration run this command in the activated venv.

```shell
alembic revision -m "<migration summary goes here>"
```

As the models are imperatively mapped, Alembic does not autogenerate the migration. The above command generates a 'template' which needs to be edited.

Migrations are run as part of the docker-entrypoint script. To upgrade or downgrade migrations, exec into the running container.

Link to [Alembic documentation](https://alembic.sqlalchemy.org/en/latest/index.html).

## Design Notes

### Commands

> Commands are sent by one actor to another specific actor with the expectation that a particular thing will happen as a result.

Commands will be HTTP requests from outside systems e.g. a request to start a benchmark, a request to add a document upload start or end time.

Each command will have a dedicated endpoint.

For example, `start_benchmark` is a command with the endpoint `/api/v1/benchmarks/start`.

An example Payload (WIP) would be:

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

- CreateBenchmark
- UpdateDocument (with upload start or end time)
  - omit events: updated_document
  - this is instrumentation in the Eigen app, http requests to the `slowking`
- CreateReport

### Events

> Events are broadcast by an actor to all interested listeners.
> We often use events to spread the knowledge about successful commands.
> Events capture facts about things that happened in the past.

- BenchmarkCreated
  - handlers: create_project
  - omit events: created_project
- created_project
  - handlers: upload_documents

- DocumentUpdated
  - handlers: check_all_docs_processed
  - omit events: completed_benchmark (conditional: only if all docs are processed)

- BenchmarkCompleted
  - handlers: generate_report
  - omit events: completed_report

- ReportCompleted
  - handlers: send_notification

- ErrorStatus | ErrorOccurred
  - handlers: send_notification

- Get artifacts (for POC, have them locally rather than pulling from S3)
- Login to instance
- Create project
- Upload documents
- Doc upload started (instrumented event sent by Eigen application)
- Doc upload completed (instrumented event sent by Eigen application)
- All docs uploaded (a check to see if all docs are uploaded)
- Create benchmark report (simply log or if time create a csv, maybe take the code from Geo?)

### Domain Models

- Benchmark
  - includes reference to a benchmark-instance
  - includes reference to documents to upload and measure upload latency

### Database Tables

- benchmark
  - id | uuid (pk)
  - name
  - type e.g. latency
  - infra e.g. docker, k8s or local
  - project (doc_type)
  - documents (ids) ?
- benchmark-instance (get_or_create | get/update if username/pw are different)
  - id (pk)
  - fk to benchmark
  - url
  - username
  - password
- document
  - (used to measure upload latency)
  - id (pk)
  - fk to benchmark
  - (fk to project | benchmark.project.id)
  - eigenapp doc.id
  - doc upload start timestamp (utc)
  - doc upload end timestamp (utc)
  - doc upload total time (calculated property)

### Unit of Work

- Abstract & Repository
  - benchmarks
- Unit of Work
  - e.g. `self.benchmarks = repository.SqlAlchemyRepository(self.session)`

## Open Issues

None

## Closed Issues

### Concurrent DB connection issues

#### Solution 1
Wrap the uom in a try/catch and retry. The uow `__exit__` rollsback if there is an exception. This appears to work and means the uow can be injected into the handler, making testing much easier and cleaner.

#### Solution 2
Resolved by not injecting the UoW into bootstrap. Instead the handler instantiates its own UoW i.e. it is a session just for that handler. Drawback of this approach is cannot inject a mock UoW for tests.

```
sqlalchemy.exc.InvalidRequestError: Object '<Benchmark at 0xffff8d290fd0>' is already attached to session '5' (this is '6')

sqlalchemy.exc.InvalidRequestError: This session is provisioning a new connection; concurrent operations are not permitted (Background on this error at: https://sqlalche.me/e/20/isce)

sqlalchemy.exc.IllegalStateChangeError: Method 'rollback()' can't be called here; method 'commit()' is already in progress and this would cause an unexpected state change to <SessionTransactionState.CLOSED: 5>
(Background on this error at: https://sqlalche.me/e/20/isce)
```

https://docs.sqlalchemy.org/en/20/orm/session_basics.html#session-faq-threadsafe

> The concurrency model for SQLAlchemy’s Session and AsyncSession is therefore Session per thread, AsyncSession per task.
> The best way to ensure this use is by using the standard context manager pattern locally within the top level Python function that is inside the thread or task, which will ensure the lifespan of the Session or AsyncSession is maintained within a local scope.

https://github.com/sqlalchemy/sqlalchemy/discussions/8554

https://github.com/sqlalchemy/sqlalchemy/discussions/9114

https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#synopsis-core



```
raise sa_exc.InvalidRequestError(
slowking-api-eventbus    | sqlalchemy.exc.InvalidRequestError: Object '<Benchmark at 0xffff8ab36a90>' is already attached to session '5' (this is '6')


raise sa_exc.IllegalStateChangeError(
slowking-api-eventbus    | sqlalchemy.exc.IllegalStateChangeError: Method 'close()' can't be called here; method '_connection_for_bind()' is already in progress and this would cause an unexpected state change to <SessionTransactionState.CLOSED: 5> (Background on this error at: https://sqlalche.me/e/20/isce)
```
