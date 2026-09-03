# M126A OAS Production Trust Material and Host Trust-Bootstrap Authority Contract Proof

Document role: FINALIZED DESIGN / DISCOVERY / SECURITY-AND-OPERATIONS CONTRACT PROOF ONLY.

This record is subordinate to `CONSTITUTION > ARCHITECTURE > SECURITY_ARCHITECTURE > CURRENT IMPLEMENTATION`. M117A remains the single-Owner LAN trust-root direction, M119A remains the separate-principal OAS and local-presence boundary, M121A remains the repository-to-host release and trust contract, M122A remains the repository artifact foundation, M123A remains the non-mutating readiness boundary, M124A remains the controlled first-install authorization boundary, and M125A remains the isolated-root rollback foundation. M126A addresses only production signing/trust-anchor and host trust-bootstrap authority. It does not implement or provision that authority.

Aether remains one persistent digital mind. The execution chain remains:

```text
Receive -> Understand -> Think -> Plan -> Act -> Observe -> Verify
-> Critic -> Repair -> Learn -> Report
```

The following boundaries remain invariant:

```text
AUTHENTICATION != INTENT_INTERPRETATION
GOAL_ACCEPTANCE != ACTION_AUTHORIZATION
ACTION_SUCCESS != COMPLETION
COMPLETION REQUIRES OBSERVATION + VERIFICATION
ROOT_POSSESSION != OWNER_INTENT
PROCESS_LOCAL_CALLER != TRUTHFUL_OWNER_AUTHORITY
CANDIDATE_MATERIAL != TRUST_ROOT_AUTHORITY
```

## 1. Authority, Scope, and Current Truth

The authority precedence is exact:

```text
CONSTITUTION
    >
ARCHITECTURE
    >
SECURITY_ARCHITECTURE
    >
CURRENT MILESTONE AUTHORIZATION
    >
CURRENT IMPLEMENTATION
```

Milestone records and external summaries are evidence and decision provenance,
not another authority layer. M126A does not rewrite M117A-M125A. Its finalization
updates only the bounded canonical traceability in `SECURITY_ARCHITECTURE.md` and
`PROGRESS.md`; the external summary remains evidence only.

The current truthful repository state is:

| Fact | Result | Meaning |
| --- | --- | --- |
| Production signing authority | `NOT_PROVEN` | No production private key was assumed, searched for, generated, imported, or accessed |
| Production public trust anchor | `NOT_PROVEN` | Repository test fixtures are not production authority |
| Host trust-bootstrap authority | `NOT_PROVEN` | No live local-console ceremony, helper, or host evidence exists |
| Fixed host trust objects | `NOT_DEPLOYED` | M124A/M125A do not provision the five objects |
| Truthful Owner deployment authority | `NOT_PROVEN` | M117A HA1 remains incomplete; trust bootstrap is not activation authority |
| M126A design | `PROVEN_BY_DESIGN` | This record and its static lock define the bounded contract |
| M126A implementation | `NOT_IMPLEMENTED` | No production code is changed |

M126A does not assume that production keys already exist. The selected model is
a future custody and authority contract, not evidence that any key, anchor,
verifier, certificate, account, service, or trust object exists on this host.

## 2. M126A Boundary and Non-Goals

M126A covers only the production trust-material and host trust-bootstrap
authority contract. It keeps these separate:

1. production signing material and release-signing authority;
2. release approval authority;
3. host trust-bootstrap authority;
4. fixed host verifier identity;
5. truthful Owner deployment and activation authority;
6. actual host trust provisioning;
7. actual deployment and live rollback verification.

M126A does not generate, search for, import, display, copy, install, rotate, or
revoke real secrets or trust objects. It does not modify `/etc`, `/usr`, systemd, accounts, OAS runtime, deployment code, or host state. It does not
sign a production candidate, implement a trust-bootstrap helper or signing
service, integrate hardware tokens, implement Owner authentication, authorize
Generic Act, expand Tool-Operation-Capability security, expose a public
listener, or start a successor milestone.

## 3. Selected Authority Model

The selected model is:

```text
SELECTED_AUTHORITY_MODEL:
MODEL_A_OFFLINE_PRODUCTION_SIGNING_PLUS_SEPARATE_LOCAL_CONSOLE_HOST_TRUST_BOOTSTRAP
BOOTSTRAP_AUTHORITY_ROOT_MODEL:
BOOTSTRAP_AUTHORITY_ROOT_MODEL_A_OS_IMAGE_PROVISIONING_BASELINE
PRE_INSTANCE_MODEL:
PRE_INSTANCE_MODEL_B_HOST_RELEASE_TRUST_BEFORE_EXPLICIT_INSTANCE_BINDING
```

Model A uses independent offline production signing custody and a separate
host-local trust-bootstrap ceremony. The production signing authority signs
release material but never writes host trust objects. The host trust-bootstrap
authority publishes only an independently approved public trust set and fixed
verifier identity. The deployment executor consumes the resulting trust proof
but cannot create or replace the trust root.

The model is selected because it supports one Owner, one Aether Instance,
private-LAN deployment, offline operation, independent custody, candidate
self-authorization resistance, explicit root/kernel trust limits, and direct
compatibility with M117A-M125A. The model does not claim protection from host
root, kernel, systemd, physical, or equivalent trust-base compromise.

### 3.1 Model comparison

| Model | Custody and operation | Main security result | Operational result | Compatibility | Decision |
| --- | --- | --- | --- | --- | --- |
| `MODEL_A` | Offline production signer; separate OS-attested local-console host bootstrap | Separates signing, approval, host bootstrap, and deployment; candidate cannot publish its verifier | Works offline with explicit ceremony and bounded recovery | Directly extends M117A/M119A/M121A | **SELECTED** |
| `MODEL_B` | Host-local root creates and controls signing and bootstrap material | Root becomes signer and bootstrap authority; compromised host can self-authorize candidates | Simple but custody is not independent and recovery is circular | Conflicts with M121A external trust-root rule | **REJECTED** |
| `MODEL_C` | OAS or ordinary runtime manages signing and bootstrap | Runtime compromise or OAS compromise can replace the root used to verify candidates | Convenient but creates confused deputy and candidate self-trust | Conflicts with M119A and M121A | **REJECTED** |
| `MODEL_D` | External signing service or hardware-backed signer plus local bootstrap | Strong possible signing custody, but external availability, key policy, hardware semantics, and local bootstrap still require separate contracts | Higher operational complexity and no guaranteed offline path without defined escrow | Not sufficiently bounded by existing M117A-M125A evidence | **REJECTED FOR THIS PASS** |
| `MODEL_E` | No production trust material or trust model selected | Safely stops but leaves the authority contract unresolved | No Build recommendation can be made | Too incomplete for the stated M126A design objective | **REJECTED AS THE DESIGN RESULT** |

Model D remains a possible future defense-in-depth variant only after a separate
authority decision. Model E is the current implementation fact for production
material availability, not the selected M126A design model. Selecting Model A
does not mean that production material is available.

### 3.2 Bootstrap-authority root model comparison

The bootstrap-authority verification key is a separate root from release trust,
Owner trust, and governance records. The candidates are:

| Root model | Authoritative origin and target acquisition | Security result | Decision |
| --- | --- | --- | --- |
| `BOOTSTRAP_AUTHORITY_ROOT_MODEL_A_OS_IMAGE_PROVISIONING_BASELINE` | A public-key record is included in a separately trusted OS/image provisioning baseline before Aether installation; the target obtains it only from that verified baseline | Non-circular for an empty host because the OS/image trust base exists before the Aether trust transaction | **SELECTED** |
| `BOOTSTRAP_AUTHORITY_ROOT_MODEL_B_OUT_OF_BAND_KEY_CONFIRMED_BY_LOCAL_CONSOLE` | An offline public key is carried out of band and fingerprint-confirmed during the local ceremony | Possible, but its truthful human confirmation and transport are not currently evidenced | REJECTED FOR THIS PASS |
| `BOOTSTRAP_AUTHORITY_ROOT_MODEL_C_HARDWARE_OR_EXTERNAL_AUTHENTICATED_RESULT` | Hardware or an external authority supplies an authenticated result | Requires a separate hardware/external protocol and availability contract not bounded here | REJECTED FOR THIS PASS |
| `BOOTSTRAP_AUTHORITY_ROOT_MODEL_D_NO_NON_CIRCULAR_ROOT_PROVEN` | No root is selected | Safest current implementation statement, but does not close the requested design contract | REJECTED AS THE DESIGN RESULT |

