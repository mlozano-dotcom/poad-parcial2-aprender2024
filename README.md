# 📊 Dashboard — Operativo Aprender 2024: Desempeño en Matemática

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Dash-Plotly-00cc96?style=for-the-badge&logo=plotly&logoColor=white"/>
  <img src="https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white"/>
  <img src="https://img.shields.io/badge/IES%20Belgrano-POAD-0ea5e9?style=for-the-badge"/>
</p>

> **Trabajo Final — Examen Parcial N° 1**  
> Materia: Programación Orientada al Análisis de Datos (POAD)  
> Instituto Superior Manuel Belgrano · Tecnicatura en Ciencia de Datos e Inteligencia Artificial

---

## 📌 Descripción

Este proyecto es un **dashboard interactivo** que analiza y visualiza los resultados del **Operativo Aprender 2024** en el área de Matemática. Permite explorar el desempeño estudiantil por provincia, tipo de gestión (pública/privada) y ámbito (urbano/rural) a través de visualizaciones interactivas y estáticas.

Los datos provienen de la fuente oficial: [datos.gob.ar](https://datos.gob.ar).

---

## ✨ Funcionalidades

- 🔢 **KPIs automáticos**: promedio nacional, promedio de Mendoza y provincia líder en desempeño.
- 📊 **Ranking interactivo** de provincias por porcentaje de alumnos en nivel Satisfactorio + Avanzado, con filtro por tipo de gestión.
- 📈 **Gráfico de barras estático** (Matplotlib): distribución de desempeño en Mendoza.
- 🌡️ **Mapa de calor estático** (Seaborn): comparativa de gestión pública vs. privada por provincia.
- 🎨 Diseño moderno con tema oscuro, paleta de colores curada y tipografías de Google Fonts.

---

## 🗂️ Estructura del Proyecto

```
poad_final_18del6/
│
├── main2.py                          # App principal Dash
├── requirements.txt                  # Dependencias del proyecto
├── Documentacion_Dashboard_...pdf    # Documentación del proyecto
│
├── src/
│   ├── cleaning2.py                  # Script de limpieza y procesamiento del CSV
│   └── static_plots2.py              # Generación de gráficos estáticos (Matplotlib + Seaborn)
│
├── data/
│   └── aprender2024_matematica.csv   # Dataset oficial Aprender 2024
│
└── assets/
    └── (estilos CSS del dashboard)
```

---

## 🚀 Instalación y Uso

### 1. Clonar el repositorio

```bash
git clone https://github.com/vartodesing/poad-Final.git
cd poad-Final
```

### 2. Crear un entorno virtual e instalar dependencias

```bash
python -m venv .venv

# En Windows:
.venv\Scripts\activate

# En Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Generar los gráficos estáticos

Antes de ejecutar el dashboard, generá las imágenes estáticas:

```bash
python src/static_plots2.py
```

### 4. Ejecutar el dashboard

```bash
python main2.py
```

Luego abrí tu navegador en: **http://localhost:8050**

---

## 🛠️ Tecnologías Utilizadas

| Librería | Uso |
|---|---|
| `Dash` | Framework principal para el dashboard interactivo |
| `Plotly` | Gráficos interactivos (ranking de barras) |
| `Pandas` | Carga, limpieza y análisis del dataset |
| `Matplotlib` | Gráfico de barras estático (Mendoza) |
| `Seaborn` | Mapa de calor estático (gestión por provincia) |

---

## 📄 Datos

- **Fuente**: Ministerio de Educación de la Nación — Operativo Aprender 2024
- **URL**: [datos.gob.ar](https://datos.gob.ar/dataset/educacion-aprender)
- **Archivo**: `data/aprender2024_matematica.csv`

---

## 👤 Autores

Valentin Rasjido y Manuel Lozano 
Instituto Superior Manuel Belgrano  
Tecnicatura en Ciencia de Datos e Inteligencia Artificial — 2° Año  
Programación Orientada al Análisis de Datos (POAD)

---

<p align="center">
  Hecho con ❤️ para el parcial de POAD · 2026
</p>
