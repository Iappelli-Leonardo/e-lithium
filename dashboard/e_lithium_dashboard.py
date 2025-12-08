import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import os
import numpy as np
import subprocess
import sys
from datetime import datetime, timedelta
from dash.dependencies import Input, Output, State, ALL, MATCH
from dash import Dash, html, dcc, callback
from scipy import stats
from scipy.stats import gaussian_kde


# Dashboard Interattiva E-Lithium S.p.A. - Versione 2.0
# Sistema di monitoraggio e analisi dei dati di produzione
# Visualizzazione real-time delle metriche aziendali

# Configurazione del percorso assoluto
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(project_dir, "data", "e_lithium_data.csv")
simulatore_path = os.path.join(project_dir, "simulatore", "e_lithium_simulatore.py")

# Avvia il simulatore per generare i dati freschi (solo una volta, non in debug reload)
if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
    print("[Dashboard] Avviamento del simulatore per generare i dati...")
    try:
        subprocess.run([sys.executable, simulatore_path], check=True, cwd=project_dir)
        print("[Dashboard] Simulatore completato con successo!")
    except Exception as e:
        print(f"[Dashboard] Errore nell'avvio del simulatore: {str(e)}")

# Funzione per caricare i dati in modo fresco da CSV
def load_data():
    df = pd.read_csv(csv_path)
    df["data"] = pd.to_datetime(df["data"])
    return df

# Inizializzazione dell'applicazione interattiva con supporto mobile
app = Dash(
    __name__, 
    external_stylesheets=[dbc.themes.SOLAR],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes"}
    ]
)
app.title = "E-Lithium S.p.A"
app.config.suppress_callback_exceptions = True 

# Mappa dei mesi in italiano per riferimenti dinamici
ITALIAN_MONTHS = {
    1: "Gennaio",
    2: "Febbraio",
    3: "Marzo",
    4: "Aprile",
    5: "Maggio",
    6: "Giugno",
    7: "Luglio",
    8: "Agosto",
    9: "Settembre",
    10: "Ottobre",
    11: "Novembre",
    12: "Dicembre"
}


def get_current_month_year_it():
    """Restituisce mese e anno correnti in italiano"""
    now = datetime.now()
    month_name = ITALIAN_MONTHS.get(now.month, str(now.month))
    return f"{month_name} {now.year}"

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
            html.Span(
                "v2.0.1",
                style={
                    "color": "#6c757d",
                    "fontSize": "0.9rem",
                    "marginLeft": "auto",
                    "alignSelf": "center"
                }
            ),
        ],
        fluid=True,
        style={"display": "flex", "justifyContent": "space-between"}
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
    """Creazione delle card KPI con indicatori visivi per trend e performance - Responsive Mobile"""
    trend_color = "success" if trend_value >= 0 else "danger"
    trend_icon = "↑" if trend_value >= 0 else "↓"
    
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
                html.H6(title, className="mb-2 fw-bold", style={
                    "color": "#ffffff", 
                    "fontSize": "clamp(0.9rem, 2.5vw, 1.1rem)",  # Responsive font size
                    "textAlign": "center", 
                    "borderBottom": "2px solid rgba(255,255,255,0.3)", 
                    "paddingBottom": "8px"
                }),
                html.H4(value, className="mb-2", style={
                    "color": "#ffffff", 
                    "fontWeight": "700", 
                    "textAlign": "center",
                    "fontSize": "clamp(1.2rem, 4vw, 1.5rem)"  # Responsive font size
                }),
                html.Small(description, className="text-muted d-block mb-2", style={
                    "textAlign": "center",
                    "fontSize": "clamp(0.7rem, 2vw, 0.85rem)"  # Responsive font size
                }),
                html.Div(trend, style={
                    "color": "#ffffff", 
                    "fontWeight": "600", 
                    "fontSize": "clamp(0.8rem, 2.5vw, 0.9rem)",  # Responsive font size
                    "textAlign": "center"
                }),
                html.Small("Rispetto ad oggi", className="d-block", style={
                    "color": "rgba(255, 255, 255, 0.8)",
                    "textAlign": "center",
                    "fontSize": "clamp(0.65rem, 2vw, 0.8rem)",
                    "marginTop": "0.15rem"
                })
            ], style={"width": "100%", "padding": "0.5rem"})
        ], style={"padding": "0.75rem"})
    ], color=color, inverse=True, className="h-100 mb-3")


def detect_outliers(series, method='iqr'):
    """Identificazione di valori anomali utilizzando il metodo dell'intervallo interquartile"""
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return (series < lower_bound) | (series > upper_bound)


def genera_insights_automatici(df):
    """Genera insights automatici in linguaggio semplice per utenti non tecnici"""
    insights = []
    
    if len(df) < 2:
        return [html.Li("Dati insufficienti per generare insights", className="text-muted")]
    
    # Analisi produzione
    prod_media = df["litio_estratto_kg"].mean()
    prod_std = df["litio_estratto_kg"].std()
    prod_ultima_settimana = df.tail(7)["litio_estratto_kg"].mean()
    
    if prod_ultima_settimana > prod_media + prod_std:
        insights.append(html.Li([
            html.Span("✅ ", style={"color": "#28a745", "fontSize": "1.2rem"}),
            html.Strong("Ottima produzione! "),
            f"Nell'ultima settimana hai estratto {prod_ultima_settimana:.0f} kg/giorno, ben sopra la media di {prod_media:.0f} kg."
        ], className="mb-2"))
    elif prod_ultima_settimana < prod_media - prod_std:
        insights.append(html.Li([
            html.Span("⚠️ ", style={"color": "#ffc107", "fontSize": "1.2rem"}),
            html.Strong("Attenzione alla produzione: "),
            f"Nell'ultima settimana la produzione è scesa a {prod_ultima_settimana:.0f} kg/giorno, sotto la media di {prod_media:.0f} kg."
        ], className="mb-2"))
    
    # Analisi purezza
    purezza_media = df["purezza_%"].mean()
    purezza_ultima = df.tail(7)["purezza_%"].mean()
    
    if purezza_ultima >= 98.5:
        insights.append(html.Li([
            html.Span("🌟 ", style={"color": "#28a745", "fontSize": "1.2rem"}),
            html.Strong("Qualità eccellente! "),
            f"La purezza media è al {purezza_ultima:.2f}%, perfetta per batterie premium."
        ], className="mb-2"))
    elif purezza_ultima < 97:
        insights.append(html.Li([
            html.Span("⚠️ ", style={"color": "#dc3545", "fontSize": "1.2rem"}),
            html.Strong("Purezza sotto target: "),
            f"La purezza attuale è {purezza_ultima:.2f}%. Considera di verificare il processo di raffinazione."
        ], className="mb-2"))
    
    # Analisi profitti
    profitto_medio = df["profitto_eur"].mean()
    profitto_ultimo = df.tail(7)["profitto_eur"].mean()
    variazione_profitto = ((profitto_ultimo - profitto_medio) / abs(profitto_medio) * 100) if profitto_medio != 0 else 0
    
    if variazione_profitto > 10:
        insights.append(html.Li([
            html.Span("📈 ", style={"color": "#28a745", "fontSize": "1.2rem"}),
            html.Strong("Trend positivo! "),
            f"I profitti sono cresciuti del {variazione_profitto:.1f}% rispetto alla media (€{profitto_ultimo:,.0f}/giorno)."
        ], className="mb-2"))
    elif variazione_profitto < -10:
        insights.append(html.Li([
            html.Span("📉 ", style={"color": "#dc3545", "fontSize": "1.2rem"}),
            html.Strong("Calo profitti: "),
            f"I profitti sono diminuiti del {abs(variazione_profitto):.1f}% rispetto alla media. Verifica i costi operativi."
        ], className="mb-2"))
    
    # Analisi costi
    costi_medio = df["costi_eur"].mean()
    costi_ultimo = df.tail(7)["costi_eur"].mean()
    
    if costi_ultimo > costi_medio * 1.15:
        insights.append(html.Li([
            html.Span("💸 ", style={"color": "#ffc107", "fontSize": "1.2rem"}),
            html.Strong("Aumento costi operativi: "),
            f"I costi sono saliti a €{costi_ultimo:,.0f}/giorno (+{((costi_ultimo/costi_medio-1)*100):.1f}%)."
        ], className="mb-2"))
    
    # Analisi guasti
    guasti_totali = df.tail(30)["guasti"].sum()
    if guasti_totali > 15:
        insights.append(html.Li([
            html.Span("🔧 ", style={"color": "#dc3545", "fontSize": "1.2rem"}),
            html.Strong("Alert manutenzione: "),
            f"Rilevati {int(guasti_totali)} guasti negli ultimi 30 giorni. Programma manutenzione preventiva."
        ], className="mb-2"))
    elif guasti_totali < 5:
        insights.append(html.Li([
            html.Span("✅ ", style={"color": "#28a745", "fontSize": "1.2rem"}),
            html.Strong("Macchinari efficienti: "),
            f"Solo {int(guasti_totali)} guasti negli ultimi 30 giorni. Gli impianti funzionano bene!"
        ], className="mb-2"))
    
    if not insights:
        insights.append(html.Li("📊 Le metriche sono nella norma. Continua il buon lavoro!", className="text-info mb-2"))
    
    return insights


