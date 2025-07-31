# Madrid Police Data Processor

Automated tool to download and process Madrid police crime statistics from the official Madrid Open Data portal.

## Overview

This tool automatically downloads historical Madrid police intervention data (Excel files spanning 2017-2025) from the Madrid Open Data portal and converts it into a single, analysis-ready CSV dataset.

## Key Files

- `madrid_data_processor.py` - Complete pipeline that downloads Excel files and creates the final CSV
- `madrid_datos_actuaciones_policiales.csv` - Final consolidated dataset with 2,200+ rows covering all 23 Madrid districts

## Dataset Structure

The final dataset contains:
- **2,200 rows** (one per district per month)
- **17 columns** including interpretable crime categories
- **23 Madrid districts** 
- **Date range**: 2017-2025

### Key Columns
- `fecha` - Date (YYYY-MM-DD format)
- `distrito` - Madrid district name
- `relacionadas_con_personas` - Person-related incidents
- `relacionadas_con_patrimonio` - Property-related incidents
- `por_tenencia_armas` - Weapons possession incidents
- `por_tenencia_drogas` - Drug possession incidents
- `personas_detenidas` - Total detained persons
- `accidentes_con_victimas` - Traffic accidents with victims
- `infracciones_alcohol_adultos` - Adult alcohol violations

## Usage

Run the complete pipeline to download and process all data:

```bash
# Download from Madrid portal and create CSV dataset
uv run --with requests --with pandas --with openpyxl --with beautifulsoup4 madrid_data_processor.py
```

## Data Sources

- **Source**: Madrid Open Data Portal (datos.madrid.es)
- **Files**: Historical Excel files `policia-estadisticas-*.xlsx` (files 9-138+)
- **Date range**: April 2017 - Present
- **Sheets processed**: SEGURIDAD, PERS. DETENIDAS X DISTRITOS, ACCIDENTES, CONSUMO ALCOHOL

## Dependencies

- requests (for downloading)
- pandas (for data processing)
- openpyxl (for Excel file handling)
- beautifulsoup4 (for web scraping)

## Data Quality

The dataset is thoroughly validated with robust numeric validation and proper header processing logic.

## License

This project is for educational and research purposes analyzing publicly available police statistics data.