from datetime import date, timedelta
import json
import os
import streamlit as st
from streamlit_calendar import calendar

DATA_FILE = "diario_bimbo.json"
CONFIG_FILE = "config_periodi.json"

st.set_page_config(
    page_title="Diario Tommy", 
    page_icon="icona_tommy.jpg",  # Icona nella scheda del browser
    layout="wide"
)

def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

dati = load_json(DATA_FILE)
config = load_json(CONFIG_FILE)

# Inizializzazione dello stato
if "vista" not in st.session_state:
    st.session_state.vista = "calendario"
if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()
if "menu_precedente" not in st.session_state:
    st.session_state.menu_precedente = ""

# Intestazione con l'immagine della Lambretta affiancata al titolo
col_img, col_title = st.columns([0.1, 0.9])
with col_img:
    if os.path.exists("icona_tommy.jpg"):
        st.image("icona_tommy.jpg", width=70)
with col_title:
    st.title("Diario Giornaliero - Tommy")

# Menu laterale
scelta_menu = st.sidebar.selectbox(
    "Navigazione", ["📅 Calendario Principale", "⚙️ Gestione Periodi (Bimbo con me)", "📊 Genera Report"]
)

# Se l'utente cambia opzione nel menu laterale, resettiamo la vista sul calendario principale
if scelta_menu != st.session_state.menu_precedente:
    st.session_state.menu_precedente = scelta_menu
    if scelta_menu == "📅 Calendario Principale":
        st.session_state.vista = "calendario"

