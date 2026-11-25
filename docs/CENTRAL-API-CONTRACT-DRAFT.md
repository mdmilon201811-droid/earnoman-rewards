# Central integration API contract — draft

This is a design contract only; it is not a live API.

## Principles
- Each product remains a separate application with its own user store and financial ledger.
- Central Command receives only the minimum operational summaries needed for monitoring.
- Authenticate service-to-service requests with short-lived credentials and scoped permissions.
- Sign requests, validate timestamps/nonces, rate-limit endpoints and reject replayed requests.
- Every command must include an actor, target product, requested action, reason, risk classification and correlation ID.

## Draft endpoints
- GET /v1/health — service health summary.
- GET /v1/metrics/summary — approved aggregate metrics only.
- POST /v1/commands/preview — validate and preview; never execute.
- POST /v1/approvals — create a human approval request.
- POST /v1/audit-events — append an audit event.

## Execution policy
No money movement, bank changes, role changes, ownership changes, legal declarations or destructive operations may execute from a preview. These require explicit human approval and server-side authorization. The central system must not bypass a product's own controls.

## Data boundaries
Do not send passwords, authentication tokens, full payment details, identity documents or biometric templates to the central dashboard. Prefer aggregate counts and pseudonymous references.
