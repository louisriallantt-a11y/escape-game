import streamlit as st
import time

# --- CONFIGURATION ET STYLE ---
st.set_page_config(page_title="Manoir Goorse", layout="centered")

# CSS pour éviter l'effet grisé et stabiliser l'interface
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    div[data-testid="stMetricValue"] { color: #FFA500 !important; }
    /* Cache le message de chargement de Streamlit pour plus de fluidité */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DONNÉES PARTAGÉE ---
@st.cache_resource
def get_db():
    return {
        "start": False, "t_zero": 0.0, "msgs": [],
        "teams": {"Lumière": {"noms": "", "ready": False}, "Ombre": {"noms": "", "ready": False}}
    }

db = get_db()

# --- LOGIQUE DE NAVIGATION ---
if 'role' not in st.session_state:
    st.title("🏰 UNLOCK : L'île de Goorse")
    # Remplace par ton image de couverture si tu en as une
    st.write("Bienvenue dans l'aventure. Choisissez votre accès.")
    c1, c2 = st.columns(2)
    if c1.button("🔑 LOUIS"): st.session_state.role = "Admin_Login"; st.rerun()
    if c2.button("🎮 JOUEURS"): st.session_state.role = "Config"; st.rerun()
    st.stop()

# --- INTERFACE LOUIS (ADMIN) ---
if st.session_state.role == "Admin":
    st.title("🛡️ Supervision")
    
    col_stat1, col_stat2 = st.columns(2)
    col_stat1.metric("Équipe Lumière", db['teams']['Lumière']['noms'] if db['teams']['Lumière']['noms'] else "Vide")
    col_stat2.metric("Équipe Ombre", db['teams']['Ombre']['noms'] if db['teams']['Ombre']['noms'] else "Vide")
    
    if not db["start"]:
        if st.button("🚀 LANCER LE TIMER (90 MIN)", use_container_width=True):
            db["t_zero"] = time.time(); db["start"] = True; st.rerun()
    else:
        elapsed = time.time() - db["t_zero"]
        rem = max(0, (90 * 60) - elapsed)
        st.header(f"⌛ {int(rem//60):02d}:{int(rem%60):02d}")
        
        # Envoi de message Admin
        dest = st.radio("Cible", ["Tous", "Lumière", "Ombre"], horizontal=True)
        txt = st.text_input("Message / Indice")
        if st.button("Envoyer"):
            db["msgs"].append({"f": "LOUIS", "t": dest, "m": txt, "h": time.strftime("%H:%M")})
            st.rerun()
            
        if st.button("🔴 RESET TOUT"): db["start"] = False; st.rerun()

# --- INTERFACE JOUEUR ---
elif "Joueur_" in st.session_state.role:
    eq = st.session_state.role.split('_')[1]
    
    if not db["start"]:
        st.info(f"Équipe {eq} connectée. En attente de Louis...")
        time.sleep(2); st.rerun()
    else:
        rem = max(0, (90 * 60) - (time.time() - db["t_zero"]))
        mins, secs = divmod(int(rem), 60)
        
        st.metric("TEMPS RESTANT", f"{mins:02d}:{secs:02d}")

        t1, t2 = st.tabs(["🧩 JEU", "💬 CHAT"])
        
        with t1:
            # AFFICHAGE DE TES CAPTURES D'ÉCRAN
            if eq == "Lumière":
                st.subheader("☀️ Équipe Lumière (Désert)")
                # ICI : Mets le nom exact de ton fichier image uploadé sur GitHub
                try:
                    st.image("Capture d’écran 2026-04-15 à 18.51.11.png", caption="Vos indices")
                except:
                    st.warning("Image Lumière manquante dans le dossier.")
            else:
                st.subheader("🌙 Équipe Ombre (Jungle)")
                try:
                    st.image("Capture d’écran 2026-04-15 à 18.51.45.png", caption="Vos indices")
                except:
                    st.warning("Image Ombre manquante dans le dossier.")

            st.write("---")
            res = st.text_input("Saisir un code (Solution: 8821 ou 7567) :")
            if st.button("Vérifier"):
                if res == "8821": st.balloons(); st.success("LIBERTÉ !")
                elif res == "7567": st.info("Code Sphinx : 10 min de sursis !")
                else: st.error("Code erroné.")

        with t2:
            target_j = "Ombre" if eq == "Lumière" else "Lumière"
            msg_j = st.text_input(f"Message à l'équipe {target_j} :")
            if st.button("Envoyer"):
                db["msgs"].append({"f": eq, "t": target_j, "m": msg_j, "h": time.strftime("%H:%M")})
                st.rerun()
            
            for m in reversed(db["msgs"]):
                if m["t"] in ["Tous", eq] or m["f"] == eq:
                    st.write(f"**{m['f']}** : {m['m']}")

# --- LOGIN & INSCRIPTION ---
elif st.session_state.role == "Admin_Login":
    if st.text_input("Mdp", type="password") == "louis654321":
        if st.button("Entrer"): st.session_state.role = "Admin"; st.rerun()
elif st.session_state.role == "Config":
    choix = st.radio("Équipe", ["Lumière", "Ombre"])
    noms = st.text_input("Vos noms")
    if st.button("Lancer"):
        db["teams"][choix]["noms"] = noms; st.session_state.role = f"Joueur_{choix}"; st.rerun()

# Boucle de rafraîchissement (toutes les 3 sec pour éviter le gris)
if db["start"]:
    time.sleep(3)
    st.rerun()
