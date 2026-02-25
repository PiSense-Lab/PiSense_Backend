import nox

@nox.session(python=["3.12"])
def tests(session):
    """Runs tests with pytest."""
    session.install("pytest", "pandas", "openpyxl", "mariadb", "sqlalchemy")
    session.run("pytest", "tests") # Runs tests in tests folder ( files must be named `test_*` )

@nox.session
def lint(session):
    """Lints the code with flake8."""
    session.install("flake8")
    session.run("flake8", "pisense") # Runs linter on python code in `pisense/*`
