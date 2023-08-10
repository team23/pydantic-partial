install-pre-commit:
    #!/usr/bin/env bash
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

ruff *args: (poetry "run" "ruff" "pydantic_partial" "tests" args)

mypy *args:  (poetry "run" "mypy" "pydantic_partial" args)

lint: ruff mypy

publish: (poetry "publish" "--build")
