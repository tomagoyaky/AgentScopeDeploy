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
ensure_agent_scope_setup() {
    if [ -z "$(find "$dir_venv_site_packages" -maxdepth 1 -type d -name 'agentscope*')" ]; then
        # we will install agentscope use setup.sh, input y continue
        read -p "agentscope is not installed in the virtual environment. Do you want to install it now? (y/n): " choice
        if [[ "$choice" != "y" && "$choice" != "Y" ]]; then
            echo "Exiting. Please install agentscope manually."
            exit 1
        fi
        
        echo "Installing agentscope..."
        bash "$dir_current/setup.sh"
    else
        echo "agentscope is already installed."
    fi
}
# Judge .env file exists
check_env_file() {
    if [ ! -f "$dir_workspace/.env" ]; then
        echo "Please create a .env file in the workspace directory with necessary environment variables."
        exit 1
    else
        echo "Loading environment variables from .env file..."
        source "$dir_workspace/.env"
    fi
}
main() {
    # Activate python virtual environment
    setup_python_venv

    # Ensure the agent scope setup is complete
    ensure_agent_scope_setup

    # Check .env file
    check_env_file

    echo "Starting agentscope-runtime..."
    if [ "$1" == "single" ]; then
        echo "Starting single agent chat..."
        $dir_venv/bin/python "$dir_current/agent/SingleAgentScope.py"
    elif [ "$1" == "multi" ]; then
        echo "Starting multi-agent chat..."
        $dir_venv/bin/python "$dir_current/agent/MultiAgentScope.py"
    else
        echo "Usage: $0 {single|multi}"
        exit 1
    fi
}
main $1