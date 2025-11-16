import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import os
import numpy as np
from datetime import datetime, timedelta
from dash.dependencies import Input, Output, State
from dash import Dash, html, dcc, callback


# Dashboard Interattiva E-Lithium S.p.A. - Versione 2.0
# Sistema di monitoraggio e analisi dei dati di produzione
# Visualizzazione real-time delle metriche aziendali

# Lettura e preparazione dati dal file CSV
df = pd.read_csv("./data/e_lithium_data.csv")
df["data"] = pd.to_datetime(df["data"])

# Inizializzazione dell'applicazione interattiva
app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
app.title = "E-Lithium S.p.A"
app.config.suppress_callback_exceptions = True 

navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand(
                html.Button(
                    "E-Lithium S.p.A.",
                    id="brand-button",
                    style={
                        "background": "none",
                        "border": "none",
                        "color": "white",
                        "fontSize": "1.25rem",
                        "cursor": "pointer",
                        "fontWeight": "500"
                    }
                ),
                href="#"
            ),
        ],
        fluid=True,
    ),
    color="dark",
    dark=True,
    className="mb-4",
)


# Funzioni di supporto per elaborazione dati e visualizzazione
def calcola_kpi(df):
    """Calcolo dei KPI con analisi di trend nel tempo"""
    if len(df) < 2:
        return {
            "avg_profitto": 0, "trend_profitto": 0,
            "avg_purezza": 0, "trend_purezza": 0,
            "avg_produzione": 0, "trend_produzione": 0,
            "avg_margine": 0, "trend_margine": 0
        }
    
    mid = len(df) // 2
    prima_meta = df.iloc[:mid]
    seconda_meta = df.iloc[mid:]
    
    avg_profitto = df["profitto_eur"].mean()
    avg_profitto_prima = prima_meta["profitto_eur"].mean()
    avg_profitto_dopo = seconda_meta["profitto_eur"].mean()
    trend_profitto = ((avg_profitto_dopo - avg_profitto_prima) / abs(avg_profitto_prima) * 100) if avg_profitto_prima != 0 else 0
    
    avg_purezza = df["purezza_%"].mean()
    avg_purezza_prima = prima_meta["purezza_%"].mean()
    avg_purezza_dopo = seconda_meta["purezza_%"].mean()
    trend_purezza = ((avg_purezza_dopo - avg_purezza_prima) / avg_purezza_prima * 100) if avg_purezza_prima != 0 else 0
    
    avg_produzione = df["litio_estratto_kg"].mean()
    avg_produzione_prima = prima_meta["litio_estratto_kg"].mean()
    avg_produzione_dopo = seconda_meta["litio_estratto_kg"].mean()
    trend_produzione = ((avg_produzione_dopo - avg_produzione_prima) / avg_produzione_prima * 100) if avg_produzione_prima != 0 else 0
    
    avg_margine = df["margine_%"].mean()
    avg_margine_prima = prima_meta["margine_%"].mean()
    avg_margine_dopo = seconda_meta["margine_%"].mean()
    trend_margine = ((avg_margine_dopo - avg_margine_prima) / avg_margine_prima * 100) if avg_margine_prima != 0 else 0
    
    return {
        "avg_profitto": avg_profitto, "trend_profitto": trend_profitto,
        "avg_purezza": avg_purezza, "trend_purezza": trend_purezza,
        "avg_produzione": avg_produzione, "trend_produzione": trend_produzione,
        "avg_margine": avg_margine, "trend_margine": trend_margine
    }


def create_kpi_card(title, value, trend, color, trend_value):
    """Creazione delle card KPI con indicatori visivi per trend e performance"""
    trend_color = "success" if trend_value >= 0 else "danger"
    trend_icon = "↑" if trend_value >= 0 else "↓"
    
    # Mapping emoji per le diverse metriche
    emoji_map = {
        "Produzione": "📦",
        "Purezza": "✨",
        "Profitto": "💰",
        "Margine": "📊"
    }
    emoji = emoji_map.get(title.split()[0], "📈")
    
    # Descrizioni user-friendly
    descriptions = {
        "Produzione Media": "Quantità media di litio estratta ogni giorno",
        "Purezza Media": "Qualità media del litio estratto (più alta è meglio)",
        "Profitto Medio": "Guadagno medio giornaliero dopo i costi",
        "Margine Medio": "Percentuale di guadagno su ogni euro di ricavi"
    }
    description = descriptions.get(title, "")
    
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Span(emoji, style={"fontSize": "2rem", "marginRight": "15px"}),
                html.Div([
                    html.H6(title, className="mb-1 fw-bold"),
                    html.H4(value, className="mb-2"),
                    html.Small(description, className="text-muted d-block mb-2"),
                    html.Span([
                        html.I(className="fas fa-arrow-up me-2") if trend_value >= 0 else html.I(className="fas fa-arrow-down me-2"),
                        trend
                    ], className=f"text-{trend_color} fw-bold small")
                ], style={"flex": "1"})
            ], style={"display": "flex", "alignItems": "flex-start"})
        ])
    ], color=color, inverse=True, className="h-100")


