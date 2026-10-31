"""
BACKEND DE ANÁLISIS — Examen Parcial N° 2 (POAD)

Este módulo agrega "inteligencia" al dashboard del Parcial 1. Hace dos cosas:

1. DESCRIPCIÓN ESTADÍSTICA (numpy + scipy)
   - Estadísticos descriptivos (media, mediana, desvío, mínimo, máximo).
   - Prueba t de Welch para saber si la diferencia entre dos grupos
     (Estatal vs Privado, Urbano vs Rural) es real o puede ser casualidad.

2. APRENDIZAJE PROFUNDO (scikit-learn)
   - Una red neuronal (perceptrón multicapa) que, a partir de la provincia,
     el ámbito y el tipo de gestión, estima qué porcentaje de estudiantes
     queda en cada uno de los 4 niveles de desempeño.

El dashboard (main2.py) importa estas funciones. También se puede correr
solo, desde la carpeta del proyecto, para ver los resultados en la terminal:

    python src/analysis.py
"""

import os
import warnings

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.exceptions import ConvergenceWarning

# El algoritmo lbfgs a veces avisa que "no convergió" cuando ya no puede
# mejorar los pesos con más precisión. El modelo igual queda entrenado y
# lo evaluamos con validación cruzada, así que ocultamos ese aviso.
warnings.filterwarnings('ignore', category=ConvergenceWarning)

# Los 4 niveles, ordenados de menor a mayor desempeño
NIVELES = ['Por debajo del básico', 'Básico', 'Satisfactorio', 'Avanzado']

# Las 3 columnas que la red neuronal usa como "entrada"
ENTRADAS = ['jurisdiccion', 'ambito', 'tipo_gestion']

# Semilla fija: hace que los resultados salgan siempre iguales
SEMILLA = 42


# ---------------------------------------------------------------------------
# 1. PREPARAR LOS DATOS
# ---------------------------------------------------------------------------
def preparar_datos(df):
    """Pasa el CSV de formato largo a formato ancho.

    Formato largo (el CSV): 4 filas por grupo, una por cada nivel.
    Formato ancho (lo que devuelve): 1 fila por grupo y una columna por nivel.
    Además agrega la columna 'optimo' = Satisfactorio + Avanzado.
    """
    ancho = (df.pivot_table(index=ENTRADAS,
                            columns='nivel_desempeno',
                            values='porcentaje')
               .reset_index())
    ancho = ancho[ENTRADAS + NIVELES]          # ordena las columnas
    ancho.columns.name = None                  # quita el nombre que deja pivot_table
    ancho['optimo'] = ancho['Satisfactorio'] + ancho['Avanzado']
    return ancho


# ---------------------------------------------------------------------------
# 2. DESCRIPCIÓN ESTADÍSTICA
# ---------------------------------------------------------------------------
def describir_por_grupo(ancho, columna):
    """Tabla de estadísticos descriptivos del % óptimo, separada por grupo."""
    filas = []
    for grupo, datos in ancho.groupby(columna):
        valores = datos['optimo'].to_numpy()   # array de numpy
        filas.append({
            'grupo': grupo,
            'n': len(valores),
            'media': np.mean(valores),
            'mediana': np.median(valores),
            'desvio': np.std(valores, ddof=1),  # ddof=1 -> desvío muestral
            'minimo': np.min(valores),
            'maximo': np.max(valores),
        })
    return pd.DataFrame(filas)


def comparar_grupos(ancho, columna, grupo_a, grupo_b, alfa=0.05):
    """Prueba t de Welch: ¿el % óptimo del grupo A es distinto al del grupo B?

    - Hipótesis nula (H0): los dos grupos tienen la misma media.
    - Si el p-valor es menor que alfa (0,05), rechazamos H0:
      la diferencia es estadísticamente significativa.
    """
    a = ancho.loc[ancho[columna] == grupo_a, 'optimo'].to_numpy()
    b = ancho.loc[ancho[columna] == grupo_b, 'optimo'].to_numpy()

    prueba = stats.ttest_ind(a, b, equal_var=False)   # Welch
    diferencia = np.mean(a) - np.mean(b)

    # Intervalo de confianza del 95% para la diferencia de medias
    ic = prueba.confidence_interval(confidence_level=0.95)

    # d de Cohen: tamaño del efecto (qué tan grande es la diferencia)
    desvio_combinado = np.sqrt((np.var(a, ddof=1) + np.var(b, ddof=1)) / 2)
    d_cohen = diferencia / desvio_combinado

    return {
        'grupo_a': grupo_a,
        'grupo_b': grupo_b,
        'media_a': np.mean(a),
        'media_b': np.mean(b),
        'diferencia': diferencia,
        'ic_bajo': ic.low,
        'ic_alto': ic.high,
        't': prueba.statistic,
        'p_valor': prueba.pvalue,
        'd_cohen': d_cohen,
        'significativa': prueba.pvalue < alfa,
    }