### 3.3 Selected bootstrap-authority root contract

The authoritative origin is a versioned pre-Aether OS/image provisioning baseline
created before Aether installation by a separately governed OS/image custodian. Its fixed
record path is:

```text
/usr/lib/aether/host-bootstrap/authority-set.json
```

This path is not one of the five M126A mutation objects. The verified OS/image
baseline installs it as a root-owned regular file with mode `0444`, and its exact
bytes and baseline membership are covered by the preexisting OS/image integrity
mechanism. The baseline is established before any candidate, OAS, ordinary
runtime, or M126A trust-bootstrap transaction exists. Aether does not create,
replace, or select this record.

The authority-set record is canonical UTF-8 JSON with sorted keys, bounded size,
no duplicate or unknown fields, and no trailing newline. Its complete wrapper
fields are:

```text
authority_set_version
baseline_id
authority_records
minimum_accepted_authority_generation
set_fingerprint_sha256
image_baseline_manifest_digest
```

Each authority record has exactly these fields:

```text
authority_id
authority_role
algorithm
public_key_base64url
key_fingerprint_sha256
authority_generation
valid_from_utc
valid_until_utc
revoked_at_utc
```

`authority_role` is exactly `HOST_TRUST_BOOTSTRAP_AUTHORITY` and `algorithm` is
exactly `ED25519`. `public_key_base64url` is the 32-byte raw Ed25519 public key
encoded as unpadded base64url. The key fingerprint is the lowercase SHA-256 of:

```text
UTF8("aether.m126a.host-bootstrap-authority-key.v1")
+ BYTE(0x00)
+ UTF8(canonical(authority record without key_fingerprint_sha256))
```

The set fingerprint is the lowercase SHA-256 of the same domain-separated
canonical wrapper with `set_fingerprint_sha256` omitted. Neither fingerprint
hashes itself. The independent host-security approver and the OS/image
provisioning approver approve the exact fingerprint and generation policy before
the baseline is published. Neither may substitute a release-signing key,
release-approval key, M117A Owner credential key, OAS key, TLS key, or PM record.

The target obtains the authority set only by booting or receiving the already
verified OS/image baseline and reading the fixed path through the preexisting
OS/root trust base. The root executor checks path, regular-file type, owner,
mode, baseline membership, canonical bytes, role, algorithm, key length,
validity interval, revocation state, minimum generation, and both recomputed
fingerprints before it reads the selected public key. It compares the envelope's
`verification_key_or_trust_source` to the exact `authority_id`, key fingerprint,
authority generation, set fingerprint, and baseline manifest digest. Only then
does it verify the detached envelope signature. A valid signature under a key
that is not in this independently authenticated baseline fails closed.

The local-console evidence binds the exact authority-set fingerprint, authority
generation, set-record digest, target identity, boot identity, transaction,
nonce, and expiry. It proves that the future human ceremony acknowledged the
same preexisting trust source; it does not make a caller-supplied key trusted.
Missing, duplicated, expired, revoked, ambiguous, baseline-mismatched, or
fingerprint-mismatched records fail closed before mutation intent. Candidate,
OAS, ordinary runtime, PM/governance records, and root possession cannot supply
or replace this trust source. The root and OS/image trust base are assumptions
of this design proof, not live evidence from the current host.

## 4. Trust Roles and Separation

Every role has one bounded authority. Same-person or same-organization custody
does not remove the required record and transaction separation.

| Role | Exact authority | Explicit non-authority |
| --- | --- | --- |
| Production release signing authority | Signs the exact release envelope from separately controlled offline custody | Cannot approve its own release, publish host objects, or activate a release |
| Release approval authority | Approves the exact release, evidence digest, policy, key IDs, and validity window | Cannot sign as release signer, publish host objects, or activate a host |
| Project Manager / governance approval | Approves milestone scope and security policy only; supplies `GovernanceScopeEvidence` | Cannot provide Owner evidence, select trust contents, or authorize target mutation |
| Owner | Provides future instance/host-specific deployment and activation authorization in the later M124A transaction | Does not authorize host release-trust provisioning and cannot turn a candidate, OAS, or root process into universal authority |
| Host trust-bootstrap authority | Validates the OS-attested local-console operator evidence, the OS/image authority baseline, and governance evidence, then authenticates one exact bootstrap envelope | Does not perform filesystem mutation, sign releases, authenticate an Owner, or change deployment state |
| Root trust-bootstrap executor | Verifies the envelope and performs only the exact bounded filesystem mutation | Cannot select policy, anchor, verifier, generation, object contents, or Owner intent |
| Root transaction executor | Performs later M124A/M125A deployment or rollback using preexisting trust proof | Cannot create, replace, or select the trust root or fixed verifier |
| Fixed host verifier | Verifies release artifacts only after its own identity is independently established | Cannot establish its own identity recursively, install objects, select keys, or authorize deployment |
| OAS service principal | Consumes bounded public results and its own canonical state where later contracts permit | Cannot access private signing keys, access or select the bootstrap-authority root, authorize bootstrap, publish trust objects, or become Owner |
| Ordinary Aether runtime | Receives only bounded public verification results where later contracts permit | Cannot read private keys, select trust anchors, mint Owner evidence, or bootstrap the host |

Root is the host trust base, not the source of Owner intent. A process-local
caller, root possession, an OAS request, a release candidate, or a test fixture
cannot establish truthful Owner authority.

## 5. Authenticated Bootstrap Authority Envelope

The bootstrap authorization is not a bare digest and is not an unsigned JSON
object. Four external evidence objects and one durable consumption record are
distinct:

```text
TrustBootstrapAuthorizationPayload
TrustBootstrapAuthorizationEnvelope
LocalConsoleAttestationEvidence
GovernanceScopeEvidence
DurableConsumptionRecord
```

### 5.1 TrustBootstrapAuthorizationPayload

The payload is the exact mutation request. It is canonical UTF-8 JSON with sorted
keys, `separators=(',', ':')`, `ensure_ascii=true`, finite values only, no
duplicate or unknown fields, bounded size, and no trailing newline. Its complete
field set is:

```text
payload_version
authorization_id
transaction_id
target_host_identity_digest
target_boot_digest
trust_generation
minimum_accepted_generation
object_set_digest
requested_objects
mutation_scope
local_console_attestation_digest
governance_scope_digest
bootstrap_authority_root_fingerprint
bootstrap_authority_generation
authority_set_record_digest
issued_at_utc
expires_at_utc
nonce
```

The selected pre-instance rule is `PRE_INSTANCE_MODEL_B`: host-level release
trust may be established before an Aether Instance exists. This payload therefore
contains no nullable or fabricated `aether_instance_id`. It binds only the target
host, current boot, host trust generation, authority generation, and exact object
set. It authenticates software provenance only; it cannot authenticate an Owner,
authorize an Aether Instance, or activate software.

`requested_objects` is exactly the five fixed paths in section 7. `mutation_scope`
is exactly `PUBLISH_EXACT_FIVE_HOST_TRUST_OBJECTS_FOR_TARGET_HOST_AND_GENERATION`; it cannot
contain a candidate path, a release path, a service action, an account action,
or an implicit wildcard. The payload binds the target, boot, next host
generation, generation floor, object-set digest, local-console evidence digest,
governance scope digest, bootstrap-authority root fingerprint, authority
generation, authority-set record digest, nonce, transaction ID, and bounded
issue/expiry interval.

### 5.2 TrustBootstrapAuthorizationEnvelope

The envelope is a separate canonical UTF-8 JSON object that carries no secret
and does not contain a reconstructed payload. Its complete field set is:

```text
envelope_version
payload_sha256
authorizing_role
authorizing_authority_id
authenticated_evidence_algorithm
detached_signature
verification_key_or_trust_source
issued_at_utc
expires_at_utc
target_host_identity_digest
target_boot_digest
bootstrap_authority_root_fingerprint
bootstrap_authority_generation
authority_set_record_digest
trust_generation
object_set_digest
nonce
transaction_id
domain_separator
```

The signing input is:

```text
ASCII("aether.m126a.trust-bootstrap-authorization.v1")
+ BYTE(0x00)
+ UTF8(canonical(TrustBootstrapAuthorizationPayload))
+ BYTE(0x00)
+ UTF8(canonical(TrustBootstrapAuthorizationEnvelope without detached_signature))
```