def genera_report_narrativo(df):
    """Genera un report narrativo che racconta la storia dei dati"""
    if len(df) < 2:
        return "Dati insufficienti per generare un report completo."
    
    # Adatta il periodo in base ai dati disponibili
    num_giorni = len(df)
    periodo_desc = f"{num_giorni} Giorni" if num_giorni < 30 else "Ultimi 30 Giorni"
    
    # Usa tutti i dati disponibili se meno di 30 giorni, altrimenti ultimi 30
    periodo_analisi = df if num_giorni <= 30 else df.tail(30)
    giorni_analisi = len(periodo_analisi)
    
    prod_media = periodo_analisi["litio_estratto_kg"].mean()
    prod_totale = periodo_analisi["litio_estratto_kg"].sum()
    purezza_media = periodo_analisi["purezza_%"].mean()
    profitto_totale = periodo_analisi["profitto_eur"].sum()
    profitto_medio = periodo_analisi["profitto_eur"].mean()
    guasti_totali = periodo_analisi["guasti"].sum()
    
    # Confronto con periodo precedente (se disponibile)
    var_prod = 0
    var_profitto = 0
    confronto_disponibile = False
    
    if len(df) >= giorni_analisi * 2:
        periodo_precedente = df.iloc[-(giorni_analisi*2):-giorni_analisi]
        if len(periodo_precedente) > 0:
            confronto_disponibile = True
            prod_media_prec = periodo_precedente["litio_estratto_kg"].mean()
            profitto_medio_prec = periodo_precedente["profitto_eur"].mean()
            
            if prod_media_prec != 0:
                var_prod = ((prod_media - prod_media_prec) / prod_media_prec * 100)
            if profitto_medio_prec != 0:
                var_profitto = ((profitto_medio - profitto_medio_prec) / abs(profitto_medio_prec) * 100)
    
    # Costruzione narrativa
    report = f"""
    📊 **Situazione {periodo_desc}**
    
    L'azienda ha estratto un totale di **{prod_totale:,.0f} kg di litio** con una media giornaliera di **{prod_media:,.0f} kg**. 
    """
    
    if confronto_disponibile:
        report += f"""Rispetto al periodo precedente, la produzione è {"aumentata" if var_prod > 0 else "diminuita"} del **{abs(var_prod):.1f}%**."""
    else:
        report += f"""Periodo di analisi: **{giorni_analisi} giorni**."""
    
    report += f"""
    
    La purezza media del litio estratto si è attestata al **{purezza_media:.2f}%**, {"superando" if purezza_media >= 98 else "rimanendo sotto"} 
    gli standard premium per batterie ad alta prestazione.
    
    💰 **Performance Finanziaria**
    
    Il profitto totale del periodo è stato di **€{profitto_totale:,.0f}** (media giornaliera: €{profitto_medio:,.0f})"""
    
    if confronto_disponibile:
        report += f""", 
    con una variazione del **{var_profitto:+.1f}%** rispetto al periodo precedente. 
    {"Ottimo risultato che conferma la solidità operativa!" if var_profitto > 5 else "Si consiglia di monitorare attentamente i costi." if var_profitto < -5 else "Performance stabile nel periodo."}"""
    else:
        report += "."
    
    report += f"""
    
    ⚙️ **Efficienza Operativa**
    
    Gli impianti hanno registrato **{int(guasti_totali)} guasti** nel periodo, 
    {"un numero elevato che richiede interventi di manutenzione" if guasti_totali > 15 else "un livello accettabile che indica buona manutenzione" if guasti_totali > 5 else "un numero molto basso che testimonia l'eccellente stato degli impianti"}.
    """
    
    return report


def get_status_indicator(value, thresholds):
    """Ritorna indicatore a semaforo (colore + emoji) basato su soglie"""
    if "ottimo" in thresholds and thresholds["ottimo"][0] <= value <= thresholds["ottimo"][1]:
        return ("🟢", "success", "Ottimo")
    elif "buono" in thresholds and thresholds["buono"][0] <= value <= thresholds["buono"][1]:
        return ("🟡", "warning", "Buono")
    else:
        return ("🔴", "danger", "Critico")


def create_kpi_card_with_semaphore(title, value, trend, color, trend_value, status_indicator):
    """Card KPI con indicatore a semaforo e tooltip"""
    emoji, badge_color, status_text = status_indicator
    
    descriptions = {
        "Produzione Media": "Quantità media di litio estratta ogni giorno",
        "Purezza Media": "Qualità media del litio estratto (più alta è meglio)",
        "Profitto Medio": "Guadagno medio giornaliero dopo i costi",
        "Margine Medio": "Percentuale di guadagno su ogni euro di ricavi"
    }
    description = descriptions.get(title, "")
    
    tooltips = {
        "Produzione Media": "Target ottimale: 900-1100 kg/giorno. Sotto 800 kg richiede attenzione.",
        "Purezza Media": "Target premium: >98%. Accettabile: 97-98%. Sotto 97% richiede intervento.",
        "Profitto Medio": "Target: >€20,000/giorno. Monitorare se scende sotto €15,000.",
        "Margine Medio": "Target ottimale: >30%. Buono: 20-30%. Sotto 20% rivedere strategie."
    }
    tooltip_text = tooltips.get(title, "")
    
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Div([
                    html.H6([
                        title,
                        html.Span(" ❓", id=f"tooltip-{title.replace(' ', '-')}", 
                                 style={"cursor": "help", "fontSize": "0.9rem", "marginLeft": "5px"})
                    ], className="mb-2 fw-bold", style={
                        "color": "#ffffff", 
                        "fontSize": "clamp(0.9rem, 2.5vw, 1.1rem)",
                        "textAlign": "center", 
                        "borderBottom": "2px solid rgba(255,255,255,0.3)", 
                        "paddingBottom": "8px"
                    }),
                    dbc.Tooltip(tooltip_text, target=f"tooltip-{title.replace(' ', '-')}", 
                               placement="top", style={"fontSize": "0.85rem"})
                ]),
                html.Div([
                    html.Span(emoji, style={"fontSize": "1.5rem", "marginRight": "10px"}),
                    dbc.Badge(status_text, color=badge_color, className="mb-2")
                ], style={"textAlign": "center", "marginBottom": "10px"}),
                html.H4(value, className="mb-2", style={
                    "color": "#ffffff", 
                    "fontWeight": "700", 
                    "textAlign": "center",
                    "fontSize": "clamp(1.2rem, 4vw, 1.5rem)"
                }),
                html.Small(description, className="d-block mb-2", style={
                    "textAlign": "center",
                    "fontSize": "clamp(0.7rem, 2vw, 0.85rem)",
                    "color": "#ffffff"
                }),
                html.Div(trend, style={
                    "color": "#ffffff", 
                    "fontWeight": "600", 
                    "fontSize": "clamp(0.8rem, 2.5vw, 0.9rem)",
                    "textAlign": "center"
                }),
                html.Small("Rispetto ad oggi", className="d-block", style={
                    "color": "rgba(255, 255, 255, 0.8)",
                    "textAlign": "center",
                    "fontSize": "clamp(0.65rem, 2vw, 0.8rem)",
                    "marginTop": "0.15rem"
                })
            ], style={"width": "100%", "padding": "0.5rem"})
        ], style={"padding": "0.75rem"})
    ], color=color, inverse=True, className="h-100 mb-3")


