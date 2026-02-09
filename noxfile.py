import nox

# @nox.session(python=["3.11", "3.12"])
# def tests(session):
#     """Runs tests with pytest."""
#     session.install("pytest")
#     session.run("pytest")

@nox.session
def lint(session):
    """Lints the code with flake8."""
    session.install("flake8")
    session.run("flake8", "backend") # Runs linter on backend
