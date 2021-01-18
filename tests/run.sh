#!/bin/bash

# Utils
python -m unittest test_logging.py
python -m unittest test_load_layers.py
python -m unittest test_load_metadata.py

# Indicators
python -m unittest test_indicator_ghspop.py
python -m unittest test_indicator_last_edit_2.py
python -m unittest test_indicator_poi_density_2.py