if scelta_menu == "📅 Calendario Principale":
    
    # VISTA 1: SOLO IL CALENDARIO
    if st.session_state.vista == "calendario":
        st.subheader("📅 Calendario Attività e Giornate di Tommy")
        st.info("💡 I giorni in cui tuo figlio è con te sono colorati in **Celeste**. **Clicca su un giorno** per aprire i campi di compilazione di quella giornata.")

        events = []
        
        # Giorni in cui il bimbo è con te (Sfondo Celeste)
        periodi_bimbo = config.get("periodi", [])
        for p in periodi_bimbo:
            d_i = date.fromisoformat(p["inizio"])
            d_f = date.fromisoformat(p["fine"])
            curr = d_i
            while curr <= d_f:
                events.append({
                    "start": str(curr),
                    "end": str(curr + timedelta(days=1)),
                    "display": "background",
                    "backgroundColor": "#00b4d8"
                })
                curr += timedelta(days=1)

        # Giorni compilati (Badge verde)
        for d_str in dati.keys():
            events.append({
                "title": "✅ Compilato",
                "start": d_str,
                "allDay": True,
                "backgroundColor": "#2a9d8f",
                "borderColor": "#264653"
            })

        # Configurazione FullCalendar in Italiano e con inizio settimana a Lunedì (firstDay=1)
        calendar_options = {
            "editable": False,
            "selectable": True,
            "locale": "it",
            "firstDay": 1,
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek"
            },
            "initialView": "dayGridMonth",
            "themeSystem": "standard",
        }

        calendar_state = calendar(events=events, options=calendar_options, key="calendario_principale")

        # Gestione del click sulla data (corretto il bug dello sfasamento temporale)
        clicked_raw = None
        if calendar_state.get("dateClick"):
            clicked_raw = calendar_state["dateClick"]["date"][:10]
        elif calendar_state.get("select"):
            clicked_raw = calendar_state["select"]["start"][:10]

        if clicked_raw:
            # Correggiamo lo sfasamento di fuso orario aggiungendo un giorno se necessario, 
            # oppure prendendo direttamente la data corretta spezzando la stringa
            data_cliccata = date.fromisoformat(clicked_raw) + timedelta(days=1)
            st.session_state.selected_date = data_cliccata
            st.session_state.vista = "form_giornata"
            st.rerun()

    # VISTA 2: FORM DI COMPILAZIONE GIORNATA DOPO IL CLICK SUL CALENDARIO
    elif st.session_state.vista == "form_giornata":
        
        if st.button("⬅️ Torna al Calendario"):
            st.session_state.vista = "calendario"
            st.rerun()

        data_str = str(st.session_state.selected_date)
        giorno_data = dati.get(data_str, {})
        
        st.markdown(f"## 📝 Compilazione Giornata: {data_str}")
        
        with st.form(key="form_giornata_singola"):
            
            st.markdown("#### 📌 Impegni e Promemoria")
            impegni = st.text_input("Impegni (es. riunione a scuola, visite...)", value=giorno_data.get("impegni", ""))

            st.markdown("#### 💧 Bisogni e Salute")
            c1, c2 = st.columns(2)
            with c1:
                pipi_notte = st.checkbox("Pipì a letto (notte)", value=giorno_data.get("pipi_notte", False))
                pipi_giorno = st.selectbox("Pipì giorno", ["Regolare", "Poca", "Tanta", "Incidenti"], index=0)
                pipi_addosso = st.checkbox("Pipì addosso (durante il giorno)", value=giorno_data.get("pipi_addosso", False))
            with c2:
                salute = st.selectbox("Stato di salute", ["Ottimo", "Raffreddato", "Febbre", "Altro"], index=0)
                stato_piedino = st.text_input("Stato piedino", value=giorno_data.get("stato_piedino", ""))
                denti_lavati = st.selectbox("Denti lavati (quante volte)", [0, 1, 2, 3], index=giorno_data.get("denti_lavati", 2))

            st.markdown("#### 🍎 Alimentazione")
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                colazione = st.text_input("Colazione con cosa", value=giorno_data.get("colazione", ""))
                cibo_casa = st.text_area("Pranzo/Cena con me", value=giorno_data.get("cibo_casa", ""))
            with col_a2:
                merenda = st.text_input("Merenda con cosa", value=giorno_data.get("merenda", ""))
                cibo_nido = st.text_area("Cosa ha mangiato al nido", value=giorno_data.get("cibo_nido", ""))

            st.markdown("#### 🧸 Umore e Attività")
            c_u1, c_u2 = st.columns(2)
            with c_u1:
                umore = st.selectbox("Umore generale", ["Felice / Sereno", "Tranquillo", "Irritabile", "Capriccioso"], index=0)
            with c_u2:
                capricci = st.selectbox("Capricci", ["Nessuno", "Lieve", "Medio", "Intenso"], index=0)

            bevuti = st.slider("Idratazione (Litri bevuti)", 0.0, 2.0, float(giorno_data.get("bevuti", 1.0)), 0.25, format="%.2f L")
            sonno = st.selectbox("Ore di sonno", ["Molto", "Normale", "Poco"], index=1)
            
            attivita = st.text_area("Chi ha visto / Giochi e Attività", value=giorno_data.get("attivita", ""))
            note_extra = st.text_area("Note generali", value=giorno_data.get("note_extra", ""))

            submit_button = st.form_submit_button(label="💾 Salva Giornata")

            if submit_button:
                dati[data_str] = {
                    "impegni": impegni,
                    "pipi_notte": pipi_notte,
                    "pipi_giorno": pipi_giorno,
                    "pipi_addosso": pipi_addosso,
                    "salute": salute,
                    "stato_piedino": stato_piedino,
                    "denti_lavati": denti_lavati,
                    "colazione": colazione,
                    "merenda": merenda,
                    "cibo_casa": cibo_casa,
                    "cibo_nido": cibo_nido,
                    "umore": umore,
                    "capricci": capricci,
                    "bevuti": bevuti,
                    "sonno": sonno,
                    "attivita": attivita,
                    "note_extra": note_extra
                }
                save_json(DATA_FILE, dati)
                st.success(f"Salvato con successo per il {data_str}!")
                st.session_state.vista = "calendario"
                st.rerun()

