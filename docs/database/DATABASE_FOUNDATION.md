# Database Foundation

## 1. Purpose

This document defines the database foundation for the Holter ECG Analysis Platform.

The database layer is designed for a commercial, on-premises clinical application supporting:

- Patient management
- Holter monitoring sessions
- ECG acquisition
- ECG recording metadata
- Analysis execution
- Clinical observations
- Clinician review
- Diary/timeline information
- Report generation
- Auditability
- Multi-organization/tenant separation

PostgreSQL is the system of record for structured application and clinical metadata.

Large ECG recordings and generated binary artifacts are stored outside PostgreSQL in object storage.

---

## 2. Database Technology

### Primary database

PostgreSQL.

Current development environment:

- PostgreSQL 18
- SQLAlchemy 2.x
- Psycopg 3
- Alembic

PostgreSQL is the authoritative source of truth for structured application state.

### Dependency management

Python dependencies are managed using:

- `pyproject.toml` — declared project dependencies
- `uv.lock` — resolved dependency graph
- `.python-version` — project Python version selection

`requirements.txt` is not maintained as a second dependency source.

---

## 3. Database Responsibilities

PostgreSQL stores:

- Organizations
- Users and application identity mapping
- Patients
- Patient identifiers
- Devices
- Holter sessions
- Acquisition sessions
- Recording metadata
- Analysis run metadata
- Clinical observations
- Observation review state
- Diary/timeline entries
- Reports and report revisions
- Audit events
- Model/version metadata

PostgreSQL does not store large ECG binary recordings directly.

---

## 4. Storage Boundary

The platform separates structured metadata from large binary artifacts.

### PostgreSQL

Stores metadata such as:

- Patient identity
- Session state
- Recording metadata
- Recording checksum
- Object-storage location
- Analysis state
- Observation metadata
- Report metadata
- Audit information

### MinIO

Target on-premises object storage for:

- Raw ECG recordings
- Processed ECG artifacts
- ECG evidence/strip artifacts
- Generated PDF reports
- Other large binary clinical artifacts

The application stores the corresponding bucket/object key in PostgreSQL.

### Redis

Redis is a runtime infrastructure component rather than the clinical source of truth.

Expected responsibilities include:

- Runtime cache
- Job coordination
- Temporary processing state
- Progress information
- Distributed coordination where required

Clinical records must remain recoverable from PostgreSQL and MinIO without relying on Redis.

---

## 5. Multi-Organization Boundary

The system is designed with an organization boundary from the beginning.

Organization-scoped entities include:

- Users
- Patients
- Patient identifiers
- Devices
- Holter sessions
- Acquisition sessions
- Recordings
- Analysis-related resources
- Audit events

Application authorization must enforce organization/resource boundaries.

Database foreign keys establish structural relationships, while application authorization is responsible for determining whether an authenticated user is allowed to access or modify a resource.

---

## 6. Core Clinical Domain

The current database foundation contains the following tables:

1. `organizations`
2. `users`
3. `patients`
4. `patient_identifiers`
5. `devices`
6. `holter_sessions`
7. `acquisition_sessions`
8. `recordings`

The schema intentionally separates the clinical concepts below.

```text
Patient
   │
   └── Holter Session
          │
          ├── Acquisition Session
          │
          └── Recording
                  │
                  └── Analysis Run
                         │
                         └── Observations