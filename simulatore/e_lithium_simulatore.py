import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta


# ==========================================================
#  Simulatore dati per E-lithium S.p.A.
#  Azienda mineraria di litio per batterie elettriche
# ==========================================================

NUM_GIORNI = 60  # giorni simulati
DATA_INIZIO = datetime.now() - timedelta(days=NUM_GIORNI)  # Parte da 60 giorni fa fino ad oggi

os.makedirs("data", exist_ok=True)
OUTPUT_FILE = "data/e_lithium_data.csv"

def simulate_environmental_data(num_days: int):
    """Simula condizioni ambientali nella miniera"""
    temperatura = np.random.normal(27.5, 1.8, num_days)           # °C
    umidita = np.random.normal(62, 5, num_days)                   # %
    co2 = np.random.normal(410, 25, num_days)                     # ppm
    polveri = np.random.normal(40, 8, num_days)                   # µg/m3
    falda = np.random.normal(29, 2, num_days)                     # metri
    return temperatura, umidita, co2, polveri, falda


def simulate_production_data(num_days: int):
    """Simula dati produttivi: quantità, purezza, energia, guasti"""
    litio_estratto = np.random.normal(980, 100, num_days)         # kg/giorno
    #purezza = np.random.normal(97.5, 1.2, num_days)              # %
    grade = np.random.normal(0.975, 0.012, num_days)              # frazione 0-1 (97.5%)
    energia = np.random.normal(3400, 200, num_days)               # kWh/giorno
    guasti = np.random.poisson(0.15, num_days)                    # guasti/giorno
    return litio_estratto, grade, energia, guasti


def simulate_economic_data(num_days: int, litio_estratto):
    """Simula dati economici legati alla vendita di litio"""
    prezzo = np.random.normal(70, 4, num_days)                    # €/kg
    costi = np.random.normal(52000, 4500, num_days)               # €/giorno
    ricavi = litio_estratto * prezzo
    profitto = ricavi - costi
    return prezzo, costi, ricavi, profitto


def generate_dataset(num_days=NUM_GIORNI, data_inizio=DATA_INIZIO):
    """Genera dataset completo per E-lithium S.p.A."""
    date_rng = [data_inizio + timedelta(days=i) for i in range(num_days)]

    temp, hum, co2, dust, water = simulate_environmental_data(num_days)
    litio, grade, energia, guasti = simulate_production_data(num_days)
    prezzo, costi, ricavi, profitto = simulate_economic_data(num_days, litio)

    df = pd.DataFrame({
        "data": date_rng,
        "temperatura_C": temp,
        "umidita_%": hum,
        "CO2_ppm": co2,
        "polveri_ug_m3": dust,
        "livello_falda_m": water,
        "litio_estratto_kg": litio,
        "purezza_%": grade,
        "energia_kWh": energia,
        "guasti": guasti,
        "prezzo_litio_eur_kg": prezzo,
        "costi_eur": costi,
        "ricavi_eur": ricavi,
        "profitto_eur": profitto
    })


    df["efficienza_kWh_kg"] = df["energia_kWh"] / df["litio_estratto_kg"]
    df["margine_%"] = (df["profitto_eur"] / df["ricavi_eur"]) * 100
    df["costo_unitario_eur_kg"] = df["costi_eur"] / df["litio_estratto_kg"]
    return df


if __name__ == "__main__":
    df = generate_dataset()
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"[DEBUG] Directory di lavoro attuale: {os.getcwd()}")
    print(f"[DEBUG] Percorso file di output: {OUTPUT_FILE}")

    
    print(f"[E-lithium S.p.A.] Dati simulati salvati in: {OUTPUT_FILE}")
    print(df.head())
