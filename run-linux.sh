#!/bin/bash

docker build -t phishing-prevention-proxy .
docker run --rm -p 8080:8080 phishing-prevention-proxy
