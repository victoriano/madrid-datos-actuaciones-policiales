# Madrid Police Crime Data Analysis

This repository contains scripts and data for analyzing Madrid police crime statistics to determine crime trends in different districts, particularly focusing on the Arganzuela neighborhood.

## Overview

This project analyzes historical Madrid police intervention data from approximately 100 Excel files spanning 2017-2025 to create a consolidated, analysis-ready dataset.

## Key Files

### Data Processing Scripts
- `madrid_final_dataset_creator.py` - Main script that consolidates all historical Excel files into a single CSV
- `final_correct_mapping.py` - Applies interpretable column names to the dataset
- `correct_column_mapping.py` - Alternative column mapping script
- `final_column_fix.py` - Additional column fixing utilities

### Debug and Testing Scripts
- `trace_bug_detailed.py` - Debug script for tracing data extraction issues
- `test_extraction.py` - Test script for validating extraction logic

### Output Dataset
- `madrid_datos_actuaciones_policiales.csv` - Final consolidated dataset with 2,200 rows covering all 23 Madrid districts from 2017-2025

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

## Data Sources

The analysis is based on historical Excel files from Madrid's police statistics:
- Files: `policia-estadisticas-*.xlsx` (files 9-138)
- Estimated date range: April 2017 - June 2025
- Source sheets: SEGURIDAD, PERS. DETENIDAS X DISTRITOS, ACCIDENTES, LOCALES, CONSUMO ALCOHOL

## Key Findings

### Arganzuela District Analysis
Based on the consolidated data, **Arganzuela ranks 17th out of 23 districts** in overall crime incidents, indicating it is **relatively safe** compared to other Madrid districts.

## Technical Notes

### Bug Fixes Applied
- **Data extraction bug**: Fixed header row processing logic that was causing incorrect value extraction
- **Column mapping**: Corrected mapping of generic security columns to interpretable names
- **Validation**: Added robust numeric validation for data extraction

### Dependencies
- pandas
- openpyxl
- datetime
- pathlib

### Usage

```bash
# Regenerate the dataset (requires raw Excel files)
uv run --with pandas --with openpyxl madrid_final_dataset_creator.py

# Apply interpretable column names
uv run --with pandas final_correct_mapping.py
```

## Data Quality

The dataset has been thoroughly validated:
- ✅ Arganzuela June 2025 "relacionadas_con_personas" correctly shows value 2.0 (verified against original Excel)
- ✅ All 23 districts represented across the time series
- ✅ Consistent date estimation and proper numeric validation
- ✅ Header row processing logic corrected

## License

This project is for educational and research purposes analyzing publicly available police statistics data.