# Struttura principale dell'interfaccia utente - Responsive Mobile
app.layout = dbc.Container([
    navbar,
    html.H1("Sistema di Monitoraggio", className="text-center my-4"),
    html.P(
        "La piattaforma analizza produzione, qualità, costi e profitti del litio per offrire una visione chiara delle performance dell'azienda.",
        className="text-center text-muted",
        style={"maxWidth": "720px", "margin": "0 auto 1.5rem", "fontSize": "0.95rem"}
    ),

    dcc.Tabs(
        id="tabs",
        value="tab-summary",
        children=[
            dcc.Tab(
                label="📋 Riepilogo Esecutivo",
                value="tab-summary",
                style={'backgroundColor': '#2B3E50', 'color': '#fff', 'border': '1px solid #4E5D6C'},
                selected_style={'backgroundColor': '#4E5D6C', 'color': '#fff', 'border': '1px solid #4E5D6C'}
            ),
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
    dcc.Store(id="quick-filter-selection", data={"filter": "all"}),
    dcc.Store(id="welcome-shown", storage_type='session', data=False),
    
    # Modal di Benvenuto
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle([
            html.I(className="fas fa-battery-full me-2"),
            "Benvenuti in E-Lithium S.p.A."
        ]), close_button=True),
        dbc.ModalBody([
            html.Div([
                html.H4("🏭 Sistema di Monitoraggio Produzione", className="text-center mb-4"),
                html.P([
                    "Benvenuti nella dashboard interattiva di ", html.Strong("E-Lithium S.p.A."), 
                    ", azienda leader nell'estrazione e raffinazione di litio ad alta purezza per il settore della mobilità elettrica."
                ], className="lead text-center mb-4"),
                
                html.Hr(),
                
                html.H5("📊 Funzionalità Principali:", className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("📋 Riepilogo Esecutivo", className="text-primary"),
                                html.P("Vista semplificata con KPI, insights automatici e filtri rapidi", className="small mb-0")
                            ])
                        ], className="h-100 mb-3")
                    ], xs=12, md=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("📊 Dashboard Operativa", className="text-primary"),
                                html.P("Analisi dettagliata con distribuzioni statistiche e correlazioni", className="small mb-0")
                            ])
                        ], className="h-100 mb-3")
                    ], xs=12, md=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("🔮 Simulazione What-If", className="text-primary"),
                                html.P("Scenari futuri modificando produzione, prezzi e costi", className="small mb-0")
                            ])
                        ], className="h-100 mb-3")
                    ], xs=12, md=6),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H6("🏭 Info Aziendali", className="text-primary"),
                                html.P("Informazioni su processi, mercato e tecnologie utilizzate", className="small mb-0")
                            ])
                        ], className="h-100 mb-3")
                    ], xs=12, md=6),
                ]),
                
                html.Hr(className="my-4"),
                
                html.Div([
                    html.P([
                        html.I(className="fas fa-car-battery me-2"),
                        html.Strong("Destinazione: "),
                        "Batterie per veicoli elettrici ed ibridi (auto e moto)"
                    ], className="mb-2"),
                    html.P([
                        html.I(className="fas fa-chart-line me-2"),
                        html.Strong("Monitoraggio: "),
                        "365 giorni di dati produttivi, ambientali ed economici"
                    ], className="mb-0")
                ], className="text-center bg-light p-3 rounded")
            ])
        ]),
        dbc.ModalFooter([
            dbc.Button("Inizia l'Esplorazione", id="close-welcome", color="primary", size="lg", className="w-100")
        ])
    ], id="welcome-modal", is_open=True, backdrop="static", keyboard=False, size="lg", centered=True),

    html.Div(id="tab-content", className="flex-grow-1 w-100"),
    
    # Sezione inferiore con informazioni aziendali
    html.Footer(
        dbc.Container([
            html.Hr(className="my-3"),
            dbc.Row([
                dbc.Col([
                    html.H6("Contatti", className="text-primary mb-2"),
                    html.P([
                        html.Span("Monte Amiata, Grosseto (GR) - Siena (SI) | "),
                        html.Span("Tel: +39 070 1234567 | "),
                        html.Span("info@e-lithium.it")
                    ], className="mb-0 small")
                ], width=6),
                dbc.Col(width=6, children=[
                    html.H6("Info Legali", className="text-primary mb-2"),
                    html.P([
                        "P.IVA: IT12345678901 | REA: CA-123456 | ",
                        "Cap. Soc.: € 52.000.000 i.v."
                    ], className="mb-0 small")
                ])
            ], className="mb-2"),
        ], fluid=True), 
        className="bg-dark text-light py-3 mt-auto",
        style={"width": "100%"}
    ),
    
    # Script JavaScript per formattare i tooltip degli slider
    html.Script("""
        document.addEventListener('DOMContentLoaded', function() {
            // Formattazione tooltip profitto in formato "k" arrotondato a 1 decimale
            setTimeout(function() {
                const profittoSlider = document.querySelector('#profitto-range');
                if (profittoSlider) {
                    const observer = new MutationObserver(function(mutations) {
                        const tooltips = document.querySelectorAll('#profitto-range .rc-slider-tooltip-inner');
                        tooltips.forEach(tooltip => {
                            const value = parseFloat(tooltip.textContent.replace(/[^0-9.-]/g, ''));
                            if (!isNaN(value)) {
                                const rounded = Math.round(value/100) / 10;
                                tooltip.textContent = '€' + rounded.toFixed(1) + 'k';
                            }
                        });
                    });
                    observer.observe(profittoSlider, { childList: true, subtree: true });
                }
                
                // Formattazione tooltip purezza con 4 decimali
                const purezzaSlider = document.querySelector('#purezza-range');
                if (purezzaSlider) {
                    const observer = new MutationObserver(function(mutations) {
                        const tooltips = document.querySelectorAll('#purezza-range .rc-slider-tooltip-inner');
                        tooltips.forEach(tooltip => {
                            const value = parseFloat(tooltip.textContent);
                            if (!isNaN(value)) {
                                tooltip.textContent = value.toFixed(4);
                            }
                        });
                    });
                    observer.observe(purezzaSlider, { childList: true, subtree: true });
                }
            }, 1000);
        });
    """)
], fluid=True, className="d-flex flex-column min-vh-100", style={"paddingBottom": "0"})


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
    [Input("tabs", "value"),
     Input("quick-filter-selection", "data")],
    prevent_initial_call=False
)
def render_tab_content(tab, filter_selection):
    """Renderizza il contenuto del tab selezionato e gestisce i filtri del summary"""
    df_full = load_data()
    
    # Se siamo nel tab summary, applico il filtro selezionato
    if tab == "tab-summary":
        df_filtered = df_full.copy()
        active_filter = "all"
        
        if filter_selection and "filter" in filter_selection:
            filter_type = filter_selection["filter"]
            active_filter = filter_type
            
            if filter_type == "7d":
                max_date = df_full["data"].max()
                start_date = max_date - timedelta(days=6)
                df_filtered = df_full[df_full["data"] >= start_date]
            elif filter_type == "30d":
                max_date = df_full["data"].max()
                start_date = max_date - timedelta(days=29)
                df_filtered = df_full[df_full["data"] >= start_date]
            elif filter_type == "best":
                # Filtra per migliori performance (profitto > media + 0.5*std)
                media_profitto = df_full["profitto_eur"].mean()
                std_profitto = df_full["profitto_eur"].std()
                df_filtered = df_full[df_full["profitto_eur"] > (media_profitto + 0.5 * std_profitto)]
            elif filter_type == "alerts":
                # Filtra per criticità (profitto < media - 0.5*std o purezza < 97)
                media_profitto = df_full["profitto_eur"].mean()
                std_profitto = df_full["profitto_eur"].std()
                df_filtered = df_full[(df_full["profitto_eur"] < (media_profitto - 0.5 * std_profitto)) | 
                                      (df_full["purezza_%"] < 97)]
        
        return create_executive_summary_tab(df_filtered, active_filter)
    elif tab == "tab-dashboard":
        return create_dashboard_tab(df_full, df_full)
    elif tab == "tab-about":
        return create_about_tab()
    elif tab == "tab-whatif":
        return create_whatif_tab(df_full)
    elif tab == "tab-source":
        return create_source_tab()
    
    return html.Div("Tab non trovato")


# Callback Pattern-Matching per gestire i click sui filtri rapidi
@app.callback(
    Output("quick-filter-selection", "data"),
    Input({"type": "quick-filter", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def update_filter_selection(n_clicks_list):
    """Aggiorna lo Store quando viene cliccato un filtro rapido"""
    from dash import ctx
    
    if not ctx.triggered or ctx.triggered[0]["value"] is None:
        return {"filter": "all"}
    
    # Estrai l'index del bottone cliccato
    triggered_id = ctx.triggered_id
    if triggered_id and "index" in triggered_id:
        filter_type = triggered_id["index"]
        return {"filter": filter_type}
    
    return {"filter": "all"}


def create_executive_summary_tab(df, active_filter="all"):
    """Tab Executive Summary - Vista semplificata per management non tecnico"""
    if len(df) < 2:
        return html.Div("Dati insufficienti")
    
    kpi = calcola_kpi(df)
    
    # Calcola indicatori a semaforo
    prod_indicator = get_status_indicator(kpi['avg_produzione'], {
        "ottimo": (900, 1100), "buono": (800, 1200)
    })
    
    purezza_indicator = get_status_indicator(kpi['avg_purezza'], {
        "ottimo": (98, 100), "buono": (97, 98)
    })
    
    profitto_indicator = get_status_indicator(kpi['avg_profitto'], {
        "ottimo": (20000, float('inf')), "buono": (15000, 20000)
    })
    
    margine_indicator = get_status_indicator(kpi['avg_margine'], {
        "ottimo": (30, 100), "buono": (20, 30)
    })
    
    return dbc.Container([
        # Intestazione
        html.Div([
            html.H2("📋 Riepilogo Esecutivo", className="mb-2"),
            html.P("Vista semplificata delle performance aziendali - Aggiornamento in tempo reale", 
                   className="text-muted", style={"fontSize": "0.95rem"}),
            html.P(
                "Questa sezione raccoglie i numeri principali dell'azienda in formato facile da leggere: "
                "valori medi, variazioni recenti e consigli automatici per capire subito dove intervenire.",
                className="text-secondary",
                style={"fontSize": "0.9rem"}
            )
        ], className="text-center mb-4"),
        
        # Filtri rapidi pre-configurati
        dbc.Card([
            dbc.CardBody([
                html.H5("🔍 Filtri Rapidi", className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Button("📅 Ultimi 7 giorni", id={"type": "quick-filter", "index": "7d"}, 
                                  color="primary", outline=(active_filter != "7d"), className="w-100 mb-2")
                    ], xs=12, md=3),
                    dbc.Col([
                        dbc.Button("📅 Ultimi 30 giorni", id={"type": "quick-filter", "index": "30d"}, 
                                  color="primary", outline=(active_filter != "30d"), className="w-100 mb-2")
                    ], xs=12, md=3),
                    dbc.Col([
                        dbc.Button("🌟 Migliori Performance", id={"type": "quick-filter", "index": "best"}, 
                                  color="success", outline=(active_filter != "best"), className="w-100 mb-2")
                    ], xs=12, md=3),
                    dbc.Col([
                        dbc.Button("⚠️ Alert Criticità", id={"type": "quick-filter", "index": "alerts"}, 
                                  color="danger", outline=(active_filter != "alerts"), className="w-100 mb-2")
                    ], xs=12, md=3),
                ])
            ])
        ], className="mb-4"),
        
        # KPI Cards con semaforo
        html.H4("📊 Indicatori Chiave di Performance", className="mb-3"),
        dbc.Row([
            dbc.Col(create_kpi_card_with_semaphore(
                "Produzione Media",
                f"{kpi['avg_produzione']:,.0f} kg/giorno",
                f"{kpi['trend_produzione']:+.1f}%",
                "primary",
                kpi['trend_produzione'],
                prod_indicator
            ), xs=12, sm=6, md=3, className="mb-3"),
            dbc.Col(create_kpi_card_with_semaphore(
                "Purezza Media",
                f"{kpi['avg_purezza']:.2f}%",
                f"{kpi['trend_purezza']:+.1f}%",
                "success",
                kpi['trend_purezza'],
                purezza_indicator
            ), xs=12, sm=6, md=3, className="mb-3"),
            dbc.Col(create_kpi_card_with_semaphore(
                "Profitto Medio",
                f"€ {kpi['avg_profitto']:,.0f}",
                f"{kpi['trend_profitto']:+.1f}%",
                "info",
                kpi['trend_profitto'],
                profitto_indicator
            ), xs=12, sm=6, md=3, className="mb-3"),
            dbc.Col(create_kpi_card_with_semaphore(
                "Margine Medio",
                f"{kpi['avg_margine']:.2f}%",
                f"{kpi['trend_margine']:+.1f}%",
                "warning",
                kpi['trend_margine'],
                margine_indicator
            ), xs=12, sm=6, md=3, className="mb-3"),
        ], className="mb-4"),
        
        # Insights automatici
        dbc.Card([
            dbc.CardHeader(html.H4("💡 Insights e Raccomandazioni", className="mb-0")),
            dbc.CardBody([
                html.Ul(genera_insights_automatici(df), className="mb-0", 
                       style={"listStyle": "none", "paddingLeft": "0"})
            ])
        ], className="mb-4"),
        
        # Grafico principale trend profitti
        html.H4("📈 Trend Profitti (Ultimi 30 Giorni)", className="mb-3"),
        dbc.Row([
            dbc.Col(dcc.Graph(id="summary-profit-trend", config={'responsive': True}), xs=12, className="mb-3"),
        ]),
        
        # Report narrativo
        dbc.Card([
            dbc.CardHeader(html.H4("📄 Report Esecutivo", className="mb-0")),
            dbc.CardBody([
                dcc.Markdown(genera_report_narrativo(df), className="mb-0")
            ])
        ], className="mb-4"),
    ])


