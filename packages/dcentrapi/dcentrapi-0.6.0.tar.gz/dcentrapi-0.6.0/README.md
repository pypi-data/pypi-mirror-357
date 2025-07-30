# DAPI

## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Use this [link](https://app.clickup.com/3857237/v/dc/3npun-28475/3npun-46355) in order to set up the repository.

## Development Setup

### Install Dependencies

```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync

# Install with testing dependencies
uv sync --extra test
```

## Testing

The project includes comprehensive tests located in the `tests/` directory. For detailed testing instructions, see [tests/README_TESTING.md](tests/README_TESTING.md).

### Quick Test Commands

```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=dcentrapi --cov-report=html --cov-report=term

# Run specific test categories
uv run pytest tests/ -m unit          # Unit tests only
uv run pytest tests/ -m integration   # Integration tests only
uv run pytest tests/ -m ethereum      # Ethereum tests only
```

## Test and Deploy

- Make your changes on staging branch.
- Change the package version in Base.py and setup.py. If you added a new file make sure to add it to __init__.py file.
- Install the test package using your virtual environment. run ```pip install --index-url https://test.pypi.org/simple/ dcentrapi==<the version you deployed> ```
- Create a local test.py file (do not add to git), import your changes and test them.

- Once you finished testing, add the changes to main side branch and create a merge request.