The future authenticated-evidence algorithm is the explicitly selected
`ED25519_DETACHED_SIGNATURE_V1`; `detached_signature` is exactly 64 raw bytes
encoded as base64url without padding. The verification source is the exact
pre-Aether OS/image authority-set baseline defined in section 3.3, not a
candidate, ordinary runtime, OAS, PM record, or root possession. The authorizing
role is exactly `HOST_TRUST_BOOTSTRAP_AUTHORITY`, and its authority identifier
must be present in that independently authenticated set with an unambiguous key,
validity interval, and non-revoked status.

The envelope copies the target, boot, generation, object-set, nonce, and
transaction bindings from the payload. A mismatch fails closed. M126A defines
the future algorithm and evidence shape only; it creates no key, signature, or
credential and does not claim that the live authority source exists.

`verification_key_or_trust_source` is a structured reference, not caller-chosen
key material. Its exact value is:

```text
source_kind
authority_set_path
authority_set_record_digest
authority_id
key_fingerprint_sha256
authority_generation
image_baseline_manifest_digest
```

`source_kind` is exactly `PREEXISTING_OS_IMAGE_AUTHORITY_SET`, and every value is
copied from the authenticated baseline or recomputed by the root executor. A
candidate-supplied public key, fingerprint, path, or digest is rejected even if
the detached signature is mathematically valid.

### 5.3 LocalConsoleAttestationEvidence

This evidence is a separately identified, future authenticated record proving
the OS-attested local-console ceremony and host-operator authorization to use the
preexisting OS/image authority baseline. It is not Owner deployment evidence. Its
exact fields are:

```text
evidence_version
attestation_id
target_host_identity_digest
target_boot_digest
bootstrap_authority_root_fingerprint
bootstrap_authority_generation
authority_set_record_digest
local_console_authority_id
session_class
remote
fresh_authentication
human_confirmation_digest
issued_at_utc
expires_at_utc
nonce
evidence_algorithm
authenticated_evidence
```

The required values are `session_class=LOCAL_CONSOLE`, `remote=false`, and
`fresh_authentication=true`. OS/kernel evidence establishes the local session
fact; the future host operator source establishes authorization to use the
baseline. Neither a
process-local caller, root possession, PM approval, OAS result, candidate
fixture, nor a caller assertion can replace this evidence. The evidence is
bound to the exact authority baseline, target, boot, nonce, transaction scope,
and expiry. It does not create an Aether Instance or an Owner trust root.

The local-console record is authenticated by the separate OS-attested local-seat
mechanism and the fixed helper/peer contract; it is not self-signed by the
bootstrap-authority key. The bootstrap key therefore cannot manufacture its own
human-presence evidence or turn local key possession into Owner authority.

### 5.4 GovernanceScopeEvidence

Governance evidence is separate from local-console operator evidence and cannot
be promoted to Owner or bootstrap-key authority. Its exact fields are:

```text
evidence_version
governance_evidence_id
milestone
approved_scope_digest
approved_policy_digest
approved_object_set_digest
approved_generation_policy_digest
issuer_role
issuer_authority_id
issued_at_utc
expires_at_utc
authenticated_evidence_algorithm
authenticated_evidence
```

`issuer_role` is exactly `PM_GOVERNANCE`; it authorizes milestone scope and
security policy only. It does not authorize the Owner, select a private key,
authenticate local presence, or authorize target mutation by itself.

### 5.5 DurableConsumptionRecord

The future root-owned durable state store is `/var/lib/aether/trust-bootstrap`,
owned by `root:root`, mode `0700`; its canonical state database and journal are
owned by the fixed root trust-bootstrap executor and are inaccessible to OAS,
ordinary runtime, candidate code, and the host trust-bootstrap authority after
authorization. The canonical record has these exact fields:

```text
record_version
transaction_id
authorization_id
envelope_sha256
payload_sha256
local_console_attestation_digest
governance_scope_digest
target_host_identity_digest
target_boot_digest
bootstrap_authority_root_fingerprint
bootstrap_authority_generation
authority_set_record_digest
trust_generation
object_set_digest
nonce
state
previous_record_digest
journal_head_digest
issued_at_utc
expires_at_utc
consumed_at_utc
result
failure_class
```

The durable record is a consumption record, not a replacement authorization.
It is created only after envelope and evidence verification succeeds. Its
`state` is one exact state from section 9, and its `previous_record_digest`
and `journal_head_digest` form the forward audit chain.

### 5.6 Envelope verification before mutation intent

The future root trust-bootstrap executor performs these checks in order before
persisting any mutation intent:

1. Parse the payload, envelope, local-console evidence, and governance evidence
   with exact fields, canonical encoding, bounded sizes, and no duplicates.
2. Recompute `payload_sha256` and both domain-separated authenticated-evidence
   inputs.
3. Read the fixed OS/image authority-set record, recompute its key and set
   fingerprints, compare the baseline membership and exact trust-source
   reference, and reject any key not in that authenticated set.
4. Verify the detached envelope evidence with the selected baseline key and
   require the exact role, authority identifier, algorithm, domain, validity
   window, and non-revocation state.
5. Verify the local-console evidence and the governance evidence independently;
   PM approval is not Owner evidence, and root possession is not Owner evidence.
6. Bind every copied envelope field to the payload and bind both evidence
   digests to the payload's exact mutation scope and host trust source.
7. Verify the target host identity, current boot, unused transaction/nonce,
   generation floor, exact five-object set, and independently approved object
   bytes without accepting candidate-provided verification authority.
8. Confirm that no durable intent exists for this transaction and that no
   conflicting intent, authority, target, boot, generation, nonce, object-set,
   or authority identifier is present.
9. Only then persist `TRUST_BOOTSTRAP_REQUESTED` and its canonical
   `DurableConsumptionRecord`, fsync the record and state directory, and begin
   the bounded publication state machine.

The executor rejects a bare digest, unsigned JSON, a valid signature under an
untrusted key, unknown or ambiguous signing authority, PM-only evidence,
root-only evidence, candidate verification keys, ordinary-runtime evidence, OAS
evidence, expired authority for a new transaction, and any changed binding. No
key, signature, credential, or live source is created or accessed during M126A.

## 6. Key and Artifact Classes

The classes are intentionally distinct:

| Class | Owner/source | Public or secret | M126A rule |
| --- | --- | --- | --- |
| Private release signing key | Offline production signing custody | Secret | Never in repository, host, release, OAS, runtime, backup, logs, or summaries |
| Private approval key | Separate approval custody | Secret | Never co-located with release signing custody or exposed to candidate/runtime |
| Public trust anchor | Approved host trust-bootstrap input | Public metadata | Exact canonical anchor; not release-supplied |
| Anchor fingerprint | Independent approval of canonical anchor payload | Public digest | Non-self-referential SHA-256; fixed file is not candidate-supplied |
| Signed release envelope | Release signer plus approval authority | Public signature metadata | Carries exact manifest and approval payload bindings |
| Approval signature | Release approval authority | Public signature metadata | Signs exact carried approval payload, not reconstructed metadata |
| Approved test-evidence digest | Independent validation/review record | Public digest | Binds named evidence; candidate cannot select the approved value |
| Fixed-verifier identity | Independent host-trust review | Public digest and executable bytes | Path, mode, version, and SHA-256 are jointly bound |
| Trust-bootstrap authorization record | Governance, Owner, and host-bootstrap procedure | Non-secret evidence | One-use, target-bound, generation-bound, expiry-bound record |
| Trust-bootstrap audit record | Host-bootstrap authority | Non-secret evidence | Records decisions and digests; never secrets |
| Revocation record | Approved trust policy | Public metadata | Key ID and UTC revocation time; no silent fallback |
| Rotation record | Approved trust policy | Public metadata | Old/new generation, overlap, floor, and final retirement evidence |
| Recovery evidence | Host-bootstrap and governance review | Non-secret evidence | Proves custody/review and exact replacement; never contains secret values |

### 6.1 Private-Key Boundary

Private production signing and approval keys may exist only in separately
controlled offline custody, such as an approved offline encrypted store or a
reviewed hardware-backed custody system. Model A does not require a particular
hardware device and does not claim that one exists. A future custody procedure
must require independent key identifiers, an approved custodian set, physical
or equivalent access controls, encrypted backup policy, and an auditable signing
request record.

Private keys must never exist in the repository checkout, release tree,
wheelhouse, manifest, envelope, target host, `/etc/aether`, `/usr/libexec`,
OAS state, ordinary runtime memory, environment, command-line arguments,
temporary verification staging after use, backups, logs, test fixtures, or
external summaries. M126A performed no private-key search, access, import,
generation, display, copy, or cryptographic signing operation.

