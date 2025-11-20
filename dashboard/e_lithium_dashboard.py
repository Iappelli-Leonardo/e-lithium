import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import os
import numpy as np
from scipy import stats
from datetime import datetime, timedelta
from dash.dependencies import Input, Output
from dash import Dash, html, dcc, callback


# ==========================================================|
# Dashboard interattiva E-Lithium S.p.A.                    |
# Analisi delle prestazioni operative della miniera di litio|
# ==========================================================|

# ---- Caricamento dati iniziale ----
df = pd.read_csv("./data/e_lithium_data.csv")
df["data"] = pd.to_datetime(df["data"])

# ---- Inizializzazione app Dash ----
app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
app.title = "E-Lithium S.p.A"
app.config.suppress_callback_exceptions = True 

navbar = dbc.NavbarSimple(
    brand="E-Lithium S.p.A.",
    brand_href="#",
    color="dark",
    dark=True,
    className="mb-4"
)

# ---- KPI sintetici ----
def calcola_kpi(df):
    """Calcola KPI con trend e variazioni percentuali"""
    if len(df) < 2:
        return {
            "avg_profitto": 0, "trend_profitto": 0,
            "avg_purezza": 0, "trend_purezza": 0,
            "avg_produzione": 0, "trend_produzione": 0,
            "avg_margine": 0, "trend_margine": 0
        }
    
    # Dividi i dati in due metà per calcolare il trend
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

kpi = calcola_kpi(df)


dcc.DatePickerRange(
    id="filtro-date",
    min_date_allowed=df["data"].min(),
    max_date_allowed=df["data"].max(),
    start_date=df["data"].min(),
    end_date=df["data"].max()
)


# ---- Layout ----
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

    # Sezione Filtri
    html.Div(id="filtri-container", style={"display": "none"}),

    html.Div(id="tab-content"),
    
    # Footer
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



