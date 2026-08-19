# Architecture Decisions

## ADR-001 — New engineering repository

**Decision:** Build the product in `holter-ecg-platform` and preserve `Med_project` as the reference repository.

**Reason:** The reference repository contains valuable implementation work but mixes legacy and newer architecture. A clean engineering repository prevents legacy boundaries from becoming permanent dependencies.

## ADR-002 — FastAPI as backend framework

**Decision:** FastAPI is the backend API framework.

**Reason:** The target architecture requires REST APIs, WebSocket support, typed request/response contracts, dependency injection, and an API structure appropriate for the desktop/on-premise application.

## ADR-003 — PostgreSQL as system of record

**Decision:** PostgreSQL is the authoritative structured database.

**Reason:** The application requires durable multi-patient state, concurrent acquisition sessions, lifecycle state, observations, reports, auditability, and future role-based access control. SQLite is not the target production database.

## ADR-004 — Object storage for ECG waveforms

**Decision:** ECG waveform data is stored through an object-storage abstraction rather than inside PostgreSQL rows.

**Development:** Local filesystem/HDF5 adapter.

**Planned on-premise deployment:** MinIO adapter.

**Reason:** ECG recordings can be large and should not be coupled to relational-row storage. The abstraction also permits deployment-specific storage without changing domain services.

## ADR-005 — Acquisition adapter boundary

**Decision:** Device-specific acquisition is isolated behind an adapter boundary.

**Reason:** The hardware/firmware team has not yet finalized the Holter recorder configuration/protocol. We can implement normalized sessions, frames, buffering, storage, WebSocket handling, and simulation now without inventing the final device protocol.

## ADR-006 — Simulator before hardware integration

**Decision:** A deterministic acquisition simulator is a first-class development/testing component.

**Reason:** It allows concurrent-session, WebSocket, storage, lifecycle, and failure-recovery testing while the real hardware interface remains pending.

## ADR-007 — Phase separation

**Decision:** Phase 1 platform work is separated from Phase 2 clinical analysis/model work.

**Reason:** The data acquisition boundary and platform infrastructure can be developed and tested independently of the final ML/DL model and hardware integration.
