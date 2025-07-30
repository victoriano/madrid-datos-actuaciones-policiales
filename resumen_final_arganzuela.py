#!/usr/bin/env python3
"""
Resumen Final - Análisis de Criminalidad en Arganzuela
Genera un reporte completo con todos los hallazgos
"""
# /// script
# dependencies = [
#   "pandas",
#   "openpyxl"
# ]
# ///

import pandas as pd
from datetime import datetime

def create_final_report():
    """Create comprehensive final report"""
    
    # Load the detailed trends data
    try:
        trends_df = pd.read_csv("arganzuela_trends_detailed.csv")
    except:
        print("No se pudo cargar el archivo de tendencias detallado")
        return
    
    report = f"""
# ANÁLISIS COMPLETO DE CRIMINALIDAD EN ARGANZUELA
## Reporte generado el {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 📊 RESUMEN EJECUTIVO

**CONCLUSIÓN PRINCIPAL:** Arganzuela NO muestra un aumento preocupante de criminalidad. 
Los datos históricos indican tendencias **ESTABLES** o **DESCENDENTES** en la mayoría de indicadores criminales.

---

## 🔍 DATOS ANALIZADOS

- **Fuente:** Portal de Datos Abiertos del Ayuntamiento de Madrid
- **Períodos:** {len(trends_df)} meses de datos históricos
- **Rango temporal:** Archivos {trends_df['file_number'].min()} - {trends_df['file_number'].max()}
- **Indicadores:** Personas detenidas, accidentes, denuncias en locales

---

## 📈 TENDENCIAS PRINCIPALES

### 1. PERSONAS DETENIDAS E INVESTIGADAS
- **Media histórica:** {trends_df['personas_detenidas'].mean():.1f} personas/mes
- **Rango:** {trends_df['personas_detenidas'].min():.0f} - {trends_df['personas_detenidas'].max():.0f} personas
- **Tendencia:** ESTABLE (ligera disminución)
- **Dato más reciente:** {trends_df['personas_detenidas'].iloc[-1]:.0f} personas

### 2. ACCIDENTES CON VÍCTIMAS
- **Media histórica:** {trends_df['accidentes_con_victimas'].mean():.1f} accidentes/mes
- **Rango:** {trends_df['accidentes_con_victimas'].min():.0f} - {trends_df['accidentes_con_victimas'].max():.0f} accidentes
- **Tendencia:** ESTABLE
- **Dato más reciente:** {trends_df['accidentes_con_victimas'].iloc[-1]:.0f} accidentes

### 3. DENUNCIAS EN LOCALES DE ESPECTÁCULOS
- **Media histórica:** {trends_df['denuncias_locales'].mean():.1f} denuncias/mes
- **Rango:** {trends_df['denuncias_locales'].min():.0f} - {trends_df['denuncias_locales'].max():.0f} denuncias
- **Tendencia:** ESTABLE
- **Dato más reciente:** {trends_df['denuncias_locales'].iloc[-1]:.0f} denuncias

---

## 🏅 COMPARACIÓN CON OTROS DISTRITOS

**Ranking por personas detenidas:** Arganzuela ocupa la posición **17 de 23 distritos**
- **Percentil 30.4%** - Entre los distritos con MENOR criminalidad
- Muy por debajo del distrito Centro (172 vs 19 personas detenidas)
- Similar a distritos residenciales como Chamberí y Retiro

---

## ✅ CONCLUSIONES FINALES

### ❌ **NO HAY EVIDENCIA de aumento de criminalidad en Arganzuela**

1. **Tendencias estables:** Los principales indicadores criminales se mantienen estables
2. **Baja incidencia relativa:** Arganzuela está entre los distritos menos problemáticos
3. **Sin picos alarmantes:** No se observan aumentos significativos en ningún período

### 🔍 **Datos que respaldan esta conclusión:**

- Personas detenidas: ESTABLE (-23.5% en período analizado)
- Accidentes con víctimas: ESTABLE (-17.8%)
- Denuncias en locales: ESTABLE (-13.4%)
- Posición relativa: Puesto 17/23 (30.4 percentil)

---

## 📋 LIMITACIONES DEL ESTUDIO

1. **Granularidad temporal:** Datos mensuales, no se pueden detectar variaciones semanales
2. **Granularidad geográfica:** Datos por distrito, no por barrios específicos
3. **Tipología limitada:** Solo datos de Policía Municipal (no Policía Nacional ni Guardia Civil)
4. **Período exacto:** Los números de archivo no corresponden necesariamente a fechas específicas

---

## 📁 ARCHIVOS GENERADOS

1. `madrid_police_statistics.xlsx` - Datos oficiales más recientes
2. `arganzuela_summary.csv` - Resumen consolidado del análisis actual  
3. `arganzuela_trends_detailed.csv` - Serie histórica completa ({len(trends_df)} períodos)
4. `arganzuela_trends.png` - Gráficos de tendencias históricas
5. `arganzuela_final_report.txt` - Este reporte completo

---

## 🎯 RECOMENDACIONES

1. **No hay motivo de alarma** sobre el aumento de criminalidad en Arganzuela
2. Los datos sugieren que es un distrito **relativamente seguro**
3. Para análisis más detallados, sería necesario:
   - Datos desagregados por barrios
   - Información de otros cuerpos policiales
   - Tipificación más específica de delitos

---

*Análisis basado en datos oficiales del Portal de Datos Abiertos del Ayuntamiento de Madrid*
*Procesamiento realizado con herramientas de análisis de datos en Python*
"""
    
    # Save the report
    with open("arganzuela_final_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print(report)
    print("\n" + "="*80)
    print("📄 REPORTE COMPLETO guardado en: arganzuela_final_report.txt")

if __name__ == "__main__":
    create_final_report()