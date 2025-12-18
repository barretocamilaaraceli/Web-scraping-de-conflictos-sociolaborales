# Web-scraping-de-conflictos-sociolaborales
# 📰 Observatorio de Conflictos Laborales — Santa Fe y Entre Ríos

El **Observatorio de Conflictos Laborales** es una herramienta automatizada de recolección, filtrado y clasificación de noticias relacionadas con **conflictos laborales, sindicales o gremiales** en las provincias de **Santa Fe** y **Entre Ríos (Argentina)**.

El sistema utiliza scraping semántico, análisis de coocurrencias y procesamiento básico de lenguaje natural (NLP) para identificar eventos laborales relevantes en medios locales, regionales y nacionales.

---

## 🎯 Objetivos

- Relevar medios periodísticos locales y nacionales con foco en Santa Fe y Entre Ríos.  
- Detectar noticias relacionadas con **acciones colectivas de trabajadores**, **reclamos laborales** y **movilizaciones sindicales**.  
- Evitar temas no laborales mediante un diccionario de exclusiones (policiales, accidentes, etc.).  
- Clasificar los conflictos por **tipo de actor, acción y territorio**.  
- Generar una base histórica limpia, actualizable y analizable.

---

## 🧠 Metodología general

El proceso se organiza en tres etapas:

1. **Extracción y filtrado semántico (`scraping_er_sf.py`)**
   - Descarga titulares y textos de noticias mediante scraping y RSS.
   - Filtra por coocurrencia de *actores*, *acciones* y *reclamos*.
   - Identifica el *territorio* (Santa Fe o Entre Ríos) y calcula un *nivel de conflicto* (0–1).

2. **Depuración de duplicados (`deduplicador.py`)**
   - Combina los CSV de ambas provincias y elimina noticias repetidas o muy similares usando comparación textual (*RapidFuzz*).
   - Devuelve una base limpia (`conflictos_limpios.csv`).

3. **Clasificación temática (`clasificador_conflictos.py`)**
   - Clasifica los conflictos por *sector* (docente, salud, transporte, estatal, etc.).
   - Permite incorporar reglas o modelos NLP más complejos en futuras versiones.

---
```bash
📂 Estructura del repositorio

📦 ConflictoER/
├── 📁 data/ # Archivos CSV acumulativos
│ ├── historico_santafe.csv
│ ├── historico_entreríos.csv
│ └── historico_nacionales.csv
│ └── conflictos_limpios.csv
│ └── conflictos_clasificados.csv
├── 📄 diccionario.json # Diccionario de términos laborales y geográficos
├── 🧠 scraping_er_sf.py # Script principal de scraping y filtrado semántico
├── 🧹 deduplicador.py # Script de limpieza de duplicados
└── 🧾 README.md # Documentación del proyecto

```
---

# ⚙️ Instalación y configuración

## 1. Clonar el repositorio
```bash
git clone https://github.com/<tu_usuario>/ConflictoER.git
cd ConflictoER
```

## **2. Crear un entorno virtual (opcional)**
```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
```

## **3. Instalar dependencias**
```bash
pip install requests beautifulsoup4 feedparser pandas rapidfuzz
```
----

# **🚀 Ejecución paso a paso**

## 1️⃣ Relevar noticias
*python scraping_er_sf.py*

📥 Este script:
Extrae noticias de medios locales y nacionales.
Filtra por coocurrencias (actores + acciones + reclamos).
Detecta provincia o localidad.
Calcula nivel de conflicto (nivel_conflicto entre 0 y 1).

*Salidas:*
data/historico_santafe.csv
data/historico_entreríos.csv
data/historico_nacionales.csv


## 2️⃣ Eliminar duplicados
*python deduplicador.py*

🧹 Este script:
Combina los CSV anteriores.
Elimina duplicados exactos y por similitud (>90%).

*Devuelve una base consolidada y limpia:*
data/conflictos_limpios.csv


## **3️⃣ Clasificar los conflictos**
*python clasificador_conflictos.py*

*🧠 Este script:*
Clasifica los conflictos por tipo de sector laboral.
Agrega las columnas:
- categoria_conflicto
- fecha_clasificacion
- subnivel_conflicto (opcional: bajo / medio / alto)

