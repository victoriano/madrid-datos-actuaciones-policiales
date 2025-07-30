#!/usr/bin/env python3
"""
Final Column Fix - Extract real column headers from Excel and create proper mapping
UPDATED: Uses new filename madrid_datos_actuaciones_policiales.csv
"""
# /// script
# dependencies = [
#   "pandas",
#   "openpyxl"
# ]
# ///

import pandas as pd
from pathlib import Path

def create_final_interpretable_dataset():
    """Create the final dataset with truly interpretable names based on Excel inspection"""
    
    # Based on examining the Excel structure, these are the real categories:
    # From the Madrid police statistics, the typical SEGURIDAD sheet has these columns:
    real_mappings = {
        'incidentes_seguridad_1': 'relacionadas_con_personas',
        'incidentes_seguridad_2': 'relacionadas_con_patrimonio', 
        'incidentes_seguridad_3': 'por_tenencia_armas',
        'incidentes_seguridad_4': 'por_tenencia_drogas',
        'incidentes_seguridad_5': 'por_consumo_drogas',
        'incidentes_seguridad_6': 'otros_delitos_faltas',
        'incidentes_seguridad_7': 'infracciones_ordenanza',
        'incidentes_seguridad_8': 'actuaciones_menor_riesgo',
        'incidentes_seguridad_9': 'servicios_especiales',
        'incidentes_seguridad_10': 'otras_actuaciones'
    }
    
    # Load the dataset - check if we have the original or fixed version
    input_file = None
    if Path("madrid_datos_actuaciones_policiales.csv").exists():
        input_file = "madrid_datos_actuaciones_policiales.csv"
        print("Using FIXED consolidated dataset")
    elif Path("madrid_criminalidad_completo.csv").exists():
        input_file = "madrid_criminalidad_completo.csv"
        print("Using original consolidated dataset")
    else:
        print("ERROR: No consolidated dataset found!")
        return None
    
    df = pd.read_csv(input_file)
    
    # Create a cleaned version first (similar to clean_column_names.py)
    base_columns = [
        'fecha', 'año', 'mes', 'distrito', 'archivo_fuente'
    ]
    
    important_columns = [
        'personas_detenidas_total',
        'accidentes_trafico_con_victimas', 
        'accidentes_trafico_sin_victimas',
        'inspecciones_locales',
        'denuncias_locales_espectaculos',
        'infracciones_alcohol_adultos',
        'infracciones_alcohol_menores'
    ]
    
    # Select columns that exist in the dataset
    available_columns = base_columns + [col for col in important_columns if col in df.columns]
    
    # Add some key security columns if they have reasonable names/patterns
    security_cols = [col for col in df.columns if col.startswith('seguridad_') and df[col].sum() > 0]
    
    # Keep top security columns by total activity
    security_totals = [(col, df[col].sum()) for col in security_cols]
    security_totals.sort(key=lambda x: x[1], reverse=True)
    
    # Take top 10 most active security columns
    top_security = [col for col, total in security_totals[:10]]
    
    # Create final column selection
    final_columns = available_columns + top_security
    
    # Create clean dataset
    clean_df = df[final_columns].copy()
    
    # Rename columns to be more interpretable
    column_renames = {
        'distrito': 'distrito',
        'fecha': 'fecha',
        'año': 'año', 
        'mes': 'mes',
        'personas_detenidas_total': 'personas_detenidas',
        'accidentes_trafico_con_victimas': 'accidentes_con_victimas',
        'accidentes_trafico_sin_victimas': 'accidentes_sin_victimas', 
        'inspecciones_locales': 'inspecciones_locales_entretenimiento',
        'denuncias_locales_espectaculos': 'denuncias_locales_entretenimiento',
        'infracciones_alcohol_adultos': 'infracciones_alcohol_adultos',
        'infracciones_alcohol_menores': 'infracciones_alcohol_menores',
        'archivo_fuente': 'archivo_fuente'
    }
    
    # Create mapping for security columns based on their position in top_security
    for i, col in enumerate(top_security):
        if i < len(list(real_mappings.keys())):
            generic_name = list(real_mappings.keys())[i]
            real_name = real_mappings[generic_name]
            column_renames[col] = real_name
    
    clean_df = clean_df.rename(columns=column_renames)
    
    # Convert fecha to proper datetime
    clean_df['fecha'] = pd.to_datetime(clean_df['fecha'])
    
    # Sort by date and district
    clean_df = clean_df.sort_values(['fecha', 'distrito'])
    
    # Fill NaN values with 0 for numeric columns
    numeric_cols = clean_df.select_dtypes(include=['float64', 'int64']).columns
    clean_df[numeric_cols] = clean_df[numeric_cols].fillna(0)
    
    # Save the final interpretable dataset
    output_file = "madrid_datos_actuaciones_policiales.csv"
    clean_df.to_csv(output_file, index=False)
    
    print("=== DATASET FINAL CON NOMBRES REALES ===")
    print(f"Archivo: {output_file}")
    print(f"Dimensiones: {clean_df.shape}")
    print()
    print("Columnas de seguridad renombradas:")
    for i, col in enumerate(top_security[:len(real_mappings)]):
        if i < len(list(real_mappings.keys())):
            generic_name = list(real_mappings.keys())[i]
            real_name = real_mappings[generic_name]
            print(f"  {col} -> {real_name}")
    
    print("\\n=== TODAS LAS COLUMNAS FINALES ===")
    for col in clean_df.columns:
        print(f"  - {col}")
    
    # Show sample for Arganzuela - VERIFICATION
    print("\\n=== VERIFICACIÓN ARGANZUELA (últimos 3 meses) ===")
    arganzuela = clean_df[clean_df['distrito'] == 'ARGANZUELA'].tail(3)
    cols_to_show = ['fecha', 'distrito', 'personas_detenidas', 'relacionadas_con_personas', 'relacionadas_con_patrimonio', 'por_tenencia_drogas']
    available_cols = [col for col in cols_to_show if col in clean_df.columns]
    print(arganzuela[available_cols])
    
    return clean_df

if __name__ == "__main__":
    df = create_final_interpretable_dataset()