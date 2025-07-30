#!/usr/bin/env python3
"""
Madrid Final Dataset Creator - FIXED VERSION
Creates a clean, interpretable CSV with all districts, proper dates, and descriptive column names
FIXES: Data extraction bug + changes output filename
"""
# /// script
# dependencies = [
#   "pandas",
#   "openpyxl",
#   "datetime"
# ]
# ///

import pandas as pd
from pathlib import Path
import logging
from datetime import datetime, timedelta
import re
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MadridFinalDatasetCreatorFixed:
    def __init__(self, data_dir="/Users/victoriano/madrid_historical_data"):
        self.data_dir = Path(data_dir)
        
    def estimate_dates_from_files(self, files):
        """Estimate actual dates based on file numbers and chronological order"""
        # Sort files by number
        sorted_files = sorted(files, key=lambda x: int(re.search(r'(\d+)', x.name).group(1)))
        
        # Start from a reasonable date (going backwards from most recent)
        # Assuming file 138 is June 2025 (most recent known)
        end_date = datetime(2025, 6, 1)
        
        dates = []
        for i, file_path in enumerate(reversed(sorted_files)):
            # Go backwards month by month
            estimated_date = end_date - timedelta(days=30 * i)
            dates.append((file_path, estimated_date))
        
        # Reverse to get chronological order
        return list(reversed(dates))
    
    def extract_all_districts_from_file(self, file_path, estimated_date):
        """Extract data for ALL districts from a single file"""
        try:
            xl = pd.ExcelFile(file_path)
            all_district_data = []
            
            # Get all districts from the main sheets
            districts_data = self._get_districts_data(xl, file_path)
            
            for district, data in districts_data.items():
                district_record = {
                    'fecha': estimated_date.strftime('%Y-%m-%d'),
                    'año': estimated_date.year,
                    'mes': estimated_date.month,
                    'distrito': district,
                    'archivo_fuente': file_path.name
                }
                district_record.update(data)
                all_district_data.append(district_record)
            
            return all_district_data
            
        except Exception as e:
            logger.warning(f"Error processing {file_path.name}: {e}")
            return []
    
    def _get_districts_data(self, xl, file_path):
        """Extract data for all districts from key sheets"""
        districts_data = {}
        
        # Security data
        if 'SEGURIDAD' in xl.sheet_names:
            security_data = self._extract_security_data_fixed(xl, file_path)
            for district, data in security_data.items():
                if district not in districts_data:
                    districts_data[district] = {}
                districts_data[district].update(data)
        
        # Detained persons
        if 'PERS. DETENIDAS X DISTRITOS' in xl.sheet_names:
            detained_data = self._extract_detained_data(xl, file_path)
            for district, data in detained_data.items():
                if district not in districts_data:
                    districts_data[district] = {}
                districts_data[district].update(data)
        
        # Traffic accidents
        if 'ACCIDENTES' in xl.sheet_names:
            accidents_data = self._extract_accidents_data(xl, file_path)
            for district, data in accidents_data.items():
                if district not in districts_data:
                    districts_data[district] = {}
                districts_data[district].update(data)
        
        # Local inspections
        if 'LOCALES' in xl.sheet_names:
            locals_data = self._extract_locals_data(xl, file_path)
            for district, data in locals_data.items():
                if district not in districts_data:
                    districts_data[district] = {}
                districts_data[district].update(data)
        
        # Alcohol consumption
        if 'CONSUMO ALCOHOL' in xl.sheet_names:
            alcohol_data = self._extract_alcohol_data(xl, file_path)
            for district, data in alcohol_data.items():
                if district not in districts_data:
                    districts_data[district] = {}
                districts_data[district].update(data)
        
        return districts_data
    
    def _extract_security_data_fixed(self, xl, file_path):
        """Extract security data for all districts - FIXED VERSION"""
        df = pd.read_excel(file_path, sheet_name='SEGURIDAD')
        districts_data = {}
        
        try:
            # Find header row
            header_row = None
            for i, row in df.iterrows():
                if 'DISTRITOS' in str(row.iloc[0]).upper():
                    header_row = i
                    break
            
            if header_row is not None:
                headers = df.iloc[header_row].fillna('').astype(str)
                
                # Process district rows  
                for i in range(header_row + 1, len(df)):
                    row = df.iloc[i]
                    district_name = str(row.iloc[0]).strip()
                    
                    if district_name and district_name != 'nan' and 'TOTAL' not in district_name.upper():
                        district_data = {}
                        
                        # Map columns to descriptive names - FIXED LOGIC
                        for j, header in enumerate(headers[1:], 1):
                            if j < len(row) and header and header != 'nan':
                                value = row.iloc[j]
                                
                                # FIXED: More flexible validation
                                if pd.notna(value) and self._is_numeric_value(value):
                                    clean_header = self._clean_header_name(header)
                                    district_data[f'seguridad_{clean_header}'] = float(value)
                        
                        if district_data:
                            districts_data[district_name] = district_data
        
        except Exception as e:
            logger.debug(f"Error extracting security data: {e}")
        
        return districts_data
    
    def _is_numeric_value(self, value):
        """Check if a value can be converted to a number - FIXED VERSION"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def _extract_detained_data(self, xl, file_path):
        """Extract detained persons data for all districts"""
        df = pd.read_excel(file_path, sheet_name='PERS. DETENIDAS X DISTRITOS')
        districts_data = {}
        
        try:
            # Find data rows (skip headers)
            for i, row in df.iterrows():
                district_name = str(row.iloc[0]).strip()
                if (district_name and district_name != 'nan' and 
                    'DISTRITO' not in district_name.upper() and 
                    'TOTAL' not in district_name.upper() and
                    len(district_name) > 2):
                    
                    detained_count = row.iloc[1]
                    if pd.notna(detained_count) and self._is_numeric_value(detained_count):
                        districts_data[district_name] = {
                            'personas_detenidas_total': float(detained_count)
                        }
        
        except Exception as e:
            logger.debug(f"Error extracting detained data: {e}")
        
        return districts_data
    
    def _extract_accidents_data(self, xl, file_path):
        """Extract traffic accidents data for all districts"""
        df = pd.read_excel(file_path, sheet_name='ACCIDENTES')
        districts_data = {}
        
        try:
            # Find data rows
            for i, row in df.iterrows():
                district_name = str(row.iloc[0]).strip()
                if (district_name and district_name != 'nan' and 
                    'DISTRITO' not in district_name.upper() and 
                    'TOTAL' not in district_name.upper() and
                    len(district_name) > 2):
                    
                    district_data = {}
                    
                    # Accidents with victims
                    if len(row) > 1:
                        con_victimas = row.iloc[1]
                        if pd.notna(con_victimas) and self._is_numeric_value(con_victimas):
                            district_data['accidentes_trafico_con_victimas'] = float(con_victimas)
                    
                    # Accidents without victims
                    if len(row) > 2:
                        sin_victimas = row.iloc[2]
                        if pd.notna(sin_victimas) and self._is_numeric_value(sin_victimas):
                            district_data['accidentes_trafico_sin_victimas'] = float(sin_victimas)
                    
                    if district_data:
                        districts_data[district_name] = district_data
        
        except Exception as e:
            logger.debug(f"Error extracting accidents data: {e}")
        
        return districts_data
    
    def _extract_locals_data(self, xl, file_path):
        """Extract local inspections data for all districts"""
        df = pd.read_excel(file_path, sheet_name='LOCALES')
        districts_data = {}
        
        try:
            for i, row in df.iterrows():
                district_name = str(row.iloc[0]).strip()
                if (district_name and district_name != 'nan' and 
                    'DISTRITO' not in district_name.upper() and 
                    'TOTAL' not in district_name.upper() and
                    len(district_name) > 2):
                    
                    district_data = {}
                    
                    # Inspections
                    if len(row) > 1:
                        inspecciones = row.iloc[1]
                        if pd.notna(inspecciones) and self._is_numeric_value(inspecciones):
                            district_data['inspecciones_locales'] = float(inspecciones)
                    
                    # Complaints/fines
                    if len(row) > 2:
                        denuncias = row.iloc[2]
                        if pd.notna(denuncias) and self._is_numeric_value(denuncias):
                            district_data['denuncias_locales_espectaculos'] = float(denuncias)
                    
                    if district_data:
                        districts_data[district_name] = district_data
        
        except Exception as e:
            logger.debug(f"Error extracting locals data: {e}")
        
        return districts_data
    
    def _extract_alcohol_data(self, xl, file_path):
        """Extract alcohol consumption data for all districts"""
        df = pd.read_excel(file_path, sheet_name='CONSUMO ALCOHOL')
        districts_data = {}
        
        try:
            for i, row in df.iterrows():
                district_name = str(row.iloc[0]).strip()
                if (district_name and district_name != 'nan' and 
                    'DISTRITO' not in district_name.upper() and 
                    'TOTAL' not in district_name.upper() and
                    len(district_name) > 2):
                    
                    district_data = {}
                    
                    # Adults
                    if len(row) > 1:
                        adultos = row.iloc[1]
                        if pd.notna(adultos) and self._is_numeric_value(adultos):
                            district_data['infracciones_alcohol_adultos'] = float(adultos)
                    
                    # Minors
                    if len(row) > 2:
                        menores = row.iloc[2]
                        if pd.notna(menores) and self._is_numeric_value(menores):
                            district_data['infracciones_alcohol_menores'] = float(menores)
                    
                    if district_data:
                        districts_data[district_name] = district_data
        
        except Exception as e:
            logger.debug(f"Error extracting alcohol data: {e}")
        
        return districts_data
    
    def _clean_header_name(self, header):
        """Clean and standardize header names"""
        header = str(header).lower().strip()
        
        # Common mappings
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
        
        # Default cleaning
        clean = re.sub(r'[^a-z0-9]', '_', header)
        clean = re.sub(r'_+', '_', clean).strip('_')
        return clean
    
    def create_final_dataset(self):
        """Create the final clean dataset - FIXED VERSION"""
        files = list(self.data_dir.glob("*.xlsx"))
        if not files:
            logger.error("No Excel files found")
            return None
        
        # Estimate dates for files
        file_dates = self.estimate_dates_from_files(files)
        
        all_data = []
        
        for file_path, estimated_date in file_dates:
            logger.info(f"Processing {file_path.name} -> {estimated_date.strftime('%Y-%m-%d')}")
            
            districts_data = self.extract_all_districts_from_file(file_path, estimated_date)
            all_data.extend(districts_data)
        
        if not all_data:
            logger.error("No data extracted")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Clean district names
        df['distrito'] = df['distrito'].str.strip().str.upper()
        
        # Sort by date and district
        df = df.sort_values(['fecha', 'distrito'])
        
        # Fill missing values with 0 for numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].fillna(0)
        
        # Save the final dataset - FIXED FILENAME
        output_file = "madrid_datos_actuaciones_policiales.csv"
        df.to_csv(output_file, index=False)
        
        logger.info(f"Final dataset saved: {output_file}")
        logger.info(f"Shape: {df.shape}")
        logger.info(f"Date range: {df['fecha'].min()} to {df['fecha'].max()}")
        logger.info(f"Districts: {df['distrito'].nunique()}")
        
        # Show sample
        print("\\n=== MUESTRA DEL DATASET FINAL CORREGIDO ===")
        print(df.head(10))
        print(f"\\nColumnas disponibles: {list(df.columns)}")
        print(f"\\nDistritos únicos: {sorted(df['distrito'].unique())}")
        
        return df

def main():
    creator = MadridFinalDatasetCreatorFixed()
    final_df = creator.create_final_dataset()
    
    if final_df is not None:
        print(f"\\n✅ Dataset final corregido: madrid_datos_actuaciones_policiales.csv")
        print(f"📊 {len(final_df)} filas, {len(final_df.columns)} columnas")
        print(f"📅 Rango: {final_df['fecha'].min()} - {final_df['fecha'].max()}")
        print(f"🏘️ {final_df['distrito'].nunique()} distritos")

if __name__ == "__main__":
    main()