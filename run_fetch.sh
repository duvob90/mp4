#!/bin/sh
set -e
cd "$(dirname "$0")"
exec /usr/bin/env python fetch_licitaciones.py
