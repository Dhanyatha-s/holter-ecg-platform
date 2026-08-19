# Migration Map from `Med_project`

This is the approved starting map for selective migration. The old repository is a reference source and is not modified.

| Source area | New repository action | Notes |
|---|---|---|
| React frontend | Migrate + refactor | Rewire legacy Flask API client after new API contract exists |
| ECG viewer/components | Migrate + refactor | Preserve useful UI behavior; validate against dynamic 1–12 lead requirement |
| FastAPI foundation | Rebuild cleanly using existing concepts | Avoid carrying mixed legacy structure forward |
| SQLAlchemy | Keep | Use as ORM/data-access foundation |
| PostgreSQL direction | Keep | Redesign domain schema rather than copying old tables |
| Alembic | Keep concept | Establish new migration history in new repository |
| Existing Patient/Recording/Annotation/Report models | Redesign | Expand around device/session/analysis/observation/report lifecycle |
| Existing REST routers | Refactor/rebuild | Establish versioned resource-oriented contracts |
| HDF5 implementation | Reuse selectively | Put behind storage abstraction |
| Filesystem storage | Keep as development adapter | Useful before MinIO deployment |
| MinIO | Add | Planned on-premise object-storage adapter |
| EDF/parser utilities | Audit + selective reuse | Do not assume EDF is the final hardware format |
| HDF5 writer | Audit + selective reuse | Normalize through storage service |
| Acquisition simulator | Keep + redesign | Required for development/testing before hardware protocol is final |
| Wi-Fi/USB/Bluetooth receivers | Isolate/review | Protocol-specific code must sit behind acquisition adapters |
| Legacy progress/session SQLite store | Replace | Session state belongs in PostgreSQL |
| Flask `api.py` | Do not migrate as architecture | Business logic may be extracted only after review |
| Legacy Flask acquisition documentation | Replace | New documentation will describe FastAPI/acquisition boundary |
| `__pycache__` and generated artifacts | Do not migrate | Covered by new `.gitignore` |
| Existing tests | Use as seeds + expand | New test strategy will cover unit/API/integration/WebSocket/e2e/performance layers |
| Report generator | Audit | Keep useful report logic separate from transport/API code |
| Priority manager / clinical analysis | Defer and audit | Phase 2 clinical logic; preserve requirements/provenance |
| ML/DL work | Keep separately | Phase 2; do not couple to Phase 1 platform foundation |
| Root diagnostic scripts | Audit individually | Only production-relevant utilities migrate |

## Explicit non-goals of migration

- No direct copy of the old SQLite architecture.
- No direct copy of the old Flask routing architecture.
- No assumption that the existing device transport implementation is the final hardware protocol.
- No Phase 2 clinical model implementation as part of the initial platform bootstrap.
- No destructive changes to `Med_project`.
