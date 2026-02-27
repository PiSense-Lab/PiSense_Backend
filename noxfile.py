import nox

@nox.session(python=["3.12"])
def tests(session):
    """Runs tests with pytest."""
    session.install("pytest") # Installs pytest and dependencies for testing FastAPI
    session.install(".")
    session.run("pytest", "tests") # Runs tests in tests folder ( files must be named `test_*` )

@nox.session
def lint(session):
    """Lints the code with ruff."""
    session.install("ruff")
    session.run("ruff", "check", "--fix") # Runs linter on python code in `pisense/*`