# ---- CALLBACK per aggiornare automaticamente i dati ----
@app.callback(
    Output("tab-content", "children"),
    [
        Input("tabs", "value"),
        Input("date-picker", "start_date"),
        Input("date-picker", "end_date"),
        Input("purezza-slider", "value"),
        Input("profitto-slider", "value")
    ],
    prevent_initial_call=False
)
def render_tab_content(tab, start_date, end_date, purezza_range, profitto_range):
    if tab == "tab-dashboard":
        return html.Div([
            dcc.Interval(id="aggiornamento", interval=10*1000, n_intervals=0),

            html.Div(className="mt-4"),  # Additional top margin

            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardHeader("Produzione media"),
                    dbc.CardBody(html.H4(id="kpi-produzione"))
                ], color="primary", inverse=True), width=3),

                dbc.Col(dbc.Card([
                    dbc.CardHeader("Purezza media"),
                    dbc.CardBody(html.H4(id="kpi-purezza"))
                ], color="success", inverse=True), width=3),

                dbc.Col(dbc.Card([
                    dbc.CardHeader("Profitto medio"),
                    dbc.CardBody(html.H4(id="kpi-profitto"))
                ], color="info", inverse=True), width=3),

                dbc.Col(dbc.Card([
                    dbc.CardHeader("Margine medio"),
                    dbc.CardBody(html.H4(id="kpi-margine"))
                ], color="warning", inverse=True), width=3),
            ], className="mb-4"),

            dbc.Row([
                dbc.Col(dcc.Graph(id="grafico-produzione"), width=6),
                dbc.Col(dcc.Graph(id="grafico-profitto"), width=6),
            ], className="mb-4"),

            dbc.Row([
                dbc.Col(dcc.Graph(id="grafico-grade"), width=6),
                dbc.Col(dcc.Graph(id="grafico-prezzo"), width=6),
            ], className="mb-4"),

            dbc.Row([
                dbc.Col(dcc.Graph(id="grafico-costi"), width=6),
                dbc.Col(dcc.Graph(id="grafico-guasti"), width=6),
            ], className="mb-4"),

            dbc.Row([
                dbc.Col(dcc.Graph(id="grafico-purezza"), width=6),
                dbc.Col(dcc.Graph(id="grafico-ambiente"), width=6),
            ])
        ])

    elif tab == "tab-source":
        return dbc.Container([
            html.Div([
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
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("File Principali"),
                            dbc.CardBody([
                                html.Ul([
                                    html.Li([
                                        html.A("e_lithium_dashboard.py", 
                                              href="https://github.com/Iappelli-Leonardo/e-lithium/blob/main/dashboard/e_lithium_dashboard.py",
                                              target="_blank")
                                    ]),
                                    html.Li([
                                        html.A("e_lithium_simulatore.py",
                                              href="https://github.com/Iappelli-Leonardo/e-lithium/blob/main/simulatore/e_lithium_simulatore.py",
                                              target="_blank")
                                    ])
                                ])
                            ])
                        ], className="mb-4")
                    ])
                ])
            ])
        ])
    
    elif tab == "tab-about":
        return dbc.Container([
            html.H2("Chi è E-Lithium S.p.A.", className="mt-4"),
            html.P("""
                E-Lithium S.p.A. è una società mineraria italiana specializzata 
                nell’estrazione e raffinazione di litio ad alta purezza, destinato 
                alla produzione di batterie per veicoli elettrici e sistemi di 
                accumulo energetico di nuova generazione.
            """),
            html.H4("🌍 Mercato e Clienti"),
            html.P("""
                L’azienda rifornisce i principali produttori europei di celle agli ioni di litio,
                con partnership strategiche nel settore automobilistico, motociclistico e
                dell’elettronica di consumo.
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

@app.callback(
    [
        Output("grafico-produzione", "figure"),
        Output("grafico-profitto", "figure"),
        Output("grafico-purezza", "figure"),
        Output("grafico-ambiente", "figure"),
        Output("kpi-produzione", "children"),
        Output("kpi-purezza", "children"),
        Output("kpi-profitto", "children"),
        Output("kpi-margine", "children"),
        Output("grafico-grade", "figure"),
        Output("grafico-prezzo", "figure"),
        Output("grafico-costi", "figure"),
        Output("grafico-guasti", "figure"),
    ],
    Input("aggiornamento", "n_intervals")
)


def aggiorna_dati(n):
    df = pd.read_csv("./data/e_lithium_data.csv")
    df["data"] = pd.to_datetime(df["data"])

    kpi = {
        "avg_profitto": df["profitto_eur"].mean(),
        "avg_purezza": df["purezza_%"].mean(),
        "avg_produzione": df["litio_estratto_kg"].mean()
    }

    #------nuova---

    fig_grade = px.histogram(
    df, x="purezza_%", nbins=30, histnorm="probability density",
    title="Distribuzione Gaussiana del Tenore (%)"
    )
    fig_grade.add_vline(x=df["purezza_%"].mean(), line_dash="dash")



    oggi = datetime.now()
    un_anno_fa = oggi - timedelta(days=365)
    df_ultimo_anno = df[df['data'] >= un_anno_fa]


    fig_profitto = px.histogram(
    df_ultimo_anno, 
    x="profitto_eur", 
    nbins=30, 
    histnorm=None,  # None = conta i casi, non densità
    title="Distribuzione del Profitto (€) nell'ultimo anno"
    )


    fig_purezza = px.histogram(
    df, x="purezza_%", nbins=30, histnorm="probability density",
    title="Distribuzione della Purezza (%)"
    )
    fig_purezza.add_vline(x=df["purezza_%"].mean(), line_dash="dash")

    fig_prezzo = px.histogram(
    df[df["prezzo_litio_eur_kg"] > 0],
    x="prezzo_litio_eur_kg",
    nbins=30,
    histnorm="probability density",
    title="Distribuzione Lognormale del Prezzo del Litio (€/kg)"
    )

    fig_prezzo.update_xaxes(type="linear")
    fig_prezzo.update_layout(template="plotly_dark")

    fig_costi = px.histogram(
    df, x="costi_eur", nbins=30, histnorm="probability density",
    title="Distribuzione dei Costi Operativi (Gauss)"
    )
    fig_costi.add_vline(x=df["costi_eur"].mean(), line_dash="dash")

    fig_guasti = px.histogram(
    df,
    x="guasti",
    nbins=int(df["guasti"].max()) + 1,  # <- qui
    title="Distribuzione di Poisson dei Guasti"
    )

    fig_produzione = px.histogram(
    df, x="litio_estratto_kg", nbins=30, histnorm="probability density",
    title="Distribuzione Gaussiana della Produzione giornaliera di litio (kg)"
    )
    fig_produzione.add_vline(x=df["litio_estratto_kg"].mean(), line_dash="dash")
    fig_produzione.update_layout(template="plotly_dark")

    import plotly.graph_objects as go

    fig_ambiente = go.Figure()

    for col, colore in zip(["temperatura_C", "umidita_%", "CO2_ppm"], ["red", "blue", "green"]):
        fig_ambiente.add_trace(
            go.Histogram(
                x=df[col],
                name=col,
                nbinsx=30,
                histnorm="probability density",
                marker_color=colore,
                opacity=0.7
            )
        )

    fig_ambiente.update_layout(
        barmode='overlay',
        title="Distribuzione Gaussiana delle condizioni ambientali",
        template="plotly_dark"
    )



    #------nuova---

    # fig_produzione = px.line(df, x="data", y="litio_estratto_kg", title="Produzione giornaliera di litio (kg)", markers=True)
    # fig_profitto = px.line(df, x="data", y="profitto_eur", title="Andamento del profitto (€)", markers=True)
    # fig_purezza = px.line(df, x="data", y="purezza_%", title="Purezza media del litio (%)", markers=True)
    # fig_ambiente = px.line(df, x="data", y=["temperatura_C", "umidita_%", "CO2_ppm"], title="Condizioni ambientali nella miniera")
    # fig_grade = px.line(df, x="data", y="purezza_%", title="Tenore medio del minerale (Grade)", markers=True)
    # fig_prezzo = px.line(df, x="data", y="prezzo_litio_eur_kg", title="Prezzo medio del litio (€/kg)", markers=True)
    # fig_costi = px.line(df, x="data", y="costi_eur", title="Costi operativi giornalieri (€/giorno)", markers=True)
    # fig_guasti = px.line(df, x="data", y="guasti", title="Guasti macchinari (eventi/giorno)", markers=True)

    for f in [fig_produzione, fig_profitto, fig_purezza, fig_ambiente, fig_grade, fig_prezzo, fig_costi, fig_guasti]:
        f.update_layout(template="plotly_dark", hovermode="x unified")

    return (
    fig_produzione,
    fig_profitto,
    fig_purezza,
    fig_ambiente,

    f"{kpi['avg_produzione']:,.0f} kg/giorno",
    f"{kpi['avg_purezza']:.2f} %",
    f"€ {kpi['avg_profitto']:,.0f}",
    f"{df['margine_%'].mean():.2f} %",

    fig_grade,
    fig_prezzo,
    fig_costi,
    fig_guasti,
)






# ---- Avvio server ----
if __name__ == "__main__":
    app.run(debug=True)
