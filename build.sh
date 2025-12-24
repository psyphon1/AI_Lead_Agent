#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# This part is handled by the Render Chrome Buildpack, 
# but ensuring dependencies are clean:
pip install gunicorn