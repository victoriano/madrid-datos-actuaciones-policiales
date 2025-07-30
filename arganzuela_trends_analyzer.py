#!/usr/bin/env python3
"""
Arganzuela Trends Analyzer
Analyzes historical police data trends for Arganzuela district
"""
# /// script
# dependencies = [
#   "pandas",
#   "openpyxl",
#   "matplotlib",
#   "seaborn",
#   "numpy"
# ]
# ///

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArganzuelaTrendsAnalyzer:
    def __init__(self, data_dir="madrid_historical_data"):
        self.data_dir = Path(data_dir)
        self.consolidated_data = None
        
    def extract_arganzuela_trends(self):
        """Extract Arganzuela data from all historical files"""
        files = sorted(list(self.data_dir.glob("*.xlsx")), key=lambda x: int(re.search(r'(\d+)', x.name).group(1)))
        
        trends_data = []
        
        for i, file_path in enumerate(files):
            try:
                file_num = int(re.search(r'(\d+)', file_path.name).group(1))
                
                # Approximate date mapping (this is a guess - files seem chronological)
                # Later files likely represent more recent data
                approximate_period = f"Period_{file_num:03d}"
                
                xl = pd.ExcelFile(file_path)
                monthly_record = {
                    'period': approximate_period,
                    'file_number': file_num,
                    'filename': file_path.name
                }
                
                # Extract key crime indicators for Arganzuela
                crime_indicators = self._extract_crime_indicators(xl, file_path)
                monthly_record.update(crime_indicators)
                
                trends_data.append(monthly_record)
                
                if i % 10 == 0:
                    logger.info(f"Processed {i+1}/{len(files)} files")
                    
            except Exception as e:
                logger.warning(f"Error processing {file_path.name}: {e}")
        
        self.consolidated_data = pd.DataFrame(trends_data)
        return self.consolidated_data
    
    def _extract_crime_indicators(self, xl, file_path):
        """Extract key crime indicators for Arganzuela from a single file"""
        indicators = {}
        
        try:
            # Security incidents
            if 'SEGURIDAD' in xl.sheet_names:
                df = pd.read_excel(file_path, sheet_name='SEGURIDAD')
                arganzuela_mask = df.iloc[:, 0].astype(str).str.contains('ARGANZUELA', na=False, case=False)
                if arganzuela_mask.any():
                    arganzuela_row = df[arganzuela_mask].iloc[0]
                    # Try to extract numeric values from the row
                    for i, val in enumerate(arganzuela_row[1:], 1):
                        if pd.notna(val) and str(val).replace('.', '').replace('-', '').isdigit():
                            indicators[f'seguridad_col_{i}'] = float(val)
            
            # Detained persons
            if 'PERS. DETENIDAS X DISTRITOS' in xl.sheet_names:
                df = pd.read_excel(file_path, sheet_name='PERS. DETENIDAS X DISTRITOS')
                arganzuela_mask = df.iloc[:, 0].astype(str).str.contains('ARGANZUELA', na=False, case=False)
                if arganzuela_mask.any():
                    arganzuela_row = df[arganzuela_mask].iloc[0]
                    detained = arganzuela_row.iloc[1]
                    if pd.notna(detained) and str(detained).replace('.', '').replace('-', '').isdigit():
                        indicators['personas_detenidas'] = float(detained)
            
            # Traffic accidents
            if 'ACCIDENTES' in xl.sheet_names:
                df = pd.read_excel(file_path, sheet_name='ACCIDENTES')
                arganzuela_mask = df.iloc[:, 0].astype(str).str.contains('ARGANZUELA', na=False, case=False)
                if arganzuela_mask.any():
                    arganzuela_row = df[arganzuela_mask].iloc[0]
                    if len(arganzuela_row) > 1:
                        con_victimas = arganzuela_row.iloc[1]
                        if pd.notna(con_victimas) and str(con_victimas).replace('.', '').replace('-', '').isdigit():
                            indicators['accidentes_con_victimas'] = float(con_victimas)
                    if len(arganzuela_row) > 2:
                        sin_victimas = arganzuela_row.iloc[2]
                        if pd.notna(sin_victimas) and str(sin_victimas).replace('.', '').replace('-', '').isdigit():
                            indicators['accidentes_sin_victimas'] = float(sin_victimas)
            
            # Local inspections (entertainment venues)
            if 'LOCALES' in xl.sheet_names:
                df = pd.read_excel(file_path, sheet_name='LOCALES')
                arganzuela_mask = df.iloc[:, 0].astype(str).str.contains('ARGANZUELA', na=False, case=False)
                if arganzuela_mask.any():
                    arganzuela_row = df[arganzuela_mask].iloc[0]
                    if len(arganzuela_row) > 2:
                        denuncias = arganzuela_row.iloc[2]
                        if pd.notna(denuncias) and str(denuncias).replace('.', '').replace('-', '').isdigit():
                            indicators['denuncias_locales'] = float(denuncias)
            
        except Exception as e:
            logger.debug(f"Error extracting indicators: {e}")
        
        return indicators
    
    def analyze_trends(self):
        """Analyze crime trends over time"""
        if self.consolidated_data is None:
            logger.error("No data available for analysis")
            return
        
        # Create analysis summary
        print("=== ANÁLISIS DE TENDENCIAS EN ARGANZUELA ===\n")
        
        # Filter data with valid crime indicators
        valid_data = self.consolidated_data.dropna(subset=['personas_detenidas'])
        
        if len(valid_data) < 3:
            print("⚠️ Datos insuficientes para análisis de tendencias")
            return
        
        print(f"Períodos analizados: {len(valid_data)}")
        print(f"Rango de archivos: {valid_data['file_number'].min()} - {valid_data['file_number'].max()}\n")
        
        # Key metrics analysis
        metrics = ['personas_detenidas', 'accidentes_con_victimas', 'accidentes_sin_victimas', 'denuncias_locales']
        
        for metric in metrics:
            if metric in valid_data.columns:
                values = valid_data[metric].dropna()
                if len(values) > 2:
                    trend = self._calculate_trend(values)
                    print(f"{metric.replace('_', ' ').title()}:")
                    print(f"  - Media: {values.mean():.1f}")
                    print(f"  - Mín/Máx: {values.min():.0f} / {values.max():.0f}")
                    print(f"  - Tendencia: {trend}")
                    print()
        
        # Create trend visualization
        self._create_trend_plots(valid_data)
        
        # Save detailed data
        output_file = "arganzuela_trends_detailed.csv"
        valid_data.to_csv(output_file, index=False)
        print(f"📊 Datos detallados guardados en: {output_file}")
        
        return valid_data
    
    def _calculate_trend(self, values):
        """Calculate trend direction"""
        if len(values) < 3:
            return "Datos insuficientes"
        
        # Simple linear trend
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        recent_avg = values.tail(3).mean()
        older_avg = values.head(3).mean()
        change_pct = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        
        if slope > 0.1:
            return f"SUBIENDO ({change_pct:+.1f}%)"
        elif slope < -0.1:
            return f"BAJANDO ({change_pct:+.1f}%)"
        else:
            return f"ESTABLE ({change_pct:+.1f}%)"
    
    def _create_trend_plots(self, data):
        """Create trend visualization plots"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Tendencias de Criminalidad en Arganzuela', fontsize=16)
            
            metrics = [
                ('personas_detenidas', 'Personas Detenidas'),
                ('accidentes_con_victimas', 'Accidentes con Víctimas'),
                ('accidentes_sin_victimas', 'Accidentes sin Víctimas'),
                ('denuncias_locales', 'Denuncias en Locales')
            ]
            
            for i, (metric, title) in enumerate(metrics):
                ax = axes[i//2, i%2]
                if metric in data.columns:
                    clean_data = data[metric].dropna()
                    if len(clean_data) > 1:
                        ax.plot(range(len(clean_data)), clean_data, marker='o', linewidth=2)
                        ax.set_title(title)
                        ax.set_xlabel('Período')
                        ax.set_ylabel('Número de casos')
                        ax.grid(True, alpha=0.3)
                        
                        # Add trend line
                        if len(clean_data) > 2:
                            z = np.polyfit(range(len(clean_data)), clean_data, 1)
                            p = np.poly1d(z)
                            ax.plot(range(len(clean_data)), p(range(len(clean_data))), 
                                   "--", alpha=0.7, color='red')
                    else:
                        ax.text(0.5, 0.5, 'Datos insuficientes', 
                               transform=ax.transAxes, ha='center', va='center')
                else:
                    ax.text(0.5, 0.5, 'Sin datos', 
                           transform=ax.transAxes, ha='center', va='center')
            
            plt.tight_layout()
            plt.savefig('arganzuela_trends.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            print("📈 Gráficos guardados en: arganzuela_trends.png")
            
        except Exception as e:
            logger.warning(f"Error creating plots: {e}")

def main():
    analyzer = ArganzuelaTrendsAnalyzer()
    
    print("Extrayendo datos históricos de Arganzuela...")
    trends_data = analyzer.extract_arganzuela_trends()
    
    if trends_data is not None and len(trends_data) > 0:
        print(f"Datos extraídos de {len(trends_data)} archivos")
        analyzer.analyze_trends()
    else:
        print("No se pudieron extraer datos históricos")

if __name__ == "__main__":
    main()