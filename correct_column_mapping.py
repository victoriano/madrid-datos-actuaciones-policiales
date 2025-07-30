#!/usr/bin/env python3
"""
Correct Column Mapping - Maps columns in their ORIGINAL order, not by activity
"""
# /// script
# dependencies = [
#   "pandas",
#   "openpyxl"
# ]
# ///

import pandas as pd

def create_correct_mapping():
    """Create correct mapping preserving original column order"""
    
    # Load the dataset
    df = pd.read_csv("madrid_datos_actuaciones_policiales.csv")
    
    # The correct mapping based on original column positions:
    # seguridad_incidentes_personas -> relacionadas_con_personas (this should be 2.0 for Arganzuela June 2025)
    # seguridad_incidentes_patrimonio -> relacionadas_con_patrimonio
    # etc.
    
    correct_mappings = {
        'seguridad_incidentes_personas': 'relacionadas_con_personas',
        'seguridad_incidentes_patrimonio': 'relacionadas_con_patrimonio', 
        'seguridad_incidentes_armas': 'por_tenencia_armas',
        'seguridad_tenencia_drogas': 'por_tenencia_drogas',
        'seguridad_consumo_drogas': 'por_consumo_drogas'
    }
    
    # Apply the correct renames
    df_renamed = df.rename(columns=correct_mappings)
    
    # Also rename other columns for clarity
    other_renames = {
        'personas_detenidas_total': 'personas_detenidas',
        'accidentes_trafico_con_victimas': 'accidentes_con_victimas',
        'accidentes_trafico_sin_victimas': 'accidentes_sin_victimas',
        'inspecciones_locales': 'inspecciones_locales_entretenimiento',
        'denuncias_locales_espectaculos': 'denuncias_locales_entretenimiento'
    }
    
    df_renamed = df_renamed.rename(columns=other_renames)
    
    # Convert fecha to proper datetime
    df_renamed['fecha'] = pd.to_datetime(df_renamed['fecha'])
    
    # Sort by date and district
    df_renamed = df_renamed.sort_values(['fecha', 'distrito'])
    
    # Fill NaN values with 0 for numeric columns
    numeric_cols = df_renamed.select_dtypes(include=['float64', 'int64']).columns
    df_renamed[numeric_cols] = df_renamed[numeric_cols].fillna(0)
    
    # Save the corrected dataset
    output_file = "madrid_datos_actuaciones_policiales.csv"
    df_renamed.to_csv(output_file, index=False)
    
    print("=== DATASET CORREGIDO CON MAPEO CORRECTO ===")
    print(f"Archivo: {output_file}")
    print(f"Dimensiones: {df_renamed.shape}")
    
    # VERIFICATION: Check Arganzuela June 2025
    print("\n=== VERIFICACIÓN CRÍTICA: Arganzuela Junio 2025 ===")
    arganzuela_june = df_renamed[
        (df_renamed['distrito'] == 'ARGANZUELA') & 
        (df_renamed['fecha'] == '2025-06-01')
    ]
    
    if len(arganzuela_june) > 0:
        key_cols = ['fecha', 'distrito', 'relacionadas_con_personas', 'relacionadas_con_patrimonio', 'por_tenencia_drogas']
        available_cols = [col for col in key_cols if col in df_renamed.columns]
        print(arganzuela_june[available_cols])
        
        relacionadas_personas_value = arganzuela_june['relacionadas_con_personas'].iloc[0]
        print(f"\n🎯 VALOR CRÍTICO: relacionadas_con_personas = {relacionadas_personas_value}")
        
        if relacionadas_personas_value == 2.0:
            print("✅ CORRECTO! El valor es 2.0 como esperado")
        else:
            print(f"❌ ERROR! Esperado 2.0, obtenido {relacionadas_personas_value}")
    else:
        print("❌ No se encontró data para Arganzuela Junio 2025")
    
    return df_renamed

if __name__ == "__main__":
    df = create_correct_mapping()