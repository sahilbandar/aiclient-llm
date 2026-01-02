# Contributing to aiclient-llm

First off, thanks for taking the time to contribute! 🎉

We welcome contributions from everyone. Whether it's a bug fix, new feature, documentation improvement, or just spotting a typo.

## How to Contribute

### 1. Fork the Repository
Click the "Fork" button on the top right of the GitHub repository page.

### 2. Clone Your Fork
```bash
git clone https://github.com/YOUR_USERNAME/aiclient.git
cd aiclient
```

### 3. Set Up Development Environment
We use `pip` and `venv` (standard Python tools).

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"
```

### 4. Create a Branch
```bash
git checkout -b feature/my-amazing-feature
```

### 5. Make Changes & Test
Implement your changes. Ensure you add tests for any new functionality.

Run the test suite:
```bash
pytest
```

Run linting:
```bash
ruff check .
mypy .
```

### 6. Commit and Push
```bash
git commit -m "feat: Add support for X feature"
git push origin feature/my-amazing-feature
```

### 7. Open a Pull Request
Go to the original repository and open a Pull Request from your fork.

## Code Style
- Follow PEP 8.
- Use `ruff` for formatting and linting.
- Use type hints (`mypy` strict mode is enabled).

## Reporting Issues
If you find a bug, please search existing issues first. If it's new, open an issue with:
- A clear title
- Description of the bug
- Minimal reproduction code
- Expected vs actual behavior

## License
By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.
