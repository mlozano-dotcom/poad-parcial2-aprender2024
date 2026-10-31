import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def generate_plots():
    input_file = os.path.join("data", "aprender2024_matematica.csv")
    graphics_dir = "graficos"
    os.makedirs(graphics_dir, exist_ok=True)

    print(f"Cargando dataset limpio desde: {input_file}")
    df = pd.read_csv(input_file, sep=',', encoding='utf-8')

    print("Generando gráfico de barras de Matplotlib para la provincia de Mendoza...")

    df_mza = df[df['jurisdiccion'].str.upper() == 'MENDOZA']
    levels_order = ['Por debajo del básico', 'Básico', 'Satisfactorio', 'Avanzado']
    porcentajes = [df_mza[df_mza['nivel_desempeno'] == level]['porcentaje'].mean() for level in levels_order]

    plt.figure(figsize=(10, 6))
    colors = ['#e74c3c', '#f39c12', '#2ecc71', '#27ae60']
    bars = plt.bar(levels_order, porcentajes, color=colors, edgecolor='none', width=0.6, zorder=3)

    plt.title('Desempeño en Matemática — Mendoza — Operativo Aprender 2024', fontsize=14, fontweight='bold', pad=20, color='#1e293b')
    plt.xlabel('Nivel de desempeño', fontsize=12, labelpad=10, color='#475569')
    plt.ylabel('Porcentaje de estudiantes (%)', fontsize=12, labelpad=10, color='#475569')

    plt.grid(axis='y', linestyle='--', alpha=0.5, zorder=0)
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')
    ax.tick_params(axis='both', colors='#475569')
    plt.ylim(0, 100)

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height + 2,
                 f'{height:.2f}%', ha='center', va='bottom',
                 fontsize=10, fontweight='bold', color='#334155')

    plt.tight_layout()
    bar_chart_path = os.path.join(graphics_dir, "barras_desempeno_mendoza.png")
    plt.savefig(bar_chart_path, dpi=150)
    plt.close()
    print(f"Gráfico de barras de Mendoza guardado en: {bar_chart_path}")

    print("Generando mapa de calor de Seaborn por Provincia y Tipo de Gestión...")

    df_ok = df[df['nivel_desempeno'].isin(['Satisfactorio', 'Avanzado'])]

    pivot = (df_ok.groupby(['jurisdiccion', 'tipo_gestion', 'ambito'])['porcentaje'].sum()
                  .groupby(['jurisdiccion', 'tipo_gestion']).mean()
                  .unstack('tipo_gestion'))

    pivot = pivot.loc[pivot.mean(axis=1).sort_values(ascending=False).index]

    sns.set_theme(style='whitegrid')
    plt.figure(figsize=(10, 12))
    sns.heatmap(
        pivot,
        annot=True,
        fmt='.1f',
        cmap='RdYlGn',
        linewidths=0.5,
        linecolor='#cbd5e1',
        cbar_kws={'label': '% Satisfactorio + Avanzado'},
        annot_kws={'fontsize': 10, 'weight': 'bold'}
    )

    plt.title('Desempeño Matemática por Provincia y Tipo de Gestión\n% Nivel Satisfactorio + Avanzado — Operativo Aprender 2024',
              fontsize=13, fontweight='bold', pad=25, color='#1e293b')
    plt.xlabel('Tipo de Gestión', fontsize=11, labelpad=12, color='#475569')
    plt.ylabel('Provincia', fontsize=11, labelpad=12, color='#475569')
    plt.xticks(fontsize=10, fontweight='bold')
    plt.yticks(fontsize=9)

    plt.tight_layout()
    heatmap_path = os.path.join(graphics_dir, "heatmap_gestion_provincia.png")
    plt.savefig(heatmap_path, dpi=150)
    plt.close()
    print(f"Mapa de calor de Seaborn guardado en: {heatmap_path}")

if __name__ == "__main__":
    generate_plots()
