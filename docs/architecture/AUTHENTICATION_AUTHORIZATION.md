**HOLTER ECG PLATFORM**

**Authentication & Authorization Architecture
Development → Hospital Production**

_Keycloak • OIDC/OAuth 2.0 • PKCE • FastAPI • Electron/React • PostgreSQL_

Version 1.0 | 25 September 2026 | Architecture / Implementation Planning

# 1\. Executive Summary

This report defines how authentication and authorization will be built for the Holter ECG platform during development and how the same security architecture will evolve when the software is deployed inside a hospital environment. The objective is not to create two unrelated security systems. Development implements the same security boundaries that production will use, while production adds stronger identity integration, availability, operational controls, audit integration and hospital-specific policies.

Core decision: Keycloak is the identity and authentication authority; FastAPI is the authoritative application authorization enforcement point; PostgreSQL stores application identity mapping, organizations, roles/permissions and clinical/application audit records; Electron/React provides the UI and UX layer but is never the final security boundary.

# 2\. Core Security Architecture

```
                 ┌───────────────┐
                 │   Keycloak    │
                 │ Authentication│
                 │ Sessions/MFA  │
                 │ Roles         │
                 └───────┬───────┘
                         │ OIDC / tokens
                         ▼
                 ┌───────────────┐
                 │ Electron/React│
                 └───────┬───────┘
                         │ Bearer access token
                         ▼
                 ┌───────────────┐
                 │    FastAPI    │
                 │ JWT validation│
                 │ RBAC          │
                 │ Organization  │
                 │ Resource rules│
                 └───────┬───────┘
                         │
                 ┌───────┴────────┐
                 ▼                ▼
           PostgreSQL           MinIO
        identity/domain/audit  ECG/report data
```

The frontend may hide menus and buttons for usability, but every protected API operation must be independently authorized by FastAPI. Direct API calls must receive the same security decision as UI-driven calls.

# 3\. What We Are Implementing Now — Development

The development environment will use a real Keycloak instance and real OIDC authentication rather than a temporary custom login system. This lets us test the production security contract early.

| **Component**       | **Development implementation**      | **Purpose**                                              |
| ------------------- | ----------------------------------- | -------------------------------------------------------- |
| Keycloak            | Local/on-prem development instance  | Authentication, sessions, roles and test users           |
| Realm               | Dedicated development realm         | Isolation of development identities/configuration        |
| Client              | Desktop/API clients as appropriate  | Define OIDC trust relationships                          |
| Authentication flow | Authorization Code + PKCE           | Native desktop authentication                            |
| FastAPI             | Local backend                       | JWT validation and authorization                         |
| PostgreSQL          | Existing development database       | Users, organizations, permissions and audit              |
| MinIO               | Development object storage          | ECG files/reports                                        |
| MFA                 | Testable/configurable               | Validate integration without hard-coding hospital policy |
| Audit               | Keycloak events + application audit | Validate traceability                                    |

# 4\. Development Login Flow

1. User opens the Electron application.
2. Electron checks the current application session.
3. Electron launches the system browser to Keycloak.
4. Keycloak authenticates the user.
5. Authorization Code + PKCE returns an authorization code to the desktop application.
6. The code is exchanged for tokens.
7. Electron calls FastAPI using the access token.
8. FastAPI validates the token using Keycloak OIDC metadata and JWKS.
9. FastAPI maps the external identity using issuer + subject.
10. FastAPI checks user status, organization, role/permission and resource rules.
11. The API allows or denies the operation.

Keycloak's current OIDC documentation describes Authorization Code as a flow in which the user agent is redirected to Keycloak, an authorization code is returned, and the application exchanges that code for tokens; it also identifies the flow as suitable for native applications where a user agent can be used. citeturn0search6

# 5\. Initial RBAC Model

| **Role** | **Initial responsibility**                                                                                             |
| -------- | ---------------------------------------------------------------------------------------------------------------------- |
| ADMIN    | System/user administration, configuration and authorized data-management functions.                                    |
| DOCTOR   | Clinical workflow: patients, sessions, recordings, analysis, observations, diary and reports according to permissions. |
| STAFF    | Initial read-only clinical/application access.                                                                         |