def detect_outliers(series, method='iqr'):
    """Identificazione di valori anomali utilizzando il metodo dell'intervallo interquartile"""
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return (series < lower_bound) | (series > upper_bound)


# Struttura principale dell'interfaccia utente
app.layout = dbc.Container([
    navbar,
    html.H1("Sistema di Monitoraggio", className="text-center my-4"),

    dcc.Tabs(
        id="tabs",
        value="tab-dashboard",
        children=[
            dcc.Tab(
                label="📊 Dashboard Operativa",
                value="tab-dashboard",
                style={'backgroundColor': '#2B3E50', 'color': '#fff', 'border': '1px solid #4E5D6C'},
                selected_style={'backgroundColor': '#4E5D6C', 'color': '#fff', 'border': '1px solid #4E5D6C'}
            ),
            dcc.Tab(
                label="🏭 Scheda Aziendale",
                value="tab-about",
                style={'backgroundColor': '#2B3E50', 'color': '#fff', 'border': '1px solid #4E5D6C'},
                selected_style={'backgroundColor': '#4E5D6C', 'color': '#fff', 'border': '1px solid #4E5D6C'}
            ),
            dcc.Tab(
                label="🔮 What-If Simulation",
                value="tab-whatif",
                style={'backgroundColor': '#2B3E50', 'color': '#fff', 'border': '1px solid #4E5D6C'},
                selected_style={'backgroundColor': '#4E5D6C', 'color': '#fff', 'border': '1px solid #4E5D6C'}
            ),
            dcc.Tab(
                label="📈 Analisi Statistica",
                value="tab-analysis",
                style={'backgroundColor': '#2B3E50', 'color': '#fff', 'border': '1px solid #4E5D6C'},
                selected_style={'backgroundColor': '#4E5D6C', 'color': '#fff', 'border': '1px solid #4E5D6C'}
            ),
            dcc.Tab(
                label="💻 Codice Sorgente", 
                value="tab-source",
                style={'backgroundColor': '#2B3E50', 'color': '#fff', 'border': '1px solid #4E5D6C'},
                selected_style={'backgroundColor': '#4E5D6C', 'color': '#fff', 'border': '1px solid #4E5D6C'}
            ),
        ],
        style={
            "fontWeight": "bold",
            "fontSize": "16px",
            "marginBottom": "2rem"
        }
    ),

    # Gestione dello stato dei filtri applicati
    dcc.Store(id="date-picker", data={"start_date": None, "end_date": None}),
    dcc.Store(id="purezza-slider", data=[0, 100]),
    dcc.Store(id="profitto-slider", data=[0, 100000]),

    html.Div(id="tab-content"),
    
    # Sezione inferiore con informazioni aziendali
    html.Footer(
        dbc.Container([
            html.Hr(className="my-3"),
            dbc.Row([
                dbc.Col([
                    html.H6("Contatti", className="text-primary mb-2"),
                    html.P([
                        html.Span("Via Roma 123, Roma | "),
                        html.Span("Tel: +39 070 1234567 | "),
                        html.Span("info@e-lithium.it")
                    ], className="mb-0 small")
                ], width=6),
                dbc.Col(width=6, children=[
                    html.H6("Info Legali", className="text-primary mb-2"),
                    html.P([
                        "P.IVA: IT12345678901 | REA: CA-123456 | ",
                        "Cap. Soc.: € 5.000.000 i.v."
                    ], className="mb-0 small")
                ])
            ], className="mb-2"),
        ]), 
        className="mt-4 bg-dark text-light py-3"
    )
], fluid=True)


