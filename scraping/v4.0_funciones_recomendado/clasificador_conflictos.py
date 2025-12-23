# clasipip installficador_conflictos_v4.py — NLP + reglas
# Clasificación semántica y territorial de conflictos laborales

import pandas as pd
from pathlib import Path
import json
import re
import spacy

# ----------------------------
# CONFIGURACIÓN
# ----------------------------
DATA_PATH = Path("data/Bases de datos originales/")
archivos_fuente = [DATA_PATH / "conflictos_limpios.csv"]
salida = DATA_PATH / "conflictos_clasificados_nlp.csv"

# Carga modelo spaCy español
print("🧠 Cargando modelo de lenguaje spaCy (es_core_news_md)...")
nlp = spacy.load("es_core_news_md")

# ----------------------------
# DICCIONARIOS (como versión 3.0)
# ----------------------------
TIPOS_CONFLICTO = {
    "Reivindicativo": [
        "reclamo", "reclaman", "exigen", "pedido", "petitorio", "demanda", "aumento", "paritaria",
        "incremento", "recomposición", "revisión salarial", "mejora salarial", "convenio colectivo",
        "mejoras en las condiciones", "regularización", "bono", "equiparación"
    ],
    "Defensivo": [
        "despido", "cesante", "cesantías", "suspensión", "lockout", "crisis", "recorte", "cierre",
        "retiro voluntario", "liquidación", "atraso salarial", "falta de pago", "reducción"
    ],
    "Institucional": [
        "ministerio", "intendencia", "municipio", "funcionario", "autoridad", "gobernador", "secretaría",
        "ministro", "consejo", "gobierno", "paritaria provincial"
    ],
    "Político-solidario": [
        "reforma laboral", "protesta nacional", "ajuste del gobierno", "ley", "política nacional",
        "represión", "crisis económica", "solidaridad"
    ],
    "Sindical interno": [
        "asamblea", "delegados", "comisión directiva", "elección sindical", "internas gremiales",
        "disputa gremial", "cambio de conducción", "renovación autoridades"
    ],
    "Laboral general": [
        "trabajador", "trabajadores", "empleado", "empleados", "paro", "huelga", "manifestación", "piquete"
    ],
}

SECTORES = {
    "educación": ["docente", "maestro", "profesor", "universidad", "facultad", "escuela", "amafe", "amsafe"],
    "salud": ["hospital", "médico", "enfermero", "sanatorio", "clínica", "salud pública"],
    "transporte": ["chofer", "colectivo", "transporte", "camionero", "uta", "taxista", "ferroviario"],
    "industria": ["fábrica", "metalúrgico", "planta", "obreros", "industrial", "smata", "uom"],
    "estatales": ["ate", "upcn", "empleado público", "ministerio", "provincia"],
    "municipales": ["municipal", "intendencia", "empleados municipales", "obrador"],
    "bancarios": ["banco", "bancario", "la bancaria"],
    "rurales": ["campo", "peón", "uatre", "agro", "tractor"],
    "comercio": ["empleado de comercio", "supermercado", "vendedor", "shopping"],
    "servicios": ["telefonía", "energía", "gas", "agua", "obra social", "electricista"],
    "seguridad": ["policía", "penitenciario", "guardia", "bombero"]
}

TERRITORIOS = {
    "Santa Fe": [
        "santa fe", "rafaela", "reconquista", "esperanza", "venado tuerto", "santa fe capital",
        "san lorenzo", "casilda", "galvez", "ceres", "sunchales", "cañada de gómez", "coronda"
    ],
    "Entre Ríos": [
        "paraná", "concordia", "gualeguaychú", "concepción del uruguay",
        "villaguay", "nogoyá", "victoria", "colón", "gualeguay", "diamante", "feliciano", "san josé", "villa elisa", "ubajay", "oro verde", "santa ana", "liebig", "rosario del tala", "basavilbaso", "concordia"
    ],
}

