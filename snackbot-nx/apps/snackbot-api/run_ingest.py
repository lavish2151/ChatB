#!/usr/bin/env python
"""Helper script to run ingestion from the correct directory."""
import sys
import os

# Add the current directory to Python path so 'app' module can be found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from scripts.ingest_gdocs import main
    main()
