#!/bin/bash

# Real Estate Project Environment Checker
# This script helps diagnose and fix common virtual environment issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Real Estate Project Environment Checker${NC}"
echo "========================================"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check virtual environment
check_venv() {
    echo -e "\n${BLUE}1. Checking Virtual Environment...${NC}"
    
    if [ -d ".venv" ]; then
        echo -e "${GREEN}✅ .venv directory exists${NC}"
        
        if [ -f ".venv/bin/python" ]; then
            echo -e "${GREEN}✅ Python executable found${NC}"
            
            # Test if Python works
            if .venv/bin/python -c "import sys" 2>/dev/null; then
                echo -e "${GREEN}✅ Python executable works${NC}"
                PYTHON_VERSION=$(.venv/bin/python --version)
                echo -e "   Version: ${PYTHON_VERSION}"
            else
                echo -e "${RED}❌ Python executable is broken${NC}"
                return 1
            fi
        else
            echo -e "${RED}❌ Python executable missing${NC}"
            return 1
        fi
        
        if [ -f ".venv/bin/pip" ]; then
            echo -e "${GREEN}✅ pip executable found${NC}"
            
            # Test if pip works
            if .venv/bin/pip --version >/dev/null 2>&1; then
                echo -e "${GREEN}✅ pip executable works${NC}"
                PIP_VERSION=$(.venv/bin/pip --version)
                echo -e "   Version: ${PIP_VERSION}"
            else
                echo -e "${RED}❌ pip executable is broken${NC}"
                return 1
            fi
        else
            echo -e "${RED}❌ pip executable missing${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  .venv directory not found${NC}"
        return 1
    fi
    
    return 0
}

# Function to check for multiple virtual environments
check_multiple_venvs() {
    echo -e "\n${BLUE}2. Checking for Multiple Virtual Environments...${NC}"
    
    venv_count=0
    
    if [ -d ".venv" ]; then
        echo -e "${GREEN}Found: .venv/${NC}"
        venv_count=$((venv_count + 1))
    fi
    
    if [ -d "venv" ]; then
        echo -e "${YELLOW}Found: venv/${NC}"
        venv_count=$((venv_count + 1))
    fi
    
    if [ -d "env" ]; then
        echo -e "${YELLOW}Found: env/${NC}"
        venv_count=$((venv_count + 1))
    fi
    
    if [ $venv_count -gt 1 ]; then
        echo -e "${YELLOW}⚠️  Multiple virtual environments detected${NC}"
        echo -e "   Recommendation: Remove extra environments to avoid confusion"
        return 1
    elif [ $venv_count -eq 1 ]; then
        echo -e "${GREEN}✅ Single virtual environment found${NC}"
        return 0
    else
        echo -e "${RED}❌ No virtual environment found${NC}"
        return 1
    fi
}

# Function to check Python installation
check_python() {
    echo -e "\n${BLUE}3. Checking System Python...${NC}"
    
    if command_exists python3; then
        SYSTEM_PYTHON_VERSION=$(python3 --version)
        echo -e "${GREEN}✅ System Python found: ${SYSTEM_PYTHON_VERSION}${NC}"
        return 0
    else
        echo -e "${RED}❌ python3 not found in PATH${NC}"
        return 1
    fi
}

# Function to check project dependencies
check_dependencies() {
    echo -e "\n${BLUE}4. Checking Project Dependencies...${NC}"
    
    if [ ! -f "requirements.txt" ]; then
        echo -e "${RED}❌ requirements.txt not found${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ requirements.txt found${NC}"
    
    if check_venv; then
        # Check if common packages are installed
        if .venv/bin/python -c "import requests, pandas, flask" 2>/dev/null; then
            echo -e "${GREEN}✅ Core dependencies installed${NC}"
            
            # Count installed packages
            PACKAGE_COUNT=$(.venv/bin/pip list | wc -l)
            echo -e "   Installed packages: $((PACKAGE_COUNT - 2))"
            return 0
        else
            echo -e "${YELLOW}⚠️  Some dependencies missing or broken${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  Cannot check dependencies without working virtual environment${NC}"
        return 1
    fi
}

# Function to provide recommendations
provide_recommendations() {
    echo -e "\n${BLUE}5. Recommendations:${NC}"
    
    if ! check_venv >/dev/null 2>&1; then
        echo -e "${YELLOW}→ Create a fresh virtual environment:${NC}"
        echo -e "   make venv-create"
        echo -e "   make install"
    fi
    
    if ! check_dependencies >/dev/null 2>&1; then
        echo -e "${YELLOW}→ Install/reinstall dependencies:${NC}"
        echo -e "   make install"
    fi
    
    if [ -d "venv" ] && [ -d ".venv" ]; then
        echo -e "${YELLOW}→ Remove duplicate virtual environment:${NC}"
        echo -e "   rm -rf venv"
    fi
    
    echo -e "\n${GREEN}For a complete reset:${NC}"
    echo -e "   make venv-reset"
}

# Main execution
main() {
    check_python
    check_multiple_venvs
    check_venv
    check_dependencies
    provide_recommendations
    
    echo -e "\n${BLUE}Environment check complete!${NC}"
}

# Run main function
main
