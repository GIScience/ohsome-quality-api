#!/bin/bash

# Utils
python -m unittest test_logging.py
python -m unittest test_load_layers.py
python -m unittest test_load_metadata.py
python -m unittest test_name_to_class.py

# Indicators
python -m unittest test_indicator_ghspop.py
python -m unittest test_indicator_last_edit_2.py
python -m unittest test_indicator_poi_density_2.py

# Reports
python -m unittest test_report_remote_mapping_level_one.py
python -m unittest test_report_simple_report.py
python -m unittest test_report_sketchmap_fitness.py

# oqt.py
python -m unittest oqt.py
python -m unittest cli.py
