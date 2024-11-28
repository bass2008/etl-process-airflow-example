#!/bin/bash

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "Conda is not installed. Please install Miniconda or Anaconda first."
    exit 1
fi

# Define versions and paths
PYTHON_VERSION="3.12"
AIRFLOW_VERSION="2.10.3"
AIRFLOW_DIR="./airflow"

create_environment() {
    echo "Creating conda environment airflow with Python ${PYTHON_VERSION}..."
    conda create -y -n airflow python=${PYTHON_VERSION}

    echo "Downloading constraints file..."
    curl -Lo "${AIRFLOW_DIR}/constraints.txt" https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt

    echo "Installing dependencies from requirements.txt with constraints..."
    conda run -n airflow pip install -r "${AIRFLOW_DIR}/requirements.txt" --constraint "${AIRFLOW_DIR}/constraints.txt"
}

# Check if environment exists
if conda info --envs | grep -q "airflow"; then
    echo "Environment 'airflow' already exists."
    read -p "Do you want to recreate it? (y/n): " answer

    if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
        echo "Removing existing environment..."
        conda env remove -n airflow
        create_environment
    else
        echo "Keeping existing environment."
    fi
else
    create_environment
fi

echo "Setup completed!"