# ---------------------------------------------------------------------------
# 3. APRENDIZAJE PROFUNDO — RED NEURONAL
# ---------------------------------------------------------------------------
def crear_red_neuronal():
    """Arma la red: codificador one-hot + perceptrón multicapa.

    - OneHotEncoder: convierte texto ('Mendoza', 'Urbano', 'Privado')
      en columnas de 0 y 1, porque la red solo entiende números.
    - MLPRegressor: red con 2 capas ocultas (32 y 16 neuronas),
      activación ReLU y 4 neuronas de salida (una por nivel).
    """
    return make_pipeline(
        OneHotEncoder(handle_unknown='ignore'),
        MLPRegressor(
            hidden_layer_sizes=(32, 16),  # 2 capas ocultas
            activation='relu',            # función de activación
            solver='lbfgs',               # algoritmo que ajusta los pesos
            alpha=0.1,                    # regularización: evita "memorizar"
            max_iter=5000,                # máximo de vueltas de entrenamiento
            random_state=SEMILLA,
        ),
    )


def entrenar_red_neuronal(ancho):
    """Evalúa la red con validación cruzada y la entrena con todos los datos.

    Validación cruzada de 5 partes: se divide el dataset en 5 pedazos.
    5 veces se entrena con 4 pedazos (80%) y se prueba con el que queda (20%).
    Así cada grupo se predice una vez "sin haberlo visto" en el entrenamiento.
    """
    X = ancho[ENTRADAS]
    y = ancho[NIVELES] / 100          # escala 0-1: la red aprende mejor

    particion = KFold(n_splits=5, shuffle=True, random_state=SEMILLA)
    pred = cross_val_predict(crear_red_neuronal(), X, y, cv=particion) * 100

    real_optimo = ancho['optimo'].to_numpy()
    pred_optimo = pred[:, 2] + pred[:, 3]   # Satisfactorio + Avanzado

    # Línea de base: "predecir" siempre el promedio. La red debe superarla.
    base_optimo = np.full_like(real_optimo, real_optimo.mean())

    metricas = {
        'mae': mean_absolute_error(real_optimo, pred_optimo),
        'mae_base': mean_absolute_error(real_optimo, base_optimo),
        'r2': r2_score(real_optimo, pred_optimo),
        'n_grupos': len(ancho),
    }

    tabla = ancho[ENTRADAS].copy()
    tabla['real'] = real_optimo
    tabla['predicho'] = pred_optimo

    # Modelo final: se entrena con el 100% de los datos para el simulador
    modelo = crear_red_neuronal()
    modelo.fit(X, y)

    return modelo, metricas, tabla


def predecir(modelo, jurisdiccion, ambito, tipo_gestion):
    """Pide a la red los 4 porcentajes para una combinación elegida."""
    entrada = pd.DataFrame([[jurisdiccion, ambito, tipo_gestion]], columns=ENTRADAS)
    salida = modelo.predict(entrada)[0] * 100

    # La red no "sabe" que los 4 niveles suman 100%: lo corregimos acá
    salida = np.clip(salida, 0, None)          # sin valores negativos
    salida = salida / salida.sum() * 100       # que sumen exactamente 100
    return dict(zip(NIVELES, salida))


# ---------------------------------------------------------------------------
# 4. FUNCIÓN PRINCIPAL — la que llama el dashboard
# ---------------------------------------------------------------------------
def ejecutar_analisis(df):
    """Corre todo el backend y devuelve los resultados en un diccionario."""
    ancho = preparar_datos(df)
    modelo, metricas, tabla_validacion = entrenar_red_neuronal(ancho)
    return {
        'ancho': ancho,
        'desc_gestion': describir_por_grupo(ancho, 'tipo_gestion'),
        'desc_ambito': describir_por_grupo(ancho, 'ambito'),
        'prueba_gestion': comparar_grupos(ancho, 'tipo_gestion', 'Privado', 'Estatal'),
        'prueba_ambito': comparar_grupos(ancho, 'ambito', 'Urbano', 'Rural'),
        'modelo': modelo,
        'metricas': metricas,
        'tabla_validacion': tabla_validacion,
    }


if __name__ == '__main__':
    df = pd.read_csv(os.path.join('data', 'aprender2024_matematica.csv'))
    r = ejecutar_analisis(df)

    print('\n=== DESCRIPCIÓN POR TIPO DE GESTIÓN ===')
    print(r['desc_gestion'].round(2).to_string(index=False))
    print('\n=== DESCRIPCIÓN POR ÁMBITO ===')
    print(r['desc_ambito'].round(2).to_string(index=False))

    for clave in ['prueba_gestion', 'prueba_ambito']:
        p = r[clave]
        print(f"\n=== PRUEBA T DE WELCH: {p['grupo_a']} vs {p['grupo_b']} ===")
        print(f"Diferencia de medias: {p['diferencia']:.2f} puntos "
              f"(IC 95%: {p['ic_bajo']:.2f} a {p['ic_alto']:.2f})")
        print(f"t = {p['t']:.2f} | p-valor = {p['p_valor']:.2e} | d de Cohen = {p['d_cohen']:.2f}")
        print('Significativa' if p['significativa'] else 'No significativa')

    m = r['metricas']
    print('\n=== RED NEURONAL (validación cruzada de 5 partes) ===')
    print(f"Grupos analizados: {m['n_grupos']}")
    print(f"Error medio de la red: {m['mae']:.2f} puntos")
    print(f"Error medio de la línea de base: {m['mae_base']:.2f} puntos")
    print(f"R²: {m['r2']:.3f}")

    ejemplo = predecir(r['modelo'], 'Mendoza', 'Urbano', 'Estatal')
    print('\nPredicción para Mendoza / Urbano / Estatal:')
    for nivel, valor in ejemplo.items():
        print(f'  {nivel}: {valor:.1f}%')