Every future signing request must bind a request ID, release ID, manifest
digest, source commit/tree, approved test-evidence digest, key ID, signer role,
issue/expiry window, nonce, and approval record digest. The signer must refuse
an unapproved, duplicate, conflicting, expired, revoked, or candidate-selected
request. Signing output is a detached public signature; it is not authority to
install or activate a release.

Logs and evidence record only key IDs, roles, public digests, result classes,
transaction IDs, and timestamps. Secret values, private-key bytes, passphrases,
raw tokens, and custody locations are excluded.

## 7. The Five Fixed Host Trust Objects

The following five paths are fixed M124A objects. They are a trust set, not
candidate release files. All are root-owned regular files. The parent
`/etc/aether` is root-owned mode `0755`.

| Object | Source authority | Policy approval | Transaction authorization | Mutation executor | Postcondition verifier | Owner/mode and encoding | Binding and verification | Candidate supply |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `/etc/aether/release-trust-anchor.pub` | Independently approved out-of-band anchor custody | PM/governance policy plus independent trust review | Valid envelope with exact object-set digest | Root trust-bootstrap executor | Preexisting OS/root trust base plus independent host observation | `root:root`, regular, `0444`; canonical UTF-8 JSON with exact M121A anchor fields; fingerprint excluded from hashed payload | Non-self-referential anchor fingerprint, path/type/mode/link checks, and generation binding | **NEVER** |
| `/etc/aether/release-trust-anchor.fingerprint` | Independent approval of the exact anchor payload digest | Same policy record, independently checked | Same exact envelope and object-set digest | Root trust-bootstrap executor | Preexisting OS/root trust base plus independent host observation | `root:root`, regular, `0444`; lowercase SHA-256 hex with at most one terminal newline | Must equal the independently computed anchor fingerprint; mismatch fails closed | **NEVER** |
| `/etc/aether/release-test-evidence.sha256` | Independent validation/review record | Release approval plus PM/governance evidence review | Same exact envelope and object-set digest | Root trust-bootstrap executor | Independent host observation and digest comparison | `root:root`, regular, `0444`; lowercase SHA-256 hex with at most one terminal newline | Binds approved evidence to host trust generation and later release packet | **NEVER** |
| `/etc/aether/release-verifier.sha256` | Independent fixed-verifier identity approval | Host trust-bootstrap authority plus independent verifier review | Same exact envelope and object-set digest | Root trust-bootstrap executor | Preexisting OS/root trust base plus independent host observation | `root:root`, regular, `0444`; lowercase SHA-256 hex with at most one terminal newline | Equals the independently approved executable digest and fixed execution boundary | **NEVER** |
| `/usr/libexec/aether-release-verify` | Separately reviewed fixed verifier artifact outside the candidate release | Independent host-trust/verifier review | Same exact envelope and object-set digest | Root trust-bootstrap executor | Preexisting OS/root trust base verifies identity before this verifier runs | `root:root`, regular executable, `0555`; exact reviewed bytes | Path, owner, mode, hard-link identity, hash, version, interpreter/native identity, dependency policy, fixed argv and environment | **NEVER** |

The fixed verifier is not part of a release. The candidate cannot replace or select the anchor, fingerprint, approved evidence digest, verifier digest, verifier executable, verifier version, trust path, approval policy, or key IDs.
Candidate self-authorization is forbidden even when the candidate is signed by
an otherwise valid release key.

The five-object set is accepted only when every object is present, regular,
root-owned, exact-mode, hard-link-unambiguous, cross-bound to one approved trust
generation, and verified by the future host-bootstrap transaction. A partial or
mixed set is not a usable trust root.

The complete trust set is cross-bound to one approved trust generation.

### 7.1 Fixed-verifier bootstrap without recursion

`/usr/libexec/aether-release-verify` is not trusted to establish its own
identity. Before the fixed verifier is executed, a smaller preexisting
`PREEXISTING_OS_ROOT_TRUST_BASE` verifies all of the following against
independent approved inputs:

```text
exact executable bytes
approved SHA-256
absolute path
root:root owner
mode 0555
regular-file type
hard-link identity
interpreter or native-executable identity
library/dependency policy
fixed argv contract
fixed environment contract
```

The preexisting base may be an approved OS/image/package trust mechanism or a
separately reviewed bootstrap verifier. M126A does not claim that it exists,
and it does not execute the candidate fixed verifier to prove the candidate's
fixed-verifier identity. Only after the independent digest and execution
boundary pass may the fixed verifier verify release artifacts. The fixed
verifier verifies release signatures and approval signatures only; it must not
recursively establish its own trust.

The assumed base includes the OS, kernel, root filesystem ownership and mode
controls, the cryptographic hash implementation, and the fixed bootstrap
execution mechanism. Root, kernel, systemd, filesystem, package/image supply
chain, and hash-implementation compromise remain outside this proof. No
protection from compromise of that base is claimed.

### 7.2 Trust-object authority matrix

For every object, source authority supplies bytes, policy approval approves the
policy, transaction authorization permits this exact transaction, the mutation
executor performs the write, and the postcondition verifier independently
checks the live result. These are distinct semantic roles even when the root
executor is the process that performs the write. The host trust-bootstrap
authority authenticates the envelope; it is not the mutation executor.

## 8. Initial Bootstrap Ceremony

This is an exact future design ceremony for an untrusted `NOT_DEPLOYED` host.
It is not implemented or executed by M126A.

### 8.1 Starting state and prerequisites

The starting state is an untrusted host with no accepted production trust set,
no candidate accepted, no deployment activation, and no live OAS trust boundary.
The host may have absent or incomplete fixed paths; absence is not proof of
global production-material unavailability. The candidate release and its
contents are not an input to trust-root creation.

Required prerequisites are:

- a PM/governance-approved trust policy and exact object inventory;
- an independently approved anchor payload and non-self-referential fingerprint;
- independently approved verifier bytes, version, path, mode, and digest;
- independently approved test-evidence digest policy and exact value;
- an OS-attested local-console session with no remote or SSH indicators;
- the fixed OS/image authority-set record and its independently approved
  fingerprint, authority generation, set digest, and validity interval;
- a future one-use authorization record bound to the target host, trust
  generation, object-set digest, nonce, and expiry;
- independent review of the custody and approval records;
- no candidate-provided trust input and no private-key input.

OS-attested local presence is a host trust prerequisite, not proof of universal
Owner intent and not deployment activation authority. Current M117A local
presence and Owner sources remain design-only and unproven.

### 8.2 Ordered ceremony

| Step | Exact action | Required evidence | Failure result |
| --- | --- | --- | --- |
| TB-00 | Establish `UNTRUSTED_NOT_DEPLOYED` and reject candidate trust input | Read-only target/profile state and no candidate-derived trust fields | Stop before mutation |
| TB-01 | Validate OS-attested local-console presence and fresh human ceremony | Kernel peer credentials, active non-remote local seat, session identity, fresh authentication, one-use confirmation | Reject before mutation |
| TB-02 | Read and verify the independently authenticated OS/image authority baseline, then obtain the approved public trust set | Fixed authority-set path, baseline membership, key/set fingerprints, authority generation, anchor payload, verifier bytes/digest, approved test-evidence digest, custody/review references | Reject missing, conflicting, expired, revoked, baseline-mismatched, or candidate-supplied inputs |
| TB-03 | Validate the canonical payload, authenticated envelope, local-console attestation, and governance evidence | Exact fields, canonical payload digest, detached authenticated evidence, baseline trust-source comparison, target identity, generation, nonce, expiry, and object-set digest | Reject bare digest, unsigned JSON, valid signature under an untrusted key, replay, mismatch, ambiguous authority, or expired authority |
| TB-04 | Validate all five staged inputs read-only | Exact JSON fields, canonical bytes, fingerprint, executable hash, modes, paths, no symlink/hard-link ambiguity | Reject without publication |
| TB-05 | Stage each object under a root-only transaction directory | Root-owned `0700` staging, exclusive no-follow files, bounded sizes, exact content and metadata | Retain evidence; remove only exact unreferenced staging |
| TB-06 | Recompute cross-object trust-set digest and generation | Anchor fingerprint, verifier digest, evidence digest, object paths, policy version, trust generation | Reject mixed or stale set |
| TB-07 | Write and fsync each staged file | File flush/fsync, exact mode, exact owner, no secrets | Storage failure prevents publication |
| TB-08 | Publish objects across `/etc/aether` and `/usr/libexec` by ordered per-file rename | Parent directory fsync after each publication; five-object publication is not filesystem-atomic and every partial/mixed set is unusable | Fail closed; no candidate verification is allowed |
| TB-09 | Persist the durable journal/state transition and non-secret audit in the root-owned state store | Transaction ID, generation, journal chain, object digests, authorization/envelope/payload digests, result, timestamps, no secret | Do not claim success; require root review |
| TB-10 | Observe the complete published set | `lstat`, type, owner, mode, link count, bytes/digests, path confinement, generation consistency | Mark `TRUST_BOOTSTRAP_REVIEW_REQUIRED`; do not accept trust |
| TB-11 | Verify fixed verifier identity and public anchor independently | Verifier digest, anchor fingerprint, approved evidence digest, key status and validity | Fail closed before any release verification |
| TB-12 | Record `TRUST_SET_ACTIVE` only after all gates pass | Final trust-set digest, generation floor, authorization and audit references | Preserve prior valid set or require review; never guess |
| TB-13 | Release the bounded lock and return only public result metadata | Completion digest, result class, transaction identity, timestamps | Unknown result remains review-required and is not retried blindly |