Roles are not the complete authorization model. Application permissions include concepts such as PATIENT_VIEW, PATIENT_CREATE, ANALYSIS_RUN, OBSERVATION_CREATE, OBSERVATION_VERIFY, REPORT_CREATE, USER_MANAGE and AUDIT_VIEW. This keeps business authorization extensible without turning every permission into a Keycloak realm role.

# 6\. Identity Mapping

```
Keycloak identity
   iss = identity issuer
   sub = identity subject
              │
              ▼
PostgreSQL users
(identity_issuer, identity_subject)
              │
              ▼
organization + roles + status
```

The application user is identified by the issuer + subject pair, not by email alone. PostgreSQL does not store Keycloak passwords. This matches the database foundation already established for the project.

# 7\. Token Design and PHI Boundary

- Do not place patient names, medical record numbers, ECG measurements or other PHI in access or ID tokens.
- Validate issuer, signature, algorithm, expiration and configured audience.
- Use Keycloak's OIDC discovery/JWKS information and cache public keys appropriately.
- Keep access-token contents limited to information required for identity and authorization.
- Keep clinical information in PostgreSQL/MinIO rather than embedding it into tokens.

Keycloak exposes an OpenID Connect discovery endpoint and signing-key/JWKS mechanisms for clients and services to discover provider configuration and validate tokens. citeturn0search6

# 8\. Where Authorization Happens

```
Request
  ↓
JWT validation
  ↓
Authenticated application user
  ↓
active? → organization? → role? → permission?
  ↓
resource belongs to organization?
  ↓
business/workflow rule?
  ↓
ALLOW / DENY
```

Keycloak establishes identity and supplies identity/role information. FastAPI remains the authoritative decision point for whether a particular API operation on a particular resource is permitted.

# 9\. Why We Are Not Starting With Full Keycloak Authorization Services

Keycloak supports fine-grained authorization, but we should not introduce a second centralized policy engine before our application's basic RBAC, organization isolation and resource rules are stable. We will implement the first authorization layer in FastAPI with a clean permission model. Keycloak Authorization Services can be evaluated later if hospital requirements justify centralized policy decisions.

This is a sequencing decision, not a limitation claim about Keycloak.

# 10\. Development Security Tests

| **Test**                  | **Expected result**                                  |
| ------------------------- | ---------------------------------------------------- |
| Valid login               | Authenticated session and authorized functions work. |
| Expired token             | FastAPI rejects request.                             |
| Malformed token           | FastAPI rejects request.                             |
| Wrong issuer              | FastAPI rejects request.                             |
| Wrong audience            | Rejected when audience validation is configured.     |
| Invalid signature         | Rejected.                                            |
| Unsupported algorithm     | Rejected.                                            |
| Insufficient permission   | 403.                                                 |
| Cross-organization access | Denied.                                              |
| Direct API bypass         | Same authorization result as UI.                     |
| Disabled application user | Denied.                                              |
| Logout/session expiry     | Access ends according to policy.                     |
| PKCE/state/nonce failure  | Authentication flow rejected.                        |
| Audit event               | Security-sensitive action produces evidence.         |

# 11\. Hospital Production: What Changes

Production is not simply 'the development Keycloak server with real users.' A hospital deployment adds identity ownership, directory integration, availability, network segmentation, TLS, audit retention, monitoring, backup/recovery, MFA policy and operational governance.

| **Area**          | **Development**             | **Hospital production**                                  |
| ----------------- | --------------------------- | -------------------------------------------------------- |
| Identity source   | Keycloak-managed test users | Hospital directory/IdP may be federated through Keycloak |
| Keycloak topology | Single instance             | HA topology when required                                |
| Database          | Development PostgreSQL      | Production-grade, backed up and sized                    |
| Users             | Small test population       | Hospital-managed lifecycle                               |
| MFA               | Test/configurable           | Hospital security policy                                 |
| Network           | Developer/LAN               | Segmented hospital network + TLS + controlled ingress    |
| Audit             | Local structured logs       | Central retention/monitoring/SIEM as required            |
| Availability      | Restart/recovery            | Defined SLA/RTO/RPO and failover                         |
| Break-glass       | Not initially implemented   | Governed emergency-access workflow if required           |
| Operations        | Developer                   | Hospital IT/security/operations                          |

# 12\. Hospital Identity Integration

A mature hospital may not want separate application passwords for every clinician. Keycloak can act as the federation layer between the hospital identity infrastructure and the Holter application. The exact mechanism—LDAP/Active Directory, another identity provider, or Keycloak-managed accounts—must be selected with the hospital.

