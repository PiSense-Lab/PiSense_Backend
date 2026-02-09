import nox

@nox.session(python=["3.12"])
def tests(session):
    """Runs tests with pytest."""
    session.install("pytest")
    session.run("pytest", "tests") # Runs tests 

@nox.session
def lint(session):
    """Lints the code with flake8."""
    session.install("flake8")
    session.run("flake8", "backend", '-v') # Runs linter on backend
