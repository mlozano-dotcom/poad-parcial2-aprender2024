import os
import pandas as pd

def clean_data():
    input_file = "2024 Base APRENDER - Censal - Secundaria 5-6 año - Agregada - Desempeños de Matematica(in).csv"
    output_file = os.path.join("data", "aprender2024_matematica.csv")

    print(f"Cargando datos crudos desde: {input_file}")
    df = pd.read_csv(input_file, sep=';', encoding='utf-8-sig')
    df = df.rename(columns={'sector': 'tipo_gestion'})

    print(f"Dimensiones iniciales del dataset crudo: {df.shape}")

    perf_cols = {
        'mdesemp_Por_debajo_del_nivel_básico': 'Por debajo del básico',
        'mdesemp_Básico': 'Básico',
        'mdesemp_Satisfactorio': 'Satisfactorio',
        'mdesemp_Avanzado': 'Avanzado'
    }

    for col in perf_cols:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.').str.strip(), errors='coerce')

    df = df.dropna(subset=list(perf_cols.keys()), how='all')
    print(f"Dimensiones del dataset tras eliminar nulos de rendimiento: {df.shape}")

    df_agg = df.groupby(['jurisdiccion', 'ambito', 'tipo_gestion'])[list(perf_cols.keys())].sum()
    df_agg['total_estudiantes'] = df_agg.sum(axis=1)
    df_agg = df_agg.reset_index()

    df_melted = df_agg.melt(
        id_vars=['jurisdiccion', 'ambito', 'tipo_gestion', 'total_estudiantes'],
        value_vars=list(perf_cols.keys()),
        var_name='nivel_desempeno_raw',
        value_name='cantidad_estudiantes'
    )

    df_melted['nivel_desempeno'] = df_melted['nivel_desempeno_raw'].map(perf_cols)
    df_melted['porcentaje'] = df_melted['cantidad_estudiantes'] / df_melted['total_estudiantes'] * 100

    df_final = df_melted[['jurisdiccion', 'ambito', 'tipo_gestion', 'nivel_desempeno', 'porcentaje']].copy()
    df_final['anio_evaluacion'] = 2024
    df_final['nivel_educativo'] = 'Secundario'
    df_final['anio_escolar'] = '5to año / 6to año'

    df_final = df_final.dropna(subset=['porcentaje'])
    print(f"Dimensiones del dataset limpio final (formato largo): {df_final.shape}")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df_final.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Dataset procesado guardado exitosamente en: {output_file}")

if __name__ == "__main__":
    clean_data()
