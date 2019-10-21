#!/bin/bash
python3 -m flask run --host=0.0.0.0 --port=3001 &
python3 REST.py &
