# Holter ECG Platform — Architecture Baseline

## 1. Purpose

This document is the engineering baseline for the new Holter ECG Platform repository.

The product is an on-premise clinical decision support application for Holter ECG workflows. It supports two planned analysis paths:

1. real-time/on-spot ECG streaming while a patient is wearing the recorder;
2. retrospective analysis of a completed recording, including recordings up to 48 hours.

Phase 1 in this repository focuses on the application/platform foundation and intentionally excludes final device-specific acquisition implementation until the hardware/firmware team provides the confirmed recorder configuration and communication protocol.

## 2. Architecture principles

- Keep acquisition, storage, clinical analysis, API, and presentation as separate boundaries.
- Do not couple business logic directly to a specific Holter communication protocol.
- PostgreSQL is the structured system of record.
- ECG waveform data and other large binary artifacts are stored through an object-storage abstraction rather than inside PostgreSQL rows.
- Local filesystem/HDF5 may be used during development; MinIO is the planned on-premise object-storage implementation.
- FastAPI is the backend API framework.
- REST is used for resource-oriented application operations; WebSocket is used for real-time ECG streaming/session communication where appropriate.
- Domain state must be persisted durably and must not depend on process-local memory.
- Tests are part of feature completion, not a final cleanup activity.
- Hardware uncertainty is isolated behind adapters and simulators.

## 3. Logical architecture

```text
React Frontend
     |
     | HTTPS / REST + WebSocket
     v
FastAPI Application
     |
     +-- API / schemas / validation
     +-- Application services
     +-- Repositories
     +-- Acquisition/session boundary
     +-- Storage service
     |
     +----------------------+-------------------+
     |                      |                   |
     v                      v                   v
 PostgreSQL          ECG Object Storage   Background work
 structured state    Local/HDF5 or MinIO  analysis/processing
```

## 4. Core domain direction

The domain is expected to evolve around these concepts:

- Patient
- Device
- Recording
- AcquisitionSession
- ECG storage reference
- DiaryEntry
- Annotation
- AnalysisRun
- Observation
- ObservationEvidence
- Measurement
- Report
- ReportVersion
- AuditLog
- User / Role / Permission (authentication/RBAC is planned for a later phase)

The exact schema is intentionally not frozen by this document. It must be reviewed before database implementation.

## 5. Data boundary

PostgreSQL stores structured metadata, lifecycle state, relationships, clinical observations, measurements, report metadata, audit information, and references to stored ECG objects.

Object storage stores large waveform and binary artifacts such as raw ECG, processed ECG, analysis artifacts, and report artifacts where appropriate.

The application should depend on a storage interface rather than directly on MinIO APIs.

## 6. Acquisition boundary

The final hardware protocol is pending. The application therefore uses an adapter boundary:

```text
Holter device / file source
        |
        v
Acquisition Adapter
        |
        v
Acquisition Session
        |
        v
ECG Frame / normalized signal data
        |
        v
Storage + downstream processing
```

Candidate transports may include Wi-Fi, USB, Bluetooth, or file/SD-card workflows, but no transport-specific behavior is considered final until confirmed by the device team.

A simulator is required so the application can be developed and tested before hardware integration is finalized.

## 7. Real-time and retrospective paths

The two paths share patient, recording, observation, storage, and review concepts but have different processing characteristics.

### Real-time

```text
Device -> acquisition adapter -> WebSocket/session -> buffering -> storage/processing -> observations/timeline
```

Multiple patient sessions must be possible concurrently. A session is associated with the patient and, when available, a device identifier.

### Retrospective

```text
Completed recording -> registration/import -> storage -> analysis run -> observations/measurements -> physician review -> report
```

## 8. Frontend boundary

The existing React frontend from the reference repository is reusable, but its API client currently targets the legacy Flask API. It will be migrated only after the new API contract is established.

## 9. Database strategy

The new project will not mechanically convert the old SQLite schema. PostgreSQL schema design will be derived from the product domain and lifecycle requirements, followed by Alembic migrations.

The database design must account for:

- multi-patient operation;
- multiple recordings per patient;
- concurrent acquisition sessions;
- dynamic lead counts from 1 to 12;
- recording metadata and storage references;
- analysis runs and model/version provenance;
- observations and review state;
- patient diary/timeline entries;
- reports and report versions;
- auditability.

## 10. Phase boundary

### Phase 1

Platform foundation excluding final device-specific data acquisition and Phase 2 clinical ML analysis.

Includes the backend/API foundation, PostgreSQL, storage abstraction, acquisition boundary/simulator, ECG recording metadata and access, real-time WebSocket foundation, frontend integration, testing, and deployment foundations.

### Phase 2

Clinical signal processing, ML/DL analysis, observations, measurements, clinical timeline, review workflow, and reporting according to the approved clinical requirements and model validation plan.

### Phase 2+

Additional approved risk markers, personalization, adaptive logic, and automated reporting enhancements.

### Later

Role-based authentication/authorization and related administrative/security workflows are planned and will be integrated without breaking the domain boundaries.

## 11. Reference repository

`Med_project` remains the historical/source repository. It is not modified as part of this rebuild. Useful implementation pieces are selectively migrated only after architectural review.

## 12. Architecture change rule

A significant architectural change should be documented and reviewed before implementation. Hardware-dependent assumptions must not be hidden inside general application services.
