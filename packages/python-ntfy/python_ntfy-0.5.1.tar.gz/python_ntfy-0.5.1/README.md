# A Python Library For ntfy

![GitHub Release](https://img.shields.io/github/v/release/MatthewCane/python-ntfy?display_name=release&label=latest%20release&link=https%3A%2F%2Fgithub.com%2FMatthewCane%2Fpython-ntfy%2Freleases%2Flatest)
![PyPI - Downloads](https://img.shields.io/pypi/dm/python-ntfy?logo=pypi&link=http%3A%2F%2Fpypi.org%2Fproject%2Fpython-ntfy%2F)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/MatthewCane/python-ntfy/publish.yml?logo=githubactions&link=https%3A%2F%2Fgithub.com%2FMatthewCane%2Fpython-ntfy%2Factions%2Fworkflows%2Fpublish.yml)

An easy-to-use python library for the [ntfy notification service](https://ntfy.sh/). Aiming for full feature support and a super easy to use interface.

## Quickstart

1. Install using pip with `pip3 install python-ntfy`
2. Configure the following environment variables:
    - `NTFY_USER`: The username for your server (if required)
    - `NTFY_PASSWORD`: The password for your server (if required)
    - `NTFY_SERVER`: The server URL (defaults to `https://ntft.sh`)
3. Setup your application to use the library:

```python
# Import the ntfy client
from python_ntfy import NtfyClient

# Create an `NtfyClient` instance with a topic
client = NtfyClient(topic="Your topic")

# Send a message
client.send("Your message here")
```

## Documentation

See the full documentation at [https://matthewcane.github.io/python-ntfy/](https://matthewcane.github.io/python-ntfy/).

## Supported Features

- Username + password auth
- Access token auth
- Custom servers
- Sending plaintext messages
- Sending Markdown formatted text messages
- Scheduling messages
- Retrieving cached messages
- Scheduled delivery
- Tags
- Action buttons

## Future Features

- [Email notifications](https://docs.ntfy.sh/publish/#e-mail-notifications)
- Send to multiple topics at once

## Testing and Development

This project uses:

- [Poetry](https://python-poetry.org/) as it's dependency manager
- [Ruff](https://docs.astral.sh/ruff/) for linting and code formatting
- [MyPy](https://mypy-lang.org/) for static type checking
- [Pre-Commit](https://pre-commit.com/) for running the above tools before committing

To install dev dependencies, run `poetry install --with dev`.

To install pre-commit hooks, run `pre-commit install`.

### Linting, Formatting and Type Checking

These can be run with:

- `poetry run ruff format`
- `poetry run ruff check`
- `poetry run mypy .`

These tools are also run in the CI pipeline and must pass before merging.

### Tests

This project is aiming for 95% code coverage. Any added features must include comprehensive tests.

#### Testing Steps

1. Make sure you have `docker` and `docker-compose` installed
2. Run the tests with `poetry run pytest --cov` or use the VSCode testing extension