# ----------------------------
# FUNCIONES AUXILIARES
# ----------------------------
def normalizar_texto(txt):
    txt = str(txt).lower()
    txt = re.sub(r"[^a-záéíóúüñ0-9\s]", " ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt

def clasificar_tipo_conflicto(texto):
    texto = normalizar_texto(texto)
    for tipo, palabras in TIPOS_CONFLICTO.items():
        if any(p in texto for p in palabras):
            return tipo
    return "Indeterminado"

def clasificar_sector(texto):
    texto = normalizar_texto(texto)
    for sector, terminos in SECTORES.items():
        if any(t in texto for t in terminos):
            return sector
    return "general"

def detectar_territorio_y_localidad(texto, medio):
    texto_lower = normalizar_texto(texto)
    medio_lower = normalizar_texto(medio)

    # 1️⃣ Buscar localidad explícita
    for provincia, localidades in TERRITORIOS.items():
        for loc in localidades:
            if re.search(rf"\b{re.escape(loc)}\b", texto_lower):
                return provincia, loc.capitalize()

    # 2️⃣ Inferencia por medio
    if "santa fe" in medio_lower or "rosario" in medio_lower:
        return "Santa Fe", "no se menciona localidad"
    if "ríos" in medio_lower or "entrerios" in medio_lower or "paraná" in medio_lower:
        return "Entre Ríos", "no se menciona localidad"

    return "no identificado", "no se menciona localidad"

def analizar_nlp(texto):
    """Usa spaCy para extraer entidades y posibles actores laborales/geográficos."""
    doc = nlp(texto)
    entidades = [ent.text for ent in doc.ents]
    actores = [ent.text for ent in doc.ents if ent.label_ in ("ORG", "PER")]

    # Detectar si hay entidades geográficas no reconocidas por reglas
    geos = [ent.text for ent in doc.ents if ent.label_ in ("LOC", "GPE")]

    return {
        "entidades_detectadas": ", ".join(set(entidades)),
        "actores_nlp": ", ".join(set(actores)),
        "geos_detectadas": ", ".join(set(geos))
    }

# ----------------------------
# PROCESAMIENTO PRINCIPAL
# ----------------------------
def procesar_datasets():
    df_total = []

    for archivo in archivos_fuente:
        if not archivo.exists():
            print(f"⚠️ No se encontró {archivo}")
            continue

        df = pd.read_csv(archivo)
        if df.empty:
            continue

        print(f"📄 Procesando {archivo.name} ({len(df)} filas)")
        df["uid"] = df.apply(lambda x: hash((str(x.get("titulo", "")).lower().strip() + str(x.get("medio", "")).lower().strip())), axis=1)

        df["tipo_conflicto"] = df["texto"].fillna("").apply(clasificar_tipo_conflicto)
        df["sector"] = df["texto"].fillna("").apply(clasificar_sector)

        territorios_localidades = df.apply(lambda x: detectar_territorio_y_localidad(str(x.get("texto", "")), x.get("medio", "")), axis=1)
        df["territorio"] = territorios_localidades.apply(lambda t: t[0])
        df["localidad"] = territorios_localidades.apply(lambda t: t[1])

        # 🔍 NLP enrichment
        nlp_resultados = df["texto"].fillna("").apply(analizar_nlp)
        df["entidades_detectadas"] = nlp_resultados.apply(lambda d: d["entidades_detectadas"])
        df["actores_nlp"] = nlp_resultados.apply(lambda d: d["actores_nlp"])
        df["geos_detectadas"] = nlp_resultados.apply(lambda d: d["geos_detectadas"])

        df_total.append(df)

    if not df_total:
        print("⚠️ No hay datos para procesar.")
        return

    df_final = pd.concat(df_total, ignore_index=True)

    if salida.exists():
        df_existente = pd.read_csv(salida)
        if "uid" not in df_existente.columns:
            df_existente["uid"] = df_existente.apply(lambda x: hash((str(x.get("titulo", "")).lower().strip() + str(x.get("medio", "")).lower().strip())), axis=1)
    else:
        df_existente = pd.DataFrame(columns=df_final.columns)

    uids_existentes = set(df_existente["uid"].tolist())
    nuevos = df_final[~df_final["uid"].isin(uids_existentes)]
    df_actualizado = pd.concat([df_existente, nuevos], ignore_index=True)
    df_actualizado.to_csv(salida, index=False, encoding="utf-8-sig")

    print(f"✅ Dataset actualizado: {len(nuevos)} nuevas noticias agregadas ({len(df_actualizado)} totales).")
    print("\n=== Distribución por tipo de conflicto ===")
    print(df_actualizado["tipo_conflicto"].value_counts().to_string())
    print("\n=== Distribución por sector ===")
    print(df_actualizado["sector"].value_counts().to_string())
    print("\n=== Distribución por territorio ===")
    print(df_actualizado["territorio"].value_counts().to_string())


# ----------------------------
# MAIN
# ----------------------------
if __name__ == "__main__":
    procesar_datasets()

