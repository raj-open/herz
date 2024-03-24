# set shell := [ "bash", "-c" ]
_default:
    @- just --unsorted --list
menu:
    @- just --unsorted --choose

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Justfile
# Recipes for various workflows.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

set dotenv-load := true

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# VARIABLES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

REPO_NAME := "herz"
PROJECT_NAME := "herz"

PATH_ROOT := justfile_directory()
CURRENT_DIR := invocation_directory()
OS := if os_family() == "windows" { "windows" } else { "linux" }
PYTHON := if os_family() == "windows" { "${PYTHON_PATH:-py -3.11}" } else { "${PYTHON_PATH:-python3.11}" }
PYVENV := if os_family() == "windows" { "${PYTHON_PATH_VENV:-python}" } else { "${PYTHON_PATH_VENV:-python3}" }
LINTING := "black"
GITHOOK_PRECOMMIT := "pre_commit"
GEN_MODELS := "datamodel_code_generator"
GEN_APIS := "openapi-generator"
TOOL_TEST_BDD := "behave"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Macros
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

_create-file-if-not-exists fname:
    #!/usr/bin/env bash
    touch "{{fname}}";
    exit 0;

_create-folder-if-not-exists path:
    #!/usr/bin/env bash
    if ! [[ -d "{{path}}" ]]; then
        mkdir -p "{{path}}";
    fi
    exit 0;

_create-temp-folder path="." name="tmp":
    #!/usr/bin/env bash
    k=-1;
    tmp_folder="{{path}}/{{name}}";
    while [[ -d "${tmp_folder}" ]] || [[ -f "${tmp_folder}" ]]; do
        k=$(( $k + 1 ));
        tmp_folder="{{path}}/{{name}}_${k}";
    done
    mkdir "${tmp_folder}";
    echo "${tmp_folder}";
    exit 0;

_delete-if-file-exists fname:
    #!/usr/bin/env bash
    if [[ -f "{{fname}}" ]]; then
        rm "{{fname}}";
    fi
    exit 0;

_delete-if-folder-exists path:
    #!/usr/bin/env bash
    if [[ -d "{{path}}" ]]; then
        rm -rf "{{path}}";
    fi
    exit 0;

_clean-all-files path pattern:
    #!/usr/bin/env bash
    find {{path}} -type f -name "{{pattern}}" -exec basename {} \; 2> /dev/null
    find {{path}} -type f -name "{{pattern}}" -exec rm {} \; 2> /dev/null
    exit 0;

_clean-all-folders path pattern:
    #!/usr/bin/env bash
    find {{path}} -type d -name "{{pattern}}" -exec basename {} \; 2> /dev/null
    find {{path}} -type d -name "{{pattern}}" -exec rm -rf {} \; 2> /dev/null
    exit 0;

_check-python-tool tool name:
    @just _check-tool "{{PYVENV}} -m {{tool}}" "{{name}}"

_check-python-bin tool name:
    @just _check-tool "{{tool}}" "{{name}}"

_check-tool tool name:
    #!/usr/bin/env bash
    success=false
    ${ACTIVATE_VENV:-echo "venv:off"} && {{tool}} --version >> /dev/null 2> /dev/null && success=true;
    ${ACTIVATE_VENV:-echo "venv:off"} && {{tool}} --help >> /dev/null 2> /dev/null && success=true;
    # NOTE: if exitcode is 251 (= help or print version), then render success.
    if [[ "$?" == "251" ]]; then success=true; fi
    # FAIL tool not installed
    if ( $success ); then
        echo -e "Tool \x1b[2;3m{{name}}\x1b[0m installed correctly.";
        exit 0;
    else
        echo -e "Tool \x1b[2;3m{{name}}\x1b[0m did not work." >> /dev/stderr;
        echo -e "Ensure that \x1b[2;3m{{name}}\x1b[0m (-> \x1b[1mjust build\x1b[0m) installed correctly and system paths are set." >> /dev/stderr;
        exit 1;
    fi

