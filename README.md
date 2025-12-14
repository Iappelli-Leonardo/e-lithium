
## Codice sorgente elaborato tesi triennale Leonardo Iappelli 




## E-Lithium – Dashboard di Monitoraggio Produzione Litio

Questo progetto realizza una **dashboard interattiva** per l'azienda simulata
_E‑Lithium S.p.A._, specializzata nell'estrazione e raffinazione di litio per
batterie di veicoli elettrici. 

Il lavoro copre **l'intera filiera dei dati**:

- simulazione statistica dei dati di produzione, qualità e performance
- salvataggio su file CSV
- costruzione di una dashboard web con KPI, grafici avanzati e scenari _what‑if_
- spiegazioni testuali (insights automatici e report narrativo) pensate anche
  per utenti non tecnici.

---

## Obiettivi del progetto

- Creare un **dataset realistico ma simulato** sui processi produttivi di una
  miniera di litio (produzione giornaliera, purezza, costi, profitti, guasti).
- Progettare una **dashboard gestionale** leggibile dal management, con
  indicatori sintetici, semafori e commenti automatici.
- Integrare **analisi statistica avanzata** (distribuzioni Normali, Log‑Normali
  e Poisson) per descrivere in modo rigoroso il comportamento delle variabili.
- Implementare un **modulo di simulazione What‑If** per valutare scenari futuri
  variando produzione, prezzi e costi.
- Curare la **documentazione** e la presentazione (README, report, sezione
  "Codice Sorgente" in dashboard, repository GitHub e note di deploy su Render).

---

## Architettura del progetto

Struttura principale del repository:

- `simulatore/e_lithium_simulatore.py`  
  Simula 365 giorni di dati ambientali, produttivi ed economici (produzione,
  purezza, costi, profitti, prezzo, guasti) usando distribuzioni statistiche
  realistiche. Salva il risultato in `data/e_lithium_data.csv`.

- `data/e_lithium_data.csv`  
  File CSV generato dal simulatore. È la **fonte dati** consumata dalla
  dashboard per grafici, KPI, analisi e simulazioni.

- `dashboard/e_lithium_dashboard.py`  
  Applicazione **Dash/Plotly** che legge il CSV, calcola i KPI e costruisce
  l'interfaccia web multi‑tab:
  - Riepilogo Esecutivo
  - Dashboard Operativa
  - Scheda Aziendale
  - Simulazione What‑If
  - Codice Sorgente e Stack Tecnologico

- `requirements.txt`  
  Elenco delle dipendenze Python necessarie per eseguire simulatore e dashboard.

L'architettura segue uno schema tipo **MVC** adattato:

- **Model** – simulatore, caricamento CSV, calcolo KPI, analisi statistiche
- **View** – componenti Dash/Bootstrap (UI responsive, card, grafici)
- **Controller** – callback di Dash che reagiscono a filtri, tab, slider ecc.

---

## Funzionalità principali

### 1. Simulatore di produzione (backend dati)

- Generazione di un dataset giornaliero (circa 1 anno) con:
  - litio estratto (kg)
  - purezza del litio (%)
  - costi operativi (€)
  - ricavi e profitti (€)
  - prezzo di vendita (€/kg)
  - guasti agli impianti (conteggio giornaliero)
- Calcolo di **indicatori derivati** (margine %, efficienza, costo unitario).
- Salvataggio automatico del CSV e log a console per verificare la generazione.

### 2. Dashboard interattiva (frontend dati)

La dashboard è composta da più tab:

- **📋 Riepilogo Esecutivo**  
  Vista sintetica per il management con:
  - KPI medi (produzione, purezza, profitto, margine) con trend
  - card con **semaforo** (verde/giallo/rosso) e tooltip esplicativi
  - filtri rapidi (ultimi 7/30 giorni, migliori performance, alert criticità)
  - "insights" automatici in linguaggio semplice
  - **report narrativo** Markdown che racconta le performance del periodo.

- **📊 Dashboard Operativa**  
  Sezione tecnica con:
  - filtri interattivi (intervallo date, range di purezza, range di profitto)
  - distribuzioni **Gaussiane** per produzione, purezza, margine, costi
  - distribuzioni **Log‑Normali** per profitti e prezzi
  - distribuzione **di Poisson** per i guasti
  - matrice di correlazione in heatmap per individuare relazioni tra variabili.

- **🔮 Simulazione What‑If**  
  Modulo per scenari futuri:
  - selezione del periodo storico di riferimento con uno slider temporale
  - slider per modificare produzione (%), prezzo (€/kg) e costi (%)
  - grafici che confrontano scenario storico vs scenario simulato (profitto e
    margine), per vedere l'impatto economico delle scelte operative.

- **🏭 Scheda Aziendale**  
  Descrizione dell'azienda E‑Lithium S.p.A., processo produttivo, mercato di
  riferimento e dati aziendali (sede, dipendenti, capacità produttiva,
  fatturato, ultimo aggiornamento dinamico mese/anno).

- **💻 Codice Sorgente e Tecnologie**  
  Sezione che documenta:
  - repository GitHub
  - stack tecnologico (Python, Dash, Plotly, Pandas, NumPy, SciPy, Bootstrap)
  - architettura MVC
  - dettagli di hosting e deploy su Render.

In apertura è presente una **modale di benvenuto** che spiega in modo
introduttivo cosa fa la dashboard e quali sono le principali funzionalità.

---

## Stack tecnologico

**Linguaggio**

- Python 3.13.5

**Framework & Librerie principali**

- Dash – framework web interattivo per applicazioni data‑driven
- Dash Bootstrap Components (Solar Theme) – componenti UI responsive
- Plotly – grafici interattivi
- Pandas / NumPy – analisi e calcoli numerici
- SciPy – analisi statistica avanzata (fit di distribuzioni teoriche)

**Formattazione & UI**

- HTML5, CSS3 / Bootstrap 5
- Markdown per il report narrativo integrato nella dashboard

**Distribuzioni statistiche implementate**

- Normale (produzione, purezza, margine, costi)
- Log‑Normale (profitti, prezzi)
- Poisson (eventi rari / guasti)