# Gestione degli eventi e aggiornamento dinamico dei componenti
@app.callback(
    Output("tabs", "value"),
    Input("brand-button", "n_clicks"),
    prevent_initial_call=True
)
def redirect_to_dashboard(n_clicks):
    """Reindirizza al dashboard quando clicchi sul brand"""
    if n_clicks:
        return "tab-dashboard"
    return "tab-dashboard"


@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value"),
    prevent_initial_call=False
)
def render_tab_content(tab):
    df_full = pd.read_csv("./data/e_lithium_data.csv")
    df_full["data"] = pd.to_datetime(df_full["data"])
    
    if tab == "tab-dashboard":
        return create_dashboard_tab(df_full, df_full)
    elif tab == "tab-about":
        return create_about_tab()
    elif tab == "tab-whatif":
        return create_whatif_tab(df_full)
    elif tab == "tab-analysis":
        return create_analysis_tab(df_full)
    elif tab == "tab-source":
        return create_source_tab()
    
    return html.Div("Tab non trovato")


def create_dashboard_tab(df, df_full):
    """Tab Dashboard principale con filtri e KPI dinamici"""
    kpi = calcola_kpi(df)
    
    start_date = df_full["data"].min()
    end_date = df_full["data"].max()
    purezza_range = [df_full["purezza_%"].min(), df_full["purezza_%"].max()]
    profitto_range = [df_full["profitto_eur"].min(), df_full["profitto_eur"].max()]
    
    return html.Div([
        dcc.Interval(id="aggiornamento", interval=10*1000, n_intervals=0),

        # Sezione di controllo per filtrare i dati per periodo e parametri
        dbc.Card([
            dbc.CardBody([
                html.H5("🔍 Filtri Interattivi", className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Periodo:", className="fw-bold"),
                        dcc.DatePickerRange(
                            id="date-range",
                            start_date=start_date,
                            end_date=end_date,
                            display_format="YYYY-MM-DD",
                            style={"width": "100%"}
                        )
                    ], md=4),
                    dbc.Col([
                        html.Label("Purezza (%)", className="fw-bold"),
                        dcc.RangeSlider(
                            id="purezza-range",
                            min=df_full["purezza_%"].min(),
                            max=df_full["purezza_%"].max(),
                            value=purezza_range,
                            marks={i: f"{i:.1f}" for i in np.linspace(df_full["purezza_%"].min(), df_full["purezza_%"].max(), 5)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], md=4),
                    dbc.Col([
                        html.Label("Profitto (€)", className="fw-bold"),
                        dcc.RangeSlider(
                            id="profitto-range",
                            min=df_full["profitto_eur"].min(),
                            max=df_full["profitto_eur"].max(),
                            value=profitto_range,
                            marks={i: f"€{i/1000:.0f}k" for i in np.linspace(df_full["profitto_eur"].min(), df_full["profitto_eur"].max(), 5)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], md=4),
                ])
            ])
        ], className="mb-4"),

        # Indicatori chiave di prestazione con trend e variazioni
        dbc.Row([
            dbc.Col(create_kpi_card(
                "📦 Produzione Media",
                f"{kpi['avg_produzione']:,.0f} kg/giorno",
                f"{kpi['trend_produzione']:+.1f}%",
                "primary",
                kpi['trend_produzione']
            ), width=3, className="mb-3"),
            dbc.Col(create_kpi_card(
                "✨ Purezza Media",
                f"{kpi['avg_purezza']:.2f}%",
                f"{kpi['trend_purezza']:+.1f}%",
                "success",
                kpi['trend_purezza']
            ), width=3, className="mb-3"),
            dbc.Col(create_kpi_card(
                "💰 Profitto Medio",
                f"€ {kpi['avg_profitto']:,.0f}",
                f"{kpi['trend_profitto']:+.1f}%",
                "info",
                kpi['trend_profitto']
            ), width=3, className="mb-3"),
            dbc.Col(create_kpi_card(
                "📊 Margine Medio",
                f"{kpi['avg_margine']:.2f}%",
                f"{kpi['trend_margine']:+.1f}%",
                "warning",
                kpi['trend_margine']
            ), width=3, className="mb-3"),
        ], className="mb-4"),

        # Serie temporali delle principali metriche operative
        dbc.Row([
            dbc.Col(dcc.Graph(id="time-produzione"), width=6),
            dbc.Col(dcc.Graph(id="time-profitto"), width=6),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col(dcc.Graph(id="time-purezza"), width=6),
            dbc.Col(dcc.Graph(id="time-margine"), width=6),
        ], className="mb-4"),

        # Visualizzazione multidimensionale delle relazioni tra variabili
        dbc.Row([
            dbc.Col(dcc.Graph(id="scatter-3d"), width=12),
        ], className="mb-4"),

        # Mappa di calore della matrice di correlazione
        dbc.Row([
            dbc.Col(dcc.Graph(id="heatmap-correlazioni"), width=12),
        ], className="mb-4"),

        # Grafici di distribuzione dei dati di produzione e profitto
        dbc.Row([
            dbc.Col(dcc.Graph(id="dist-produzione"), width=6),
            dbc.Col(dcc.Graph(id="dist-profitto"), width=6),
        ], className="mb-4"),
    ])


def create_about_tab():
    """Tab Info Aziendali"""
    return dbc.Container([
        html.H2("Chi è E-Lithium S.p.A.", className="mt-4"),
        html.P("""
            E-Lithium S.p.A. è una società mineraria italiana specializzata 
            nell'estrazione e raffinazione di litio ad alta purezza, destinato 
            alla produzione di batterie per veicoli elettrici e sistemi di 
            accumulo energetico di nuova generazione.
        """),
        html.H4("🌍 Mercato e Clienti"),
        html.P("""
            L'azienda rifornisce i principali produttori europei di celle agli ioni di litio,
            con partnership strategiche nel settore automobilistico, motociclistico e
            dell'elettronica di consumo.
        """),
        html.H4("⚙️ Processo Produttivo"),
        html.Ul([
            html.Li("Estrazione del minerale di spodumene dalle miniere sarde"),
            html.Li("Frantumazione e separazione meccanica del minerale grezzo"),
            html.Li("Purificazione chimica fino al 99,9% di purezza del litio"),
            html.Li("Controllo qualità e stoccaggio per la distribuzione ai clienti"),
        ]),
        html.H4("🏢 Dati Aziendali"),
        html.Ul([
            html.Li("Sede: Roma (Italia)"),
            html.Li("Dipendenti: 250"),
            html.Li("Capacità produttiva: 1.000 kg/giorno di litio raffinato"),
            html.Li("Fatturato annuo: €18 milioni"),
        ]),
        html.P("Ultimo aggiornamento: Novembre 2025", className="text-muted fst-italic")
    ])


def create_whatif_tab(df):
    """Tab Simulazione What-If"""
    return dbc.Container([
        html.H2("🔮 Pannello Simulazione What-If", className="mt-4 mb-4"),
        dbc.Card([
            dbc.CardBody([
                html.P("Analizza scenari futuri modificando i parametri di produzione"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Aumento Produzione (%):"),
                        dcc.Slider(
                            id="slider-prod",
                            min=-50, max=50, step=5,
                            value=0,
                            marks={i: f"{i}%" for i in range(-50, 51, 10)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], md=4),
                    dbc.Col([
                        html.Label("Variazione Prezzo (€/kg):"),
                        dcc.Slider(
                            id="slider-prezzo",
                            min=-30, max=30, step=5,
                            value=0,
                            marks={i: f"€{i}" for i in range(-30, 31, 10)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], md=4),
                    dbc.Col([
                        html.Label("Riduzione Costi (%):"),
                        dcc.Slider(
                            id="slider-costi",
                            min=-50, max=50, step=5,
                            value=0,
                            marks={i: f"{i}%" for i in range(-50, 51, 10)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], md=4),
                ])
            ])
        ]),
        html.Hr(),
        dbc.Row([
            dbc.Col(dcc.Graph(id="whatif-profitto"), width=6),
            dbc.Col(dcc.Graph(id="whatif-margine"), width=6),
        ], className="mt-4"),
    ])


def create_analysis_tab(df):
    """Tab Analisi Statistica Avanzata"""
    return dbc.Container([
        html.H2("📈 Analisi Statistica Avanzata", className="mt-4 mb-4"),
        
        dbc.Row([
            dbc.Col(dcc.Graph(id="correlazione-matrix"), width=6),
            dbc.Col(dcc.Graph(id="outliers-produzione"), width=6),
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                html.H5("Statistiche Descrittive"),
                html.Pre(id="stats-description", style={"backgroundColor": "#f5f5f5", "padding": "15px"})
            ], width=12),
        ]),
    ])


def create_source_tab():
    """Tab Codice Sorgente"""
    return dbc.Container([
        html.H2("Codice Sorgente", className="mt-4"),
        html.P([
            "Esplora il codice sorgente di questa dashboard su GitHub ",
            html.A([
                html.I(className="fab fa-github me-2"),
                "Iappelli-Leonardo/e-lithium"
            ], 
            href="https://github.com/Iappelli-Leonardo/e-lithium",
            className="text-decoration-none",
            target="_blank")
        ], className="lead"),
        dbc.Card([
            dbc.CardHeader("File Principali"),
            dbc.CardBody([
                html.Ul([
                    html.Li(html.A("e_lithium_dashboard.py", href="https://github.com/Iappelli-Leonardo/e-lithium/blob/main/dashboard/e_lithium_dashboard.py", target="_blank")),
                    html.Li(html.A("e_lithium_simulatore.py", href="https://github.com/Iappelli-Leonardo/e-lithium/blob/main/simulatore/e_lithium_simulatore.py", target="_blank"))
                ])
            ])
        ])
    ])


# Aggiornamento automatico dei grafici nel dashboard principale
@app.callback(
    [
        Output("time-produzione", "figure"),
        Output("time-profitto", "figure"),
        Output("time-purezza", "figure"),
        Output("time-margine", "figure"),
        Output("scatter-3d", "figure"),
        Output("heatmap-correlazioni", "figure"),
        Output("dist-produzione", "figure"),
        Output("dist-profitto", "figure"),
    ],
    Input("aggiornamento", "n_intervals"),
    prevent_initial_call=False
)
def update_dashboard_graphs(n):
    try:
        df = pd.read_csv("./data/e_lithium_data.csv")
        df["data"] = pd.to_datetime(df["data"])
        
        # Controllo della disponibilità e validità dei dati
        if len(df) == 0:
            empty_fig = go.Figure()
            empty_fig.add_annotation(text="Nessun dato disponibile")
            return [empty_fig] * 8
        
        # Serie temporali della produzione, profitto, purezza e margine
        fig_prod = px.line(df, x="data", y="litio_estratto_kg", 
                           title="Produzione Giornaliera (kg)",
                           markers=True)
        fig_prof = px.line(df, x="data", y="profitto_eur", 
                           title="Profitto Giornaliero (€)",
                           markers=True)
        fig_pure = px.line(df, x="data", y="purezza_%", 
                           title="Purezza Media (%)",
                           markers=True)
        fig_marg = px.line(df, x="data", y="margine_%", 
                           title="Margine Medio (%)",
                           markers=True)
        
        # Rappresentazione tridimensionale delle interazioni tra variabili produttive
        fig_3d = px.scatter_3d(df, x="litio_estratto_kg", y="purezza_%", 
                               z="profitto_eur",
                               color="margine_%",
                               title="Correlazione 3D: Produzione-Purezza-Profitto")
        
        # Heatmap Correlazioni
        # Calcolo delle correlazioni tra le principali metriche
        corr_cols = ["litio_estratto_kg", "purezza_%", "profitto_eur", "margine_%", "costi_eur"]
        corr_matrix = df[corr_cols].corr()
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_cols,
            y=corr_cols,
            colorscale="RdBu",
            zmid=0
        ))
        fig_heatmap.update_layout(title="Matrice di Correlazione")
        
        # Istogrammi che mostrano il comportamento distributivo dei dati di produzione e profitto
        fig_dist_prod = px.histogram(df, x="litio_estratto_kg", 
                                     nbins=30,
                                     title="Distribuzione Produzione")
        fig_dist_prof = px.histogram(df, x="profitto_eur", 
                                     nbins=30,
                                     title="Distribuzione Profitto")
        
        for fig in [fig_prod, fig_prof, fig_pure, fig_marg, fig_3d, fig_heatmap, fig_dist_prod, fig_dist_prof]:
            fig.update_layout(template="plotly_dark", hovermode="x unified")
        
        return fig_prod, fig_prof, fig_pure, fig_marg, fig_3d, fig_heatmap, fig_dist_prod, fig_dist_prof
    
    except Exception as e:
        print(f"Errore nei grafici dashboard: {str(e)}")
        empty_fig = go.Figure()
        empty_fig.add_annotation(text=f"Errore: {str(e)}")
        return [empty_fig] * 8


