# Test Strategy — Phase 1 Foundation

## Objective

Every implemented feature must have evidence that it behaves correctly, fails safely, and does not regress previously working behavior.

## Test layers

### Unit tests

Test pure functions, validation, domain rules, storage-key construction, lifecycle transitions, and small services without external infrastructure.

### API tests

Test FastAPI endpoints through an HTTP client. Verify status codes, request/response schemas, validation, authorization boundaries when RBAC is introduced, and error behavior.

### Database integration tests

Run against a dedicated PostgreSQL test database. Verify transactions, constraints, relationships, indexes, migrations, and concurrent state updates.

### Storage integration tests

Test the storage abstraction against the local adapter first and MinIO in an integration environment when available. Verify upload/read/delete semantics, checksums, missing-object behavior, and metadata consistency.

### WebSocket tests

Test connection lifecycle, patient/session association, message validation, sequence handling, malformed frames, disconnect/reconnect behavior, multiple concurrent sessions, backpressure, and cleanup.

### Acquisition tests

Use the simulator to produce deterministic ECG frames and verify that normalized frames reach storage and downstream processing without corruption or loss.

### End-to-end tests

Verify major user workflows across frontend/API/database/storage boundaries, beginning with patient creation, recording registration, ECG retrieval, and real-time session simulation.

### Performance tests

Measure ECG window retrieval, ingestion throughput, concurrent sessions, storage throughput, and relevant API latency. Phase 2 will add analysis-time performance targets, including the 48-hour analysis requirement.

## Required quality gates

A feature is not considered complete merely because it runs locally. At minimum, its relevant automated tests must pass, error paths must be considered, and API/data-contract changes must be reviewed.

## AI-generated code review rule

AI-generated code is treated exactly like human-written code. It must be reviewed for correctness, security, maintainability, data integrity, failure handling, and test coverage before merge.
