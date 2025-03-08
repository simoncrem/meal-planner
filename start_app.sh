#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
# Get local IP address
ip=$(ipconfig getifaddr en0)
echo "App will be available at: http://$ip:3000"
flask run --host=0.0.0.0 --port 3000 