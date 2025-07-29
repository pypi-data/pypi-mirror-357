#!/bin/bash
# Kubernetes Demo Setup Script for Dravik
# This script sets up a full Kubernetes environment with k3d for testing

set -e
set -o pipefail  # Return value of a pipeline is the status of the last command to exit with a non-zero status

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Dravik Kubernetes Demo Setup ===${NC}"
echo -e "This script will set up a complete Kubernetes environment for testing Dravik.\n"

# Step 1: Set up Python virtual environment
echo -e "${YELLOW}Step 1: Setting up Python virtual environment...${NC}"
if [ ! -d "k8s_venv" ]; then
    python3 -m venv k8s_venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment. Please install python3-venv package.${NC}"
        echo -e "${YELLOW}On Ubuntu/Debian: sudo apt install python3-venv${NC}"
        echo -e "${YELLOW}On CentOS/RHEL: sudo yum install python3-virtualenv${NC}"
        exit 1
    fi
    echo -e "${GREEN}Virtual environment created successfully.${NC}"
else
    echo -e "${GREEN}Virtual environment already exists.${NC}"
fi

# Verify the virtual environment exists
if [ ! -f "k8s_venv/bin/activate" ]; then
    echo -e "${RED}Virtual environment exists but activate script is missing!${NC}"
    echo -e "${YELLOW}Removing broken environment and recreating...${NC}"
    rm -rf k8s_venv
    python3 -m venv k8s_venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to recreate virtual environment.${NC}"
        exit 1
    fi
fi

# Activate the virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source k8s_venv/bin/activate

# Check if activation was successful
if [ $? -ne 0 ] || [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}Failed to activate virtual environment.${NC}"
    exit 1
fi

echo -e "${GREEN}Virtual environment activated successfully.${NC}"

# Step 2: Install k3d if not installed
echo -e "\n${YELLOW}Step 2: Checking for k3d...${NC}"
if ! command -v k3d &> /dev/null; then
    echo -e "k3d not found. Installing..."
    curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install k3d. Please install it manually:${NC}"
        echo -e "curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash"
        exit 1
    fi
else
    echo -e "${GREEN}✓ k3d is already installed.${NC}"
fi

# Step 3: Check for existing cluster
echo -e "\n${YELLOW}Step 3: Checking for existing Kubernetes cluster...${NC}"
if k3d cluster list | grep -q "dravik-cluster"; then
    echo -e "Dravik cluster already exists."
    read -p "Do you want to delete and recreate it? (y/n): " recreate
    if [[ "$recreate" == "y" || "$recreate" == "Y" ]]; then
        echo -e "Deleting existing cluster..."
        k3d cluster delete dravik-cluster
        echo -e "Creating new cluster..."
        k3d cluster create dravik-cluster
    fi
else
    echo -e "Creating new Dravik cluster..."
    k3d cluster create dravik-cluster
fi

# Step 4: Verify cluster is running
echo -e "\n${YELLOW}Step 4: Verifying cluster status...${NC}"
kubectl cluster-info
if [ $? -ne 0 ]; then
    echo -e "${RED}Kubernetes cluster is not running properly.${NC}"
    exit 1
fi

echo -e "\n${GREEN}✓ Kubernetes cluster is running.${NC}"
kubectl get nodes

# Step 5: Apply Dravik resources
echo -e "\n${YELLOW}Step 5: Creating Dravik resources...${NC}"
kubectl apply -f k8s_setup.yaml
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to create Dravik resources.${NC}"
    exit 1
fi

echo -e "\n${GREEN}✓ Dravik resources created successfully.${NC}"
kubectl get namespace dravik
kubectl get pvc -n dravik
kubectl get serviceaccount -n dravik

# Step 6: Run the test
echo -e "\n${YELLOW}Step 6: Running the Kubernetes test...${NC}"
echo -e "Activating virtual environment and running test..."
source k8s_venv/bin/activate
pip install --upgrade pip
pip install kubernetes pytest pytest-kubernetes pytest-xdist
python -m pytest kubernetes_tests/ -v

# Deactivate the virtual environment when done
deactivate

# Final message
echo -e "\n${GREEN}=== Demo Setup Complete ===${NC}"
echo -e "You now have a working Kubernetes environment with Dravik resources set up."
echo -e "\nTo use the Kubernetes tools in the future, run:"
echo -e "  ${YELLOW}./k8s_tools.sh test${NC} - Run the test script"
echo -e "  ${YELLOW}./k8s_tools.sh info${NC} - Get cluster information"
echo -e "  ${YELLOW}./k8s_tools.sh setup${NC} - Set up Kubernetes resources"

exit 0