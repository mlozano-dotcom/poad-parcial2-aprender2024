import os
import base64
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Parcial 2: backend de análisis (estadística + red neuronal)
from src.analysis import ejecutar_analisis, predecir, NIVELES

external_stylesheets = [
    'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap'
]
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Dashboard Aprender 2024 — Desempeño en Matemática"

file_path = os.path.join("data", "aprender2024_matematica.csv")
df = pd.read_csv(file_path)

df_ok = df[df['nivel_desempeno'].isin(['Satisfactorio', 'Avanzado'])].copy()

def get_base64_image(image_filename):
    image_path = os.path.join("graficos", image_filename)
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
    return ""

national_avg = df_ok.groupby(['jurisdiccion', 'tipo_gestion', 'ambito'])['porcentaje'].sum().mean()

mendoza_avg = df_ok[df_ok['jurisdiccion'] == 'Mendoza'].groupby(['tipo_gestion', 'ambito'])['porcentaje'].sum().mean()

prov_series = df_ok.groupby(['jurisdiccion', 'tipo_gestion', 'ambito'])['porcentaje'].sum().groupby('jurisdiccion').mean()
best_prov_name = prov_series.idxmax()
best_prov_pct = prov_series.max()

opciones_gestion = [{'label': 'Todos', 'value': 'Todos'}] + [
    {'label': g, 'value': g} for g in sorted(df['tipo_gestion'].unique())
]

def crear_tarjeta_kpi(titulo, valor, descripcion, color_valor):
    return html.Div(
        className="kpi-card",
        children=[
            html.P(titulo, className="kpi-title"),
            html.H2(valor, className="kpi-value", style={'color': color_valor}),
            html.P(descripcion, className="kpi-desc")
        ]
    )

# ---------------------------------------------------------------------------
# PARCIAL 2 — Resultados del backend
# Se calculan una sola vez, al iniciar el dashboard.
# ---------------------------------------------------------------------------
resultados = ejecutar_analisis(df)
ancho = resultados['ancho']
prueba_gestion = resultados['prueba_gestion']
prueba_ambito = resultados['prueba_ambito']
metricas = resultados['metricas']
modelo = resultados['modelo']

# Colores fijos para cada grupo (los mismos en todos los gráficos)
COLORES_GRUPOS = {
    'Estatal': '#38bdf8', 'Privado': '#34d399',
    'Rural': '#f59e0b', 'Urbano': '#a78bfa'
}

def formatear_p(p_valor):
    """Muestra el p-valor de forma legible."""
    return "p < 0,001" if p_valor < 0.001 else f"p = {p_valor:.3f}"

def describir_prueba(prueba):
    """Texto corto para la tarjeta KPI de cada prueba estadística."""
    conclusion = "diferencia significativa" if prueba['significativa'] else "diferencia no significativa"
    return f"{formatear_p(prueba['p_valor'])} · {conclusion}"

def tamano_efecto(d):
    """Interpretación habitual de la d de Cohen."""
    d = abs(d)
    if d >= 0.8:
        return "efecto grande"
    if d >= 0.5:
        return "efecto mediano"
    if d >= 0.2:
        return "efecto pequeño"
    return "efecto despreciable"

def aplicar_estilo(fig, titulo):
    """Aplica el tema oscuro del tablero a cualquier figura de Plotly."""
    fig.update_layout(
        title=titulo,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family='"Inter", sans-serif',
        font_color='#cbd5e1',
        title_font_family='"Outfit", sans-serif',
        title_font_size=15,
        title_font_color='#f8fafc',
        margin=dict(l=10, r=10, t=50, b=10),
        legend_title_text='',
        legend=dict(orientation='h', yanchor='top', y=0.99, xanchor='left', x=0.01,
                    bgcolor='rgba(15,23,42,0.7)'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)', zerolinecolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)', zerolinecolor='rgba(255,255,255,0.1)')
    )
    return fig

def titulo_seccion(titulo, subtitulo):
    return html.Div(
        className="section-heading",
        children=[html.H2(titulo), html.P(subtitulo)]
    )

def etiqueta(texto):
    return html.Label(texto, style={'fontSize': '12px', 'fontWeight': '500', 'color': '#94a3b8', 'display': 'block', 'marginBottom': '6px'})

