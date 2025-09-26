#!/usr/bin/env python3
"""
Main entry point for Genesys Learning Content Extractor
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from universal_genesys_extractor import UniversalGenesysExtractor

def main():
    """Main execution function"""
    print("=== Genesys Learning Content Extractor v2.1.0 ===")
    print("Universal extraction system with organized structure")

    # Initialize extractor with config from root directory
    config_path = Path(__file__).parent / "config.json"
    extractor = UniversalGenesysExtractor(str(config_path))

    # For now, just extract e-learning (existing data)
    # In the future, add 'webinars', 'self-study' when lists are provided
    content_types = ['e-learning']

    results = extractor.run_extraction(content_types)

    print(f"\n🎉 Extraction complete!")
    print(f"Check data/output/current/ for results")

    return results

if __name__ == "__main__":
    main()