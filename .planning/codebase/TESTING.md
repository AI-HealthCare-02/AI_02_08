# Testing Strategy

## Backend
- **Framework**: `pytest` with `pytest-asyncio`.
- **Target**: High coverage for `services` and `apis`.
- **Naming**: Files should be prefixed with `test_`.
- **Critical Tests**:
  - `test_signup_api.py`
  - `test_login_api.py`
  - `test_token_api.py`
  - *Note: These files must not be modified as they are core to verification.*

## Frontend
- **Framework**: (To be determined - Vite/Vitest is likely).
- **Target**: Critical user flows and UI component rendering.

## CI/CD
- **Linting**: Automated checks for Ruff (Python) and ESLint (JS) on Pull Requests.
- **Tests**: Automated test runs on major branches.
