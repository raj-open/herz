# set shell := [ "bash", "-c" ]
_default:
    @- just --unsorted --list
menu:
    @- just --unsorted --choose

# ----------------------------------------------------------------
# Justfile
# Recipes for various workflows.
# ----------------------------------------------------------------

set dotenv-load := true
# set dotenv-path := [".env", ".env.docker-vars"]
set positional-arguments := true

# --------------------------------
# VARIABLES
# --------------------------------

PATH_ROOT := justfile_directory()
CURRENT_DIR := invocation_directory()
OS := if os_family() == "windows" { "windows" } else { "linux" }
PYVENV_ON := if os_family() == "windows" { ". .venv/Scripts/activate" } else { ". .venv/bin/activate" }
PYVENV := if os_family() == "windows" { "python" } else { "python3" }
LINTING := "ruff"
GITHOOK_PRECOMMIT := "pre_commit"
GEN_MODELS := "datamodel_code_generator"
GEN_MODELS_DOCUMENTATION := "openapi-generator-cli"
RUST_TO_PY_BINDINGS := "maturin"
TOOL_TEST_BDD := "behave"

# --------------------------------
# Macros
# --------------------------------

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
    {{PYVENV_ON}} && {{tool}} --version >> /dev/null 2> /dev/null && success=true;
    {{PYVENV_ON}} && {{tool}} --help >> /dev/null 2> /dev/null && success=true;
    # NOTE: if exitcode is 251 (= help or print version), then render success.
    if [[ "$?" == "251" ]]; then success=true; fi
    # FAIL tool not installed
    if ( $success ); then
        echo -e "Tool \x1b[2;3m{{name}}\x1b[0m installed correctly.";
        exit 0;
    else
        echo -e "Tool \x1b[2;3m{{tool}}\x1b[0m did not work." >> /dev/stderr;
        echo -e "Ensure that \x1b[2;3m{{name}}\x1b[0m (-> \x1b[1mjust build\x1b[0m) installed correctly and system paths are set." >> /dev/stderr;
        exit 1;
    fi

_generate-documentation path_schema target_path name:
    @{{PYVENV_ON}} && {{GEN_MODELS_DOCUMENTATION}} generate \
        --skip-validate-spec \
        --input-spec {{path_schema}}/schema-{{name}}.yaml \
        --generator-name markdown \
        --output "{{target_path}}/{{name}}"

