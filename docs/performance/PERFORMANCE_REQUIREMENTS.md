# Holter ECG Platform — Performance & Latency Requirements

**Status:** Draft approved for implementation

## 1. Purpose

This document defines the performance requirements and measurement strategy for the Holter ECG Analysis Platform.

The system must support:

- real-time ECG acquisition and analysis;
- complete retrospective analysis of recordings up to 48 hours;
- dynamic 1–12 lead configurations;
- multiple patients operating concurrently;
- clinical analysis covering the approved client requirements and dataset taxonomy;
- physician-ready observations and reports.

Performance is an end-to-end product concern, not only an ML inference concern.

## 2. Performance targets

### 2.1 Existing client requirement

The original client technical specification requires up to 48 hours of ECG recording to be automatically analyzed in less than 5 minutes. This remains the current formal baseline.

### 2.2 Client-requested target

The client has additionally expressed a desired target of approximately **1–2 minutes for the complete process**.

For engineering purposes, this is currently a **target requiring validation**, not a guaranteed capability.

Where technically applicable, the target covers:

```text
ECG available
  → ingestion / transmission
  → storage
  → signal processing
  → ML/DL analysis
  → clinical measurements
  → observation curation
  → report generation
  → result available to physician
```

The exact start and end points will be confirmed with the client and hardware/firmware team.

## 3. Performance modes

### Mode A — Real-time / On-Spot

The system continuously receives ECG data from an active Holter recording and processes appropriate windows without waiting for the complete recording.

Primary metrics:

- ECG transmission latency
- ingestion latency
- buffering latency
- processing latency
- model inference latency
- event detection latency
- observation creation latency
- UI delivery latency

Primary metric: **event-to-result latency**, from an ECG event becoming available to the corresponding clinical finding becoming visible to the user.

### Mode B — Retrospective

For a completed recording:

```text
Completed ECG
  → import / acquisition
  → persistent storage
  → preprocessing
  → beat detection
  → classification
  → clinical analysis
  → observation engine
  → report
```

Primary metric: **complete recording to physician-ready result**.

The 48-hour recording requirement must be explicitly benchmarked.

## 4. Clinical processing scope

Performance benchmarks must include the computational work required by the approved product scope, including as applicable:

- filtering, baseline-wander removal, noise/artifact handling and signal quality assessment;
- R-peak detection and beat segmentation;
- normal, atrial, ventricular, paced and artifact classification;
- the arrhythmia categories specified by the client and approved dataset/model taxonomy;
- ST-segment analysis;
- HRV analysis;
- RR analysis and histogram generation;
- QT/QTc analysis;
- observation grouping, confidence/severity handling and physician review state;
- report generation.

Phase 2+ additions such as HRT, TWA, DC and fQRS will be included in performance acceptance only after their algorithms and clinical validation requirements are finalized.

## 5. Data storage architecture

Structured application data belongs in PostgreSQL. Large ECG/binary artifacts belong in object storage.

### PostgreSQL

Expected domains include:

```text
Patient
Device
Recording
AcquisitionSession
LeadConfiguration
AnalysisRun
Observation
Measurement
DiaryEntry
Report
Audit information
```

### Object storage

Expected objects include:

```text
Raw ECG
Processed ECG
Analysis artifacts
Other large binary objects
```

Development may use local filesystem/HDF5 where appropriate. The planned on-premise deployment may use MinIO. Application services should use a storage abstraction rather than coupling clinical logic directly to a specific object-storage implementation.

## 6. Latency breakdown

Every analysis run must expose measurable timing information. Conceptual stages are:

```text
T1  Device → application
T2  Receive → buffer
T3  Buffer → persistent storage
T4  Preprocessing
T5  R-peak detection
T6  Beat classification
T7  Arrhythmia analysis
T8  ST analysis
T9  HRV analysis
T10 QT/QTc analysis
T11 Other clinical analysis
T12 Observation curation
T13 Report generation
T14 Result delivery to UI
```

These stages may overlap or execute in parallel. Therefore total elapsed time must be measured from wall-clock timestamps rather than assumed to be the arithmetic sum of every component duration.

## 7. Instrumentation

Each analysis run should expose lifecycle timestamps such as:

```text
analysis_started
ingestion_started
ingestion_completed
preprocessing_started
preprocessing_completed
detection_started
detection_completed
classification_started
classification_completed
clinical_analysis_started
clinical_analysis_completed
observation_started
observation_completed
report_started
report_completed
result_available
```

