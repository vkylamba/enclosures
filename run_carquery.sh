#!/bin/bash
# Script to run CadQuery with the proper conda environment

# Source conda
source /opt/anaconda3/etc/profile.d/conda.sh

# Activate the cadquery environment
conda activate cadquery-env

# Run the script
/opt/anaconda3/envs/cadquery-env/bin/python case.py

echo "CadQuery script completed!"
