#!/bin/bash
# Script to run CadQuery with the proper conda environment

# Source conda
source /opt/anaconda3/etc/profile.d/conda.sh

# Activate the cadquery environment
conda activate cadquery-env

# Run the split scripts
/opt/anaconda3/envs/cadquery-env/bin/python base.py
/opt/anaconda3/envs/cadquery-env/bin/python lid.py
/opt/anaconda3/envs/cadquery-env/bin/python side_walls.py

echo "CadQuery script completed!"
