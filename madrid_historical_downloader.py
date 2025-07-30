#!/usr/bin/env python3
"""
Madrid Historical Police Data Downloader
Downloads historical monthly Excel files and creates consolidated dataset
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MadridHistoricalDownloader:
    def __init__(self):
        self.base_url = "https://datos.madrid.es"
        self.catalog_url = "https://datos.madrid.es/sites/v/index.jsp?vgnextoid=bffff1d2a9fdb410VgnVCM2000000c205a0aRCRD&vgnextchannel=20d612b9ace9f310VgnVCM100000171f5a0aRCRD"
        self.data_dir = Path("madrid_historical_data")
        self.data_dir.mkdir(exist_ok=True)
        
    def get_download_links(self):
        """Scrape the page to find all historical download links"""
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
                    if href.startswith('/'):
                        full_url = self.base_url + href
                    else:
                        full_url = href
                    
                    # Extract date info from link text or context
                    link_text = link.get_text(strip=True)
                    download_links.append({
                        'url': full_url,
                        'text': link_text,
                        'href': href
                    })
            
            logger.info(f"Found {len(download_links)} potential download links")
            return download_links
            
        except Exception as e:
            logger.error(f"Error scraping download links: {e}")
            return []
    
    def generate_systematic_urls(self):
        """Generate systematic URLs based on known patterns"""
        urls = []
        
        # Try different URL patterns based on the known working one
        base_patterns = [
            "https://datos.madrid.es/egob/catalogo/212616-{}-policia-estadisticas.xlsx"
        ]
        
        # Try different file numbers (observed pattern from examples)
        file_numbers = range(1, 200)  # Covering a wide range
        
        for pattern in base_patterns:
            for num in file_numbers:
                url = pattern.format(num)
                urls.append({
                    'url': url,
                    'file_number': num,
                    'filename': f"policia-estadisticas-{num}.xlsx"
                })
        
        return urls
    
    def download_file(self, url, filename):
        """Download a single file"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Check if it's actually an Excel file
            if len(response.content) < 1000 or b'<html' in response.content[:1000].lower():
                return False
            
            filepath = self.data_dir / filename
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded: {filename} ({len(response.content)} bytes)")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.debug(f"Failed to download {url}: {e}")
            return False
    
    def download_all_files(self):
        """Download all available historical files"""
        # Try systematic approach first
        urls = self.generate_systematic_urls()
        successful_downloads = []
        
        for i, url_info in enumerate(urls):
            if i % 10 == 0:
                logger.info(f"Progress: {i}/{len(urls)} URLs checked")
            
            if self.download_file(url_info['url'], url_info['filename']):
                successful_downloads.append(url_info)
            
            # Be respectful to the server
            time.sleep(0.5)
        
        logger.info(f"Successfully downloaded {len(successful_downloads)} files")
        return successful_downloads
    
    def analyze_downloaded_files(self):
        """Analyze structure of downloaded files"""
        files = list(self.data_dir.glob("*.xlsx"))
        logger.info(f"Analyzing {len(files)} downloaded files")
        
        valid_files = []
        for file_path in files:
            try:
                xl = pd.ExcelFile(file_path)
                if 'SEGURIDAD' in xl.sheet_names or 'PERS. DETENIDAS X DISTRITOS' in xl.sheet_names:
                    valid_files.append(file_path)
                    logger.info(f"Valid file: {file_path.name} - Sheets: {xl.sheet_names}")
                else:
                    logger.debug(f"Invalid structure: {file_path.name}")
            except Exception as e:
                logger.debug(f"Error reading {file_path.name}: {e}")
                file_path.unlink()  # Remove invalid files
        
        return valid_files
    
    def consolidate_historical_data(self, valid_files):
        """Consolidate all historical data into a single dataset"""
        if not valid_files:
            logger.error("No valid files to consolidate")
            return None
        
        all_data = []
        
        for file_path in valid_files:
            try:
                # Extract potential date from filename
                file_num = re.search(r'(\d+)', file_path.name)
                file_id = file_num.group(1) if file_num else "unknown"
                
                # Read key sheets
                xl = pd.ExcelFile(file_path)
                
                monthly_data = {'file_id': file_id, 'filename': file_path.name}
                
                # Extract Arganzuela data from each relevant sheet
                for sheet_name in ['SEGURIDAD', 'PERS. DETENIDAS X DISTRITOS', 'ACCIDENTES', 'LOCALES']:
                    if sheet_name in xl.sheet_names:
                        df = pd.read_excel(file_path, sheet_name=sheet_name)
                        arganzuela_rows = df[df.iloc[:, 0].astype(str).str.contains('ARGANZUELA', na=False, case=False)]
                        
                        if not arganzuela_rows.empty:
                            for col_idx, value in enumerate(arganzuela_rows.iloc[0]):
                                if pd.notna(value) and str(value) != 'ARGANZUELA':
                                    monthly_data[f'{sheet_name}_col_{col_idx}'] = value
                
                all_data.append(monthly_data)
                logger.info(f"Processed: {file_path.name}")
                
            except Exception as e:
                logger.error(f"Error processing {file_path.name}: {e}")
        
        # Create consolidated DataFrame
        consolidated_df = pd.DataFrame(all_data)
        
        # Sort by file_id (approximate chronological order)
        consolidated_df = consolidated_df.sort_values('file_id')
        
        # Save consolidated data
        output_file = "arganzuela_historical_trends.csv"
        consolidated_df.to_csv(output_file, index=False)
        logger.info(f"Saved consolidated data to {output_file}")
        
        return consolidated_df

def main():
    downloader = MadridHistoricalDownloader()
    
    # Download all available files
    logger.info("Starting historical data download...")
    successful_downloads = downloader.download_all_files()
    
    # Analyze and validate files
    valid_files = downloader.analyze_downloaded_files()
    
    # Consolidate into single dataset
    if valid_files:
        consolidated_data = downloader.consolidate_historical_data(valid_files)
        
        print(f"\n=== RESUMEN DE DESCARGA ===")
        print(f"Archivos válidos encontrados: {len(valid_files)}")
        print(f"Datos consolidados guardados en: arganzuela_historical_trends.csv")
        
        if consolidated_data is not None:
            print(f"Períodos de datos: {len(consolidated_data)} archivos")
            print("\nPrimeros registros:")
            print(consolidated_data.head())
    else:
        print("No se encontraron archivos válidos con datos históricos")

if __name__ == "__main__":
    main()