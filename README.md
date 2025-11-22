
🛠️ Stack Tecnologico
Linguaggio di Programmazione
Python 3.13.5 - Linguaggio principale per logica applicativa, analisi dati e backend
Framework & Librerie Principali
Dash - Framework web interattivo per applicazioni data-driven
Dash Bootstrap Components (DBC) - Componenti UI responsive con tema SOLAR
Plotly - Libreria per grafici interattivi e visualizzazioni avanzate
Pandas - Manipolazione e analisi dati strutturati (DataFrames)
NumPy - Calcoli numerici e operazioni su array multidimensionali
SciPy - Funzioni statistiche avanzate e fit di distribuzioni teoriche
Formattazione & Presentazione
HTML5 - Struttura markup per componenti web
CSS3 / Bootstrap 5 - Styling responsive e layout mobile-first
Markdown - Formattazione testi nei report narrativi
Analisi Statistica
Il sistema implementa distribuzioni teoriche per l'analisi predittiva: Gaussiana (produzione, purezza), Log-Normale (profitti, prezzi), Poisson (eventi rari/guasti).

Hosting & Deployment
L'applicazione è hostata su Render (piano gratuito), una piattaforma cloud che offre hosting automatizzato per applicazioni web. Render si occupa di:

Build automatico dal repository GitHub
Deploy continuo ad ogni push su branch main/dev
Restart automatico del server in caso di crash
Dominio pubblico con connessione sicura HTTPS (certificato SSL gratuito)
Esecuzione con Gunicorn come WSGI server per performance ottimali
⚠️ Nota: Il piano gratuito di Render mette in sleep l'applicazione dopo 15 minuti di inattività. Il primo accesso dopo il periodo di inattività può richiedere 30-60 secondi per il riavvio.

📁 File Principali del Progetto
e_lithium_dashboard.py - Dashboard principale (~1500 righe)
e_lithium_simulatore.py - Simulatore dati di produzione
requirements.txt - Dipendenze Python
🏗️ Architettura Applicativa
L'applicazione segue un'architettura MVC (Model-View-Controller) adattata per applicazioni web interattive:

Model - Gestione dati CSV, calcolo KPI, analisi statistiche
View - Componenti Dash/HTML per UI responsive
Controller - Callbacks Pattern-Matching per interattività real-time
Sistema di callback reactivi che aggiornano automaticamente i componenti in base alle azioni dell'utente (filtri, tab, simulazioni).