def create_dashboard_tab(df, df_full):
    """Tab Dashboard principale con filtri e KPI dinamici"""
    kpi = calcola_kpi(df)
    
    min_date = df_full["data"].min()
    max_date = df_full["data"].max()
    start_date = min_date
    end_date = max_date
    purezza_range = [df_full["purezza_%"].min(), df_full["purezza_%"].max()]
    profitto_range = [df_full["profitto_eur"].min(), df_full["profitto_eur"].max()]
    
    # Converti le date in stringhe YYYY-MM-DD se sono Timestamps
    if pd.api.types.is_datetime64_any_dtype(type(start_date)):
        start_date = start_date.strftime("%Y-%m-%d")
    if pd.api.types.is_datetime64_any_dtype(type(end_date)):
        end_date = end_date.strftime("%Y-%m-%d")
    
    # Converti min/max per min_date_allowed e max_date_allowed
    min_date_str = min_date.strftime("%Y-%m-%d")
    max_date_str = max_date.strftime("%Y-%m-%d")
    
    return html.Div([
        # Sezione di controllo per filtrare i dati per periodo e parametri - Responsive
        dbc.Card([
            dbc.CardBody([
                html.H5("🔍 Filtri Interattivi", className="mb-3", style={
                    "fontSize": "clamp(1rem, 3vw, 1.25rem)"
                }),
                dbc.Row([
                    dbc.Col([
                        html.Label("Periodo:", className="fw-bold", style={
                            "fontSize": "clamp(0.85rem, 2.5vw, 1rem)"
                        }),
                        dcc.DatePickerRange(
                            id="date-range",
                            start_date=start_date,
                            end_date=end_date,
                            min_date_allowed=min_date_str,
                            max_date_allowed=max_date_str,
                            display_format="YYYY-MM-DD",
                            style={"width": "100%"}
                        )
                    ], xs=12, md=4, className="mb-3"),
                    dbc.Col([
                        html.Label("Purezza (%)", className="fw-bold", style={
                            "fontSize": "clamp(0.85rem, 2.5vw, 1rem)"
                        }),
                        html.Div(id="purezza-display", className="text-center mb-2", style={
                            "fontSize": "0.9rem",
                            "color": "#00d9ff",
                            "fontWeight": "bold"
                        }),
                        dcc.RangeSlider(
                            id="purezza-range",
                            min=df_full["purezza_%"].min(),
                            max=df_full["purezza_%"].max(),
                            step=0.001,
                            value=purezza_range,
                            marks={i: f"{i:.2f}" for i in np.linspace(df_full["purezza_%"].min(), df_full["purezza_%"].max(), 5)},
                            tooltip={"placement": "bottom", "always_visible": False}
                        )
                    ], xs=12, md=4, className="mb-3"),
                    dbc.Col([
                        html.Label("Profitto (€)", className="fw-bold", style={
                            "fontSize": "clamp(0.85rem, 2.5vw, 1rem)"
                        }),
                        html.Div(id="profitto-display", className="text-center mb-2", style={
                            "fontSize": "0.9rem",
                            "color": "#00d9ff",
                            "fontWeight": "bold"
                        }),
                        dcc.RangeSlider(
                            id="profitto-range",
                            min=df_full["profitto_eur"].min(),
                            max=df_full["profitto_eur"].max(),
                            value=profitto_range,
                            marks={i: f"€{i/1000:.1f}k" for i in np.linspace(df_full["profitto_eur"].min(), df_full["profitto_eur"].max(), 5)},
                            tooltip={"placement": "bottom", "always_visible": False}
                        )
                    ], xs=12, md=4, className="mb-3"),
                ])
            ])
        ], className="mb-4"),

        # Indicatori chiave di prestazione con trend e variazioni - Responsive
        dbc.Row([
            dbc.Col(create_kpi_card(
                "📦 Produzione Media",
                f"{kpi['avg_produzione']:,.0f} kg/giorno",
                f"{kpi['trend_produzione']:+.1f}%",
                "primary",
                kpi['trend_produzione']
            ), xs=12, sm=6, md=3, className="mb-3"),
            dbc.Col(create_kpi_card(
                "✨ Purezza Media",
                f"{kpi['avg_purezza']:.2f}%",
                f"{kpi['trend_purezza']:+.1f}%",
                "success",
                kpi['trend_purezza']
            ), xs=12, sm=6, md=3, className="mb-3"),
            dbc.Col(create_kpi_card(
                "💰 Profitto Medio",
                f"€ {kpi['avg_profitto']:,.0f}",
                f"{kpi['trend_profitto']:+.1f}%",
                "info",
                kpi['trend_profitto']
            ), xs=12, sm=6, md=3, className="mb-3"),
            dbc.Col(create_kpi_card(
                "📊 Margine Medio",
                f"{kpi['avg_margine']:.2f}%",
                f"{kpi['trend_margine']:+.1f}%",
                "warning",
                kpi['trend_margine']
            ), xs=12, sm=6, md=3, className="mb-3"),
        ], className="mb-4"),

        # Distribuzioni Teoriche - Sezione 1: Gaussiane - Responsive
        html.H3("📊 Distribuzioni Gaussiane (Normali)", className="mt-4 mb-3 text-center", style={
            "borderBottom": "3px solid #636EFA", 
            "paddingBottom": "10px",
            "fontSize": "clamp(1.2rem, 4vw, 1.75rem)"
        }),
        
        dbc.Row([
            dbc.Col(dcc.Graph(id="dist-produzione-gauss", config={'responsive': True}, style={'height': '500px'}), xs=12, lg=6, className="mb-4"),
            dbc.Col(dcc.Graph(id="dist-purezza-gauss", config={'responsive': True}, style={'height': '500px'}), xs=12, lg=6, className="mb-4"),
        ], className="mb-5"),
        
        dbc.Row([
            dbc.Col(dcc.Graph(id="dist-margine-gauss", config={'responsive': True}, style={'height': '500px'}), xs=12, lg=6, className="mb-4"),
            dbc.Col(dcc.Graph(id="dist-costi-gauss", config={'responsive': True}, style={'height': '500px'}), xs=12, lg=6, className="mb-4"),
        ], className="mb-5"),

        # Distribuzioni Teoriche - Sezione 2: Log-Normali - Responsive
        html.H3("📈 Distribuzioni Log-Normali", className="mt-5 mb-3 text-center", style={
            "borderBottom": "3px solid #00CC96", 
            "paddingBottom": "10px",
            "fontSize": "clamp(1.2rem, 4vw, 1.75rem)"
        }),
        
        dbc.Row([
            dbc.Col(dcc.Graph(id="dist-profitto-lognorm", config={'responsive': True}), xs=12, lg=6, className="mb-3"),
            dbc.Col(dcc.Graph(id="dist-prezzo-lognorm", config={'responsive': True}), xs=12, lg=6, className="mb-3"),
        ], className="mb-4"),

        # Distribuzioni Teoriche - Sezione 3: Poisson - Responsive
        html.H3("⚠️ Distribuzione di Poisson (Eventi Rari)", className="mt-5 mb-3 text-center", style={
            "borderBottom": "3px solid #AB63FA", 
            "paddingBottom": "10px",
            "fontSize": "clamp(1.2rem, 4vw, 1.75rem)"
        }),
        
        dbc.Row([
            dbc.Col(dcc.Graph(id="dist-guasti-poisson", config={'responsive': True}), xs=12, className="mb-3"),
        ], className="mb-4"),

        # Mappa di calore della matrice di correlazione - Responsive
        html.H4("🔗 Matrice di Correlazione", className="mt-4 mb-3", style={
            "fontSize": "clamp(1.1rem, 3.5vw, 1.5rem)"
        }),
        dbc.Row([
            dbc.Col(dcc.Graph(id="heatmap-correlazioni", config={'responsive': True}), xs=12, className="mb-3"),
        ], className="mb-4"),
    ])