_build-documentation-recursively path_schema target_path:
    #!/usr/bin/env bash
    while read path; do
        if [[ "${path}" == "" ]]; then continue; fi
        path="${path##*/}";
        name="$( echo """${path}""" | sed -E """s/^schema-(.*)\.yaml$/\1/g""")";
        echo "- generate documentation for ${name}."
        just _generate-documentation "{{path_schema}}" "{{target_path}}" "${name}";
    done <<< "$( ls -f {{path_schema}}/schema-*.yaml )";
    exit 0;

_generate-models path_schema target_path name:
    @ # cf. https://github.com/koxudaxi/datamodel-code-generator?tab=readme-ov-file#all-command-options
    @{{PYVENV_ON}} && {{PYVENV}} -m {{GEN_MODELS}} \
        --input-file-type openapi \
        --output-model-type pydantic_v2.BaseModel \
        --encoding "UTF-8" \
        --disable-timestamp \
        --use-schema-description \
        --use-standard-collections \
        --use-union-operator \
        --use-default-kwarg \
        --field-constraints \
        --output-datetime-class AwareDatetime \
        --capitalise-enum-members \
        --enum-field-as-literal one \
        --set-default-enum-member \
        --use-subclass-enum \
        --allow-population-by-field-name \
        --strict-nullable \
        --use-double-quotes \
        --target-python-version 3.11 \
        --input "{{path_schema}}/schema-{{name}}.yaml" \
        --output "{{target_path}}/{{name}}.py"

_generate-models-recursively path_schema target_path:
    #!/usr/bin/env bash
    while read path; do
        if [[ "${path}" == "" ]]; then continue; fi
        path="${path##*/}";
        name="$( echo """${path}""" | sed -E """s/^schema-(.*)\.yaml$/\1/g""")";
        echo "- generate models for ${name}."
        just _generate-models "{{path_schema}}" "{{target_path}}" "${name}";
    done <<< "$( ls -f {{path_schema}}/schema-*.yaml )";
    exit 0;

# ----------------------------------------------------------------
# TARGETS
# ----------------------------------------------------------------

# --------------------------------
# TARGETS: build
# --------------------------------

setup:
    @echo "TASK: SETUP"
    @mkdir -p setup
    @- cp -n "templates/template.env" ".env"
    @- cp -n "templates/template-requests.yaml" "setup/requests.yaml"

build:
    @echo "TASK: BUILD"
    @- just build-venv
    @just build-requirements
    @just check-system-requirements
    @just build-models
    @just build-githook-pc

build-venv:
    @echo "SUBTASK: create venv if not exists"
    @${PYTHON_PATH} -m venv .venv

# cf. https://pre-commit.com
build-githook-pc:
    #!/usr/bin/env bash
    echo "SUBTASK: build githook"
    if [[ -d ".git" ]]; then
        git config --unset-all core.hooksPath
        {{PYVENV_ON}} && {{PYVENV}} -m pre_commit install
    fi
    exit 0;

build-requirements:
    @echo "SUBTASK: build requirements"
    @just build-requirements-basic
    @just build-requirements-dependencies

build-requirements-basic:
    @- {{PYVENV_ON}} && {{PYVENV}} -m pip install --upgrade pip 2> /dev/null
    @{{PYVENV_ON}} && pip install ruff uv

build-requirements-dependencies:
    @{{PYVENV_ON}} && uv pip install \
        --exact \
        --strict \
        --compile-bytecode \
        --no-python-downloads \
        --requirements pyproject.toml
    @{{PYVENV_ON}} && uv sync

build-models:
    @echo "SUBTASK: build data models from schemata."
    @rm -rf "src/models/generated" 2> /dev/null
    @mkdir -p "src/models/generated"
    @touch "src/models/generated/__init__.py"
    @just _generate-models-recursively "models" "src/models/generated"

build-bindings:
    @echo "SUBTASK: build compiled bindings."
    @{{PYVENV_ON}} && cd bindings/rust && {{PYVENV}} -m {{RUST_TO_PY_BINDINGS}} develop \
        --bindings pyo3 \
        --ignore-rust-version \
        --release

build-docs:
    @echo "SUBTASK: build documentation for data models from schemata."
    @rm -rf "docs/models" 2> /dev/null
    @mkdir -p "docs/models"
    @- just _build-documentation-recursively "models" "docs/models"
    @- just _clean-all-files "." ".openapi-generator*"
    @- just _clean-all-folders "." ".openapi-generator*"

build-archive:
    @echo "TASK: create .zip archive of project"
    @# store current state
    @git add . && git commit --no-verify --allow-empty -m "temp"
    @# create archive
    @git archive -o dist/${PROJECT_NAME}-$(cat dist/VERSION).zip "HEAD"
    @# undo above commit
    @git reset --soft HEAD~1 && git reset .

# --------------------------------
# TARGETS: execution
# --------------------------------

run *args:
    @{{PYVENV_ON}} && {{PYVENV}} -m src.cli {{args}}

run-cli mode="requests" requests="setup/requests.yaml" env_path=".env" log_path="logs" session_path=".session":
    @just _reset-logs "{{log_path}}"
    @{{PYVENV_ON}} && {{PYVENV}} -m src.cli \
        "{{mode}}" \
        --requests "{{requests}}" \
        --env "{{env_path}}" \
        --log "{{log_path}}" \
        --session "{{session_path}}"

run-cli-debug mode="requests" requests="setup/requests.yaml" env_path=".env" log_path="logs" session_path=".session":
    @just _reset-logs "{{log_path}}"
    @{{PYVENV_ON}} && {{PYVENV}} -m src.cli \
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
    @{{PYVENV_ON}} && {{PYVENV}} -m src.api \
        --env "{{env_path}}" \
        --log "{{log_path}}" \
        --session "{{session_path}}"

run-api-debug env_path=".env" log_path="logs" session_path=".session" IP="${HTTP_IP:-localhost}" PORT="${HTTP_PORT:-8000}":
    @just _reset-logs "{{log_path}}"
    @# kill anything running on port
    @just kill-port "{{PORT}}"
    @echo "START API"
    @{{PYVENV_ON}} && {{PYVENV}} -m src.api \
        --debug \
        --env "{{env_path}}" \
        --log "{{log_path}}" \
        --session "{{session_path}}"

# --------------------------------
# TARGETS: development
# --------------------------------

# Recipe only works if local file test.py exists
dev *args:
    @just _reset-logs
    @{{PYVENV_ON}} && {{PYVENV}} -m dev {{args}}

# --------------------------------
# TARGETS: terminate execution
# --------------------------------

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

# --------------------------------
# TARGETS: tests
# --------------------------------

tests:
    @just tests-unit
    @just tests-behave
    @just tests-integration

tests-logs log_path="logs":
    @just _reset-logs "{{log_path}}"
    @- just tests
    @just _display-logs "{{log_path}}"

tests-unit:
    @{{PYVENV_ON}} && {{PYVENV}} -m pytest "tests/unit" \
        --cov-reset \
        --cov=.

test-unit path:
    @just _reset-test-logs "unit"
    @{{PYVENV_ON}} && {{PYVENV}} -m pytest "{{path}}"

tests-behave:
    @just test-behave "tests/behave"

test-behave path:
    @just _reset-test-logs "behave"
    @{{PYVENV_ON}} && {{PYVENV}} -m {{TOOL_TEST_BDD}} \
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

# --------------------------------
# TARGETS: qa
# NOTE: use for development only.
# --------------------------------

qa:
    @{{PYVENV_ON}} && {{PYVENV}} -m coverage report -m

coverage source_path tests_path log_path="logs":
    @just _reset-logs "{{log_path}}"
    @{{PYVENV_ON}} && {{PYVENV}} -m pytest {{tests_path}} \
        --ignore=tests/integration \
        --cov-reset \
        --cov={{source_path}} \
        --capture=tee-sys \
        2> /dev/null
    @just _display-logs

# --------------------------------
# TARGETS: prettify
# --------------------------------

lint path:
    @{{PYVENV_ON}} && {{PYVENV}} -m {{LINTING}} check \
        --respect-gitignore \
        --show-fixes \
        --no-unsafe-fixes \
        --exit-zero \
        --fix \
        "{{path}}"
    @{{PYVENV_ON}} && {{PYVENV}} -m {{LINTING}} format \
        --respect-gitignore \
        "{{path}}"

lint-dry path:
    @{{PYVENV_ON}} && {{PYVENV}} -m {{LINTING}} check \
        --respect-gitignore \
        --no-unsafe-fixes \
        --exit-zero \
        --diff \
        "{{path}}"

lint-check path:
    @{{PYVENV_ON}} && {{PYVENV}} -m {{LINTING}} check \
        --respect-gitignore \
        --no-unsafe-fixes \
        --exit-zero \
        --verbose \
        "{{path}}"

prettify:
    @just lint "src"
    @just lint "tests"
    @just lint "notebooks"

prettify-dry:
    @just lint-dry "src"
    @just lint-dry "tests"
    @just lint-dry "notebooks"

# --------------------------------
# TARGES: utilities
# --------------------------------

create-badge-pyversion:
    @{{PYVENV_ON}} && {{PYVENV}} -m pybadges \
        --left-text="python" \
        --right-text="3.10, 3.11, 3.12" \
        --whole-link="https://www.python.org/" \
        --browser \
        --logo='https://dev.w3.org/SVG/tools/svgweb/samples/svg-files/python.svg' \
        >> docs/badges/pyversion.svg

# --------------------------------
# TARGETS: clean
# --------------------------------

clean session_path=".session":
    @- just clean-basic "{{session_path}}"
    @- just clean-notebooks
    @- just clean-venv

clean-basic session_path=".session":
    @echo "All system artefacts will be force removed."
    @- just _clean-all-files "." ".DS_Store" 2> /dev/null
    @echo "All test artefacts will be force removed."
    @- rm -rf ".pytest_cache" 2> /dev/null
    @- rm -f ".coverage" 2> /dev/null
    @- rm -f "tests/behave/.session" 2> /dev/null
    @- rm -f "tests/behave/logs" 2> /dev/null
    @echo "All build artefacts will be force removed."
    @- rm -rf ".venv" 2> /dev/null
    @- rm -rf "build" 2> /dev/null
    @- rm -rf "bindings/rust/target" 2> /dev/null
    @- just _clean-all-folders "." ".idea" 2> /dev/null
    @- just _clean-all-folders "." "__pycache__" 2> /dev/null

clean-venv:
    @echo "VENV will be removed."
    @- rm -rf ".venv" 2> /dev/null

clean-notebooks:
    @echo "Clean outputs and metadata from python notebooks."
    @# NOTE: only clean outputs in notebooks/... folder
    @# FIXME: nbconvert no longer recognises the .../**/... pattern
    @{{PYVENV_ON}} && {{PYVENV}} -m jupyter nbconvert --clear-output --inplace notebooks/*.ipynb
    @{{PYVENV_ON}} && {{PYVENV}} -m jupytext --update-metadata '{"vscode":""}' **/*.ipynb 2> /dev/null
    @{{PYVENV_ON}} && {{PYVENV}} -m jupytext --update-metadata '{"vscode":null}' **/*.ipynb 2> /dev/null

clean-notebook-outputs path:
    @echo "Clean outputs from python notebook {{path}}."
    @{{PYVENV_ON}} && {{PYVENV}} -m jupyter nbconvert --clear-output --inplace "{{path}}"

clean-notebook-meta path:
    @echo "Clean metadata from python notebook {{path}}."
    @{{PYVENV_ON}} && {{PYVENV}} -m jupytext --update-metadata '{"vscode":""}' "{{path}}" 2> /dev/null
    @{{PYVENV_ON}} && {{PYVENV}} -m jupytext --update-metadata '{"vscode":null}' "{{path}}" 2> /dev/null

# --------------------------------
# TARGETS: logging, session
# --------------------------------

_clear-logs log_path="${PATH_LOGS}":
    @rm -rf "{{log_path}}" 2> /dev/null

_create-logs-part part log_path="${PATH_LOGS}":
    @mkdir -p "{{log_path}}"
    @touch "{{log_path}}/{{part}}.log"

_create-logs log_path="${PATH_LOGS}":
    @just _create-logs-part "debug" "{{log_path}}"
    @just _create-logs-part "out"   "{{log_path}}"
    @just _create-logs-part "err"   "{{log_path}}"

_reset-logs log_path="${PATH_LOGS}":
    @- just _clear-logs "{{log_path}}" 2> /dev/null
    @just _create-logs "{{log_path}}"

_display-logs:
    @echo ""
    @echo "Content of ${PATH_LOGS}/debug.log:"
    @echo "----------------"
    @echo ""
    @- cat ${PATH_LOGS}/debug.log
    @echo ""
    @echo "----------------"

watch-logs n="10":
    @tail -f -n {{n}} ${PATH_LOGS}/out.log

watch-logs-err n="10":
    @tail -f -n {{n}} ${PATH_LOGS}/err.log

watch-logs-debug n="10":
    @tail -f -n {{n}} ${PATH_LOGS}/debug.log

watch-logs-all n="10":
    @just watch-logs {{n}} &
    @just watch-logs-err {{n}} &
    @just watch-logs-debug {{n}} &

# appends log contents to a file with date stamp
archive-log part log_path="${PATH_LOGS}" archive_path="${PATH_LOGS}/archive":
    #!/usr/bin/env bash
    # create stamps
    DATE_NOW="$(date '+%Y-%m-%d')"
    TEMP_STAMP="${DATE_NOW}_${RANDOM}"

    echo "ARCHIVE {{log_path}}/{{part}}.log ---> {{archive_path}}/${DATE_NOW}_{{part}}.log"

    # shift entire contents to temp file and recreate an empty file
    mv "{{log_path}}/{{part}}.log" "{{log_path}}/{{part}}_${TEMP_STAMP}.log"
    touch "{{log_path}}/{{part}}.log"

    # append contents of temp file to possibly pre-existing archive and remove temp
    cat "{{log_path}}/{{part}}_${TEMP_STAMP}.log" >> "{{archive_path}}/${DATE_NOW}_{{part}}.log"
    rm "{{log_path}}/{{part}}_${TEMP_STAMP}.log"

archive-logs log_path="${PATH_LOGS}" archive_path="${PATH_LOGS}/archive":
    @# ensure logs exist
    @mkdir -p "{{archive_path}}"
    @just _create-logs "{{log_path}}"
    @# store each log
    @just archive-log "out" "{{log_path}}" "{{archive_path}}"
    @just archive-log "err" "{{log_path}}" "{{archive_path}}"
    @# NOTE: do not archive debug logs!
    @# just archive-log "debug" "{{log_path}}" "{{archive_path}}"
    @just _create-logs-part "debug" "{{log_path}}"

# --------------------------------
# TARGETS: requirements
# --------------------------------

check-system:
    @echo "Operating System detected:  {{os_family()}}"
    @echo "Python command used:        ${PYTHON_PATH}"
    @echo "Python command for venv:    {{PYVENV}}"
    @echo "Python path for venv:       $( {{PYVENV_ON}} && which {{PYVENV}} )"

check-system-requirements:
    @just _check-python-tool "{{GEN_MODELS}}" "datamodel-code-generator"
    @just _check-python-tool "{{TOOL_TEST_BDD}}" "behave"
    @just _check-python-tool "{{LINTING}}" "{{LINTING}}"