# Simulazione di scenari alternativi con variabili controllabili
@app.callback(
    [Output("whatif-profitto", "figure"), Output("whatif-margine", "figure")],
    [Input("slider-prod", "value"), Input("slider-prezzo", "value"), Input("slider-costi", "value")],
    prevent_initial_call=False
)
def update_whatif(prod_change, prezzo_change, costi_change):
    try:
        df = pd.read_csv("./data/e_lithium_data.csv")
        df["data"] = pd.to_datetime(df["data"])
        
        if len(df) == 0:
            empty_fig = go.Figure()
            empty_fig.add_annotation(text="Nessun dato disponibile")
            return empty_fig, empty_fig
        
        # Simulazione dell'impatto delle variazioni sui risultati
        df_scenario = df.copy()
        df_scenario["litio_estratto_kg"] = df_scenario["litio_estratto_kg"] * (1 + prod_change/100)
        df_scenario["prezzo_litio_eur_kg"] = df_scenario["prezzo_litio_eur_kg"] + prezzo_change
        df_scenario["costi_eur"] = df_scenario["costi_eur"] * (1 - costi_change/100)
        df_scenario["ricavi_eur"] = df_scenario["litio_estratto_kg"] * df_scenario["prezzo_litio_eur_kg"]
        df_scenario["profitto_eur"] = df_scenario["ricavi_eur"] - df_scenario["costi_eur"]
        df_scenario["margine_%"] = (df_scenario["profitto_eur"] / df_scenario["ricavi_eur"].replace(0, 1)) * 100
        
        fig_prof = px.line(df_scenario, x="data", y="profitto_eur",
                           title=f"Profitto Scenario (+Prod: {prod_change}%, €Prezzo: {prezzo_change}, -Costi: {costi_change}%)")
        fig_marg = px.line(df_scenario, x="data", y="margine_%",
                           title="Margine Scenario (%)")
        
        for fig in [fig_prof, fig_marg]:
            fig.update_layout(template="plotly_dark")
        
        return fig_prof, fig_marg
    except Exception as e:
        print(f"Errore What-If: {str(e)}")
        empty_fig = go.Figure()
        empty_fig.add_annotation(text=f"Errore: {str(e)}")
        return empty_fig, empty_fig


