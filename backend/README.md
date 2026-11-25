# EarnWorld Rewards — authentication backend starter

This folder contains an initial API implementation for email/password registration, login and the authenticated account profile.

## Run locally

1. Create a virtual environment and install `backend/requirements.txt`.
2. Copy `.env.example` to `.env` and set a unique secret. Never commit real secrets.
3. From this folder, run `uvicorn app.main:app --reload`.
4. Open `/docs` for the API test interface.

Endpoints: `POST /auth/register`, `POST /auth/login`, `GET /auth/me`, `GET /health`.

## Important limitations

This is an incomplete development foundation, not a public production login service. Before launch, configure managed PostgreSQL and HTTPS; add email verification, secure password reset, login throttling/abuse protection, refresh-token rotation or secure cookie sessions, CSRF protections where applicable, backups, monitoring, security review, privacy/retention controls and country-specific legal review. Add an approved hosting environment and secret manager. Do not use real customer accounts until those controls are complete. Access tokens are short-lived bearer tokens; do not store them in localStorage for a production browser app.
