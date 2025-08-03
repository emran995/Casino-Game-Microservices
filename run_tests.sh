#!/bin/bash
pip install -r requirements.txt
pytest -v --maxfail=1 --tb=short
