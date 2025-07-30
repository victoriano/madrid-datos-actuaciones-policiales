#!/usr/bin/env python3
"""
Detailed trace of the data extraction bug
"""
# /// script
# dependencies = [
#   "pandas",
#   "openpyxl"
# ]
# ///

import pandas as pd
from pathlib import Path

def trace_extraction_bug():
    """Trace exactly what happens during data extraction"""
    
    # Read the June 2025 file directly
    file_path = Path("/Users/victoriano/madrid_historical_data/policia-estadisticas-138.xlsx")
    
    print("=== TRACING DATA EXTRACTION BUG ===")
    print(f"File: {file_path}")
    
    # Read SEGURIDAD sheet
    df = pd.read_excel(file_path, sheet_name='SEGURIDAD')
    print(f"\nSheet shape: {df.shape}")
    
    # Find header row
    header_row = None
    for i, row in df.iterrows():
        if 'DISTRITOS' in str(row.iloc[0]).upper():
            header_row = i
            print(f"Found DISTRITOS header at row: {header_row}")
            break
    
    if header_row is not None:
        # Get headers from next row
        headers = df.iloc[header_row + 1].fillna('').astype(str)
        print(f"\nHeaders: {list(headers)}")
        
        # Find Arganzuela row
        for i in range(header_row + 2, len(df)):
            row = df.iloc[i]
            district_name = str(row.iloc[0]).strip()
            
            if 'ARGANZUELA' in district_name.upper():
                print(f"\nFound Arganzuela at row {i}: {district_name}")
                print(f"Raw row data: {list(row)}")
                
                # Show the validation process
                for j, header in enumerate(headers[1:], 1):
                    if j < len(row) and header and header != 'nan':
                        value = row.iloc[j]
                        print(f"\nColumn {j} - Header: '{header}'")
                        print(f"  Raw value: {value} (type: {type(value)})")
                        print(f"  pd.notna(value): {pd.notna(value)}")
                        
                        # Test old validation
                        old_valid = pd.notna(value) and str(value).replace('.', '').replace('-', '').replace(' ', '').isdigit()
                        print(f"  Old validation (str...isdigit): {old_valid}")
                        
                        # Test new validation
                        def is_numeric_value(val):
                            try:
                                float(val)
                                return True
                            except (ValueError, TypeError):
                                return False
                        
                        new_valid = pd.notna(value) and is_numeric_value(value)
                        print(f"  New validation (float): {new_valid}")
                        
                        if new_valid:
                            print(f"  ✅ Would extract: {float(value)}")
                        else:
                            print(f"  ❌ Would skip")
                
                break

if __name__ == "__main__":
    trace_extraction_bug()