# PiSense_Backend





### UV

#### Install UV

https://docs.astral.sh/uv/getting-started/installation/

For Linux - curl -LsSf https://astral.sh/uv/install.sh | sh


#### Add new dependency

`uv add requests`

This will resolve the new dependency and add it to our list of dependencies in `pyproject.toml`

#### Developing

git clone the repo and install uv

navigate to the project folder and run `uv sync`

In linux `source .venv/bin/activate` to enter the local environment.

This should give you access to all of the libraries that `PiSense_Backend` uses ( mostly for autocomplete context )

#### Pushing new code and updating project

Update version number in `pyproject.toml`

`uv lock` to update lock file