Object publication is atomic per file and directory entry, not a fictional
atomic replacement of five independent paths. During initial bootstrap every
partial set is unusable because the exact set validation fails. During rotation,
the prior valid set remains the recovery reference until the new complete set
and generation record are verified. A retry uses the same transaction and nonce;
an identical committed result is returned, while changed content is a conflict.

### 8.3 Bootstrap postconditions

Success requires all five exact objects, one active host trust generation, a
durable trust-set digest, a valid minimum-generation floor, a committed audit
record, terminal Observation, terminal Verification, and no candidate or
deployment mutation. It proves only that the trust set was published under the
separately defined ceremony. It does not prove release approval, Owner
deployment authorization, OAS readiness, deployment, or rollback.

### 8.4 New transaction, started transaction, expiry, and resume

Authorization to start a transaction is distinct from authority to resume one
already durably started. A `NEW TRANSACTION` has no durable bootstrap intent. It
requires an authentic, exact, unexpired envelope and all independently verified
evidence. Expiry before `TRUST_BOOTSTRAP_REQUESTED` prevents every mutation.

A `STARTED TRANSACTION` has a durable intent created while the authorization was
valid. The intent freezes the exact authorization digest, envelope digest,
  payload digest, target, boot, host trust generation, authority generation,
nonce, object-set digest, and requested five-object scope. After wall-clock
expiry, an identical retry may resume only this frozen transaction. Resume may
only complete the exact next-generation publication, restore the exact retained
prior generation, or enter `TRUST_BOOTSTRAP_REVIEW_REQUIRED`. Resume cannot
expand scope, change objects, change generation, change authority, or begin a
new transaction.

Changed authority, target, boot identity, generation, nonce, object bytes,
trust-set digest, payload/envelope digest, or transaction identity is a
conflict and fails closed. Expired authority never starts a new mutation, but
an already-started transaction is not stranded solely because wall-clock
expiry occurred after durable intent.

Examples:

| Point of expiry or crash | Exact result |
| --- | --- |
| Expiry before durable intent | `NEW TRANSACTION` rejects; no object, journal, or filesystem mutation |
| Crash after durable intent but before staging | Same transaction may resume with the frozen envelope/payload binding; a changed retry conflicts |
| Crash during publication after expiry | Resume may finish only the frozen next-generation sequence, restore the exact retained prior set, or enter review; it may not start another transaction |
| Expiry after `TRUST_SET_ACTIVE` commit | The committed result remains authoritative; an identical retry returns the same public result and cannot republish |
| Ambiguous observation at any resume point | No guessed completion or restoration; enter `TRUST_BOOTSTRAP_REVIEW_REQUIRED` |

## 9. Cross-Directory Publication, Rotation, and Recovery

The five objects span `/etc/aether` and `/usr/libexec`; therefore no claim of
atomic five-object publication is made. The exact durable state machine is:

```text
TRUST_BOOTSTRAP_REQUESTED
TRUST_BOOTSTRAP_VALIDATED
PRIOR_GENERATION_RETAINED
NEXT_GENERATION_STAGED
PUBLISHING
VERIFYING
TRUST_SET_ACTIVE
RESTORING_PRIOR_GENERATION
TRUST_BOOTSTRAP_REVIEW_REQUIRED
```

The root-owned durable journal is append-only and canonical. Each record
contains `journal_sequence`, `transaction_id`, `state`, `action`, `path`,
`expected_digest`, `observed_digest`, `previous_record_digest`,
`authorization_digest`, `envelope_digest`, `payload_digest`,
`trust_generation`, `object_set_digest`, `fsync_result`, and `record_digest`.
Every append is file-fsynced and followed by directory fsync before the next
publication step. The journal's `previous_record_digest` chains every state,
publication, observation, restoration, and terminal decision.

Before the first live-path replacement during rotation, the executor durably
retains the exact prior five-object bytes, paths, owner/mode/link identity,
prior trust generation, prior trust-set digest, prior anchor fingerprint,
prior verifier digest, and the recovery transaction binding. The retained set
is root-only, outside candidate control, transaction-bound, fsynced,
directory-fsynced, immutable to ordinary runtime and OAS, and independently
verified before restoration. If prior bytes or metadata cannot be proven, the
result is review-required; restoration is never guessed.

The exact publication order is:

```text
1. /usr/libexec/aether-release-verify
2. /etc/aether/release-verifier.sha256
3. /etc/aether/release-trust-anchor.pub
4. /etc/aether/release-trust-anchor.fingerprint
5. /etc/aether/release-test-evidence.sha256
```

The executor records `PUBLISHING`, writes each object through a root-owned
same-directory temporary file, fsyncs the file, renames the one directory
entry, fsyncs its parent directory, and records the observation before moving
to the next path. Trust acceptance is disabled unless all five live paths pass
the exact `VERIFYING` observation for one generation. A mixed set is never
active.

The exact crash and recovery matrix is:

| Interruption | Durable state and required result |
| --- | --- |
| Before `TRUST_BOOTSTRAP_REQUESTED` | No mutation intent; reject or retry only as a new exact unexpired transaction |
| After intent, before validation | Resume the same frozen transaction after revalidation; changed evidence conflicts |
| During prior-set retention | Do not publish; incomplete retention enters review |
| During staging | Discard only exact transaction staging after identity verification; ambiguity enters review |
| Before first live replacement | Prior active set remains active; no automatic new publication |
| Between `/usr/libexec` and `/etc` publication | State remains `PUBLISHING`; mixed set is unusable; restore prior only if every retained byte and identity is proven |
| After all writes, before `VERIFYING` | Do not mark active; verify every live path or restore exact prior set/review |
| After `VERIFYING`, before state/audit commit | Files may be complete but are not authoritative; retain journal and require exact retry or review |
| After state/audit commit | `TRUST_SET_ACTIVE` is authoritative only with the committed exact observation; later ambiguity fails closed and triggers reconciliation |
| Prior bytes unavailable or changed | Automatic restoration is prohibited; enter `TRUST_BOOTSTRAP_REVIEW_REQUIRED` |
| Conflicting retry | Reject; never overwrite the frozen transaction or lower the generation floor |

Restoration uses the exact retained prior generation, reverse publication order,
per-file fsync and parent-directory fsync, followed by complete Observation and
Verification. Restoration is prohibited when prior identity, bytes, link count,
ownership/mode, generation, journal chain, or transaction binding is ambiguous.
Its terminal result is either the verified prior generation or
`TRUST_BOOTSTRAP_REVIEW_REQUIRED`; no partial restoration is active.

## 10. State/Audit and Filesystem Atomicity

Filesystem publication is a multi-step mutation and is not atomic across
`/etc/aether` and `/usr/libexec`. The canonical state store is the future
root-owned `/var/lib/aether/trust-bootstrap/state.sqlite3`, mode `0600`, in
the root-owned `0700` directory. The fixed root trust-bootstrap executor is
the only writer; the host trust-bootstrap authority authorizes but does not
write, and OAS, ordinary runtime, and candidate code have no write path.

Canonical transaction state and its canonical non-secret audit record may commit
atomically in one durable state-store transaction. That database transaction
does not make filesystem writes atomic. `TRUST_SET_ACTIVE` may be committed
only after terminal Observation and Verification prove all five live paths,
their exact bytes, path/type, owner/mode, link identity, generation, and
object-set digest. The state commit includes the final journal head,
previous/current record digests, generation floor, authorization/envelope/payload
digests, and observed object-set digest.

