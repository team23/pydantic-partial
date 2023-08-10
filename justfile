install-pre-commit:
    #!/bin/bash
    if ( which pre-commit > /dev/null 2>&1 )
    then
        pre-commit install --install-hooks
    else
        b5:warn "-----------------------------------------------------------------"
        b5:warn "pre-commit is not installed - cannot enable pre-commit hooks!"
        b5:warn "Recommendation: Install pre-commit ('brew install pre-commit')."
        b5:warn "-----------------------------------------------------------------"
    fi

install: install-pre-commit (poetry "install")

update: (poetry "install")

poetry *args:
    poetry {{args}}

test *args: (poetry "run" "pytest" "--cov=pydantic_partial" "--cov-report" "term-missing:skip-covered" args)

test-all: (poetry "run" "tox")

isort: (poetry "run" "isort" "pydantic_partial" "tests")

flake8: (poetry "run" "flake8" "pydantic_partial" "tests")

mypy:  (poetry "run" "mypy" "pydantic_partial")

lint: flake8 mypy

publish: (poetry "publish" "--build")
