import streamlit as st
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Unlock! L'Île de Goorse", layout="centered", page_icon="🏝️")

# Style pour éviter le gris et rester dans l'ambiance "Aventure"
st.markdown("""
    <style>
    .stApp { background-color: #0b1a0b; color: #e0e0e0; }
    div[data-testid="stMetricValue"] { color: #f1c40f !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #1e3d1e; border-radius: 5px; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DONNÉES ---
@st.cache_resource
def get_db():
    return {
        "start": False, "t_zero": 0.0, "msgs": [],
        "teams": {
            "Désert (Jaune)": {"membres": "", "ready": False}, 
            "Jungle (Vert)": {"membres": "", "ready": False}
        }
    }

db = get_db()

# --- NAVIGATION ---
if 'role' not in st.session_state:
    st.title("🏝️ L'Île du Docteur Goorse")
    st.write("Votre avion s'est écrasé. Vous êtes séparés sur l'île.")
    c1, c2 = st.columns(2)
    if c1.button("🔑 ADMIN"): st.session_state.role = "Admin_Login"; st.rerun()
    if c2.button("🎮 JOUEURS"): st.session_state.role = "Config"; st.rerun()
    st.stop()

# --- ADMIN (LOUIS) ---
if st.session_state.role == "Admin":
    st.title("🛡️ Superviseur : Louis")
    
    col_a, col_b = st.columns(2)
    col_a.metric("Équipe Désert", db['teams']['Désert (Jaune)']['membres'] if db['teams']['Désert (Jaune)']['membres'] else "---")
    col_b.metric("Équipe Jungle", db['teams']['Jungle (Vert)']['membres'] if db['teams']['Jungle (Vert)']['membres'] else "---")

    if not db["start"]:
        if st.button("🚀 LANCER L'AVENTURE", use_container_width=True):
            db["t_zero"] = time.time(); db["start"] = True; st.rerun()
    else:
        rem = max(0, (60 * 60) - (time.time() - db["t_zero"])) # 60 minutes officiellement
        st.metric("CHRONO", f"{int(rem//60):02d}:{int(rem%60):02d}")
        
        target = st.radio("Message à :", ["Tous", "Désert (Jaune)", "Jungle (Vert)"], horizontal=True)
        m_txt = st.text_input("Envoyer un indice...")
        if st.button("Diffuser"):
            db["msgs"].append({"f": "LOUIS", "t": target, "m": m_txt, "h": time.strftime("%H:%M")})
            st.rerun()
        
        if st.button("🔴 RESET"): db["start"] = False; st.rerun()
    
    time.sleep(3); st.rerun()

# --- INTERFACE JOUEUR ---
elif "Joueur_" in st.session_state.role:
    mon_equipe = st.session_state.role.split('_')[1]
    autre_equipe = "Jungle (Vert)" if mon_equipe == "Désert (Jaune)" else "Désert (Jaune)"
    
    if not db["start"]:
        st.header(f"Équipe {mon_equipe}")
        st.info("Attente du signal de Louis pour explorer l'île...")
        time.sleep(3); st.rerun()
    else:
        rem = max(0, (60 * 60) - (time.time() - db["t_zero"]))
        m, s = divmod(int(rem), 60)
        st.metric("TEMPS RESTANT", f"{m:02d}:{s:02d}")

        tab1, tab2 = st.tabs(["🧩 EXPLORATION", "📡 RADIO"])
        
        with tab1:
            if mon_equipe == "Désert (Jaune)":
                st.subheader("📍 Zone : Plage & Désert")
                st.image("Capture d’écran 2026-04-15 à 18.51.11.png")
                st.write("**Indices :** Squelette (71), Empreintes (20), Détecteur (36).")
            else:
                st.subheader("📍 Zone : Jungle profonde")
                st.image("Capture d’écran 2026-04-15 à 18.51.45.png")
                st.write("**Indices :** Alchimie, Temple Maya, Énigmes vertes.")

            code = st.text_input("Saisir un code de carte ou de porte :")
            if st.button("VALIDER"):
                # Codes officiels du PDF
                if code == "7567": 
                    st.balloons(); st.success("INCROYABLE ! Vous avez trouvé le code du Sphinx (7567). Vous gagnez 10 minutes de sursis !")
                elif code == "8821": 
                    st.success("Le code final est correct ! L'avion décolle !")
                elif code == "56": 
                    st.info("Vous trouvez l'Amulette en or.")
                else: 
                    st.error("Rien ne se passe ici.")

        with tab2:
            st.subheader("📡 Radio de survie")
            msg_j = st.text_input("Message radio...")
            if st.button("Émettre"):
                db["msgs"].append({"f": mon_equipe, "t": autre_equipe, "m": msg_j, "h": time.strftime("%H:%M")})
                st.rerun()
            
            for m in reversed(db["msgs"]):
                if m["t"] in ["Tous", mon_equipe] or m["f"] == mon_equipe:
                    color = "#f1c40f" if m["f"] == "LOUIS" else "#ffffff"
                    st.markdown(f"<p style='color:{color}'><b>[{m['h']}] {m['f']}</b> : {m['m']}</p>", unsafe_allow_html=True)

        if rem > 0: time.sleep(3); st.rerun()

# --- CONFIG & LOGIN ---
elif st.session_state.role == "Admin_Login":
    if st.text_input("Mdp", type="password") == "louis654321":
        if st.button("Entrer"): st.session_state.role = "Admin"; st.rerun()
elif st.session_state.role == "Config":
    st.title("Choix de la zone")
    choix = st.radio("Où êtes-vous ?", ["Désert (Jaune)", "Jungle (Vert)"])
    noms = st.text_input("Noms des explorateurs")
    if st.button("S'INSCRIRE"):
        db["teams"][choix]["membres"] = noms; st.session_state.role = f"Joueur_{choix}"; st.rerun()