elif scelta_menu == "⚙️ Gestione Periodi (Bimbo con me)":
    st.subheader("⚙️ Imposta i periodi in cui tuo figlio è con te")
    st.info("Inserisci l'intervallo di date. Puoi anche impostare la **ripetizione automatica a settimane alterne**.")

    with st.form("form_periodo"):
        c_i, c_f = st.columns(2)
        with c_i:
            d_inizio = st.date_input("Data Inizio periodo base", value=date.today())
        with c_f:
            d_fine = st.date_input("Data Fine periodo base", value=date.today() + timedelta(days=6))
            
        st.markdown("---")
        ripeti_check = st.checkbox("🔄 Ripeti automaticamente a settimane alterne (ogni 2 settimane)")
        num_ripetizioni = st.number_input("Numero di volte da ripetere (settimane)", min_value=1, max_value=26, value=6)
        
        aggiungi_periodo = st.form_submit_button("Aggiungi Periodo/i Celeste/i")
        
        if aggiungi_periodo:
            if "periodi" not in config:
                config["periodi"] = []
                
            durata_periodo = (d_fine - d_inizio).days
            
            for i in range(num_ripetizioni if ripeti_check else 1):
                nuova_i = d_inizio + timedelta(weeks=2 * i)
                nuova_f = nuova_i + timedelta(days=durata_periodo)
                config["periodi"].append({"inizio": str(nuova_i), "fine": str(nuova_f)})
                
            save_json(CONFIG_FILE, config)
            st.success("Periodo/i aggiunto/i con successo!")

    st.markdown("### 📋 Periodi attualmente registrati:")
    if "periodi" in config and config["periodi"]:
        for idx, p in enumerate(config["periodi"]):
            col_p1, col_p2 = st.columns([4, 1])
            with col_p1:
                st.write(f"Dal **{p['inizio']}** al **{p['fine']}**")
            with col_p2:
                if st.button("Elimina", key=f"del_p_{idx}"):
                    config["periodi"].pop(idx)
                    save_json(CONFIG_FILE, config)
                    st.rerun()
    else:
        st.write("Nessun periodo impostato.")

elif scelta_menu == "📊 Genera Report":
    st.header("📊 Genera Report per Range di Date")
    
    if not dati:
        st.info("Nessun dato registrato al momento.")
    else:
        col_i, col_f = st.columns(2)
        with col_i:
            data_inizio = st.date_input("Data Inizio report")
        with col_f:
            data_fine = st.date_input("Data Fine report")
            
        if st.button("Crea Report Dettagliato"):
            st.subheader(f"Report dal {data_inizio} al {data_fine}")
            trovati = False
            
            for d_str, info in sorted(dati.items()):
                d_obj = date.fromisoformat(d_str)
                if data_inizio <= d_obj <= data_fine:
                    trovati = True
                    with st.expander(f"📅 {d_str} | Umore: {info.get('umore')} | Capricci: {info.get('capricci', 'N/D')}"):
                        if info.get('impegni'):
                            st.markdown(f"- **📌 Impegni/Promemoria:** {info['impegni']}")
                        st.markdown(f"- **Pipì letto (notte):** {'Sì' if info['pipi_notte'] else 'No'}")
                        st.markdown(f"- **Pipì giorno:** {info['pipi_giorno']} | **Pipì addosso:** {'Sì' if info.get('pipi_addosso') else 'No'}")
                        st.markdown(f"- **Salute:** {info['salute']} | **Stato piedino:** {info.get('stato_piedino', '-')}")
                        st.markdown(f"- **Denti lavati:** {info.get('denti_lavati', 0)} volte")
                        st.markdown(f"- **Colazione:** {info.get('colazione', '-')}")
                        st.markdown(f"- **Pranzo/Cena (casa):** {info['cibo_casa']}")
                        st.markdown(f"- **Merenda:** {info.get('merenda', '-')}")
                        st.markdown(f"- **Cibo al nido:** {info['cibo_nido']}")
                        st.markdown(f"- **Sonno:** {info['sonno']} | **Idratazione:** {info['bevuti']} L")
                        st.markdown(f"- **Attività/Incontri:** {info['attivita']}")
                        if info.get('note_extra'):
                            st.markdown(f"- **Note extra:** {info['note_extra']}")
            
            if not trovati:
                st.warning("Nessun record trovato nell'intervallo di date selezionato.")