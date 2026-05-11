## Testing & style

Follow [CONTRIBUTING.md § Test conventions](./CONTRIBUTING.md#test-conventions)
for new tests (pytest, no classes, pytest-mock, fixtures, parametrize).

Pre-commit hooks are mandatory. See
[CONTRIBUTING.md § Code Style](./CONTRIBUTING.md#code-style) for setup.
The hooks (`black`, `check-json`, `check-yaml`, `shellcheck`) are configured in
`.pre-commit-config.yaml`.