_generate-documentation path_schema target_path name:
    @${ACTIVATE_VENV:-echo "venv:off"} && {{GEN_APIS}} generate \
        --skip-validate-spec \
        --input-spec {{path_schema}}/schema-{{name}}.yaml \
        --generator-name markdown \
        --output "{{target_path}}/{{name}}"

_generate-documentation-recursively path_schema target_path:
    #!/usr/bin/env bash
    # skip if no files exist
    ls -f {{path_schema}}/schema-*.yaml >> /dev/null 2> /dev/null || exit 0;
    # otherwise proceed
    while read path; do
        if [[ "${path}" == "" ]]; then continue; fi
        path="${path##*/}";
        name="$( echo """${path}""" | sed -E """s/^schema-(.*)\.yaml$/\1/g""")";
        echo "- generate documentation for ${name}."
        just _generate-documentation "{{path_schema}}" "{{target_path}}" "${name}";
    done <<< "$( ls -f {{path_schema}}/schema-*.yaml )";
    exit 0;

_generate-models path_schema target_path name:
    @${ACTIVATE_VENV:-echo "venv:off"} && {{PYVENV}} -m {{GEN_MODELS}} \
        --input-file-type openapi \
        --output-model-type pydantic_v2.BaseModel \
        --encoding "UTF-8" \
        --disable-timestamp \
        --use-schema-description \
        --field-constraints \
        --capitalise-enum-members \
        --enum-field-as-literal one \
        --set-default-enum-member \
        --use-subclass-enum \
        --allow-population-by-field-name \
        --snake-case-field \
        --strict-nullable \
        --target-python-version 3.11 \
        --input {{path_schema}}/schema-{{name}}.yaml \
        --output {{target_path}}/{{name}}.py

_generate-models-recursively path_schema target_path:
    #!/usr/bin/env bash
    # skip if no files exist
    ls -f {{path_schema}}/schema-*.yaml >> /dev/null 2> /dev/null || exit 0;
    # otherwise proceed
    while read path; do
        if [[ "${path}" == "" ]]; then continue; fi
        path="${path##*/}";
        name="$( echo """${path}""" | sed -E """s/^schema-(.*)\.yaml$/\1/g""")";
        echo "- generate models for ${name}."
        just _generate-models "{{path_schema}}" "{{target_path}}" "${name}";
    done <<< "$( ls -f {{path_schema}}/schema-*.yaml )";
    exit 0;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: build
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

setup:
    @echo "TASK: SETUP"
    @mkdir -p setup
    @- cp -n "templates/template.env" ".env"
    @- cp -n "templates/template-config.yaml" "setup/config.yaml"

build:
    @echo "TASK: BUILD"
    @just build-venv
    @just build-requirements
    @just check-system-requirements
    @just build-models
    @just build-githook-pc

build-skip-requirements:
    @echo "TASK: BUILD (skip installing requirements)"
    @just build-venv
    @just check-system-requirements
    @just build-models
    @just build-githook-pc

build-venv:
    @- {{PYTHON}} -m venv .venv

# cf. https://pre-commit.com
build-githook-pc:
    #!/usr/bin/env bash
    echo "SUBTASK: build githook"
    if [[ -d ".git" ]]; then
        git config --unset-all core.hooksPath
        ${ACTIVATE_VENV:-echo "venv:off"} && {{PYVENV}} -m pre_commit install
    fi
    exit 0;

build-requirements:
    @echo "SUBTASK: build requirements"
    @just build-requirements-basics
    @just build-requirements-dependencies

build-requirements-basics:
    @${ACTIVATE_VENV:-echo "venv:off"} && {{PYVENV}} -m pip install --upgrade pip
    @${ACTIVATE_VENV:-echo "venv:off"} && {{PYVENV}} -m pip install --upgrade certifi wheel toml poetry

build-requirements-dependencies:
    @${ACTIVATE_VENV:-echo "venv:off"} && {{PYVENV}} -m poetry lock --no-update
    @${ACTIVATE_VENV:-echo "venv:off"} && {{PYVENV}} -m poetry install --no-interaction --no-root

build-models:
    @echo "SUBTASK: build data models from schemata."
    @just _delete-if-folder-exists "src/models/generated"
    @just _create-folder-if-not-exists "src/models/generated"
    @just _create-file-if-not-exists "src/models/generated/__init__.py"
    @just _generate-models-recursively "models" "src/models/generated"

build-docs:
    @echo "SUBTASK: build documentation for data models from schemata."
    @just _delete-if-folder-exists "docs/models"
    @just _create-folder-if-not-exists "docs/models"
    @- just _generate-documentation-recursively "models" "docs/models"
    @- just _clean-all-files "." ".openapi-generator*"
    @- just _clean-all-folders "." ".openapi-generator*"

build-archive branch="main":
    @echo "SUBTASK: build artefact"
    @echo "Create zip archive of project"
    @mkdir -p dist
    @git archive -o dist/{{PROJECT_NAME}}-$(cat dist/VERSION).zip "{{branch}}"

# process for release
dist branch="main":
    @echo "TASK: create release"
    @just clean
    @just setup
    @just build
    @just build-docs
    @just build-archive "{{branch}}"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: execution
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

run *args:
    @${ACTIVATE_VENV:-echo "venv:off"} \
    && {{PYVENV}} -m src.cli {{args}}

run-cli mode="requests" requests="setup/requests.yaml" env_path=".env" log_path="logs" session_path=".session":
    @just _reset-logs "{{log_path}}"
    @${ACTIVATE_VENV:-echo "venv:off"} \
    && {{PYTHON}} -m src.cli \
        "{{mode}}" \
        --requests "{{requests}}" \
        --env "{{env_path}}" \
        --log "{{log_path}}" \
        --session "{{session_path}}"

run-cli-debug mode="requests" requests="setup/requests.yaml" env_path=".env" log_path="logs" session_path=".session":
    @just _reset-logs "{{log_path}}"
    @${ACTIVATE_VENV:-echo "venv:off"} \
    && {{PYTHON}} -m src.cli \
        "{{mode}}" \
        --debug \
        --requests "{{requests}}" \
        --env "{{env_path}}" \
        --log "{{log_path}}" \
        --session "{{session_path}}"

run-api env_path=".env" log_path="logs" session_path=".session" IP="${HTTP_IP:-localhost}" PORT="${HTTP_PORT:-8000}":
    @just _reset-logs "{{log_path}}"
    @# kill anything running on port
    @just kill-port "{{PORT}}"
    @echo "START API"
    @${ACTIVATE_VENV:-echo "venv:off"} \
    && {{PYVENV}} -m src.api \
        --env "{{env_path}}" \
        --log "{{log_path}}" \
        --session "{{session_path}}"

run-api-debug env_path=".env" log_path="logs" session_path=".session" IP="${HTTP_IP:-localhost}" PORT="${HTTP_PORT:-8000}":
    @just _reset-logs "{{log_path}}"
    @# kill anything running on port
    @just kill-port "{{PORT}}"
    @echo "START API"
    @${ACTIVATE_VENV:-echo "venv:off"} \
    && {{PYVENV}} -m src.api \
        --debug \
        --env "{{env_path}}" \
        --log "{{log_path}}" \
        --session "{{session_path}}"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: development
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Recipe only works if local file test.py exists
dev *args:
    @just _reset-logs
    @${ACTIVATE_VENV:-echo "venv:off"} \
    && {{PYVENV}} test.py {{args}}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: terminate execution
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# finds pid based on port
get-pid PORT:
    @- lsof -ti ":{{PORT}}" 2> /dev/null

# kills process based on process ID
kill-pid PID:
    @echo "Killing {{PID}}"
    @kill {{PID}} 2> /dev/null

kill-port PORT="${HTTP_PORT:-8000}":
    #!/usr/bin/env bash
    PID="$( just get-pid "{{PORT}}" )";
    if [[ "${PID}" == "" ]]; then
        echo "No process running on PORT {{PORT}}";
    else
        echo "Process ${PID} running on PORT {{PORT}}";
        just kill-pid "${PID}";
    fi
    exit 0;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: tests
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

tests:
    @just tests-unit
    @just tests-behave
    @just tests-integration

tests-logs log_path="logs":
    @just _reset-logs "{{log_path}}"
    @- just tests
    @just _display-logs "{{log_path}}"

tests-unit:
    @just test-unit "tests/unit"

test-unit path:
    @just _reset-test-logs "unit"
    @${ACTIVATE_VENV:-echo "venv:off"} && {{PYVENV}} -m pytest "{{path}}" \
        --cov-reset \
        --cov=.

tests-behave:
    @just test-behave "tests/behave"

test-behave path:
    @just _reset-test-logs "behave"
    @${ACTIVATE_VENV:-echo "venv:off"} \
    && {{PYVENV}} -m {{TOOL_TEST_BDD}} \
        --define http-user="${HTTP_USER}" \
        --define http-password="${HTTP_PASSWORD}" \
        --color \
        --show-timings \
        --no-capture \
        --no-logcapture \
        --tags ~@skip \
        --tags ~@TODO \
        --multiline \
        --summary \
        --stop \
        "{{path}}"

tests-integration:
    @just test-integration "."

test-integration path:
    @echo "Integration tests not yet implemented"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: qa
# NOTE: use for development only.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

qa:
    @${ACTIVATE_VENV:-echo "venv:off"} && {{PYVENV}} -m coverage report -m

coverage source_path tests_path log_path="logs":
    @just _reset-logs "{{log_path}}"
    @${ACTIVATE_VENV:-echo "venv:off"} && {{PYVENV}} -m pytest {{tests_path}} \
        --ignore=tests/integration \
        --cov-reset \
        --cov={{source_path}} \
        --capture=tee-sys \
        2> /dev/null
    @just _display-logs

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: prettify
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

lint path:
    @${ACTIVATE_VENV:-echo "venv:off"} && {{PYVENV}} -m {{LINTING}} --verbose "{{path}}"

lint-check path:
    @${ACTIVATE_VENV:-echo "venv:off"} && {{PYVENV}} -m {{LINTING}} --check --verbose "{{path}}"

prettify:
    @${ACTIVATE_VENV:-echo "venv:off"} && {{PYVENV}} -m {{LINTING}} --verbose src/*
    @${ACTIVATE_VENV:-echo "venv:off"} && {{PYVENV}} -m {{LINTING}} --verbose tests/*
    @${ACTIVATE_VENV:-echo "venv:off"} && {{PYVENV}} -m {{LINTING}} --verbose notebooks/*

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGES: utilities
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

create-badge-pyversion:
    @${ACTIVATE_VENV:-echo "venv:off"} \
    && {{PYVENV}} -m pybadges \
        --left-text="python" \
        --right-text="3.10, 3.11, 3.12" \
        --whole-link="https://www.python.org/" \
        --browser \
        --logo='https://dev.w3.org/SVG/tools/svgweb/samples/svg-files/python.svg' \
        >> docs/badges/pyversion.svg

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: clean
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



clean log_path="logs" session_path=".session":
    @- just clean-basic "{{log_path}}" "{{session_path}}"
    @- just clean-notebooks
    @- just clean-venv

clean-basic log_path="logs" session_path=".session":
    @echo "All system artefacts will be force removed."
    @- just _clean-all-files "." ".DS_Store" 2> /dev/null
    @echo "All test artefacts will be force removed."
    @- just _delete-if-folder-exists ".pytest_cache" 2> /dev/null
    @- just _delete-if-file-exists ".coverage" 2> /dev/null
    @- just _delete-if-folder-exists "tests/behave/.session" 2> /dev/null
    @- just _delete-if-folder-exists "tests/behave/logs" 2> /dev/null
    @echo "All execution artefacts will be force removed."
    @- just _delete-if-folder-exists "{{log_path}}" 2> /dev/null
    @- just _delete-if-folder-exists "{{session_path}}" 2> /dev/null
    @echo "All build artefacts will be force removed."
    @- just _clean-all-folders "." ".idea" 2> /dev/null
    @- just _clean-all-folders "." "__pycache__" 2> /dev/null

clean-venv:
    @- just _delete-if-folder-exists ".venv" 2> /dev/null

clean-notebooks:
    @echo "Clean outputs and metadata from python notebooks."
    @# NOTE: only clean outputs in notebooks/... folder
    @# FIXME: nbconvert no longer recognises the .../**/... pattern
    @${ACTIVATE_VENV:-echo "venv:off"} && {{PYVENV}} -m jupyter nbconvert --clear-output --inplace notebooks/*.ipynb
    @${ACTIVATE_VENV:-echo "venv:off"} && {{PYVENV}} -m jupytext --update-metadata '{"vscode":""}' **/*.ipynb 2> /dev/null
    @${ACTIVATE_VENV:-echo "venv:off"} && {{PYVENV}} -m jupytext --update-metadata '{"vscode":null}' **/*.ipynb 2> /dev/null

clean-notebook-outputs path:
    @echo "Clean outputs from python notebook {{path}}."
    @${ACTIVATE_VENV:-echo "venv:off"} && {{PYVENV}} -m jupyter nbconvert --clear-output --inplace "{{path}}"

clean-notebook-meta path:
    @echo "Clean metadata from python notebook {{path}}."
    @${ACTIVATE_VENV:-echo "venv:off"} && {{PYVENV}} -m jupytext --update-metadata '{"vscode":""}' "{{path}}" 2> /dev/null
    @${ACTIVATE_VENV:-echo "venv:off"} && {{PYVENV}} -m jupytext --update-metadata '{"vscode":null}' "{{path}}" 2> /dev/null

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: logging, session
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

_clear-logs log_path="logs":
    @just _delete-if-folder-exists "{{log_path}}"

_create-logs log_path="logs":
    @just _create-logs-part "debug" "{{log_path}}"
    @just _create-logs-part "out" "{{log_path}}"
    @just _create-logs-part "err" "{{log_path}}"

_create-logs-part part log_path="logs":
    @just _create-folder-if-not-exists "{{log_path}}"
    @just _create-file-if-not-exists "{{log_path}}/{{part}}.log"

_reset-logs log_path="logs":
    @just _delete-if-folder-exists "{{log_path}}"
    @just _create-logs "{{log_path}}"

_reset-test-logs kind:
    @just _delete-if-folder-exists "tests/{{kind}}/logs"
    @just _create-logs-part "debug" "tests/{{kind}}/logs"

_display-logs log_path="logs":
    @echo ""
    @echo "Content of logs/debug.log:"
    @echo "----------------"
    @echo ""
    @- cat "{{log_path}}/debug.log"
    @echo ""
    @echo "----------------"

watch-logs n="10" log_path="logs":
    @tail -f -n {{n}} "{{log_path}}/out.log"

watch-logs-err n="10" log_path="logs":
    @tail -f -n {{n}} "{{log_path}}/err.log"

watch-logs-debug n="10" log_path="logs":
    @tail -f -n {{n}} "{{log_path}}/debug.log"

watch-logs-all n="10" log_path="logs":
    @just watch-logs {{n}} "{{log_path}}" &
    @just watch-logs-err {{n}} "{{log_path}}" &
    @just watch-logs-debug {{n}} "{{log_path}}" &

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: requirements
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

check-system:
    @echo "Operating System detected:  {{os_family()}}"
    @echo "Python command used:        {{PYTHON}}"
    @echo "Python command for venv:    {{PYVENV}}"
    @echo "Python path for venv:       $( ${ACTIVATE_VENV:-echo "venv:off"} && which {{PYVENV}} )"

check-system-requirements:
    @just _check-python-tool "{{GEN_MODELS}}" "datamodel-code-generator"
    @just _check-tool "{{GEN_APIS}}" "openapi-code-generator"
    @just _check-python-tool "{{LINTING}}" "{{LINTING}}"
    @just _check-python-tool "{{GITHOOK_PRECOMMIT}}" "pre-commit"