The system should also record, where applicable:

```text
pipeline_version
model_version
configuration_version
lead_count
sampling_rate
recording_duration
processing_mode
hardware/environment information
status
failure information
```

This makes bottleneck analysis and reproducibility possible.

## 8. Concurrent patient processing

The platform must not assume that only one patient is processed at a time.

Conceptually:

```text
Patient A → Session A → Processing A
Patient B → Session B → Processing B
Patient C → Session C → Processing C
Patient D → Session D → Processing D
```

The exact supported concurrency level remains **TBD with the client**. Benchmarking should progressively evaluate 1, 2, 5, 10 and additional workloads until system/resource limits are identified.

## 9. Concurrent performance metrics

For each concurrency level measure:

### Latency

- p50
- p95
- p99
- maximum

### Throughput

- recordings processed per hour;
- ECG data ingested per second;
- analysis jobs completed per minute.

### Resource utilization

- CPU;
- RAM;
- disk I/O;
- network bandwidth;
- GPU utilization where applicable;
- object-storage throughput.

## 10. Critical concurrency scenarios

The test plan must include:

1. one real-time patient;
2. multiple real-time patients;
3. multiple retrospective analyses;
4. real-time and retrospective processing simultaneously;
5. maximum supported concurrent workload.

One patient's workload must not unintentionally block, corrupt, or mix with another patient's data.

## 11. Streaming architecture requirement

Real-time processing must not require waiting for the entire recording. ECG should be handled as appropriate chunks/windows while the complete recording is persisted.

```text
Holter
  ├─ chunk 1 → processing
  ├─ chunk 2 → processing
  ├─ chunk 3 → processing
  └─ continuous
```

The system should be capable of receiving ECG, persisting it, processing appropriate windows, generating observations and updating the patient timeline while acquisition continues. Final behavior is subject to the hardware communication protocol.

## 12. Acquisition dependency

The following remain dependent on the hardware/firmware team's final configuration:

- sampling rate;
- bit depth;
- number of channels transmitted;
- packet structure and size;
- compression;
- communication protocol;
- expected throughput;
- timestamp format;
- device identifier;
- simultaneous device limit;
- reconnection behavior;
- completed-recording transfer mechanism;
- differences between real-time and bulk transfer protocols;
- final raw ECG file/data format.

Transmission latency therefore cannot currently be guaranteed. The acquisition layer remains behind an adapter boundary until these specifications are available.

## 13. Development simulator

A deterministic ECG acquisition simulator should be available before final hardware integration so the platform can be tested with multiple simulated patients.

```text
Simulated Patient A ─┐
Simulated Patient B ─┼→ WebSocket → FastAPI → storage → processing
Simulated Patient C ─┤
Simulated Patient D ─┘
```

This enables concurrency, latency and failure testing before physical Holter integration is complete.

## 14. Failure performance

Performance and resilience testing must include, where applicable:

- network interruption;
- device disconnect;
- packet loss;
- duplicate packets;
- out-of-order packets;
- storage unavailable;
- database unavailable;
- processing worker failure;
- model failure;
- report generation failure;
- application restart.

Failures must be controlled and observable, without silently losing or mis-associating patient ECG data.

## 15. Performance acceptance criteria

Arbitrary internal timing numbers will not be invented. Acceptance values should be established through baseline benchmarking using representative ECG recordings, actual lead configurations, actual sampling rates, production-like hardware, defined concurrency and production-like deployment configuration.

The eventual acceptance matrix will include:

| Metric | Target | Measured | Status |
|---|---:|---:|---|
| Real-time event → detection | TBD | — | Pending |
| Real-time event → UI | TBD | — | Pending |
| 48-hour analysis | **<5 min baseline** | — | Pending |
| End-to-end result | **1–2 min target** | — | Pending |
| Concurrent patients | TBD | — | Pending |
| p95 latency | TBD | — | Pending |
| Report generation | TBD | — | Pending |

## 16. Engineering principle

The platform must optimize the complete clinical workflow rather than only ML inference:

```text
Fast transmission
  + efficient storage
  + efficient signal processing
  + efficient ML inference
  + parallel processing
  + fast observation curation
  + fast report generation
  = fast clinical result
```

The 1–2 minute target must not be claimed as achievable until benchmarking demonstrates it. If a stage becomes the bottleneck, that stage becomes the optimization target rather than arbitrarily reducing clinical analysis or model complexity.
