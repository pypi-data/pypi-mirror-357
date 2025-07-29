# ESTAPY 🐍

**Estadística descriptiva para datos agrupados y no agrupados.**

`estapy` es una librería de Python diseñada para facilitar el análisis estadístico básico con un enfoque didáctico y práctico. Incluye funciones para generar tablas de frecuencia, medidas de tendencia central, variación, detección de valores atípicos, histogramas y boxplots, tanto para datos agrupados como no agrupados.

---

## 🚀 Características

- Soporte para **datos agrupados y no agrupados**
- Tabla de frecuencias con marcas de clase, frecuencias acumuladas y relativas
- Cálculo de **media, mediana, moda, varianza, desviación estándar**
- Detección de **valores atípicos**
- Generación de **histogramas de densidad** y **boxplots** con `seaborn`
- Cálculo de **percentiles** e **IQR**
- Visuales con `matplotlib` y `seaborn`

---

## 📦 Instalación

```bash
pip install estapy
```


## 🧮 Uso rapido

Un ejemplo para datos agrupados

```bash
from estapy import DatosAgrupados

datos = [12, 14, 15, 18, 21, 21, 22, 24, 27, 29]
grupo = DatosAgrupados(datos)

print(grupo)               # Resumen estadístico y tabla de frecuencias
grupo.histograma()         # Histograma 
grupo.boxplot()            # Boxplot aproximado

```
Un ejemplo para datos no agrupados

```bash
from estapy import DatosNoAgrupados

datos = [12, 14, 15, 18, 21, 21, 22, 24, 27, 29]
libre = DatosNoAgrupados(datos)

print(libre)               # Resumen estadístico
libre.histograma()         # Histograma (seaborn)
libre.boxplot()            # Boxplot clásico
```