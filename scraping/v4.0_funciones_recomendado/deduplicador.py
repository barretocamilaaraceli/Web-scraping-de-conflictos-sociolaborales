# deduplicador.py — Limpieza y unificación de noticias por similitud textual

import pandas as pd
from pathlib import Path
from rapidfuzz import fuzz, process

# =========================
# CONFIGURACIÓN
# =========================
DATA_PATH = Path("data/Bases de datos originales/")

ARCHIVOS_CLASIFICADOS = [
    DATA_PATH / "historico_entreríos.csv",
    DATA_PATH / "historico_santafe.csv",
    DATA_PATH / "historico_nacionales.csv",
]

ARCHIVO_SALIDA = DATA_PATH / "conflictos_limpios.csv"

# =========================
# FUNCIONES
# =========================
def cargar_y_unir_archivos(archivos):
    """Carga y une múltiples CSV existentes."""
    dataframes = []
    for archivo in archivos:
        if archivo.exists():
            print(f"📥 Cargando {archivo.name}...")
            try:
                df = pd.read_csv(archivo)
                df["origen"] = archivo.stem  # para rastrear de dónde viene
                dataframes.append(df)
            except Exception as e:
                print(f"⚠️ Error leyendo {archivo.name}: {e}")
        else:
            print(f"⚠️ No se encontró: {archivo.name}")

    if not dataframes:
        print("🚫 No se encontró ningún archivo para procesar.")
        return pd.DataFrame()

    df_total = pd.concat(dataframes, ignore_index=True)
    print(f"📄 Total combinado: {len(df_total)} registros.")
    return df_total


def eliminar_duplicados_uid(df):
    """Elimina duplicados exactos por UID (basado en título + medio)."""
    if df.empty:
        return df

    if "uid" not in df.columns:
        df["uid"] = df.apply(
            lambda x: hash(
                (str(x.get("titulo", "")).lower().strip() +
                 str(x.get("medio", "")).lower().strip())
            ),
            axis=1,
        )
    antes = len(df)
    df = df.drop_duplicates(subset=["uid"])
    eliminados = antes - len(df)
    print(f"🧹 Eliminados {eliminados} duplicados exactos (por UID).")
    return df


def eliminar_duplicados_similares(df, threshold=90):
    """
    Elimina duplicados por similitud de títulos (fuzzy matching).
    Mantiene el más informativo (más largo o más reciente).
    """
    if df.empty:
        return df

    df = df.copy()
    df["titulo_norm"] = df["titulo"].fillna("").str.lower().str.strip()
    if "fecha_relevamiento" in df.columns and "longitud_texto" in df.columns:
        df = df.sort_values(by=["fecha_relevamiento", "longitud_texto"], ascending=[False, False])

    vistos = set()
    indices_a_eliminar = set()
    titulos = df["titulo_norm"].tolist()

    for i, t1 in enumerate(titulos):
        if i in indices_a_eliminar or not t1:
            continue
        similares = process.extract(t1, titulos, scorer=fuzz.token_sort_ratio, limit=None)
        for _, score, idx in similares:
            if idx == i or idx in indices_a_eliminar:
                continue
            if score >= threshold:
                indices_a_eliminar.add(idx)

    df_limpio = df.drop(df.index[list(indices_a_eliminar)]).drop(columns=["titulo_norm"])
    print(f"🤖 Eliminados {len(indices_a_eliminar)} duplicados por similitud textual ({len(df_limpio)} finales).")
    return df_limpio


def limpiar_dataset():
    """Carga, limpia y guarda el dataset sin duplicados."""
    df = cargar_y_unir_archivos(ARCHIVOS_CLASIFICADOS)
    if df.empty:
        print("⚠️ No hay datos para limpiar.")
        return

    print(f"\n📊 Iniciando limpieza de {len(df)} registros...")
    df = eliminar_duplicados_uid(df)
    df = eliminar_duplicados_similares(df, threshold=90)

    # Guardar resultado
    df.to_csv(ARCHIVO_SALIDA, index=False, encoding="utf-8-sig")
    print(f"\n✅ Dataset limpio guardado: {ARCHIVO_SALIDA} ({len(df)} registros únicos).")


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    print("=== Limpieza avanzada de duplicados (por UID + similitud) ===\n")
    limpiar_dataset()
    print("\n🏁 Proceso completado con éxito.")
