# set shell := [ "bash", "-uc" ]
_default:
    @- just --unsorted --list
menu:
    @- just --unsorted --choose
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Justfile
# Recipes for various workflows.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# VARIABLES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

REPO_NAME := "herz"
PROJECT_NAME := "herz"

PATH_ROOT := justfile_directory()
CURRENT_DIR := invocation_directory()
OS := if os_family() == "windows" { "windows" } else { "linux" }
PYTHON := if os_family() == "windows" { "py -3" } else { "python3" }
NODE := "npm"
LINTING := "black"
GITHOOK_PRECOMMIT := "pre_commit"
GEN_MODELS := "datamodel-codegen"
GEN_MODELS_DOCUMENTATION := "openapi-generator"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Macros
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

_create-file-if-not-exists fname:
    @touch "{{fname}}";

_create-folder-if-not-exists path:
    @if ! [ -d "{{path}}" ]; then mkdir -p "{{path}}"; fi

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

_delete-if-file-exists fname:
    @if [ -f "{{fname}}" ]; then rm "{{fname}}"; fi

_delete-if-folder-exists path:
    @if [ -d "{{path}}" ]; then rm -rf "{{path}}"; fi

_clean-all-files path pattern:
    @find {{path}} -type f -name "{{pattern}}" -exec basename {} \; 2> /dev/null
    @- find {{path}} -type f -name "{{pattern}}" -exec rm {} \; 2> /dev/null

_clean-all-folders path pattern:
    @find {{path}} -type d -name "{{pattern}}" -exec basename {} \; 2> /dev/null
    @- find {{path}} -type d -name "{{pattern}}" -exec rm -rf {} \; 2> /dev/null

_check-python-tool tool name:
    @just _check-tool "{{PYTHON}} -m {{tool}}" "{{name}}"

_check-tool tool name:
    #!/usr/bin/env bash
    success=false
    {{tool}} --version >> /dev/null 2> /dev/null && success=true;
    {{tool}} --help >> /dev/null 2> /dev/null && success=true;
    # NOTE: if exitcode is 251 (= help or print version), then render success.
    [[ "$?" == "251" ]] && success=true;
    # FAIL tool not installed
    if ( $success ); then
        echo -e "Tool \x1b[2;3m{{name}}\x1b[0m installed correctly.";
        exit 0;
    else
        echo -e "Tool \x1b[2;3m{{tool}}\x1b[0m did not work." >> /dev/stderr;
        echo -e "Ensure that \x1b[2;3m{{name}}\x1b[0m (-> \x1b[1mjust build\x1b[0m) installed correctly and system paths are set." >> /dev/stderr;
        exit 1;
    fi

_generate-models path name:
    @{{GEN_MODELS}} \
        --input-file-type openapi \
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
        --input {{path}}/schema-{{name}}.yaml \
        --output {{path}}/generated/{{name}}.py

_generate-models-documentation path_schema path_docs name:
    @- {{GEN_MODELS_DOCUMENTATION}} generate \
        --skip-validate-spec \
        --input-spec {{path_schema}}/schema-{{name}}.yaml \
        --generator-name markdown \
        --output "{{path_docs}}/{{name}}"