def create_about_tab():
    """Tab Info Aziendali"""
    last_update_text = f"Ultimo aggiornamento: {get_current_month_year_it()}"
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
            html.Li([
                html.Strong("Sede:"),
                " Monte Amiata - Grosseto/Siena - Toscana (Italia)"
            ]),
            html.Li([
                html.Strong("Dipendenti:"),
                " 250"
            ]),
            html.Li([
                html.Strong("Capacità produttiva:"),
                " 1.000 kg/giorno di litio raffinato"
            ]),
            html.Li([
                html.Strong("Fatturato annuo:"),
                " €18 milioni"
            ]),
        ]),
        html.P(last_update_text, className="text-muted fst-italic")
    ])


def create_whatif_tab(df):
    """Tab Simulazione What-If - Responsive"""
    # Prepara i dati per il filtro temporale
    df['data'] = pd.to_datetime(df['data'])
    df_sorted = df.sort_values('data')
    min_date = df_sorted['data'].min()
    max_date = df_sorted['data'].max()
    
    # Crea una lista di mesi unici (uno ogni 30 giorni circa per avere ~12 marker)
    total_days = (max_date - min_date).days
    num_markers = min(13, max(2, total_days // 30 + 1))  # Max 13 marker (inizio + 12 mesi)
    
    month_marks = {}
    for i in range(num_markers):
        date = min_date + pd.DateOffset(days=i * (total_days / (num_markers - 1)))
        month_marks[i] = date.strftime('%b %y')
    
    return dbc.Container([
        html.H2("🔮 Pannello Simulazione What-If", className="mt-4 mb-4", style={
            "fontSize": "clamp(1.3rem, 4.5vw, 2rem)"
        }),
        
        html.P([
            "Questo strumento permette di simulare scenari futuri modificando i parametri operativi chiave. ",
            "Puoi aumentare o diminuire la produzione, variare i prezzi di vendita e i costi operativi per ",
            "analizzare l'impatto economico sul profitto totale. Il sistema ricalcola automaticamente i KPI ",
            "e genera grafici comparativi tra lo scenario storico e quello simulato."
        ], className="lead text-muted mb-4", style={"fontSize": "clamp(0.9rem, 2.5vw, 1.1rem)"}),
        
        # Filtro temporale
        dbc.Card([
            dbc.CardBody([
                html.H5("📅 Periodo Dati da Analizzare", className="mb-3"),
                html.P("Seleziona il range temporale dei dati storici da utilizzare per la simulazione:", 
                       className="text-muted small"),
                dcc.RangeSlider(
                    id="whatif-date-range",
                    min=0,
                    max=num_markers - 1,
                    value=[0, num_markers - 1],
                    marks=month_marks,
                    step=1,
                    tooltip={"placement": "bottom", "always_visible": False},
                    allowCross=False
                ),
                html.Div(id="whatif-date-info", className="mt-3 text-center text-info")
            ])
        ], className="mb-4"),
        
        # Parametri di simulazione
        dbc.Card([
            dbc.CardBody([
                html.H5("⚙️ Parametri di Simulazione", className="mb-3"),
                html.P("Modifica i parametri per analizzare scenari futuri", style={
                    "fontSize": "clamp(0.9rem, 2.5vw, 1rem)"
                }),
                dbc.Row([
                    dbc.Col([
                        html.Label("Aumento Produzione (%):", style={
                            "fontSize": "clamp(0.85rem, 2.5vw, 0.95rem)"
                        }),
                        dcc.Slider(
                            id="slider-prod",
                            min=-50, max=50, step=5,
                            value=0,
                            marks={i: f"{i}%" for i in range(-50, 51, 10)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], xs=12, md=4, className="mb-3"),
                    dbc.Col([
                        html.Label("Variazione Prezzo (€/kg):", style={
                            "fontSize": "clamp(0.85rem, 2.5vw, 0.95rem)"
                        }),
                        dcc.Slider(
                            id="slider-prezzo",
                            min=-30, max=30, step=5,
                            value=0,
                            marks={i: f"€{i}" for i in range(-30, 31, 10)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], xs=12, md=4, className="mb-3"),
                    dbc.Col([
                        html.Label("Riduzione Costi (%):", style={
                            "fontSize": "clamp(0.85rem, 2.5vw, 0.95rem)"
                        }),
                        dcc.Slider(
                            id="slider-costi",
                            min=-50, max=50, step=5,
                            value=0,
                            marks={i: f"{i}%" for i in range(-50, 51, 10)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], xs=12, md=4, className="mb-3"),
                ])
            ])
        ]),
        
        html.Hr(),
        dbc.Row([
            dbc.Col(dcc.Graph(id="whatif-profitto", config={'responsive': True}), xs=12, lg=6, className="mb-4"),
            dbc.Col(dcc.Graph(id="whatif-margine", config={'responsive': True}), xs=12, lg=6, className="mb-4"),
        ], className="mt-4 mb-5", style={"paddingBottom": "100px"}),
        
        # Spaziatura per evitare sovrapposizione con il footer
        html.Div(style={"height": "200px"})
    ], className="mb-5", style={"paddingBottom": "150px"})


def create_source_tab():
    """Tab Codice Sorgente"""
    return dbc.Container([
        html.H2("💻 Codice Sorgente e Tecnologie", className="mt-4 mb-4"),
        
        # Sezione GitHub
        html.P([
            "Esplora il codice sorgente di questa dashboard sul mio repository GitHub: ",
            html.A([
                html.I(className="fab fa-github me-2"),
                "Iappelli-Leonardo/e-lithium"
            ], 
            href="https://github.com/Iappelli-Leonardo/e-lithium",
            className="text-decoration-none",
            target="_blank")
        ], className="lead mb-4"),
        
        # Stack Tecnologico
        dbc.Card([
            dbc.CardHeader(html.H5("🛠️ Stack Tecnologico", className="mb-0")),
            dbc.CardBody([
                html.H6("Linguaggio di Programmazione", className="text-primary mt-3"),
                html.Ul([
                    html.Li([html.Strong("Python " + sys.version.split()[0]), " - Linguaggio principale per logica applicativa, analisi dati e backend"])
                ]),
                
                html.H6("Framework & Librerie Principali", className="text-primary mt-3"),
                html.Ul([
                    html.Li([html.Strong("Dash"), " - Framework web interattivo per applicazioni data-driven"]),
                    html.Li([html.Strong("Dash Bootstrap Components (DBC)"), " - Componenti UI responsive con tema SOLAR"]),
                    html.Li([html.Strong("Plotly"), " - Libreria per grafici interattivi e visualizzazioni avanzate"]),
                    html.Li([html.Strong("Pandas"), " - Manipolazione e analisi dati strutturati (DataFrames)"]),
                    html.Li([html.Strong("NumPy"), " - Calcoli numerici e operazioni su array multidimensionali"]),
                    html.Li([html.Strong("SciPy"), " - Funzioni statistiche avanzate e fit di distribuzioni teoriche"])
                ]),
                
                html.H6("Formattazione & Presentazione", className="text-primary mt-3"),
                html.Ul([
                    html.Li([html.Strong("HTML5"), " - Struttura markup per componenti web"]),
                    html.Li([html.Strong("CSS3 / Bootstrap 5"), " - Styling responsive e layout mobile-first"]),
                    html.Li([html.Strong("Markdown"), " - Formattazione testi nei report narrativi"])
                ]),
                
                html.H6("Analisi Statistica", className="text-primary mt-3"),
                html.P("Il sistema implementa distribuzioni statistiche per l'analisi predittiva:"),
                html.Ul([
                    html.Li([html.Strong("Gaussiana"), " - Produzione, purezza, margine, costi"]),
                    html.Li([html.Strong("Log-Normale"), " - Profitti, prezzi"]),
                    html.Li([html.Strong("Poisson"), " - Eventi rari e guasti"])
                ]),
                
                html.H6("Hosting & Deployment", className="text-primary mt-3"),
                html.P([
                    "L'applicazione è distribuita su ", html.Strong("Render"), " (piano gratuito), una piattaforma cloud ",
                    "che offre hosting automatizzato per applicazioni web. Render si occupa di:"
                ]),
                html.Ul([
                    html.Li([html.Strong("Build"), " automatico dal repository GitHub"]),
                    html.Li([html.Strong("Deploy"), " automatico impostato ad ogni nuovo commit, su branch main/dev"]),
                    html.Li([html.Strong("Restart"), " automatico del server in caso di crash, andando ad eseguire la build dell'ultima versione stabile dell'applicazione"]),
                    html.Li([html.Strong("Dominio"), " pubblico con connessione sicura con certificato SSL (HTTPS)"]),
                    html.Li([html.Strong("Esecuzione"), " con Gunicorn come WSGI server per performance ottimali"])
                ]),
                html.P([
                    html.Small([
                        "⚠️ ", html.Strong("Nota:"), " ", html.Em("Il piano gratuito di Render mette in sleep l'applicazione dopo 15 minuti di inattività, nel caso in cui non si sia traffico web."),
                        html.Br(),
                        html.Strong("Il primo accesso, dopo il periodo di inattività, può richiedere 30-60 secondi per il riavvio del server."),
                        html.Br(),
                        html.Em("L'applicazione è stata progettata per minimizzare i tempi di avvio, tuttavia alcune funzionalità potrebbero richiedere un breve caricamento iniziale data la mole di dati salvati in memoria."),
                        html.Br(),
                        html.Em("I dati visualizzati, analizzati e utilizzati per le simulazioni, sono generati a partire dalla data di avvio del server e coprono un intervallo temporale fino a un anno precedente.")
                    ], className="text-muted")
                ])
            ])
        ], className="mb-4"),
        
        # File Principali
        dbc.Card([
            dbc.CardHeader(html.H5("📁 File Principali del Progetto", className="mb-0")),
            dbc.CardBody([
                html.Ul([
                    html.Li([
                        html.A("e_lithium_dashboard.py", 
                               href="https://github.com/Iappelli-Leonardo/e-lithium/blob/main/dashboard/e_lithium_dashboard.py", 
                               target="_blank"),
                        " - Dashboard principale (~1500 righe)"
                    ]),
                    html.Li([
                        html.A("e_lithium_simulatore.py", 
                               href="https://github.com/Iappelli-Leonardo/e-lithium/blob/main/simulatore/e_lithium_simulatore.py", 
                               target="_blank"),
                        " - Simulatore dati di produzione"
                    ]),
                    html.Li([
                        html.A("requirements.txt", 
                               href="https://github.com/Iappelli-Leonardo/e-lithium/blob/main/requirements.txt", 
                               target="_blank"),
                        " - Dipendenze Python"
                    ])
                ])
            ])
        ], className="mb-4"),
        
        # Architettura
        dbc.Card([
            dbc.CardHeader(html.H5("🏗️ Architettura Applicativa", className="mb-0")),
            dbc.CardBody([
                html.P([
                    "L'applicazione segue un'architettura ", html.Strong("MVC (Model-View-Controller)"), 
                    " adattata per applicazioni web interattive:"
                ]),
                html.Ul([
                    html.Li([html.Strong("Model"), " - Gestione dati CSV, calcolo KPI, analisi statistiche"]),
                    html.Li([html.Strong("View"), " - Componenti Dash/HTML per UI responsive"]),
                    html.Li([html.Strong("Controller"), " - Callbacks Pattern-Matching per interattività real-time"])
                ]),
                html.P([
                    "Sistema di ", html.Strong("callback reattivi"), " che aggiornano automaticamente i componenti ",
                    "in base alle azioni dell'utente (filtri, tab, simulazioni)."
                ])
            ])
        ])
    ])


# Funzioni helper per creare grafici di distribuzione teorica
def create_gaussian_distribution(df, column, title, color="#636EFA"):
    """Crea istogramma con fit Gaussiano (Normale) - Stile personalizzato"""
    fig = go.Figure()
    
    data = df[column].dropna().values
    if len(data) < 2:
        fig.add_annotation(text="Dati insufficienti")
        return fig
    
    # Mappa dei nomi delle colonne in etichette leggibili
    column_labels = {
        "litio_estratto_kg": "Litio estratto (kg)",
        "purezza_%": "Purezza (%)",
        "margine_%": "Margine (%)",
        "costi_eur": "Costi (€)",
        "profitto_eur": "Profitto (€)",
        "prezzo_litio_eur_kg": "Prezzo litio (€/kg)",
        "guasti": "Guasti"
    }
    xlabel = column_labels.get(column, column)
    
    # Calcola parametri (valori originali per il fit)
    mu_orig = data.mean()
    sigma_orig = data.std()
    
    # Arrotonda per la visualizzazione
    mu = round(mu_orig, 1)
    sigma = round(sigma_orig, 1)
    cv = round((sigma_orig / mu_orig * 100) if mu_orig != 0 else 0, 1)
    
    # Istogramma empirico in blu
    fig.add_trace(go.Histogram(
        x=data,
        name='Dati Empirici',
        histnorm='probability density',
        marker_color='#6E7FCC',  # Blu
        opacity=0.7,
        nbinsx=30,
        showlegend=True
    ))
    
    # Fit Gaussiano in rosso
    try:
        x_range = np.linspace(data.min(), data.max(), 300)
        y_gaussian = stats.norm.pdf(x_range, mu_orig, sigma_orig)
        
        fig.add_trace(go.Scatter(
            x=x_range,
            y=y_gaussian,
            mode='lines',
            name=f'Gauss(μ={mu:.1f}, σ={sigma:.1f})',
            line=dict(color='#FF0000', width=3),  # Rosso
            showlegend=True
        ))
    except Exception as e:
        print(f"Errore Gaussian fit: {e}")
    
    # Layout con legenda personalizzata
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color='white')
        ),
        xaxis_title=xlabel,
        yaxis_title='Densità di Probabilità',
        template='plotly_dark',
        paper_bgcolor='#1e1e1e',
        plot_bgcolor='#2d2d2d',
        showlegend=True,
        legend=dict(
            x=0.98,
            y=0.98,
            xanchor='right',
            yanchor='top',
            bgcolor='rgba(0,0,0,0.7)',
            bordercolor='white',
            borderwidth=1,
            font=dict(size=11, color='white'),
            title=dict(
                text=f'μ = {mu:.1f}<br>σ = {sigma:.1f}<br>CV = {cv:.1f}%',
                font=dict(size=12, color='white')
            )
        ),
        font=dict(size=11, color='white'),
        margin=dict(l=50, r=30, t=70, b=50),
        autosize=True
    )
    return fig


def create_lognormal_distribution(df, column, title, color="#00CC96"):
    """Crea istogramma con fit Log-Normale - Stile personalizzato"""
    fig = go.Figure()
    
    data = df[column].dropna().values
    data = data[data > 0]  # Log-normale richiede valori positivi
    
    if len(data) < 2:
        fig.add_annotation(text="Dati insufficienti")
        return fig
    
    # Mappa dei nomi delle colonne in etichette leggibili
    column_labels = {
        "litio_estratto_kg": "Litio estratto (kg)",
        "purezza_%": "Purezza (%)",
        "margine_%": "Margine (%)",
        "costi_eur": "Costi (€)",
        "profitto_eur": "Profitto (€)",
        "prezzo_litio_eur_kg": "Prezzo litio (€/kg)",
        "guasti": "Guasti"
    }
    xlabel = column_labels.get(column, column)
    
    # Istogramma empirico in blu
    fig.add_trace(go.Histogram(
        x=data,
        name='Dati Empirici',
        histnorm='probability density',
        marker_color='#6E7FCC',  # Blu
        opacity=0.7,
        nbinsx=30,
        showlegend=True
    ))
    
    # Fit Log-Normale in arancione
    try:
        # Parametri della log-normale (originali per il fit)
        shape_orig, loc, scale_orig = stats.lognorm.fit(data, floc=0)
        
        x_range = np.linspace(data.min(), data.max(), 300)
        y_lognorm = stats.lognorm.pdf(x_range, shape_orig, loc, scale_orig)
        
        # Calcola e arrotonda per la visualizzazione
        mean_ln = round(np.exp(np.log(scale_orig) + shape_orig**2 / 2), 1)
        median_ln = round(scale_orig, 1)
        shape = round(shape_orig, 1)
        
        fig.add_trace(go.Scatter(
            x=x_range,
            y=y_lognorm,
            mode='lines',
            name=f'Log-Normale(σ={shape:.1f})',
            line=dict(color='#FF8C00', width=3),  # Arancione scuro
            showlegend=True
        ))
    except Exception as e:
        print(f"Errore Log-Normal fit: {e}")
        mean_ln, median_ln, shape = 0, 0, 0
    
    # Formatta media e mediana con notazione "k" se >= 1000
    mean_ln_str = f'{mean_ln/1000:.1f}k' if mean_ln >= 1000 else f'{mean_ln:.1f}'
    median_ln_str = f'{median_ln/1000:.1f}k' if median_ln >= 1000 else f'{median_ln:.1f}'
    
    # Layout con legenda personalizzata
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color='white')
        ),
        xaxis_title=xlabel,
        yaxis_title='Densità di Probabilità',
        template='plotly_dark',
        paper_bgcolor='#1e1e1e',
        plot_bgcolor='#2d2d2d',
        showlegend=True,
        legend=dict(
            x=0.98,
            y=0.98,
            xanchor='right',
            yanchor='top',
            bgcolor='rgba(0,0,0,0.7)',
            bordercolor='white',
            borderwidth=1,
            font=dict(size=11, color='white'),
            title=dict(
                text=f'Media = {mean_ln_str}<br>Mediana = {median_ln_str}<br>σ = {shape:.1f}',
                font=dict(size=12, color='white')
            )
        ),
        font=dict(size=11, color='white'),
        margin=dict(l=50, r=30, t=70, b=50),
        autosize=True
    )
    return fig


def create_poisson_distribution(df, column, title, color="#AB63FA"):
    """Crea grafico PMF Poissoniano con curve multiple - Stile personalizzato"""
    fig = go.Figure()
    
    data = df[column].dropna().values.astype(int)
    
    if len(data) < 2:
        fig.add_annotation(text="Dati insufficienti")
        return fig
    
    # Mappa dei nomi delle colonne in etichette leggibili
    column_labels = {
        "litio_estratto_kg": "Litio estratto (kg)",
        "purezza_%": "Purezza (%)",
        "margine_%": "Margine (%)",
        "costi_eur": "Costi (€)",
        "profitto_eur": "Profitto (€)",
        "prezzo_litio_eur_kg": "Prezzo litio (€/kg)",
        "guasti": "Numero guasti"
    }
    xlabel = column_labels.get(column, column)
    
    # Stima λ dai dati empirici
    lambda_est = data.mean()
    variance = data.var()
    
    # Definisci 3 valori di λ per confronto
    lambda_values = [
        max(0.5, lambda_est * 0.5),
        lambda_est,
        lambda_est * 2.0
    ]
    
    colors_poisson = ['#FFA500', '#AB63FA', '#19D3F3']
    
    # Range x per le curve
    x_max = max(int(lambda_values[-1] * 2.5), max(data) + 5)
    x_range = np.arange(0, x_max + 1)
    
    # Disegna le curve
    try:
        for i, lambda_val in enumerate(lambda_values):
            y_poisson = stats.poisson.pmf(x_range, lambda_val)
            
            fig.add_trace(go.Scatter(
                x=x_range,
                y=y_poisson,
                mode='lines+markers',
                name=f'λ = {lambda_val:.1f}',
                line=dict(color=colors_poisson[i], width=2.5),
                marker=dict(size=7, symbol='circle')
            ))
    except Exception as e:
        print(f"Errore Poisson fit: {e}")
    
    # Layout
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=16, color='white')
        ),
        xaxis_title=xlabel,
        yaxis_title='P(x = k)',
        template='plotly_dark',
        paper_bgcolor='#1e1e1e',
        plot_bgcolor='#2d2d2d',
        showlegend=True,
        legend=dict(
            x=0.98,
            y=0.98,
            xanchor='right',
            yanchor='top',
            bgcolor='rgba(0,0,0,0.7)',
            bordercolor='white',
            borderwidth=1,
            font=dict(size=11, color='white'),
            title=dict(
                text=f'λ stim = {lambda_est:.1f}<br>Var = {variance:.1f}<br>Eventi = {len(data)}',
                font=dict(size=12, color='white')
            )
        ),
        xaxis=dict(dtick=1),
        font=dict(size=11, color='white'),
        margin=dict(l=50, r=30, t=70, b=50),
        autosize=True
    )
    return fig