If the state/audit commit succeeds but a later observation is ambiguous or
differs, release acceptance fails closed immediately; the state, journal, and
filesystem are reconciled through a new root-reviewed transition and never by
assuming that the database made the paths atomic. External logs are asynchronous
copies and remain non-authoritative. The terminal Observation record and
terminal Verification record are required before reporting success.

The terminal result is evidence of a verified trust set only. It is not release
approval, Owner deployment authorization, OAS readiness, deployment, or live
rollback verification.

## 11. Rotation and Generation Policy

### 11.1 Bootstrap-authority verification-key lifecycle

The host-bootstrap authorization key is a distinct trust domain. Its private
signing counterpart exists only in offline host-bootstrap authority custody. The
public verification key is represented only by the `HOST_TRUST_BOOTSTRAP_AUTHORITY`
record in the pre-Aether OS/image authority baseline. It is not a production
release-signing key, release-approval key, release-trust anchor key, M117A Owner
credential key, OAS signing key, TLS key, or PM/governance record.

The key's only permitted signature domain is:

```text
aether.m126a.trust-bootstrap-authorization.v1
```

It authorizes one exact host trust-bootstrap transaction: the five fixed trust
objects, one target host, one boot identity, one host trust generation, one
authority generation, one nonce, one transaction ID, and one bounded expiry. It
cannot authorize release signing, release approval, Owner authentication,
deployment, activation, rollback, Generic Act, or unrelated host mutation.

The complete lifecycle is:

| Lifecycle stage | Exact contract | Evidence and failure boundary |
| --- | --- | --- |
| Initial approval | Offline custodian generates or imports a dedicated Ed25519 key pair; independent host-security and OS/image approvers approve `authority_id`, key fingerprint, role, validity interval, generation 1, and minimum generation | Canonical authority record and independent approval digests; no approval key or release key may approve itself as this key domain |
| Introduction | The public record is added to the verified OS/image provisioning baseline before Aether installation at `/usr/lib/aether/host-bootstrap/authority-set.json` | Preexisting OS/image integrity evidence and baseline manifest membership; candidate, OAS, runtime, and M126A cannot introduce it |
| Identity and validity | `authority_id` is unique and immutable; raw Ed25519 public key is 32 bytes; fingerprint uses `aether.m126a.host-bootstrap-authority-key.v1`; validity is an explicit UTC interval and generation | Root checks exact canonical bytes, fingerprint, role, interval, revocation, and minimum generation before signature verification |
| Normal use | One valid key signs one exact envelope during its validity interval; the envelope and local-console evidence carry the key ID, key fingerprint, authority generation, set fingerprint, and baseline digest | Durable consumption record binds the transaction, nonce, authority, and result; replay or changed binding fails closed |
| Planned rotation | A separately approved next key is prepositioned in a new OS/image baseline with a higher authority generation; there is no dual-acceptance signing overlap. The old key remains the sole accepted key until the explicit cutover baseline is installed | Cutover requires independent approvals, a new baseline, a fresh local-console ceremony, monotonic minimum-generation advance, and audit; the old key cannot authorize its own replacement |
| Revocation | A key is revoked by an independently approved OS/image authority-set update; revocation is checked before every new transaction and applies immediately to new authorizations | No silent fallback to an old or candidate key; already-started transactions may only follow the frozen resume rule and cannot create new intent |
| Compromise response | Freeze all new bootstrap requests, preserve the affected baseline and journal, and reject the compromised key as a replacement authority | Recovery requires a fresh verified OS/image baseline, independent replacement-key approval, a new authority generation, and a fresh OS-attested local-console ceremony |
| Loss and recovery | Loss of the private key stops new authorization; the public record is not used to infer a replacement private key | Offline backup or a newly approved key may restore authority only through a new baseline and independent review; root possession, PM scope approval, release keys, and candidate material are insufficient |
| Offline backup | Encrypted offline backup may retain the private key only under separately approved custody, with key ID, custody audit, and recovery controls; the target receives no private backup | Backup is not a target authority source and cannot self-activate, sign, rotate, or recover a key |
| Host replacement | The destination receives a newly verified OS/image baseline and a new host identity binding; the authority key may be reused only if independent custody policy approves it, never by copying the old host file | Fresh local-console ceremony, new baseline digest, target identity, transaction, nonce, and audit are required; copied host objects are rejected |
| Replay state | The durable root-owned store records transaction ID, nonce, authority ID, authority generation, set fingerprint, consumed state, journal head, and minimum accepted generation | Reuse, downgrade, conflicting retry, or stale generation is rejected before mutation |
| Retirement | After cutover and overlap-free revocation, the old key is removed from newly provisioned baselines and retained only as non-secret historical audit metadata | No new signature under the retired key is accepted; retirement does not erase evidence or lower the generation floor |

There is no dual-acceptance overlap. A next key can be present only as an
inert, prepositioned record until independent cutover. A compromised current key
cannot authorize its own unrestricted replacement, and root cannot rotate it by
possession alone. The truthful recovery source is therefore a fresh verified
OS/image baseline plus a fresh OS-attested local-console human ceremony; that
live source is not implemented or proven by M126A.

Trust generation is a monotonically increasing integer or equivalent approved
epoch identifier in the durable trust-bootstrap record. It is not inferred from
file modification time. The record binds:

```text
trust_generation
minimum_accepted_generation
anchor_fingerprint
verifier_sha256
approved_test_evidence_digest
trust_set_digest
rotation_transaction_id
```

The fixed anchor format remains the exact M121A format. A planned rotation
publishes a new anchor containing the old and next keys for each role and an
explicit overlap policy. During overlap:

- the new anchor fingerprint is approved before publication;
- old and next release keys and old and next approval keys are independently
  identified by key ID and role;
- a release accepted during overlap has the required old/next signatures for
  each role, with no duplicate or conflicting key IDs;
- the new trust generation is greater than the previous generation;
- `minimum_accepted_generation` never decreases;
- candidate verification binds the packet to the active generation and exact
  anchor fingerprint;
- an expired overlap does not silently extend.

Publication stages the complete next trust set and verifies it before changing
the fixed paths. A mixed old/new set is invalid. The old generation remains a
recovery reference until the next set, record, and audit are durable. After the
overlap, retired keys are explicitly revoked or expired, old signatures are no
longer accepted for new activation, and retired material is removed only by a
separately reviewed host-bootstrap transaction. A retained old release cannot
roll back if its required signing or approval key is revoked.

Power loss before the new generation commit leaves the old valid generation
authoritative or enters `TRUST_BOOTSTRAP_REVIEW_REQUIRED` if the set is mixed.
Power loss after commit leaves the new generation authoritative and rejects
stale old-generation authorization. No boot, timestamp, or file ordering can
lower the generation floor.

## 12. Revocation, Compromise, and Fail-Closed Recovery

| Event | Immediate result | Required recovery boundary |
| --- | --- | --- |
| Release signing key compromise | Revoke key ID; reject new releases and rollback requiring it | Independent replacement signing authority and approved anchor rotation |
| Approval key compromise | Revoke approval key ID; reject affected approvals | Independent approval review and new approval key generation |
| Bootstrap-authority key compromise | Freeze new bootstrap requests; reject the compromised authority for replacement or new intent | Fresh verified OS/image baseline, independently approved replacement key and generation, and fresh OS-attested local-console ceremony |
| Bootstrap-authority private-key loss | Reject new authorization; never derive or fabricate a replacement from the public key | Independent custody/recovery decision and new OS/image baseline; no root-only, PM-only, release-key, or candidate recovery |
| Host trust-anchor compromise | Stop trust acceptance; do not trust the current anchor to authorize its replacement | Local-console/bootstrap recovery with independent fingerprint approval |
| Fixed verifier compromise | Reject verifier hash/version/path; no candidate verification | Separately reviewed fixed-verifier replacement and trust-set publication |
| Lost offline signing material | No new signing and no fabricated recovery claim; existing verification remains policy-bound only | Independent replacement custody and approved anchor/rotation decision |
| Ambiguous key custody | Freeze affected signing/approval role and reject new authority | Human custody review; no automatic key selection or fallback |
| Suspected replay | Reject reused transaction, nonce, generation, or authorization digest | Root review of durable records and explicit new authorization |
| Conflicting trust generations | Reject all conflicting publication or candidate verification | Preserve evidence; local-console recovery resolves one approved generation |
| Expired bootstrap authorization | Reject before durable intent; an already-started exact frozen transaction may resume only within section 8.4 | New one-use authorization cannot extend or replace the frozen transaction |
| Interrupted publication | Treat mixed/incomplete set as unusable | Verify exact transaction-created objects; restore prior valid set or require manual review |

