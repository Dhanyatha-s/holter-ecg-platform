# Holter ECG Platform

On-premise Holter ECG analysis platform for clinical decision support.

## Repository status

This repository is the new engineering repository for the product. The previous `Med_project` repository is preserved as a reference/source repository and is not modified by this project.

## Current phase

**Phase 1 — platform foundation, excluding the final Holter hardware/data-acquisition implementation.**

The hardware/firmware acquisition protocol is intentionally isolated behind an acquisition boundary until the device team's final configuration is available.

## Architecture direction

- FastAPI REST API
- WebSocket boundary for real-time ECG streaming
- PostgreSQL for structured application state and metadata
- Object storage abstraction for ECG data and artifacts
- Local filesystem/HDF5 for development
- MinIO as the planned on-premise object-storage implementation
- React frontend
- Alembic database migrations
- Automated testing and CI

See `docs/architecture/` for the engineering baseline.
