"""Carga validada, estadísticos descriptivos y detección de atípicos IQR.

La detección no elimina registros ni implica que una observación sea errónea.
"""
from pathlib import Path
import pandas as pd

COLUMNAS = ("total_bill", "tip", "sex", "smoker", "day", "time", "size")
NUMERICAS = ("total_bill", "tip", "size")
CATEGORICAS = ("sex", "smoker", "day", "time")


def cargar_datos(ruta: str | Path) -> pd.DataFrame:
    """Lee CSV local y comprueba su esquema y coherencia, sin descartar filas."""
    df = pd.read_csv(ruta, encoding="utf-8")
    faltantes = set(COLUMNAS) - set(df.columns)
    if faltantes:
        raise ValueError(f"Columnas obligatorias ausentes: {sorted(faltantes)}")
    df = df.loc[:, COLUMNAS].copy()
    for col in NUMERICAS:
        df[col] = pd.to_numeric(df[col], errors="raise")
    if df[list(COLUMNAS)].isna().any().any():
        raise ValueError("Hay valores nulos: requieren análisis específico antes del EDA")
    if (df[["total_bill", "tip"]] < 0).any().any() or (df["size"] <= 0).any():
        raise ValueError("Montos negativos o tamaño del grupo no válido")
    if not (df["size"] % 1 == 0).all():
        raise ValueError("size debe representar un número entero de comensales")
    df["size"] = df["size"].astype("int64")
    for col in CATEGORICAS:
        df[col] = df[col].astype("category")
    # Índice sintético para rastrear registros en tablas: NO es ID original.
    df.insert(0, "registro_ref", range(1, len(df) + 1))
    return df


def resumen_descriptivo(df: pd.DataFrame) -> pd.DataFrame:
    """Incluye estadísticos de dispersión, sesgo y curtosis en exceso (Fisher)."""
    filas=[]
    for col in NUMERICAS:
        serie=df[col].astype(float).dropna()
        filas.append({
            "variable": col, "n": int(serie.size),
            "media": float(serie.mean()), "mediana": float(serie.median()),
            "desviacion_std": float(serie.std(ddof=1)),
            "minimo": float(serie.min()), "q1": float(serie.quantile(0.25)),
            "q3": float(serie.quantile(0.75)), "maximo": float(serie.max()),
            "asimetria": float(serie.skew()),
            "curtosis_exceso": float(serie.kurt()),
        })
    return pd.DataFrame(filas)


def marcar_iqr(df: pd.DataFrame, variable: str, factor: float = 1.5):
    """Devuelve copia con bandera booleana e información del intervalo IQR global."""
    if variable not in NUMERICAS:
        raise ValueError(f"Variable no admitida: {variable}")
    if factor <= 0:
        raise ValueError("factor debe ser positivo")
    serie=df[variable]
    q1,q3=float(serie.quantile(.25)),float(serie.quantile(.75))
    iqr=q3-q1
    minimo,maximo=q1-factor*iqr,q3+factor*iqr
    salida=df.copy()
    bandera=f"outlier_{variable}"
    salida[bandera]=(serie<minimo)|(serie>maximo)  # estrictamente fuera del rango
    detalle={"variable":variable,"q1":q1,"q3":q3,"iqr":iqr,
             "limite_inferior":minimo,"limite_superior":maximo,
             "n_atipicos":int(salida[bandera].sum()),"factor":factor}
    return salida,detalle
