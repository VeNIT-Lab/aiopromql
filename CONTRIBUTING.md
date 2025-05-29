# Contributing

We love your input! We want to make contributing to aiopromql as easy and transparent as possible, whether it's:

* Reporting a bug
* Discussing the current state of the code
* Submitting a fix
* Proposing new features
* Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Development Setup

1. Install development dependencies:

   ```bash
   pip install -e .[dev]
   ```

2. Run tests:

   ```bash
   make unit-test
   # run instegration tests via docker-compose
   make docker-integration-test 

   # or manually run it by specifying a PROMETHEUS_URL 
   export PROMETHEUS_URL=http://10.42.0.1:30090
   make integration-test
   ```

3. Format and lint code:

   ```bash
   make format
   make lint
   ```

4. Build documentation:

   ```bash
   make docs
   ```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Report Bugs

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/VeNIT-Lab/aiopromql/issues/new); it's that easy!

### Writing Bug Reports

**Great Bug Reports** tend to have:

* A quick summary and/or background
* Steps to reproduce
  * Be specific!
  * Give sample code if you can.
* What you expected would happen
* What actually happens
* Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Code Style

* Follow PEP 8 guidelines
* Use type hints
* Write docstrings for all public functions and classes
* Keep functions focused and small
* Write tests for new functionality

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the documentation if you've changed APIs
3. The PR will be merged once you have the sign-off of at least one maintainer
4. Make sure all tests pass and there are no linting errors

## Questions?

Feel free to open an issue for any questions you might have about contributing. 