import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import os
import pandas as pd
import numpy as np

from datetime import datetime
from dash.dependencies import Input, Output
from dash import Dash, html, dcc, Input, Output





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
    return {
        "avg_profitto": df["profitto_eur"].mean(),
        "avg_purezza": df["purezza_%"].mean(),
        "avg_produzione": df["litio_estratto_kg"].mean()
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
    html.H1("E-Lithium S.p.A. – Sistema di Monitoraggio", className="text-center my-4"),

    dcc.Tabs(
        id="tabs",
        value="tab-dashboard",
        children=[
            dcc.Tab(label="📊 Dashboard Operativa", value="tab-dashboard"),
            dcc.Tab(label="🏭 Scheda Aziendale", value="tab-about"),
        ],
        style={"fontWeight": "bold", "fontSize": "16px"}
    ),

    html.Div(id="tab-content")
], fluid=True)



# ---- CALLBACK per aggiornare automaticamente i dati ----
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value")
)
def render_tab_content(tab):
    if tab == "tab-dashboard":
        return html.Div([
            dcc.Interval(id="aggiornamento", interval=10*1000, n_intervals=0),

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
                dbc.Col(dcc.Graph(id="grafico-purezza"), width=6),
                dbc.Col(dcc.Graph(id="grafico-ambiente"), width=6),
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
                html.Li("Sede: Cagliari (Italia)"),
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

    fig_produzione = px.line(df, x="data", y="litio_estratto_kg", title="Produzione giornaliera di litio (kg)", markers=True)
    fig_profitto = px.line(df, x="data", y="profitto_eur", title="Andamento del profitto (€)", markers=True)
    fig_purezza = px.line(df, x="data", y="purezza_%", title="Purezza media del litio (%)", markers=True)
    fig_ambiente = px.line(df, x="data", y=["temperatura_C", "umidita_%", "CO2_ppm"], title="Condizioni ambientali nella miniera")

    for f in [fig_produzione, fig_profitto, fig_purezza, fig_ambiente]:
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
    )




# ---- Avvio server ----
if __name__ == "__main__":
    app.run(debug=True)
