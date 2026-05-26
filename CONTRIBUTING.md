# Contributing

Thank you for your interest in improving AI Code Explainer & Debugger.

## How to contribute

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Make your changes.
4. Run the backend lint/test commands.
5. Submit a pull request with a clear description.

## Development workflow

- Use `make setup` to create the virtual environment.
- Use `make install-backend` to install Python dependencies.
- Use `make check` to validate backend Python syntax.

## Code quality

- Keep functions small, focused, and readable.
- Add type hints when possible.
- Document public functions with clear docstrings.
- Use descriptive variable and function names.

## Testing

- Run tests with `python -m unittest discover backend/tests`.
- Add regression coverage for any bug fixes or new features.

## Reporting issues

- Open an issue for bugs, feature requests, or documentation improvements.
- Provide steps to reproduce and relevant environment details.
