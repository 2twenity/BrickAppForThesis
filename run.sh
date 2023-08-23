#!/bin/bash

echo 'This script will build and run docker container'

docker build -t stream_app2 .

docker run -p 8501:8501 --rm --name your_application stream_app2