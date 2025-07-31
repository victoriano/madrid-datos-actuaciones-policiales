#!/usr/bin/env python3
"""
Madrid Police Data Processor
Complete pipeline: Downloads Excel files from Madrid portal and creates final CSV dataset
"""
# /// script
# dependencies = [
#   "requests",
#   "pandas",
#   "openpyxl",
#   "beautifulsoup4"
# ]
# ///

import requests
import pandas as pd
from pathlib import Path
import logging
import time
from datetime import datetime, timedelta
import re
from bs4 import BeautifulSoup
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MadridDataProcessor:
    def __init__(self, data_dir="madrid_historical_data"):
        self.base_url = "https://datos.madrid.es"
        self.catalog_url = "https://datos.madrid.es/sites/v/index.jsp?vgnextoid=bffff1d2a9fdb410VgnVCM2000000c205a0aRCRD&vgnextchannel=20d612b9ace9f310VgnVCM100000171f5a0aRCRD"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    def download_historical_data(self):
        """Download all historical Excel files from Madrid portal"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(self.catalog_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links that contain "policia-estadisticas"
            download_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'policia-estadisticas' in href and '.xlsx' in href:
                    if href.startswith('http'):
                        download_links.append(href)
                    else:
                        download_links.append(self.base_url + href)
            
            logger.info(f"Found {len(download_links)} historical files to download")
            
            # Download each file
            downloaded_count = 0
            for i, url in enumerate(download_links):
                try:
                    # Extract filename from URL
                    filename = url.split('/')[-1]
                    if not filename.endswith('.xlsx'):
                        filename = f"policia-estadisticas-{i}.xlsx"
                    
                    file_path = self.data_dir / filename
                    
                    # Skip if already exists
                    if file_path.exists():
                        logger.debug(f"Skipping {filename} (already exists)")
                        continue
                    
                    # Download file
                    logger.info(f"Downloading {filename}...")
                    file_response = requests.get(url, headers=headers, timeout=30)
                    file_response.raise_for_status()
                    
                    with open(file_path, 'wb') as f:
                        f.write(file_response.content)
                    
                    downloaded_count += 1
                    time.sleep(1)  # Be nice to the server
                    
                except Exception as e:
                    logger.warning(f"Failed to download {url}: {e}")
                    continue
            
            logger.info(f"Downloaded {downloaded_count} new files")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading historical data: {e}")
            return False
    
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
    
    def _is_numeric_value(self, value):
        """Check if a value can be converted to a number"""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
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
    
    def _extract_security_data(self, xl, file_path):
        """Extract security data for all districts"""
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
                        
                        # Map columns to descriptive names
                        for j, header in enumerate(headers[1:], 1):
                            if j < len(row) and header and header != 'nan':
                                value = row.iloc[j]
                                
                                if pd.notna(value) and self._is_numeric_value(value):
                                    clean_header = self._clean_header_name(header)
                                    district_data[f'seguridad_{clean_header}'] = float(value)
                        
                        if district_data:
                            districts_data[district_name] = district_data
        
        except Exception as e:
            logger.debug(f"Error extracting security data: {e}")
        
        return districts_data
    
    def _extract_other_data(self, xl, file_path):
        """Extract data from other sheets (detained, accidents, etc.)"""
        districts_data = {}
        
        # Detained persons
        if 'PERS. DETENIDAS X DISTRITOS' in xl.sheet_names:
            try:
                df = pd.read_excel(file_path, sheet_name='PERS. DETENIDAS X DISTRITOS')
                for i, row in df.iterrows():
                    district_name = str(row.iloc[0]).strip()
                    if (district_name and district_name != 'nan' and 
                        'DISTRITO' not in district_name.upper() and 
                        'TOTAL' not in district_name.upper() and
                        len(district_name) > 2):
                        
                        detained_count = row.iloc[1]
                        if pd.notna(detained_count) and self._is_numeric_value(detained_count):
                            if district_name not in districts_data:
                                districts_data[district_name] = {}
                            districts_data[district_name]['personas_detenidas'] = float(detained_count)
            except Exception as e:
                logger.debug(f"Error extracting detained data: {e}")
        
        # Traffic accidents
        if 'ACCIDENTES' in xl.sheet_names:
            try:
                df = pd.read_excel(file_path, sheet_name='ACCIDENTES')
                for i, row in df.iterrows():
                    district_name = str(row.iloc[0]).strip()
                    if (district_name and district_name != 'nan' and 
                        'DISTRITO' not in district_name.upper() and 
                        'TOTAL' not in district_name.upper() and
                        len(district_name) > 2):
                        
                        if district_name not in districts_data:
                            districts_data[district_name] = {}
                        
                        if len(row) > 1:
                            con_victimas = row.iloc[1]
                            if pd.notna(con_victimas) and self._is_numeric_value(con_victimas):
                                districts_data[district_name]['accidentes_con_victimas'] = float(con_victimas)
                        
                        if len(row) > 2:
                            sin_victimas = row.iloc[2]
                            if pd.notna(sin_victimas) and self._is_numeric_value(sin_victimas):
                                districts_data[district_name]['accidentes_sin_victimas'] = float(sin_victimas)
            except Exception as e:
                logger.debug(f"Error extracting accidents data: {e}")
        
        # Alcohol infractions
        if 'CONSUMO ALCOHOL' in xl.sheet_names:
            try:
                df = pd.read_excel(file_path, sheet_name='CONSUMO ALCOHOL')
                for i, row in df.iterrows():
                    district_name = str(row.iloc[0]).strip()
                    if (district_name and district_name != 'nan' and 
                        'DISTRITO' not in district_name.upper() and 
                        'TOTAL' not in district_name.upper() and
                        len(district_name) > 2):
                        
                        if district_name not in districts_data:
                            districts_data[district_name] = {}
                        
                        if len(row) > 1:
                            adultos = row.iloc[1]
                            if pd.notna(adultos) and self._is_numeric_value(adultos):
                                districts_data[district_name]['infracciones_alcohol_adultos'] = float(adultos)
                        
                        if len(row) > 2:
                            menores = row.iloc[2]
                            if pd.notna(menores) and self._is_numeric_value(menores):
                                districts_data[district_name]['infracciones_alcohol_menores'] = float(menores)
            except Exception as e:
                logger.debug(f"Error extracting alcohol data: {e}")
        
        return districts_data
    
    def process_excel_files(self):
        """Process all Excel files and create final CSV dataset"""
        files = list(self.data_dir.glob("*.xlsx"))
        if not files:
            logger.error("No Excel files found. Run download_historical_data() first.")
            return None
        
        # Estimate dates for files
        file_dates = self.estimate_dates_from_files(files)
        
        all_data = []
        
        for file_path, estimated_date in file_dates:
            logger.info(f"Processing {file_path.name} -> {estimated_date.strftime('%Y-%m-%d')}")
            
            try:
                xl = pd.ExcelFile(file_path)
                
                # Extract security data
                security_data = self._extract_security_data(xl, file_path)
                
                # Extract other data
                other_data = self._extract_other_data(xl, file_path)
                
                # Merge all data for each district
                all_districts = set(security_data.keys()) | set(other_data.keys())
                
                for district in all_districts:
                    district_record = {
                        'fecha': estimated_date.strftime('%Y-%m-%d'),
                        'año': estimated_date.year,
                        'mes': estimated_date.month,
                        'distrito': district,
                        'archivo_fuente': file_path.name
                    }
                    
                    # Add security data
                    if district in security_data:
                        district_record.update(security_data[district])
                    
                    # Add other data
                    if district in other_data:
                        district_record.update(other_data[district])
                    
                    all_data.append(district_record)
                
            except Exception as e:
                logger.warning(f"Error processing {file_path.name}: {e}")
                continue
        
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
        
        # Apply final column mapping to make names interpretable
        column_mappings = {
            'seguridad_incidentes_personas': 'relacionadas_con_personas',
            'seguridad_incidentes_patrimonio': 'relacionadas_con_patrimonio',
            'seguridad_incidentes_armas': 'por_tenencia_armas',
            'seguridad_tenencia_drogas': 'por_tenencia_drogas',
            'seguridad_consumo_drogas': 'por_consumo_drogas'
        }
        
        df = df.rename(columns=column_mappings)
        
        # Save the final dataset
        output_file = "madrid_datos_actuaciones_policiales.csv"
        df.to_csv(output_file, index=False)
        
        logger.info(f"Final dataset saved: {output_file}")
        logger.info(f"Shape: {df.shape}")
        logger.info(f"Date range: {df['fecha'].min()} to {df['fecha'].max()}")
        logger.info(f"Districts: {df['distrito'].nunique()}")
        
        return df
    
    def run_complete_pipeline(self):
        """Run the complete pipeline: download + process"""
        logger.info("Starting Madrid police data processing pipeline...")
        
        # Step 1: Download historical data
        logger.info("Step 1: Downloading historical data...")
        if not self.download_historical_data():
            logger.error("Failed to download data")
            return False
        
        # Step 2: Process Excel files
        logger.info("Step 2: Processing Excel files...")
        df = self.process_excel_files()
        
        if df is not None:
            logger.info("✅ Pipeline completed successfully!")
            logger.info(f"📊 Final dataset: madrid_datos_actuaciones_policiales.csv")
            logger.info(f"📊 {len(df)} rows, {len(df.columns)} columns")
            return True
        else:
            logger.error("❌ Pipeline failed")
            return False

def main():
    processor = MadridDataProcessor()
    processor.run_complete_pipeline()

if __name__ == "__main__":
    main()