# Aggiornamento automatico dei grafici nel dashboard principale
@app.callback(
    [
        Output("dist-produzione-gauss", "figure"),
        Output("dist-purezza-gauss", "figure"),
        Output("dist-margine-gauss", "figure"),
        Output("dist-costi-gauss", "figure"),
        Output("dist-profitto-lognorm", "figure"),
        Output("dist-prezzo-lognorm", "figure"),
        Output("dist-guasti-poisson", "figure"),
        Output("heatmap-correlazioni", "figure"),
    ],
    [
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("purezza-range", "value"),
        Input("profitto-range", "value"),
    ],
    prevent_initial_call=False
)
def update_dashboard_graphs(start_date, end_date, purezza_range, profitto_range):
    try:
        df = load_data()
        
        # Applico i filtri
        if start_date:
            df = df[df["data"] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df["data"] <= pd.to_datetime(end_date)]
        
        if isinstance(purezza_range, (list, tuple)) and len(purezza_range) == 2:
            df = df[(df["purezza_%"] >= purezza_range[0]) & (df["purezza_%"] <= purezza_range[1])]
        
        if isinstance(profitto_range, (list, tuple)) and len(profitto_range) == 2:
            df = df[(df["profitto_eur"] >= profitto_range[0]) & (df["profitto_eur"] <= profitto_range[1])]
        
        # Controllo della disponibilità e validità dei dati
        if len(df) < 2:
            empty_fig = go.Figure()
            empty_fig.add_annotation(text="Dati insufficienti per l'analisi")
            empty_fig.update_layout(template="plotly_dark")
            return [empty_fig] * 8
        
        # === DISTRIBUZIONI GAUSSIANE ===
        fig_prod_gauss = create_gaussian_distribution(
            df, "litio_estratto_kg", 
            "📦 Produzione Media Litio Estratto - Distribuzione Gaussiana",
            "#636EFA"
        )
        
        fig_pure_gauss = create_gaussian_distribution(
            df, "purezza_%",
            "✨ Tenore Medio del Minerale (Purezza %) - Distribuzione Gaussiana",
            "#19D3F3"
        )
        
        fig_marg_gauss = create_gaussian_distribution(
            df, "margine_%",
            "📊 Margine Medio (%) - Distribuzione Gaussiana",
            "#FFA15A"
        )
        
        fig_costi_gauss = create_gaussian_distribution(
            df, "costi_eur",
            "💸 Costi Medi Operativi (€) - Distribuzione Gaussiana",
            "#FF6692"
        )
        
        # === DISTRIBUZIONI LOG-NORMALI ===
        fig_prof_lognorm = create_lognormal_distribution(
            df, "profitto_eur",
            "💰 Profitto Medio (€) - Distribuzione Log-Normale",
            "#00CC96"
        )
        
        fig_prezzo_lognorm = create_lognormal_distribution(
            df, "prezzo_litio_eur_kg",
            "💵 Prezzo Medio del Litio (€/kg) - Distribuzione Log-Normale",
            "#FECB52"
        )
        
        # === DISTRIBUZIONE DI POISSON ===
        fig_guasti_poisson = create_poisson_distribution(
            df, "guasti",
            "⚠️ Guasti Macchinari (Eventi Rari) - Distribuzione di Poisson",
            "#AB63FA"
        )
        
        # === HEATMAP CORRELAZIONI ===
        corr_cols = ["litio_estratto_kg", "purezza_%", "profitto_eur", "margine_%", "costi_eur", "prezzo_litio_eur_kg", "guasti"]
        corr_labels = ["Litio estratto (kg)", "Purezza (%)", "Profitto (€)", "Margine (%)", "Costi (€)", "Prezzo litio (€/kg)", "Guasti"]
        corr_matrix = df[corr_cols].corr()
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_labels,
            y=corr_labels,
            colorscale="RdBu",
            zmid=0,
            text=corr_matrix.values.round(1),
            texttemplate="%{text}",
            textfont={"size": 10},
            colorbar=dict(title="Correlazione")
        ))
        fig_heatmap.update_layout(
            title="🔗 Matrice di Correlazione tra Metriche",
            template="plotly_dark",
            height=600
        )
        
        return (fig_prod_gauss, fig_pure_gauss, fig_marg_gauss, fig_costi_gauss,
                fig_prof_lognorm, fig_prezzo_lognorm,
                fig_guasti_poisson,
                fig_heatmap)
    
    except Exception as e:
        print(f"Errore nei grafici dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        empty_fig = go.Figure()
        empty_fig.add_annotation(text=f"Errore: {str(e)}")
        empty_fig.update_layout(template="plotly_dark")
        return [empty_fig] * 8


# Callback per mostrare info sul periodo selezionato nel What-If
@app.callback(
    Output("whatif-date-info", "children"),
    Input("whatif-date-range", "value"),
    prevent_initial_call=False
)
def update_whatif_date_info(date_range_indices):
    """Mostra informazioni sul periodo selezionato"""
    try:
        if not date_range_indices or len(date_range_indices) != 2:
            return "📅 Seleziona un periodo per iniziare"
        
        df = load_data()
        df['data'] = pd.to_datetime(df['data'])
        df_sorted = df.sort_values('data')
        min_date = df_sorted['data'].min()
        max_date = df_sorted['data'].max()
        total_days = (max_date - min_date).days
        
        start_idx, end_idx = date_range_indices
        
        # Calcola le date effettive basate sugli indici
        num_markers = 13  # Stesso valore usato in create_whatif_tab
        start_date = min_date + pd.DateOffset(days=int(start_idx * (total_days / (num_markers - 1))))
        end_date = min_date + pd.DateOffset(days=int(end_idx * (total_days / (num_markers - 1))))
        
        # Filtra i dati per il periodo selezionato
        df_filtered = df[(df['data'] >= start_date) & (df['data'] <= end_date)]
        num_days = len(df_filtered)
        
        return f"📅 Periodo: {start_date.strftime('%d %b %Y')} - {end_date.strftime('%d %b %Y')} | {num_days} giorni di dati"
    except Exception as e:
        return f"⚠️ Errore nel calcolo del periodo: {str(e)}"


# Simulazione di scenari alternativi con variabili controllabili
@app.callback(
    [Output("whatif-profitto", "figure"), Output("whatif-margine", "figure")],
    [Input("slider-prod", "value"), 
     Input("slider-prezzo", "value"), 
     Input("slider-costi", "value"),
     Input("whatif-date-range", "value")],
    prevent_initial_call=False
)
def update_whatif(prod_change, prezzo_change, costi_change, date_range_indices):
    try:
        df = load_data()
        df['data'] = pd.to_datetime(df['data'])
        
        if len(df) == 0:
            empty_fig = go.Figure()
            empty_fig.add_annotation(text="Nessun dato disponibile")
            empty_fig.update_layout(template="plotly_dark")
            return empty_fig, empty_fig
        
        # Applica filtro temporale
        if date_range_indices and len(date_range_indices) == 2:
            df_sorted = df.sort_values('data')
            min_date = df_sorted['data'].min()
            max_date = df_sorted['data'].max()
            total_days = (max_date - min_date).days
            
            start_idx, end_idx = date_range_indices
            num_markers = 13
            
            start_date = min_date + pd.DateOffset(days=int(start_idx * (total_days / (num_markers - 1))))
            end_date = min_date + pd.DateOffset(days=int(end_idx * (total_days / (num_markers - 1))))
            
            df = df[(df['data'] >= start_date) & (df['data'] <= end_date)]
        
        if len(df) == 0:
            empty_fig = go.Figure()
            empty_fig.add_annotation(text="Nessun dato nel periodo selezionato", font=dict(size=16, color="white"))
            empty_fig.update_layout(template="plotly_dark", paper_bgcolor='#1e1e1e', plot_bgcolor='#2d2d2d')
            return empty_fig, empty_fig
        
        # Simulazione dell'impatto delle variazioni sui risultati
        df_scenario = df.copy()
        df_scenario["litio_estratto_kg"] = df_scenario["litio_estratto_kg"] * (1 + prod_change/100)
        df_scenario["prezzo_litio_eur_kg"] = df_scenario["prezzo_litio_eur_kg"] + prezzo_change
        df_scenario["costi_eur"] = df_scenario["costi_eur"] * (1 - costi_change/100)
        df_scenario["ricavi_eur"] = df_scenario["litio_estratto_kg"] * df_scenario["prezzo_litio_eur_kg"]
        df_scenario["profitto_eur"] = df_scenario["ricavi_eur"] - df_scenario["costi_eur"]
        df_scenario["margine_%"] = (df_scenario["profitto_eur"] / df_scenario["ricavi_eur"].replace(0, 1)) * 100
        
        # Crea colonne per tooltip formattati
        df_scenario["profitto_k"] = df_scenario["profitto_eur"] / 1000
        
        fig_prof = px.line(df_scenario, x="data", y="profitto_eur",
                           title=f"Profitto Scenario (+Prod: {prod_change}%, €Prezzo: {prezzo_change:+d}, -Costi: {costi_change}%)",
                           custom_data=["profitto_k"])
        fig_marg = px.line(df_scenario, x="data", y="margine_%",
                           title="Margine Scenario (%)")
        
        # Formattazione grafico profitti
        fig_prof.update_traces(hovertemplate='<b>Data:</b> %{x|%Y-%m-%d}<br><b>Profitto:</b> €%{customdata[0]:.1f}k<extra></extra>')
        if len(df_scenario) > 0:
            min_val = int(df_scenario["profitto_eur"].min()/1000) - 5
            max_val = int(df_scenario["profitto_eur"].max()/1000) + 10
            
            # Crea tick values e labels personalizzati
            tick_range = list(range(min_val, max_val, 5))
            tickvals = [i*1000 for i in tick_range]
            ticktext = [str(i) if i == 0 else f'{i}k' for i in tick_range]
            
            fig_prof.update_yaxes(
                tickmode='array',
                tickvals=tickvals,
                ticktext=ticktext
            )
        
        # Formattazione grafico margine
        fig_marg.update_traces(hovertemplate='<b>Data:</b> %{x|%Y-%m-%d}<br><b>Margine:</b> %{y:.1f}%<extra></extra>')
        fig_marg.update_yaxes(ticksuffix='%')
        
        for fig in [fig_prof, fig_marg]:
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor='#1e1e1e',
                plot_bgcolor='#2d2d2d',
                font=dict(color='white')
            )
        
        return fig_prof, fig_marg
    except Exception as e:
        print(f"Errore What-If: {str(e)}")
        empty_fig = go.Figure()
        empty_fig.add_annotation(text=f"Errore: {str(e)}")
        return empty_fig, empty_fig


