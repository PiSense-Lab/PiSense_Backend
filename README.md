# PiSense_Backend

Backend for PiSense written using python and FastApi 



### UV

#### Install UV

https://docs.astral.sh/uv/getting-started/installation/

For Linux - curl -LsSf https://astral.sh/uv/install.sh | sh


#### Add new dependency to project

`uv add requests`

This will resolve the new dependency and add it to our list of dependencies in `pyproject.toml`. You will need to run `uv lock` afterwards to update the lock file. ( We will later setup a pipeline to yell at you when you forget )

#### Developing ( Assuming you are using vscode with WSL )

git clone the repo and install uv

navigate to the project folder and run `uv sync`. This will create a python virtual environment and install all of the packages from the lock file.

In linux ( wsl ) `source .venv/bin/activate` to enter the local environment. ( If you setup a vscode workspace this can be done automatically ) This will give you access to all of the libraries that `PiSense_Backend` uses ( mostly for autocomplete context )

#### Pushing new code and updating project

Update version number in `pyproject.toml` ( Do we want to enforce versioning semantics )

`uv lock` to update lock file ( This will be eventually required by the pipeline )


### Configuration

All of our code is within our `pisense` within its respective folder. There are a bunch of `__init__.py` files in all of the folder, those are for `pytest` to properly import stuff, they can be ignored. There are two main parts of this project, the `backend` which contains most of the logic and the `api` part which contains the network paths for external users to access. The `api` part should contain only api related logic, all logic should be contained in the `backend` and imported to the `api`, this keeps all of our logic generic and reusable and not linked directly to a api call which may change.

### Testing

We are using `nox` to setup and run all of our python testing. `Nox` just setups up the tests so we are using `pytest` for a majority of our unit and e2e tests. `Nox` is configured in `noxfile.py` and contains a bunch of different `sessions` which each contain some testing. There is also a linter installed ( which exactly is up for debate ) which will enforce stricter typing and code styling. Its a pain but will be nice in the long run. 

You can run the tests locally using `uv run nox` which will run all of the tests, for a specific test you can add the `-s` flag and which session you are running.


### Starting fastapi

`uv run fastapi run pisense/api/main.py` 

If you are in the proper environment then you can just run `fastapi run pisense/api/main.py`

This will run an api at http://0.0.0.0:8000

Navigating to http://0.0.0.0:8000/docs will give you access to the docs page which is very useful for development and testing

sudo apt-get install python3-dev
