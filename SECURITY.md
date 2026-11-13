# Security policy

## Report a vulnerability

Email info@cognitiveinfralabs.com with the repository name, affected commit or release, impact, and minimal reproduction steps. Use synthetic inputs and redact credentials, personal data, and provider responses. Keep the report private while a fix is investigated.

Security reports are evaluated against the current default branch. Include the version if the behavior occurs in an older checkout.

## Deployment scope

Use synthetic inputs. Require authentication and restrict origins before sharing the service.

GitHub Actions runs Bandit against the application source and fails on findings rated high severity with medium or high confidence.