# Callback per il grafico trend profitti nel summary tab
@app.callback(
    Output("summary-profit-trend", "figure"),
    [Input("tabs", "value"),
     Input("quick-filter-selection", "data")],
    prevent_initial_call=False
)
def update_summary_profit_trend(tab, filter_selection):
    if tab != "tab-summary":
        return go.Figure()
    
    try:
        df_full = load_data()
        
        # Applica lo stesso filtro del summary tab
        df_filtered = df_full.copy()
        periodo_desc = "Ultimi 30 Giorni"
        
        if filter_selection and "filter" in filter_selection:
            filter_type = filter_selection["filter"]
            
            if filter_type == "7d":
                max_date = df_full["data"].max()
                start_date = max_date - timedelta(days=6)
                df_filtered = df_full[df_full["data"] >= start_date]
                periodo_desc = "Ultimi 7 Giorni"
            elif filter_type == "30d":
                max_date = df_full["data"].max()
                start_date = max_date - timedelta(days=29)
                df_filtered = df_full[df_full["data"] >= start_date]
                periodo_desc = "Ultimi 30 Giorni"
            elif filter_type == "best":
                media_profitto = df_full["profitto_eur"].mean()
                std_profitto = df_full["profitto_eur"].std()
                df_filtered = df_full[df_full["profitto_eur"] > (media_profitto + 0.5 * std_profitto)]
                periodo_desc = "Migliori Performance"
            elif filter_type == "alerts":
                media_profitto = df_full["profitto_eur"].mean()
                std_profitto = df_full["profitto_eur"].std()
                df_filtered = df_full[(df_full["profitto_eur"] < (media_profitto - 0.5 * std_profitto)) | 
                                      (df_full["purezza_%"] < 97)]
                periodo_desc = "Alert Criticità"
        
        if len(df_filtered) == 0:
            return go.Figure()
        
        fig = go.Figure()
        
        # Linea profitti
        fig.add_trace(go.Scatter(
            x=df_filtered["data"],
            y=df_filtered["profitto_eur"],
            mode='lines+markers',
            name='Profitto Giornaliero',
            line=dict(color='#00CC96', width=3),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(0, 204, 150, 0.2)',
            hovertemplate='€%{customdata:.1f}k<extra></extra>',
            customdata=df_filtered["profitto_eur"] / 1000
        ))
        
        # Linea media
        media_profitto = df_filtered["profitto_eur"].mean()
        media_profitto_k = media_profitto / 1000
        fig.add_hline(
            y=media_profitto,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Media: €{media_profitto_k:.1f}k",
            annotation_position="right"
        )
        
        fig.update_layout(
            title=f"Andamento Profitti Giornalieri - {periodo_desc}",
            xaxis_title="Data",
            yaxis_title="Profitto (€)",
            template="plotly_dark",
            hovermode='x unified',
            height=400,
            margin=dict(l=60, r=120, t=80, b=60),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Formatta asse Y in migliaia (k)
        if len(df_filtered) > 0 and df_filtered["profitto_eur"].max() > 0:
            max_val = int(df_filtered["profitto_eur"].max()/1000) + 10
            fig.update_yaxes(
                tickformat='.1f',
                ticksuffix='k',
                tickvals=[i*1000 for i in range(0, max_val, 5)],
                ticktext=[f'{i}' for i in range(0, max_val, 5)]
            )
        
        return fig
    except Exception as e:
        print(f"Errore summary profit trend: {e}")
        return go.Figure()

# Callback per mostrare i valori del filtro purezza formattati
@app.callback(
    Output("purezza-display", "children"),
    Input("purezza-range", "value")
)
def update_purezza_display(value):
    """Mostra i valori della purezza con 4 decimali."""
    if value is None:
        return ""
    return f"{value[0]:.4f} - {value[1]:.4f}"

# Callback per mostrare i valori del filtro profitto formattati in k
@app.callback(
    Output("profitto-display", "children"),
    Input("profitto-range", "value")
)
def update_profitto_display(value):
    """Mostra i valori del profitto in formato k arrotondati."""
    if value is None:
        return ""
    min_val = round(value[0] / 100) / 10
    max_val = round(value[1] / 100) / 10
    return f"€{min_val:.1f}k - €{max_val:.1f}k"

# Callback per gestire la chiusura del modal di benvenuto
@app.callback(
    [Output("welcome-modal", "is_open"),
     Output("welcome-shown", "data")],
    [Input("close-welcome", "n_clicks"),
     Input("welcome-modal", "is_open")],
    [State("welcome-shown", "data")],
    prevent_initial_call=False
)
def close_welcome_modal(n_clicks, is_open, welcome_shown):
    """Chiude il modal di benvenuto al primo click."""
    # Se l'utente ha già visto il welcome, non mostrarlo
    if welcome_shown:
        return False, True
    
    # Se l'utente clicca sul pulsante o sulla X (modal si chiude), salva lo stato
    if n_clicks is not None and n_clicks > 0:
        return False, True
    
    # Se il modal è stato chiuso (is_open diventa False), salva lo stato
    if is_open == False and not welcome_shown:
        return False, True
    
    # Prima visita: mostra il modal
    return True, False


# Avvio del server dell'applicazione
if __name__ == "__main__":
    app.run(debug=True)