# Analisi statistica avanzata e identificazione di anomalie
@app.callback(
    [Output("correlazione-matrix", "figure"), 
     Output("outliers-produzione", "figure"),
     Output("stats-description", "children")],
    Input("aggiornamento", "n_intervals"),
    prevent_initial_call=False
)
def update_analysis(n):
    try:
        df = pd.read_csv("./data/e_lithium_data.csv")
        df["data"] = pd.to_datetime(df["data"])
        
        if len(df) == 0:
            empty_fig = go.Figure()
            empty_fig.add_annotation(text="Nessun dato disponibile")
            return empty_fig, empty_fig, "Nessun dato disponibile"
        
        # Matrice correlazione
        corr_cols = ["litio_estratto_kg", "purezza_%", "profitto_eur", "margine_%", "costi_eur", "prezzo_litio_eur_kg"]
        corr_cols = [col for col in corr_cols if col in df.columns]
        corr_matrix = df[corr_cols].corr()
        fig_corr = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_cols,
            y=corr_cols,
            colorscale="RdBu",
            zmid=0
        ))
        fig_corr.update_layout(title="Correlazioni tra Metriche", template="plotly_dark")
        
        # Rilevamento di valori anomali nella produzione
        outliers_prod = detect_outliers(df["litio_estratto_kg"])
        fig_outliers = px.scatter(df, x="data", y="litio_estratto_kg",
                                 color=outliers_prod,
                                 title="Outliers nella Produzione")
        fig_outliers.update_layout(template="plotly_dark")
        
        # Elaborazione dei principali indicatori statistici
        stats_text = "Statistiche Descrittive\n\n"
        for col in corr_cols:
            stats_text += f"{col}:\n"
            stats_text += f"  Media: {df[col].mean():.2f}\n"
            stats_text += f"  Std Dev: {df[col].std():.2f}\n"
            stats_text += f"  Min: {df[col].min():.2f}\n"
            stats_text += f"  Max: {df[col].max():.2f}\n\n"
        
        return fig_corr, fig_outliers, stats_text
    except Exception as e:
        print(f"Errore Analisi: {str(e)}")
        empty_fig = go.Figure()
        empty_fig.add_annotation(text=f"Errore: {str(e)}")
        return empty_fig, empty_fig, f"Errore: {str(e)}"


# Avvio del server dell'applicazione
if __name__ == "__main__":
    app.run(debug=True)