*Salida:*
data/conflictos_clasificados.csv

---

```bash
📊 Campos del dataset final

**Campo**	             	 │  **Descripción**
fecha_relevamiento	     	 │  Fecha del scraping
medio	                 	 │  Fuente periodística
titulo	                 	 │  Título original
link	                 	 │  URL del artículo
texto	                  	 │  Cuerpo de la noticia
territorio	              	 │  Santa Fe / Entre Ríos
acciones_detectadas	         │  Palabras clave de acción
actores_detectados           │  Palabras clave de actor
reclamos_detectados	      	 │  Palabras clave de reclamo
verbos_detectados	         │  Verbos asociados a conflictos
repertorios_detectados	     │  Formas de acción colectiva
instituciones_detectadas	 │  Menciones a organismos
nivel_conflicto	             │  Valor 0–1 según coocurrencias
coocurrencia	             │  Estructura A:B:C detectada
categoria_conflicto          │	Clasificación temática (docente, salud, etc.)
subnivel_conflicto	         │  Bajo / Medio / Alto (según puntaje)
longitud_texto	             │  Longitud del texto analizado

---
	
🗞️ Medios relevados

*🟦 Entre Ríos*
Análisis Digital
El Miércoles Digital
El Heraldo de Concordia (RSS)
El Día de Gualeguaychú (RSS)
La Calle (Concepción del Uruguay)
AIM Digital
APF Digital

*🟥 Santa Fe*
Aire de Santa Fe
Santa Fe Noticias
Pausa (Santa Fe)
Diario Castellanos (Rafaela)
Esperanza Día x Día
Reconquista Hoy

*⚪ Nacionales (con cobertura regional)*
InfoGremiales
La Izquierda Diario (Entre Ríos)
La Izquierda Diario (Santa Fe)

---

🧩 Flujo de trabajo completo

*scraping_er_sf.py*           → Recolección y filtrado semántico
*deduplicador.py*             → Limpieza de duplicados
*clasificador_conflictos.py*  → Clasificación temática por sector

*Resultado final:*
data/conflictos_clasificados.csv

```
---

## ⚠️ Nota importante sobre el scraping de medios 

El funcionamiento correcto de los scripts de scraping depende directamente de la **estructura HTML de cada sitio web** (etiquetas, clases, identificadores, jerarquía del DOM). Dado que **cada medio utiliza un diseño distinto** —y que estos pueden modificarse con el tiempo—, es necesario **verificar previamente la estructura de las páginas** antes de ejecutar o adaptar el código.
Si un medio cambia su maquetación (por ejemplo, los nombres de las clases CSS o la forma en que se renderiza el contenido), el script puede dejar de capturar correctamente títulos, fechas o cuerpos de texto.

### Recomendación práctica
Ante fallas o al incorporar nuevos medios:
1. Abrir una noticia del medio en el navegador.
2. Inspeccionar el HTML (clic derecho → *Inspeccionar*).
3. Copiar los fragmentos relevantes del código (contenedores de título, fecha y texto).
4. Compartir esa estructura con una herramienta de asistencia (por ejemplo, ChatGPT) para identificar con mayor precisión:
   - etiquetas (`div`, `article`, `h1`, `p`, etc.),
   - clases o identificadores,
   - y los selectores adecuados a utilizar en el scraping.
Esta verificación previa permite **ajustar los selectores del script** y garantizar una extracción de datos consistente y reproducible.

---

## **🧰 Posibles mejoras futuras**
Incorporar embeddings o modelos de clasificación supervisada (BERT, DistilBERT, SBERT).
Analizar frecuencia temporal y territorial de conflictos (dashboards).
Detección automática de gremios y empresas involucradas.
Enlace con datasets comparativos: Mass Mobilization (Harvard) o ACEP (Nieto, UNMdP).
Agregar capa de visualización (Streamlit / Power BI).

---
## 📖 **Créditos**
Autor: *Camila Barreto*  │
Proyecto: Observatorio de Conflictos Laborales — Entre Ríos / Santa Fe  │
Colaboración técnica: GPT-5.2 (OpenAI, 2025)

