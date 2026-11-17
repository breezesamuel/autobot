#!/bin/bash
export PATH=/root/.local/bin:$PATH
cd /opt/WeMediaCrawler
uv run python main.py --help 2>&1 | /usr/bin/head -30
echo "---"
/root/.local/bin/uv python list 2>&1 | /usr/bin/head -10