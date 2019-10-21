#!/bin/bash
python3 -m flask run --host=0.0.0.0 --port=8080 &
python3 REST.py &
