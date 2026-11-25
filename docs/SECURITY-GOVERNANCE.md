# Security, privacy and governance baseline

## Access
- Apply least privilege and role-based access control.
- Require strong authentication for administrators and sensitive workflows.
- Keep production secrets in a secrets manager; never commit them to Git.
- Record privileged actions in tamper-evident audit logs.

## Human approval required
- Withdrawals, bank-account changes, payment-provider changes and large refunds.
- Pricing, commission, reward conversion or payout-policy changes.
- Adding or removing administrators and changing access roles.
- Ownership, succession, legal declarations and destructive data operations.

## Privacy and identity
- Collect only data needed for a stated purpose.
- Provide clear notices, consent and retention/deletion workflows.
- Do not store passwords or biometric templates in browser localStorage.
- Face matching alone must never reset an account password; use secure recovery and an independent verification factor.
- Do not upload identity documents, private customer data or biometric information to public source control.

## Money and rewards
- Do not promise cash value for points until the reward pool is funded and legal/provider requirements are met.
- Verify tasks and surveys server-side before crediting rewards.
- Complete KYC/AML, tax, FX, payment-provider and country-law reviews before enabling withdrawals.
- Do not pay earlier participants from later participants' deposits or use recruitment-only cash commissions.

## Advertising and content
- Review advertisements against the laws and platform rules of each target country.
- Hold uncertain or high-risk content for human/legal review before publication.
- Keep evidence of advertiser approval and moderation decisions.

## Incident response
- Revoke compromised tokens, rotate affected secrets, preserve audit evidence and notify affected parties where legally required.
- Test backups and account recovery before production launch.
