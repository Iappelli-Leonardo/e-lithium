import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import os
import pandas as pd
import numpy as np

from datetime import datetime
from dash.dependencies import Input, Output
from dash import Dash, html, dcc



# ==========================================================|
# Dashboard interattiva E-Lithium S.p.A.                    |
# Analisi delle prestazioni operative della miniera di litio|
# ==========================================================|

# ---- Caricamento dati iniziale ----
df = pd.read_csv("./data/e_lithium_data.csv")
df["data"] = pd.to_datetime(df["data"])

# ---- Inizializzazione app Dash ----
app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
app.title = "E-Lithium Dashboard"

# ---- KPI sintetici ----
def calcola_kpi(df):
    return {
        "avg_profitto": df["profitto_eur"].mean(),
        "avg_purezza": df["purezza_%"].mean(),
        "avg_produzione": df["litio_estratto_kg"].mean()
    }

kpi = calcola_kpi(df)

# ---- Layout ----
app.layout = dbc.Container([
    html.H1("E-Lithium S.p.A. – Dashboard Operativa", className="text-center my-4"),

    # Refresh automatico ogni 10 secondi
    dcc.Interval(id="aggiornamento", interval=10*1000, n_intervals=0),

    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Produzione media"),
            dbc.CardBody(html.H4(id="kpi-produzione"))
        ], color="primary", inverse=True), width=4),

        dbc.Col(dbc.Card([
            dbc.CardHeader("Purezza media"),
            dbc.CardBody(html.H4(id="kpi-purezza"))
        ], color="success", inverse=True), width=4),

        dbc.Col(dbc.Card([
            dbc.CardHeader("Profitto medio"),
            dbc.CardBody(html.H4(id="kpi-profitto"))
        ], color="info", inverse=True), width=4),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id="grafico-produzione"), width=6),
        dbc.Col(dcc.Graph(id="grafico-profitto"), width=6),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id="grafico-purezza"), width=6),
        dbc.Col(dcc.Graph(id="grafico-ambiente"), width=6),
    ]),
], fluid=True)


# ---- CALLBACK per aggiornare automaticamente i dati ----
@app.callback(
    [
        Output("grafico-produzione", "figure"),
        Output("grafico-profitto", "figure"),
        Output("grafico-purezza", "figure"),
        Output("grafico-ambiente", "figure"),
        Output("kpi-produzione", "children"),
        Output("kpi-purezza", "children"),
        Output("kpi-profitto", "children"),
    ],
    Input("aggiornamento", "n_intervals")
)
def aggiorna_dati(n):
    df = pd.read_csv("./data/e_lithium_data.csv")
    df["data"] = pd.to_datetime(df["data"])

    # Ricalcola KPI
    kpi = calcola_kpi(df)

    fig_produzione = px.line(df, x="data", y="litio_estratto_kg", title="Produzione giornaliera di litio (kg)", markers=True)
    fig_profitto = px.line(df, x="data", y="profitto_eur", title="Andamento del profitto (€)", markers=True)
    fig_purezza = px.line(df, x="data", y="purezza_%", title="Purezza media del litio (%)", markers=True)
    fig_ambiente = px.line(df, x="data", y=["temperatura_C", "umidita_%", "CO2_ppm"], title="Condizioni ambientali nella miniera")

    return (
        fig_produzione,
        fig_profitto,
        fig_purezza,
        fig_ambiente,
        f"{kpi['avg_produzione']:,.0f} kg/giorno",
        f"{kpi['avg_purezza']:.2f} %",
        f"€ {kpi['avg_profitto']:,.0f}"
    )


# ---- Avvio server ----
if __name__ == "__main__":
    app.run(debug=True)