_build-models-recursively models_path:
    #!/usr/bin/env bash
    just _delete-if-folder-exists "{{models_path}}/generated"
    just _create-folder-if-not-exists "{{models_path}}/generated"
    just _create-file-if-not-exists "{{models_path}}/generated/__init__.py"
    while read path; do
        if [[ "${path}" == "" ]]; then continue; fi
        path="${path##*/}";
        name="$( echo """${path}""" | sed -E """s/^schema-(.*)\.yaml$/\1/g""")";
        echo "- generate models for ${name}."
        just _generate-models "{{models_path}}" "${name}";
    done <<< "$( ls -f {{models_path}}/schema-*.yaml )";

_build-documentation-recursively models_path documentation_path:
    #!/usr/bin/env bash
    while read path; do
        if [[ "${path}" == "" ]]; then continue; fi
        path="${path##*/}";
        name="$( echo """${path}""" | sed -E """s/^schema-(.*)\.yaml$/\1/g""")";
        echo "- generate documentation for ${name}."
        just _generate-models-documentation "{{models_path}}" "{{documentation_path}}" "${name}";
    done <<< "$( ls -f {{models_path}}/schema-*.yaml )";

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: development
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

build-dev:
    @just build-misc
    @just build-requirements
    @just check-system-requirements-dev
    @just build-models
    @#just build-githook-husky
    @just build-githook-pc

# builds githook based on pre-commit (see https://pre-commit.com)
build-githook-pc:
    @git config --unset-all core.hooksPath
    @{{PYTHON}} -m pre_commit install

# builds githook based on node's husky
build-githook-husky:
    @npm install
    @rm -rf .husky
    @npx husky install
    @npx husky add .husky/pre-commit 'npx lint-staged'

githook-py path:
    @{{PYTHON}} -m {{LINTING}} --verbose "{{path}}"
    @{{PYTHON}} -m {{LINTING}} --check --verbose "{{path}}"

githook-ipynb path:
    @just clean-notebook "{{path}}"
    @{{PYTHON}} -m {{LINTING}} --verbose "{{path}}"
    @{{PYTHON}} -m {{LINTING}} --check --verbose "{{path}}"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: build
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

build:
    @just build-misc
    @just build-requirements
    @just check-system-requirements
    @just build-models

build-misc:
    @just _create-folder-if-not-exists "setup"
    @- cp -n "templates/template-config.yaml" "setup/config.yaml"

build-requirements:
    @{{PYTHON}} scripts/package.py "pyproject.toml" "requirements.txt"
    @{{PYTHON}} -m pip install --no-compile --disable-pip-version-check -r requirements.txt

build-models:
    @echo "Generate data models from schemata."
    @- just _build-models-recursively "src/models"

build-documentation:
    @echo "Generate documentations data models from schemata."
    @just _delete-if-folder-exists "documentation/models"
    @just _create-folder-if-not-exists "documentation/models"
    @- just _build-documentation-recursively "src/models" "documentation/models"
    @- just _clean-all-files "." ".openapi-generator*"
    @- just _clean-all-folders "." ".openapi-generator*"

build-archive branch="main":
    @echo "Create zip archive of project"
    @mkdir -p dist
    @git archive {{branch}} -o dist/{{REPO_NAME}}-$(cat dist/VERSION).zip

# process for release
dist branch="main":
    @just clean
    @just prettify
    @just build
    @just build-documentation
    @just build-archive

run path_to_config="setup/config.yaml":
    @{{PYTHON}} -m src.main "{{path_to_config}}"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: tests
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

tests:
    @- just tests-unit

tests-logs:
    @just _create-logs
    @- just tests
    @just _display-logs

tests-unit:
    @{{PYTHON}} -m pytest tests \
        --ignore=tests/integration \
        --cov-reset \
        --cov=. \
        2> /dev/null

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: qa
# NOTE: use for development only.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

qa:
    @{{PYTHON}} -m coverage report -m
coverage source_path tests_path:
    @just _create-logs
    @{{PYTHON}} -m pytest {{tests_path}} \
        --ignore=tests/integration \
        --cov-reset \
        --cov={{source_path}} \
        --capture=tee-sys \
        2> /dev/null
    @just _display-logs

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: prettify
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

check-linting:
    @{{PYTHON}} -m {{LINTING}} --check --verbose src/*
    @{{PYTHON}} -m {{LINTING}} --check --verbose tests/*
    @{{PYTHON}} -m {{LINTING}} --check --verbose notebooks/*

prettify:
    @{{PYTHON}} -m {{LINTING}} --verbose src/*
    @{{PYTHON}} -m {{LINTING}} --verbose tests/*
    @{{PYTHON}} -m {{LINTING}} --verbose notebooks/*

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: clean
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

clean:
    @just clean-basic
    @just clean-notebooks

clean-notebook path:
    @echo "Clean python notebook {{path}}."
    @{{PYTHON}} -m jupyter nbconvert --clear-output --inplace "{{path}}"
    @- {{PYTHON}} -m jupytext --update-metadata '{"vscode":""}' "{{path}}" 2> /dev/null
    @- {{PYTHON}} -m jupytext --update-metadata '{"vscode":null}' "{{path}}" 2> /dev/null

clean-notebooks:
    @echo "Clean python notebooks."
    @{{PYTHON}} -m jupyter nbconvert --clear-output --inplace **/*.ipynb
    @- {{PYTHON}} -m jupytext --update-metadata '{"vscode":""}' **/*.ipynb 2> /dev/null
    @- {{PYTHON}} -m jupytext --update-metadata '{"vscode":null}' **/*.ipynb 2> /dev/null

clean-basic:
    @echo "All system artefacts will be force removed."
    @- just _clean-all-files "." ".DS_Store" 2> /dev/null
    @echo "All test artefacts will be force removed."
    @- just _clean-all-folders "." ".pytest_cache" 2> /dev/null
    @- just _delete-if-file-exists ".coverage" 2> /dev/null
    @- just _delete-if-folder-exists "logs"
    @echo "All build artefacts will be force removed."
    @#- just _delete-if-folder-exists "documentation/models"
    @- just _delete-if-file-exists "package-lock.json" 2> /dev/null
    @- just _clean-all-folders "." ".idea" 2> /dev/null
    @- just _clean-all-folders "." "__pycache__" 2> /dev/null
    @- just _delete-if-folder-exists "src/models/generated" 2> /dev/null

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: logging, session
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

_create-logs:
    @# For logging purposes (since stdout is rechanneled):
    @just _delete-if-file-exists "logs/debug.log"
    @just _create-folder-if-not-exists "logs"
    @just _create-file-if-not-exists "logs/debug.log"

_display-logs:
    @echo ""
    @echo "Content of logs/debug.log:"
    @echo "----------------"
    @echo ""
    @- cat logs/debug.log
    @echo ""
    @echo "----------------"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: requirements
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

check-system:
    @echo "Operating System detected: {{os_family()}}."
    @echo "Python command used: {{PYTHON}}."

check-system-requirements-dev:
    @just check-system-requirements
    @#just _check-tool "{{NODE}}" "node package manager"
    @just _check-python-tool "{{GITHOOK_PRECOMMIT}}" "pre-commit"

check-system-requirements:
    @just _check-python-tool "{{LINTING}}" "{{LINTING}}"
    @just _check-tool "{{GEN_MODELS}}" "datamodel-code-generator"
    @just _check-tool "{{GEN_MODELS_DOCUMENTATION}}" "openapi-code-generator"
