#!/usr/bin/env python3
"""
Final Correct Mapping - Maps the right columns with the verified values
"""
# /// script
# dependencies = [
#   "pandas"
# ]
# ///

import pandas as pd

def apply_final_correct_mapping():
    """Apply the final correct mapping based on verified positions"""
    
    # Load the dataset with original column names
    df = pd.read_csv("madrid_datos_actuaciones_policiales.csv")
    
    # The CORRECT mapping based on verified positions:
    correct_mappings = {
        'seguridad_incidentes_personas': 'relacionadas_con_personas',  # This has 2.0 for Arganzuela June 2025 ✅
        'seguridad_incidentes_patrimonio': 'relacionadas_con_patrimonio', 
        'seguridad_incidentes_armas': 'por_tenencia_armas',
        'seguridad_tenencia_drogas': 'por_tenencia_drogas',
        'seguridad_consumo_drogas': 'por_consumo_drogas',
        'personas_detenidas_total': 'personas_detenidas',
        'accidentes_trafico_con_victimas': 'accidentes_con_victimas',
        'accidentes_trafico_sin_victimas': 'accidentes_sin_victimas',
        'inspecciones_locales': 'inspecciones_locales_entretenimiento',
        'denuncias_locales_espectaculos': 'denuncias_locales_entretenimiento'
    }
    
    # Apply the correct renames
    df_final = df.rename(columns=correct_mappings)
    
    # Convert fecha to proper datetime
    df_final['fecha'] = pd.to_datetime(df_final['fecha'])
    
    # Sort by date and district
    df_final = df_final.sort_values(['fecha', 'distrito'])
    
    # Fill NaN values with 0 for numeric columns
    numeric_cols = df_final.select_dtypes(include=['float64', 'int64']).columns
    df_final[numeric_cols] = df_final[numeric_cols].fillna(0)
    
    # Save the final corrected dataset
    output_file = "madrid_datos_actuaciones_policiales.csv"
    df_final.to_csv(output_file, index=False)
    
    print("=== DATASET FINAL CORREGIDO ===")
    print(f"Archivo: {output_file}")
    print(f"Dimensiones: {df_final.shape}")
    
    # CRITICAL VERIFICATION
    print("\n=== VERIFICACIÓN CRÍTICA FINAL ===")
    arganzuela_june = df_final[
        (df_final['distrito'] == 'ARGANZUELA') & 
        (df_final['fecha'] == '2025-06-01')
    ]
    
    if len(arganzuela_june) > 0:
        key_cols = ['fecha', 'distrito', 'relacionadas_con_personas', 'relacionadas_con_patrimonio']
        print(arganzuela_june[key_cols])
        
        relacionadas_personas_value = arganzuela_june['relacionadas_con_personas'].iloc[0]
        print(f"\n🎯 VALOR FINAL: relacionadas_con_personas = {relacionadas_personas_value}")
        
        if relacionadas_personas_value == 2.0:
            print("✅ ¡ÉXITO! El valor es 2.0 como esperado del Excel original")
        else:
            print(f"❌ ERROR! Esperado 2.0, obtenido {relacionadas_personas_value}")
    
    print(f"\n📋 Columnas finales: {list(df_final.columns)}")
    
    return df_final

if __name__ == "__main__":
    df = apply_final_correct_mapping()