```
Hospital AD / LDAP / external IdP
              │
              ▼
          Keycloak
              │ OIDC
              ▼
          Holter API
              │
              ▼
       Application identity
```

The application remains independent of the hospital's underlying directory technology: it integrates with Keycloak/OIDC rather than directly coupling clinical application code to AD/LDAP. Keycloak's current guidance emphasizes standards-based OIDC/SAML integration and using application ecosystem support where available. citeturn0search14

# 13\. Production High Availability

HA should be derived from hospital uptime and continuity requirements. It should not be added merely because the software is 'enterprise'.

Keycloak's current production guidance says a typical production environment can contain two or more Keycloak instances so users can continue logging in if an instance fails. It also emphasizes a production-grade database and health checks. citeturn0search0

```
                 Load Balancer
                 /                           ▼             ▼
          Keycloak A     Keycloak B
                \             /
                 ▼           ▼
             Production DB
                  │
              Backup / DR
```

Keycloak currently documents multiple HA architectures, including single-cluster and multi-cluster patterns, with specific network-latency, database and infrastructure requirements. citeturn0search11turn0search2

# 14\. Development vs Production — Distinctive Approach

| **Dimension** | **Development**                    | **Production**                            |
| ------------- | ---------------------------------- | ----------------------------------------- |
| Goal          | Validate security contract         | Operate it reliably under hospital policy |
| Identity      | Controlled test users              | Hospital identity lifecycle               |
| Keycloak      | Single instance                    | HA when required                          |
| Network       | Local/dev                          | Hospital segmentation + TLS               |
| Secrets       | Local development secrets          | Managed production secrets/rotation       |
| Certificates  | Development configuration          | Hospital PKI/certificate policy           |
| Audit         | Developer-visible logs             | Central retention/monitoring              |
| MFA           | Integration testing                | Hospital policy                           |
| Authorization | RBAC + organization/resource rules | Same core model + approved hospital rules |
| Directory     | Keycloak users                     | Federated directory if required           |
| Recovery      | Basic development restore          | Tested backup/restore and DR              |
| Operations    | Developer                          | Hospital IT/security/operations           |

# 15\. Production Network and Trust Boundaries

```
Hospital Network
────────────────────────────────────────────
Clinician Workstation
        │ TLS / controlled access
        ▼
Reverse Proxy / Load Balancer
        │
        ├──────────► Keycloak cluster
        │
        ▼
      FastAPI
        │
        ├──────────► PostgreSQL
        ├──────────► MinIO
        └──────────► Redis

Administrative paths:
  Hospital IT / Keycloak administration
  Application administration
  Database/storage administration
```

PostgreSQL and MinIO should not be directly exposed to clinician workstations unless a specific controlled requirement exists. Service-to-service communication and network zones should be documented as part of the hospital deployment.

# 16\. Audit Architecture

```
Keycloak events
      │
      ▼
Authentication/security audit
      │
      └────► central logging/SIEM (deployment-dependent)

FastAPI application events
      │
      ▼
PostgreSQL audit_events
      │
      └────► central logging/SIEM (deployment-dependent)

Examples:
  patient viewed
  observation created/edited/verified
  report finalized
  role changed
  authorization denied
```

Keycloak authentication events and the application's clinical audit trail serve different purposes. Clinical operations must not depend solely on login logs.

# 17\. Sessions, Logout and Revocation

- Keycloak owns identity sessions and token issuance.
- FastAPI rejects expired and invalid access tokens.
- Logout must terminate the application session according to the selected desktop flow and Keycloak policy.
- Privileged-account and workstation session policies should be configurable.
- Session idle/max limits must be defined with the hospital's clinical workflow and security requirements.
- Revocation/invalidation behavior must be tested.

Exact timeout values are intentionally not fixed in this report because they are hospital security-policy decisions.

# 18\. MFA and Privileged Access

MFA should be an identity-policy capability owned by Keycloak, not custom FastAPI authentication logic. Production can require stronger authentication for administrators or other sensitive workflows. The exact mechanism—TOTP, WebAuthn/passkeys, hardware-backed authentication or another hospital-approved method—must be decided with the hospital.

# 19\. Break-Glass / Emergency Access

Emergency access should not be implemented as a generic temporary ADMIN switch. If the hospital requires break-glass access, it should be a governed workflow with reason capture, elevated audit severity, limited duration, reviewability and explicit authorization conditions.

