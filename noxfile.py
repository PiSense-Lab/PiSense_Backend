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

@nox.session(default=False) # When running `uv run nox` this test will not run, need to run `nox -s e2e`
def e2e(session):
    """Runs e2e testing with a database to connect to"""
    session.install("pytest") # Installs pytest and dependencies for testing FastAPI
    session.install(".")
    session.run("pytest", "e2e")