No compromise path silently falls back to a candidate-provided anchor, an old
revoked key, a test key, a local runtime key, a different verifier, or a lower
trust generation. If exact ownership, content, generation, or transaction
identity cannot be proven, the state is `TRUST_BOOTSTRAP_REVIEW_REQUIRED` and
not `TRUST_SET_ACTIVE`.

## 13. Backup, Restore, Migration, and Clone/Fork

The M117A distinctions remain exact:

```text
BACKUP != RESTORE
BACKUP != CLONE_AUTHORIZATION
RESTORE != MIGRATION
CLONE_OR_FORK != SAME_ACTIVE_AETHER_IDENTITY
```

### Backup

Backup is passive. It may retain public anchor metadata, fingerprints,
verifier digests, public key IDs, trust-set digests, and non-secret audit
history. It excludes private signing/approval keys, active bootstrap
authorizations, one-use nonces, replay state, live sessions, Claim Tokens,
recovery plaintext, and temporary staging. A backup cannot activate trust.

### Restore of the same Aether Instance

Restore requires explicit local recovery, exact `aether_instance_id` continuity
evidence, destination host binding, integrity verification, and a new trust
generation. Stale bootstrap authorizations, nonces, candidate evidence, and
sessions are invalidated. Public trust material may be restored only when its
approved fingerprint and verifier identity are independently revalidated. Raw
backup bytes never self-activate.

### Host replacement and migration

Replacing a host requires a new OS-attested local-console bootstrap on the
destination. Migration requires source quiescence, Owner/governance approval,
destination identity and trust-set verification, new generation binding, source
deactivation or tombstone evidence, and an audit transaction. Copying the five
files without this ceremony is not migration and cannot establish authority.

### Clone or fork

A clone or fork receives a new `aether_instance_id` and a new M117A Owner trust
root. It cannot inherit active Owner credentials, active bootstrap authority,
replay state, or the original host trust objects as authority. It may use the
same independently approved software release-trust policy only through a fresh
host trust-bootstrap ceremony. Copying the five objects does not authorize the
clone or fork, and sharing a release-signing public anchor does not share Owner
authority. A new release anchor is required only when release-trust policy or
custody requires it, not merely because the instance ID changes.

Host trust generation and Owner trust generation remain separate namespaces;
neither generation substitutes for the other. Memory lineage may be explicitly
retained, but authority lineage is not silently inherited. Two copies may not
both claim one active identity solely because their public files match.

### Loss of all current signing material

If all current private signing material is lost, no new release is signable and
no replacement key is inferred from a public anchor. Recovery requires a new
independent custody decision, new key IDs, approved anchor rotation, and a
separate host trust-bootstrap transaction. If the host trust set is lost but
the approved public fingerprint remains independently available, restoration is
still a reviewed trust-bootstrap operation, not automatic file copying.

Absolute global split-brain prevention remains unproven without external or
hardware coordination. M126A does not add a coordinator.

### Release trust versus Owner trust

M126A defines software supply-chain release trust separately from the M117A
`OWNER <-> AETHER INSTANCE` trust root. The release anchor verifies release
manifests and release-approval signatures. It does not authenticate the Owner,
establish the Owner trust root, interpret Owner intent, or authorize deployment.
The Owner trust root authenticates the human authority for one Aether Instance;
the release trust anchor authenticates software provenance for many approved
instances under the same release policy.

A clone or fork must receive a new Aether Instance ID and a new Owner trust root.
It may use the same independently approved software release-trust policy only
through a fresh host trust-bootstrap ceremony. Copying the five host objects does
not authorize the clone or fork. A new release anchor is required only when the
release-trust policy or custody requires it, not merely because the Instance ID
changes. Host trust generation and Owner trust generation remain separate
namespaces, and neither can substitute for the other.

The selected pre-instance rule is:

```text
PRE_INSTANCE_MODEL_B_HOST_RELEASE_TRUST_BEFORE_EXPLICIT_INSTANCE_BINDING
```

The exact non-circular lifecycle is:

```text
EMPTY_HOST
 -> VERIFIED_OS_IMAGE_AUTHORITY_BASELINE
 -> TRUST_BOOTSTRAP_REQUESTED
 -> TRUST_SET_ACTIVE_FOR_TARGET_HOST_AND_GENERATION
 -> CANDIDATE_RELEASE_PROVENANCE_MAY_BE_VERIFIED
 -> M124A_DEPLOYMENT_PACKET_BINDS_VERIFIED_RELEASE_AND_EXACT_HOST_TRUST_GENERATION
 -> PACKET_BINDS_EXPLICIT_AETHER_INSTANCE_ID_AND_TRUTHFUL_OWNER_DEPLOYMENT_AUTHORITY
 -> ACTIVATION_REMAINS_BLOCKED_UNTIL_OWNER_AUTHORITY_AND_ALL_M124A_GATES_PASS
```

The host trust set authenticates software provenance only. It does not
authenticate an Owner, create an Aether Instance, authorize deployment, or
activate software. The later M124A deployment packet must bind the verified
release result, exact host trust generation, exact non-null Aether Instance ID,
truthful Owner deployment authority, target identity, boot identity, and one-use
transaction. The Instance ID is created by the separately governed M124A/M117A
Owner/Instance lifecycle at the later deployment boundary, not by a candidate,
OAS, host trust bootstrap, or nullable placeholder. Copying host trust objects
does not authorize an instance; a clone or fork still requires a new Instance ID
and new Owner trust root. The current truthful Owner source remains unimplemented
and unproven, so activation remains blocked.

## 14. Complete Release Verification Chain

The exact provenance chain is:

```text
source commit
-> source tree
-> dependency lock
-> offline wheelhouse
-> unit bundle
-> runtime entrypoint
-> initial schema
-> release manifest
-> release signature
-> approval signature
-> installed trust anchor
-> fixed verifier
-> exact deployment packet
```

| Boundary | Exact authority and evidence |
| --- | --- |
| Source commit -> source tree | Repository identity binds full commit and tree IDs; no synthetic tag or candidate-selected source |
| Source tree -> dependency lock | Manifest binds exact lock digest and direct/transitive dependency closure |
| Dependency lock -> offline wheelhouse | Lock binds each artifact hash, size, metadata, platform, and offline-only policy |
| Wheelhouse -> unit bundle | M122A unit inventory binds exact four unit bytes and generation digest |
| Unit bundle -> runtime entrypoint | Manifest binds fixed interpreter, import root, entrypoint, and installed file hashes |
| Runtime entrypoint -> initial schema | Manifest binds schema-before/schema-after and M118A-compatible initial schema policy |
| Initial schema -> release manifest | Canonical manifest binds all source, runtime, dependency, build, unit, file, schema, and policy fields |
| Release manifest -> release signature | Production release signing authority signs `aether.m121a.release-manifest.v1` plus canonical manifest bytes |
| Release signature -> approval signature | Separate release approval authority signs the exact carried approval payload and evidence digest |
| Approval signature -> OS/image bootstrap-authority baseline | The pre-Aether OS/image provisioning mechanism carries the independently approved host-bootstrap authority-set record; release signatures and approval signatures cannot populate it |
| OS/image bootstrap-authority baseline -> host-bootstrap envelope | Root recomputes the exact key/set fingerprints and accepts the envelope only when its trust-source reference matches the baseline record |
| Approval signature -> installed trust anchor | Fixed verifier checks approved key IDs and signatures against the independently installed anchor fingerprint |
| Installed anchor -> fixed verifier | Root trust-bootstrap executor installs the separately reviewed verifier and exact approved digest after the preexisting OS/root trust base verifies its identity |
| Fixed verifier -> exact deployment packet | Root executor binds verifier output, trust generation, source, release, evidence, units, authorization, mutation, and rollback digests to the packet |

The candidate may provide the release manifest and envelope as data to be
verified, but it may not supply the trust anchor, fingerprint, approved test
evidence digest, fixed verifier, verifier digest, approval policy, private key,
or trust-generation floor. OAS and ordinary runtime do not sign or install any
link in this chain.

## 15. Transaction and Evidence Semantics

### 15.1 Public evidence and sensitive-data classification

The payload, envelope, local-console evidence, governance evidence, journal,
durable consumption record, terminal Observation, terminal Verification, and
audit record are separate canonical records. None contains private keys,
private-key locations, passphrases, raw authentication material, recovery
plaintext, raw machine IDs, raw boot IDs, or secret staging bytes.

