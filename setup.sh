#!/bin/bash
clear
set -e

# ----------------------------------------------------------------------
# Check for Python 3.12
python_version_required="3.12"
python_version=$(python3 --version 2>&1)
if [[ $python_version != Python\ ${python_version_required}* ]]; then
    echo "Python ${python_version_required} is required. Current version: $python_version"
    exit 1
fi

# ----------------------------------------------------------------------
# Define directories
dir_current=$(cd "$(dirname "$0")"; pwd)
dir_workspace="$dir_current/workspace"
dir_sources="$dir_workspace/sources"
dir_build="$dir_workspace/build"
dir_venv="$dir_workspace/venv"
dir_venv_site_packages="$dir_venv/lib/python$python_version_required/site-packages"

# ----------------------------------------------------------------------
# Define functions
git_submodule_init() {
    cd "$dir_sources"
    if [ ! -d ".git" ]; then
        echo "Not a git repository. Initializing git repository."
        git config --global init.defaultBranch main
        git init
    fi
}
git_submodule_add() {
    cd "$dir_sources"
    echo "Adding git submodule $1 to $2..."
    git submodule add "$1" "$2"
}
git_submodule_update() {
    cd "$dir_sources"
    echo "Updating git submodules..."
    git submodule update --remote --merge
}
git_agentscope_family() {
    cd "$dir_sources"
    if [ ! -d "agentscope" ]; then
        echo "Adding agentscope submodules..."
        git_submodule_add "https://github.com/agentscope-ai/agentscope.git" "agentscope"
    fi
    if [ ! -d "agentscope-runtime" ]; then
        echo "Adding agentscope-runtime submodules..."
        git_submodule_add "https://github.com/agentscope-ai/agentscope-runtime.git" "agentscope-runtime"
    fi
    if [ ! -d "agentscope-studio" ]; then
        echo "Adding agentscope-studio submodules..."
        git_submodule_add "https://github.com/agentscope-ai/agentscope-studio.git" "agentscope-studio"
    fi
    echo "Ensuring .gitignore file exists..."
    if [ ! -f ".gitignore" ]; then
        echo "Creating .gitignore file..."
        touch .gitignore
        echo "*.pyc" >> .gitignore
        echo "__pycache__/" >> .gitignore
        echo ".vscode/" >> .gitignore
        echo "workspace/" >> .gitignore
        echo "build/" >> .gitignore
        echo "sources/" >> .gitignore
    fi
}
setup_python_venv() {
    cd "$dir_workspace"
    if [ ! -d "$dir_workspace/venv" ]; then
        echo "Creating python virtual environment..."
        python3 -m venv "$dir_workspace/venv"
    fi
    echo "Activating python virtual environment..."
    source "$dir_workspace/venv/bin/activate"
    # add pip mirror to speed up pip install
    pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
}
setup_agentscope() {
    cd "$dir_sources/agentscope"
    # Install the package in editable mode
    echo "Installing agentscope..."
    pip install -e . --upgrade --target=$dir_venv_site_packages
}
setup_agentscope_runtime() {
    cd "$dir_sources/agentscope-runtime"
    # Install the package in editable mode

    # Install core dependencies
    echo "Installing agentscope-runtime..."
    pip install -e . --upgrade --target=$dir_venv_site_packages

    # Install sandbox dependencies
    echo "Installing agentscope-runtime sandbox dependencies..."
    pip install -e ".[sandbox]" --upgrade --target=$dir_venv_site_packages
}
setup_agentscope_studio() {
    cd "$dir_sources/agentscope-studio"
    # Install the package in editable mode
    echo "Installing agentscope-studio..."
    npm install --force --verbose
    echo "Starting agentscope-studio..."
    npm run dev &
    echo "Waiting for agentscope-studio to start..."
    sleep 10
    echo "You can visit 'agentscope_studio' at http://localhost:3000"
}
fix_pip_dependencies() { 
    source "$dir_workspace/venv/bin/activate"
    # mcp<1.10.0
    # agentscope-runtime 0.1.3 requires mcp<1.10.0,>=1.8.0, but you have mcp 1.13.1 which is incompatible.
    pip install "mcp<1.10.0,>=1.8.0" --upgrade --target=$dir_venv_site_packages
}
main() {
    echo "Setting up the project from git sources code ..."
    cd "$dir_current"

    # Create necessary directories
    mkdir -p "$dir_sources"
    mkdir -p "$dir_build"

    # Update or add git submodules
    git_submodule_init
    git_agentscope_family
    git_submodule_update

    # Setup python virtual environment
    setup_python_venv

    # Setup agentscope
    setup_agentscope
    setup_agentscope_runtime
    setup_agentscope_studio
    fix_pip_dependencies

    echo "Setup completed successfully."

}
main $1