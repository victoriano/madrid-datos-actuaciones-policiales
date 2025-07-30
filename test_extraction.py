#!/usr/bin/env python3
"""
Test the exact extraction logic that's failing
"""
import pandas as pd
import re

def _is_numeric_value(value):
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

def _clean_header_name(header):
    header = str(header).lower().strip()
    
    mappings = {
        'relacionadas con las personas': 'incidentes_personas',
        'relacionadas con el patrimonio': 'incidentes_patrimonio',
        'por tenencia de armas': 'incidentes_armas',
        'por tenencia de drogas': 'tenencia_drogas',
        'por consumo de drogas': 'consumo_drogas'
    }
    
    for original, clean in mappings.items():
        if original in header:
            return clean
    
    clean = re.sub(r'[^a-z0-9]', '_', header)
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean

# Load the Excel file
file_path = '/Users/victoriano/madrid_historical_data/policia-estadisticas-138.xlsx'
df = pd.read_excel(file_path, sheet_name='SEGURIDAD')

# Find header row
header_row = None
for i, row in df.iterrows():
    if 'DISTRITOS' in str(row.iloc[0]).upper():
        header_row = i
        break

print(f"Header row found at: {header_row}")

if header_row is not None and header_row + 1 < len(df):
    headers = df.iloc[header_row + 1].fillna('').astype(str) 
    print(f"Headers: {list(headers)}")
    
    # Process Arganzuela row (which we know is at row 3)
    arganzuela_row = df.iloc[3]  # We know it's at row 3
    district_name = str(arganzuela_row.iloc[0]).strip()
    print(f"Processing district: {district_name}")
    
    district_data = {}
    
    # Test the mapping logic
    for j, header in enumerate(headers[1:], 1):
        if j < len(arganzuela_row) and header and header != 'nan':
            value = arganzuela_row.iloc[j]
            print(f"\nColumn {j}:")
            print(f"  Header: {repr(header)}")
            print(f"  Value: {value} (type: {type(value)})")
            print(f"  pd.notna(value): {pd.notna(value)}")
            print(f"  _is_numeric_value(value): {_is_numeric_value(value)}")
            
            if pd.notna(value) and _is_numeric_value(value):
                clean_header = _clean_header_name(header)
                final_key = f'seguridad_{clean_header}'
                final_value = float(value)
                district_data[final_key] = final_value
                print(f"  ✅ EXTRACTED: {final_key} = {final_value}")
            else:
                print(f"  ❌ SKIPPED")
    
    print(f"\nFinal district_data for Arganzuela: {district_data}")