The `DurableConsumptionRecord` in section 5.5 is the authoritative consumed
authorization record. Its `previous_record_digest` and `journal_head_digest`
chain this record to the journal. It does not become Owner authority, policy
authority, or an alternate trust root.

### 15.2 Public evidence contents and digest limits

Publicly verifiable evidence may contain object paths, modes, public key IDs,
anchor fingerprints, verifier hashes, manifest/release digests, test-evidence
digests, transaction IDs, trust generations, bounded result classes, and
timestamps. It does not contain secret values. A digest is evidence of exact
bytes only when the authoritative source, domain, input scope, and verification
time are also recorded. A digest does not prove custody, Owner intent, host
identity, deployment, or completion by itself.

## 16. Threat and Boundary Matrix

| Threat or confusion | Required control | Result |
| --- | --- | --- |
| Candidate supplies its own anchor | Anchor and fingerprint are out-of-band and fixed-path root objects | Reject before candidate verification |
| Candidate supplies its own verifier | Verifier path and hash are separately approved and installed | Reject fixed-verifier identity |
| Candidate self-approves evidence | Test-evidence digest comes from independent review and is bound in the approval record | Reject approval/evidence mismatch |
| Valid signature under an untrusted key | Root first authenticates the OS/image authority-set baseline and compares the exact key/set fingerprint before signature verification | Reject before mutation intent |
| Bootstrap key replaces itself | Replacement requires a new independently approved OS/image baseline, higher authority generation, and fresh local-console ceremony | Freeze and require recovery review |
| Release or approval key crosses domains | Exact role, key ID, fingerprint, and signature domain are distinct and allowlisted | Reject role or domain mismatch |
| Runtime reads or writes trust root | Separate service principal and root-owned `0444`/`0555` objects; no runtime write path | Access denied or fail closed |
| OAS becomes signer | OAS receives no private signing key and has no signing operation | No Owner/release evidence is minted |
| Root substitutes for Owner | Root executes only an exact one-use reviewed bootstrap record | Reject absent or expanded Owner/local-presence evidence |
| Old generation replay | Durable minimum-generation floor and nonce/transaction consumption | Reject stale generation |
| Mixed rotation set | Five-object cross-set digest and exact generation validation | Trust set unusable; review required |
| Fixed verifier replacement | Independent verifier digest and path/mode/link checks | Reject before release verification |
| Lost private keys | No inferred replacement or candidate fallback | Freeze until independent recovery decision |
| Clone inherits authority | New instance ID and new trust root required | Clone cannot impersonate original |
| Test result becomes deployment proof | Separate `TEST_VERIFIED` and `DEPLOYMENT_VERIFIED` dimensions | No deployment claim |

Root, kernel, systemd, physical custody, and equivalent host trust-base
compromise remain outside this design proof. No protection from those failures
is claimed.

## 17. Build-Readiness Decision

The design hard gates are sufficiently explicit to recommend a later bounded
trust-bootstrap implementation/proof Build for separate PM review. Such a Build
would need its own authorization and would remain separate from deployment and
Owner activation. It would not be started by M126A.

The possible later Build scope is limited to an isolated, non-production proof
of canonical payload, envelope, local-console, governance, consumption, and
audit records; authenticated-envelope parsing with fixed public-key fixtures,
precomputed detached signatures, invalid/tampered fixtures, and injected
authority-root records; exact external public-input validation; durable
state/journal semantics; isolated-root publication; generation/rotation/recovery;
replay/expiry and frozen resume; terminal Observation and Verification; and
secret-exclusion boundaries. Fixtures may not contain private keys in the
repository, and fixture verification cannot prove the live OS/image authority
baseline. The Build may not create production keys, create test private keys,
sign artifacts, implement the live Owner authority source, install real host
objects, mutate `/etc` or `/usr`, implement live root/systemd helpers, deploy
OAS, or prove production trust custody or truthful Owner deployment authority
without later authorization and evidence.

## 18. Verification Boundary

The static lock verifies the structured design, exact status, selected
bootstrap-authority root model, exact OS/image trust-source origin, key lifecycle,
selected pre-instance model, and model selection,
five-object coverage, authenticated payload/envelope separation, role
separation, non-recursive verifier bootstrap, expiry/resume rules, retained
prior-generation recovery, cross-directory publication, journal chaining,
state/audit/filesystem distinction, release-versus-Owner trust separation,
private-key exclusion, candidate self-authorization prohibition, lifecycle
coverage, release chain, negative implementation boundary, and exact repository
scope. It does not execute a bootstrap ceremony, read host trust objects, access
private keys, create test keys, invoke a verifier, mutate a target host, or
establish deployment verification.

`VERIFICATION_STATUS: TEST_VERIFIED` means only that the named repository
static lock passed for this design record. It is not production trust proof,
host trust-bootstrap proof, Owner authority proof, or deployment verification.

The finalized repository scope is exactly these five paths:

```text
PROGRESS.md
docs/architecture/SECURITY_ARCHITECTURE.md
tests/test_security_architecture_canonization.py
docs/architecture/MILESTONE_126A_OAS_PRODUCTION_TRUST_MATERIAL_AND_HOST_TRUST_BOOTSTRAP_AUTHORITY_CONTRACT_PROOF.md
tests/test_milestone_126a_oas_production_trust_material_and_host_trust_bootstrap_authority_contract_proof.py
```

The external finalization summary is evidence only and is outside repository
scope.

## 19. Authoritative Status

```text
AUTHORITATIVE_M126A_STATUS_BEGIN
M126A_AUTHORIZED: YES
M126A_STARTED: YES
M126A_FINALIZED: YES
M126A_TYPE: DESIGN_DISCOVERY_SECURITY_AND_OPERATIONS_CONTRACT_PROOF
DECISION_STATUS: CURRENT
DESIGN_STATUS: DESIGN_PROVEN
IMPLEMENTATION_STATUS: NOT_IMPLEMENTED
VERIFICATION_STATUS: TEST_VERIFIED
DEPLOYMENT_VERIFIED: NO
DEPLOYMENT_STATE: NOT_DEPLOYED
DEPLOYMENT_PROFILE: FIRST_INSTALL_LOCAL_AF_UNIX_ONLY
TRUST_MATERIAL_CONTRACT_PROVEN: YES
TRUST_BOOTSTRAP_AUTHORITY_MODEL_SELECTED: YES
BOOTSTRAP_AUTHORITY_ROOT_MODEL: BOOTSTRAP_AUTHORITY_ROOT_MODEL_A_OS_IMAGE_PROVISIONING_BASELINE
PRE_INSTANCE_MODEL: PRE_INSTANCE_MODEL_B_HOST_RELEASE_TRUST_BEFORE_EXPLICIT_INSTANCE_BINDING
PRODUCTION_TRUST_MATERIAL_PROVEN: NO
PRIVATE_KEYS_CREATED: NO
PRIVATE_KEYS_ACCESSED: NO
HOST_TRUST_OBJECTS_INSTALLED: NO
TRUST_BOOTSTRAP_IMPLEMENTED: NO
TRUTHFUL_OWNER_DEPLOYMENT_AUTHORITY_PROVEN: NO
LIVE_DEPLOYMENT_AUTHORIZED: NO
LIVE_ROLLBACK_AUTHORIZED: NO
TARGET_HOST_MUTATION_PERFORMED: NO
BUILD_READINESS: BOUNDED_TRUST_BOOTSTRAP_BUILD_JUSTIFIED_FOR_PM_REVIEW
SELECTED_EXIT: EXIT_A_BOUNDED_TRUST_BOOTSTRAP_BUILD_JUSTIFIED_FOR_PM_REVIEW
PROGRESS_UPDATED: YES
COMMIT_CREATED: YES
TAG_CREATED: YES
PUSH_PERFORMED: YES
SUCCESSOR_AUTHORIZED: NO
SUCCESSOR_NUMBER_ASSIGNED: NO
READY_FOR_PM_REVIEW: NO
AUTHORITATIVE_M126A_STATUS_END
```

`EXIT_A_BOUNDED_TRUST_BOOTSTRAP_BUILD_JUSTIFIED_FOR_PM_REVIEW` records the
finalized recommendation for a separately authorized PM hard-gate review. It does
not authorize a Build, create production trust material, install any object,
mutate the target host, deploy OAS, authorize truthful Owner deployment,
authorize live rollback, or assign a successor milestone. This record does not
assign a successor milestone.