```
Emergency request → reason → controlled temporary access
                 │
                 ├── high-priority audit
                 ├── expiry
                 └── review
```

This remains a production requirement to be specified with the hospital and is not part of the first authentication implementation.

# 20\. What Does NOT Belong in Authentication

- Patient clinical records.
- ECG waveform data.
- Diagnosis or clinical decision logic.
- Analysis results and report contents.
- Large ECG objects.
- Clinical processing workflows unrelated to identity.

Authentication and authorization establish who the user is and whether an operation is permitted. Clinical processing remains in the application domain.

# 21\. Implementation Roadmap

| **Phase** | **Work**                        | **Output**                                                  |
| --------- | ------------------------------- | ----------------------------------------------------------- |
| 1         | Security architecture           | Approved authentication/authorization architecture document |
| 2         | Keycloak development deployment | Realm, clients, roles, test users                           |
| 3         | FastAPI authentication          | OIDC discovery + JWT/JWKS validation                        |
| 4         | Identity mapping                | Keycloak (iss, sub) → PostgreSQL user                       |
| 5         | Authorization                   | Role/permission dependencies + organization checks          |
| 6         | Audit                           | Security and application audit events                       |
| 7         | Security tests                  | Token, authz, bypass and failure tests                      |
| 8         | Desktop integration             | Electron system-browser login + PKCE                        |
| 9         | Hardening                       | TLS, secrets, logs, health checks, backup/restore           |
| 10        | Hospital integration            | AD/LDAP/IdP federation if required                          |
| 11        | Production HA                   | HA Keycloak/database/load balancing as required             |
| 12        | Acceptance                      | Security, performance, failover and operational validation  |

# 22\. Hospital Decisions Required Before Production

| **Decision**             | **Why it matters**                                   |
| ------------------------ | ---------------------------------------------------- |
| Hospital identity source | Determines federation and lifecycle integration.     |
| Uptime/SLA               | Determines HA design.                                |
| RTO/RPO                  | Determines backup and disaster recovery.             |
| MFA policy               | Determines authentication requirements.              |
| Session timeout          | Balances clinical workflow and workstation security. |
| Audit retention          | Determines storage/SIEM strategy.                    |
| SIEM/security monitoring | Determines log integration.                          |
| Network zones/firewalls  | Determines service access boundaries.                |
| Break-glass policy       | Determines emergency access.                         |
| Department/role model    | Determines future resource/attribute authorization.  |
| PKI/certificate policy   | Determines TLS and certificate rotation.             |
| Backup ownership         | Determines operational responsibilities and testing. |

# 23\. Final Architecture Position

The project should be developed with the production security boundaries already present, but without prematurely implementing every hospital infrastructure component. Development therefore uses real Keycloak OIDC authentication, real JWT validation, real application authorization and real audit behavior. Production adds identity federation, stronger authentication policy, HA, operational monitoring, backup/DR, network controls and hospital governance.

In short: DEVELOPMENT validates the security design; PRODUCTION operationalizes the same design under hospital identity, availability, audit and governance requirements.

# 24\. Reference Basis

- Keycloak — OIDC layers: <https://www.keycloak.org/securing-apps/oidc-layers>
- Keycloak — Planning for securing applications/services: <https://www.keycloak.org/securing-apps/overview>
- Keycloak — Production configuration: <https://www.keycloak.org/server/configuration-production>
- Keycloak — Distributed caching: <https://www.keycloak.org/server/caching>
- Keycloak — High availability overview: <https://www.keycloak.org/high-availability/introduction>
- Keycloak — Single-cluster HA: <https://www.keycloak.org/high-availability/single-cluster/introduction>
- Keycloak — Multi-cluster HA: <https://www.keycloak.org/high-availability/multi-cluster/introduction>
- Keycloak — Supported configurations: <https://www.keycloak.org/server/supported-configurations>

# 25\. Important Qualification

This is an engineering architecture and implementation plan, not a hospital compliance certification. HIPAA, GDPR, Indian regulatory requirements, hospital accreditation requirements, retention periods and final medical-device/regulatory classifications must be validated against the actual deployment jurisdiction, organization policy, legal requirements and final product assessment. Keycloak capability statements are based on current Keycloak documentation; hospital-specific production decisions remain open until infrastructure and security requirements are known.