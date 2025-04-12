#!/bin/bash

set -e  # Exit immediately if a command fails
set -o pipefail

echo "🔄 Generating bot/config.py from config.yml..."
python yml_to_py.py config.yml bot/config.py

echo "🚀 Running bot..."
python -m bot.bot