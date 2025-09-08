#!/bin/sh
clear
set -e

# ----------------------------------------------------------------------
# Check for Python 3.13
python_version_required="3.13"
python_version=$(python --version 2>&1)
if [[ $python_version != Python\ ${python_version_required}* ]]; then
    echo "Python ${python_version_required} is required. Current version: $python_version"
    exit 1
fi
echo "Python version $python_version_required is OK."

# ----------------------------------------------------------------------
# Define directories
dir_current=$(cd "$(dirname "$0")"; pwd)
dir_workspace="$dir_current/workspace"
dir_status="$dir_workspace/status"
dir_sources="$dir_workspace/sources"
dir_build="$dir_workspace/build"
dir_venv="$dir_workspace/venv"
dir_venv_site_packages="$dir_venv/lib/python$python_version_required/site-packages"

# ----------------------------------------------------------------------
# Define functions
log_info() {
    echo -e "\033[1;32m[INFO]\033[0m $1"
}
log_warn() {
    echo -e "\033[1;33m[WARN]\033[0m $1"
}
log_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}
setup_python_venv() {
    cd "$dir_workspace"
    if [ ! -d "$dir_workspace/venv" ]; then
        log_info "Creating python virtual environment..."
        python -m venv "$dir_workspace/venv"
    fi
    log_info "Activating python virtual environment..."
    source "$dir_workspace/venv/bin/activate"

    if [ ! -f "$dir_status/pip.upgrade.set.ok.status" ]; then
        $dir_venv/bin/pip install --upgrade pip
        touch "$dir_status/pip.upgrade.set.ok.status"
    fi

    if [ ! -f "$dir_status/pip.conf.set.ok.status" ]; then
        # add pip mirror to speed up pip install
        $dir_venv/bin/pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
        touch "$dir_status/pip.conf.set.ok.status"
    else
        log_warn "pip mirror is already set."
    fi
}
ensure_agent_scope_setup() {
    if [ -z "$(find "$dir_venv_site_packages" -maxdepth 1 -type d -name 'agentscope*')" ]; then
        # we will install agentscope use setup.sh, input y continue
        read -p "agentscope is not installed in the virtual environment. Do you want to install it now? (y/n): " choice
        if [[ "$choice" != "y" && "$choice" != "Y" ]]; then
            log_warn "Exiting. Please install agentscope manually."
            exit 1
        fi
        
        log_info "Installing agentscope..."
        bash "$dir_current/setup.sh"
    else
        log_warn "agentscope is already installed."
    fi
}
# Judge .env file exists
check_env_file() {
    if [ ! -f "$dir_workspace/.env" ]; then
        log_error "Please create a .env file in the workspace directory with necessary environment variables."
        exit 1
    else
        log_info "Loading environment variables from .env file..."
        source "$dir_workspace/.env"
    fi
}
fix_pip_dependencies() { 
    source "$dir_workspace/venv/bin/activate"
    if [ ! -f "$dir_status/pip.fix.ok.status" ]; then
        # fix: agentscope-runtime 0.1.3 requires mcp<1.10.0,>=1.8.0, but you have mcp 1.13.1 which is incompatible.
        log_warn "Fixing mcp module..."
        $dir_venv/bin/pip uninstall mcp -y
        $dir_venv/bin/pip install "mcp<1.10.0,>=1.8.0" --upgrade --target=$dir_venv_site_packages

        # fix: ModuleNotFoundError: No module named 'anthropic._models'
        log_warn "Fixing anthropic module..."
        $dir_venv/bin/pip install --upgrade --force-reinstall anthropic --target=$dir_venv_site_packages

        # fix: ModuleNotFoundError: No module named 'packaging'
        log_warn "Fixing packaging module..."
        $dir_venv/bin/pip install --upgrade --force-reinstall packaging --target=$dir_venv_site_packages

        # fix: ModuleNotFoundError: No module named 'protobuf'
        log_warn "Fixing protobuf module..."
        $dir_venv/bin/pip install --upgrade --force-reinstall protobuf --target=$dir_venv_site_packages

        touch "$dir_status/pip.fix.ok.status"
    else
        log_warn "pip dependencies are already fixed."
    fi
}
CMD(){
    local cmdline=$1
    local args="$2"
    log_info "Executing command: [$cmdline $args]"
    # export PYTHONPATH="$dir_venv_site_packages"
    # log_info "PYTHONPATH: $PYTHONPATH"
    $dir_venv/bin/python "$cmdline" "$args"
}
main() {
    cd $dir_current
    # Create necessary directories
    mkdir -p "$dir_sources"
    mkdir -p "$dir_build"
    mkdir -p "$dir_status"

    # Activate python virtual environment
    setup_python_venv

    # Ensure the agent scope setup is complete
    ensure_agent_scope_setup

    # Check .env file
    check_env_file

    # Fix module dependencies
    fix_pip_dependencies

    log_info "Starting agentscope-runtime..."
    if [ "$1" == "single" ]; then
        log_info "Starting single agent chat..."
        CMD "$dir_current/agent/SingleModel.qwen-max.py"
    elif [ "$1" == "single.deepseek" ]; then
        log_info "Starting single deep seek agent chat..."
        CMD "$dir_current/agent/SingleModel.deepseek.py"
    elif [ "$1" == "single.streaming" ]; then
        log_info "Starting single streaming agent chat..."
        CMD "$dir_current/agent/SingleModel.qwen-trubo.stream.py"
    elif [ "$1" == "single.thinking" ]; then
        log_info "Starting single thinking agent chat..."
        CMD "$dir_current/agent/SingleModel.qwen-trubo.thinking.py"
    elif [ "$1" == "multi" ]; then
        log_info "Starting multi-agent chat..."
        CMD "$dir_current/agent/MultiAgentScope.py"
    else
        log_info "Usage: $0 {single|single.deepseek|single.streaming|single.thinking|multi}"
        exit 1
    fi
}
main $1