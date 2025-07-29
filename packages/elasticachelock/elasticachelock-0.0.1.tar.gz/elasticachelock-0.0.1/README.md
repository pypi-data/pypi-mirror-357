# elasticachelock
Elasticache/Redis Lock for AWS Lambdas is a pure Python lib that implements a distributed locking mechanism using Redis Pub/Sub. It's designed for scenarios where multiple concurrent Lambda executions need to ensure that certain tasks are performed exclusively by a single instance. Supports configurable TTL, retries, backoff, customizable timeouts and tz