def opciones(columna):
    return [{'label': v, 'value': v} for v in sorted(ancho[columna].unique())]

# Gráfico fijo de validación: lo real contra lo que predijo la red
tabla_val = resultados['tabla_validacion']
fig_validacion = px.scatter(
    tabla_val, x='real', y='predicho', color='tipo_gestion',
    color_discrete_map=COLORES_GRUPOS,
    hover_data={'jurisdiccion': True, 'ambito': True, 'real': ':.1f', 'predicho': ':.1f'},
    labels={'real': '% óptimo real', 'predicho': '% óptimo predicho por la red', 'tipo_gestion': 'Gestión'}
)
limite = max(tabla_val['real'].max(), tabla_val['predicho'].max()) + 3
fig_validacion.add_shape(
    type='line', x0=0, y0=0, x1=limite, y1=limite,
    line=dict(color='#64748b', dash='dash')
)
fig_validacion.update_traces(marker=dict(size=10, opacity=0.85, line=dict(width=1, color='#0f172a')))
aplicar_estilo(fig_validacion, "Validación: valor real vs. valor predicho (datos no vistos)")

app.layout = html.Div(
    style={
        'backgroundColor': '#0f172a',
        'color': '#f8fafc',
        'fontFamily': '"Inter", sans-serif',
        'minHeight': '100vh',
        'padding': '30px 40px',
        'margin': '0'
    },
    children=[
        html.Header(
            className="dashboard-header",
            children=[
                html.Div(children=[
                    html.H1(
                        "Desempeño en Matemática — Operativo Aprender 2024",
                        style={
                            'fontFamily': '"Outfit", sans-serif',
                            'fontSize': '28px',
                            'fontWeight': '700',
                            'margin': '0 0 5px 0',
                            'background': 'linear-gradient(to right, #06b6d4, #10b981)',
                            '-webkit-background-clip': 'text',
                            '-webkit-text-fill-color': 'transparent'
                        }
                    ),
                    html.P(
                        "Instituto Superior Manuel Belgrano | Tecnicatura en Ciencia de Datos e IA",
                        style={'fontSize': '14px', 'color': '#94a3b8', 'margin': '0'}
                    )
                ]),
                html.Div(
                    className="materia-badge",
                    children=[
                        html.Span("Materia: ", style={'fontWeight': 'bold', 'color': '#06b6d4'}),
                        "Programación Orientada al Análisis de Datos"
                    ]
                )
            ]
        ),
        
        html.Main(
            children=[
                html.Section(
                    className="grid-kpis",
                    children=[
                        crear_tarjeta_kpi(
                            "PROMEDIO NACIONAL (SATISF. + AVANZ.)",
                            f"{national_avg:.2f}%",
                            "Estudiantes con desempeño óptimo en el país",
                            "#38bdf8"
                        ),
                        crear_tarjeta_kpi(
                            "PROMEDIO MENDOZA (SATISF. + AVANZ.)",
                            f"{mendoza_avg:.2f}%",
                            "Estudiantes con desempeño óptimo en la provincia",
                            "#34d399"
                        ),
                        crear_tarjeta_kpi(
                            "PROVINCIA LÍDER",
                            f"{best_prov_pct:.2f}%",
                            best_prov_name,
                            "#f43f5e"
                        )
                    ]
                ),
                
                html.Section(
                    className="main-panel",
                    children=[
                        html.Div(
                            style={
                                'display': 'flex',
                                'justifyContent': 'space-between',
                                'alignItems': 'center',
                                'flexWrap': 'wrap',
                                'gap': '15px',
                                'marginBottom': '20px'
                            },
                            children=[
                                html.Div(children=[
                                    html.H3("Ranking Nacional por Nivel de Desempeño", style={'fontSize': '18px', 'fontWeight': '600', 'margin': '0 0 5px 0', 'fontFamily': '"Outfit", sans-serif'}),
                                    html.P("Compara el porcentaje de estudiantes en los niveles Satisfactorio y Avanzado.", style={'fontSize': '13px', 'color': '#94a3b8', 'margin': '0'})
                                ]),
                                html.Div(
                                    style={'width': '260px'},
                                    children=[
                                        html.Label("Filtrar por tipo de gestión:", style={'fontSize': '12px', 'fontWeight': '500', 'color': '#94a3b8', 'display': 'block', 'marginBottom': '6px'}),
                                        dcc.Dropdown(
                                            id='filtro-gestion',
                                            options=opciones_gestion,
                                            value='Todos',
                                            clearable=False,
                                            className='dash-dropdown'
                                        )
                                    ]
                                )
                            ]
                        ),
                        
                        dcc.Graph(
                            id='ranking-provincias',
                            config={'displayModeBar': False},
                            style={'height': '650px'}
                        )
                    ]
                ),
                
                html.Section(
                    className="grid-static-plots",
                    children=[
                        html.Div(
                            className="main-panel",
                            style={'marginBottom': '0'},
                            children=[
                                html.H3("Mendoza: Distribución de Desempeño", style={'fontSize': '16px', 'fontWeight': '600', 'margin': '0 0 10px 0', 'fontFamily': '"Outfit", sans-serif'}),
                                html.P("Gráfico estático generado con Matplotlib que muestra el promedio de estudiantes en cada nivel en la provincia de Mendoza.", style={'fontSize': '12px', 'color': '#94a3b8', 'marginBottom': '20px'}),
                                html.Div(
                                    id='matplotlib-container',
                                    style={'display': 'flex', 'justifyContent': 'center'},
                                    children=[
                                        html.Img(
                                            id='matplotlib-img',
                                            style={'maxWidth': '100%', 'borderRadius': '10px', 'boxShadow': '0 4px 15px rgba(0,0,0,0.2)'}
                                        )
                                    ]
                                )
                            ]
                        ),
                        html.Div(
                            className="main-panel",
                            style={'marginBottom': '0'},
                            children=[
                                html.H3("Comparativa por Gestión (Provincia x Sector)", style={'fontSize': '16px', 'fontWeight': '600', 'margin': '0 0 10px 0', 'fontFamily': '"Outfit", sans-serif'}),
                                html.P("Mapa de calor estático generado con Seaborn que compara el porcentaje Satisfactorio + Avanzado según el sector estatal y privado.", style={'fontSize': '12px', 'color': '#94a3b8', 'marginBottom': '20px'}),
                                html.Div(
                                    id='seaborn-container',
                                    style={'display': 'flex', 'justifyContent': 'center'},
                                    children=[
                                        html.Img(
                                            id='seaborn-img',
                                            style={'maxWidth': '100%', 'borderRadius': '10px', 'boxShadow': '0 4px 15px rgba(0,0,0,0.2)'}
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                ),

                # ===========================================================
                # PARCIAL 2 — SECCIÓN A: ANÁLISIS ESTADÍSTICO
                # ===========================================================
                titulo_seccion(
                    "Análisis estadístico",
                    "Descripción de los datos y prueba t de Welch (numpy + scipy): "
                    "¿las diferencias entre grupos son reales o pueden ser casualidad?"
                ),
                html.Section(
                    className="grid-kpis",
                    children=[
                        crear_tarjeta_kpi(
                            "BRECHA PRIVADO − ESTATAL",
                            f"+{prueba_gestion['diferencia']:.1f} pp",
                            describir_prueba(prueba_gestion),
                            "#34d399"
                        ),
                        crear_tarjeta_kpi(
                            "BRECHA URBANO − RURAL",
                            f"+{prueba_ambito['diferencia']:.1f} pp",
                            describir_prueba(prueba_ambito),
                            "#a78bfa"
                        ),
                        crear_tarjeta_kpi(
                            "TAMAÑO DEL EFECTO (d DE COHEN)",
                            f"{prueba_gestion['d_cohen']:.2f}",
                            f"Gestión: {tamano_efecto(prueba_gestion['d_cohen'])} · "
                            f"Ámbito: {tamano_efecto(prueba_ambito['d_cohen'])} ({prueba_ambito['d_cohen']:.2f})",
                            "#f59e0b"
                        )
                    ]
                ),
                html.Section(
                    className="grid-static-plots",
                    style={'marginBottom': '30px'},
                    children=[
                        html.Div(
                            className="main-panel",
                            style={'marginBottom': '0'},
                            children=[
                                html.Div(
                                    style={'width': '260px', 'marginBottom': '10px'},
                                    children=[
                                        etiqueta("Comparar según:"),
                                        dcc.Dropdown(
                                            id='filtro-comparacion',
                                            options=[
                                                {'label': 'Tipo de gestión', 'value': 'tipo_gestion'},
                                                {'label': 'Ámbito', 'value': 'ambito'}
                                            ],
                                            value='tipo_gestion',
                                            clearable=False,
                                            className='dash-dropdown'
                                        )
                                    ]
                                ),
                                dcc.Graph(id='grafico-distribucion', config={'displayModeBar': False}, style={'height': '420px'})
                            ]
                        ),
                        html.Div(
                            className="main-panel",
                            style={'marginBottom': '0'},
                            children=[
                                html.H3("Estadísticos descriptivos del % óptimo", className="panel-title"),
                                html.P("Cada fila resume los grupos provincia × ámbito × gestión que pertenecen a esa categoría.", className="panel-desc"),
                                html.Div(id='tabla-descriptiva'),
                                html.Div(id='texto-prueba', className="nota-prueba")
                            ]
                        )
                    ]
                ),

                # ===========================================================
                # PARCIAL 2 — SECCIÓN B: APRENDIZAJE PROFUNDO
                # ===========================================================
                titulo_seccion(
                    "Red neuronal — simulador de desempeño",
                    "Perceptrón multicapa (scikit-learn) con 2 capas ocultas de 32 y 16 neuronas. "
                    "Aprende a estimar los 4 niveles de desempeño a partir de la provincia, el ámbito y la gestión."
                ),
                html.Section(
                    className="grid-kpis",
                    children=[
                        crear_tarjeta_kpi(
                            "ERROR MEDIO DE LA RED (MAE)",
                            f"{metricas['mae']:.2f} pp",
                            "Cuánto se equivoca en promedio con datos que no vio",
                            "#38bdf8"
                        ),
                        crear_tarjeta_kpi(
                            "ERROR DE LA LÍNEA DE BASE",
                            f"{metricas['mae_base']:.2f} pp",
                            "Si siempre se predijera el promedio general",
                            "#94a3b8"
                        ),
                        crear_tarjeta_kpi(
                            "COEFICIENTE R²",
                            f"{metricas['r2']:.2f}",
                            f"La red explica el {metricas['r2'] * 100:.0f}% de la variación entre grupos",
                            "#34d399"
                        )
                    ]
                ),
                html.Section(
                    className="grid-static-plots",
                    children=[
                        html.Div(
                            className="main-panel",
                            style={'marginBottom': '0'},
                            children=[
                                html.H3("Simulador: elegí un grupo y mirá qué predice la red", className="panel-title"),
                                html.Div(
                                    className="filtros-simulador",
                                    children=[
                                        html.Div([etiqueta("Provincia:"), dcc.Dropdown(id='sim-provincia', options=opciones('jurisdiccion'), value='Mendoza', clearable=False, className='dash-dropdown')]),
                                        html.Div([etiqueta("Ámbito:"), dcc.Dropdown(id='sim-ambito', options=opciones('ambito'), value='Urbano', clearable=False, className='dash-dropdown')]),
                                        html.Div([etiqueta("Gestión:"), dcc.Dropdown(id='sim-gestion', options=opciones('tipo_gestion'), value='Estatal', clearable=False, className='dash-dropdown')])
                                    ]
                                ),
                                dcc.Graph(id='grafico-simulador', config={'displayModeBar': False}, style={'height': '380px'}),
                                html.Div(id='texto-simulador', className="nota-prueba")
                            ]
                        ),
                        html.Div(
                            className="main-panel",
                            style={'marginBottom': '0'},
                            children=[
                                html.H3("¿Qué tan bien predice la red?", className="panel-title"),
                                html.P("Cada punto es un grupo que la red predijo sin haberlo visto en el entrenamiento "
                                       "(validación cruzada de 5 partes). Cuanto más cerca de la línea punteada, mejor.",
                                       className="panel-desc"),
                                dcc.Graph(figure=fig_validacion, config={'displayModeBar': False}, style={'height': '440px'})
                            ]
                        )
                    ]
                )
            ]
        ),

        html.Footer(
            className="dashboard-footer",
            children=[
                html.P("Examen Parcial N° 2 — Programación Orientada al Análisis de Datos (POAD)"),
                html.P("Datos oficiales del Operativo Aprender 2024 (datos.gob.ar)", style={'fontSize': '10px', 'marginTop': '5px'})
            ]
        )
    ]
)

@app.callback(
    [
        Output('ranking-provincias', 'figure'),
        Output('matplotlib-img', 'src'),
        Output('seaborn-img', 'src')
    ],
    [Input('filtro-gestion', 'value')]
)
def update_dashboard(gestion):
    if not gestion or gestion == 'Todos':
        df_filtered = df_ok
        title_suffix = " (Gestión Pública y Privada)"
        group_cols = ['jurisdiccion', 'tipo_gestion', 'ambito']
    else:
        df_filtered = df_ok[df_ok['tipo_gestion'] == gestion]
        title_suffix = f" (Gestión: {gestion})"
        group_cols = ['jurisdiccion', 'ambito']
        
    df_rank = (df_filtered.groupby(group_cols)['porcentaje'].sum()
                          .groupby('jurisdiccion').mean()
                          .sort_values()
                          .reset_index(name='porcentaje'))
    
    fig = px.bar(
        df_rank,
        x='porcentaje',
        y='jurisdiccion',
        orientation='h',
        color='porcentaje',
        color_continuous_scale='RdYlGn',
        range_color=[0, 45],
        labels={'porcentaje': '% Estudiantes (Satisf. + Avanz.)', 'jurisdiccion': 'Provincia'},
        title=f"Ranking de Provincias — % Nivel Satisfactorio + Avanzado{title_suffix}"
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family='"Inter", sans-serif',
        font_color='#cbd5e1',
        title_font_family='"Outfit", sans-serif',
        title_font_size=15,
        title_font_color='#f8fafc',
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.05)',
            zerolinecolor='rgba(255,255,255,0.1)',
            ticksuffix='%',
            range=[0, 45]
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.05)',
            categoryorder='total ascending'
        ),
        coloraxis_colorbar=dict(
            title='% Desempeño',
            thicknessmode="pixels", thickness=15,
            lenmode="pixels", len=300,
            yanchor="middle", y=0.5
        )
    )
    
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>%{x:.2f}% de los estudiantes<extra></extra>"
    )
    
    matplotlib_src = get_base64_image("barras_desempeno_mendoza.png")
    seaborn_src = get_base64_image("heatmap_gestion_provincia.png")
    
    return fig, matplotlib_src, seaborn_src


# ---------------------------------------------------------------------------
# PARCIAL 2 — Callback del análisis estadístico
# ---------------------------------------------------------------------------
@app.callback(
    [
        Output('grafico-distribucion', 'figure'),
        Output('tabla-descriptiva', 'children'),
        Output('texto-prueba', 'children')
    ],
    [Input('filtro-comparacion', 'value')]
)
def update_estadistica(columna):
    if columna == 'ambito':
        descripcion = resultados['desc_ambito']
        prueba = prueba_ambito
        nombre = "ámbito"
    else:
        descripcion = resultados['desc_gestion']
        prueba = prueba_gestion
        nombre = "tipo de gestión"

    # Diagrama de caja: muestra la distribución completa de cada grupo
    fig = px.box(
        ancho, x=columna, y='optimo', color=columna, points='all',
        color_discrete_map=COLORES_GRUPOS,
        hover_data={'jurisdiccion': True, 'optimo': ':.1f'},
        labels={'optimo': '% Satisfactorio + Avanzado', columna: nombre.capitalize()}
    )
    aplicar_estilo(fig, f"Distribución del % óptimo según {nombre}")
    fig.update_layout(showlegend=False)
    fig.update_yaxes(ticksuffix='%')

    # Tabla de estadísticos descriptivos
    encabezados = ['Grupo', 'n', 'Media', 'Mediana', 'Desvío', 'Mín.', 'Máx.']
    filas = []
    for _, fila in descripcion.iterrows():
        filas.append(html.Tr([
            html.Td(fila['grupo'], style={'color': COLORES_GRUPOS[fila['grupo']], 'fontWeight': '600'}),
            html.Td(int(fila['n'])),
            html.Td(f"{fila['media']:.2f}%"),
            html.Td(f"{fila['mediana']:.2f}%"),
            html.Td(f"{fila['desvio']:.2f}"),
            html.Td(f"{fila['minimo']:.2f}%"),
            html.Td(f"{fila['maximo']:.2f}%")
        ]))
    tabla = html.Table(
        className="stats-table",
        children=[
            html.Thead(html.Tr([html.Th(e) for e in encabezados])),
            html.Tbody(filas)
        ]
    )

    # Conclusión de la prueba t de Welch, en palabras
    texto = [
        html.Strong(f"Prueba t de Welch — {prueba['grupo_a']} vs. {prueba['grupo_b']}: "),
        f"la diferencia de medias es de {prueba['diferencia']:.2f} puntos "
        f"(intervalo de confianza del 95%: {prueba['ic_bajo']:.2f} a {prueba['ic_alto']:.2f}), "
        f"t = {prueba['t']:.2f}, {formatear_p(prueba['p_valor'])}. ",
        html.Strong("Conclusión: "),
        (f"la diferencia es estadísticamente significativa ({tamano_efecto(prueba['d_cohen'])}, d = {prueba['d_cohen']:.2f})."
         if prueba['significativa'] else
         "no hay evidencia suficiente para afirmar que los grupos sean distintos.")
    ]
    return fig, tabla, texto


# ---------------------------------------------------------------------------
# PARCIAL 2 — Callback del simulador de la red neuronal
# ---------------------------------------------------------------------------
@app.callback(
    [
        Output('grafico-simulador', 'figure'),
        Output('texto-simulador', 'children')
    ],
    [
        Input('sim-provincia', 'value'),
        Input('sim-ambito', 'value'),
        Input('sim-gestion', 'value')
    ]
)
def update_simulador(provincia, ambito, gestion):
    prediccion = predecir(modelo, provincia, ambito, gestion)

    datos = pd.DataFrame({
        'nivel': NIVELES,
        'porcentaje': [prediccion[n] for n in NIVELES],
        'fuente': 'Predicción de la red'
    })

    # ¿Existe ese grupo en los datos reales? Si existe, lo mostramos al lado
    real = ancho[(ancho['jurisdiccion'] == provincia) &
                 (ancho['ambito'] == ambito) &
                 (ancho['tipo_gestion'] == gestion)]
    if len(real) > 0:
        datos_reales = pd.DataFrame({
            'nivel': NIVELES,
            'porcentaje': [real.iloc[0][n] for n in NIVELES],
            'fuente': 'Dato real'
        })
        datos = pd.concat([datos, datos_reales])

    fig = px.bar(
        datos, x='nivel', y='porcentaje', color='fuente', barmode='group',
        color_discrete_map={'Predicción de la red': '#38bdf8', 'Dato real': '#64748b'},
        labels={'nivel': 'Nivel de desempeño', 'porcentaje': '% de estudiantes', 'fuente': ''},
        text_auto='.1f'
    )
    aplicar_estilo(fig, f"{provincia} · {ambito} · {gestion}")
    fig.update_layout(legend=dict(xanchor='right', x=0.99))   # leyenda a la derecha
    fig.update_yaxes(ticksuffix='%', range=[0, 105])
    fig.update_traces(textposition='outside', cliponaxis=False)

    optimo_predicho = prediccion['Satisfactorio'] + prediccion['Avanzado']
    if len(real) > 0:
        optimo_real = real.iloc[0]['optimo']
        texto = (f"La red estima {optimo_predicho:.1f}% en niveles Satisfactorio + Avanzado. "
                 f"El dato real es {optimo_real:.1f}% (diferencia: {abs(optimo_predicho - optimo_real):.1f} puntos).")
    else:
        texto = (f"Esta combinación no existe en los datos del Operativo Aprender 2024. "
                 f"La red estima {optimo_predicho:.1f}% en niveles Satisfactorio + Avanzado a partir de lo que aprendió de grupos parecidos.")
    return fig, texto


if __name__ == '__main__':
    app.run(debug=True, port=8050)
