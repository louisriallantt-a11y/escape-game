import streamlit as st
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Manoir Goorse PRO", layout="centered")

# --- MÉMOIRE PARTAGÉE ---
@st.cache_resource
def get_global_db():
    return {
        "game_started": False,
        "start_time": None,
        "messages": [],
        "teams": {"Lumière": {"membres": [], "prets": False}, 
                  "Ombre": {"membres": [], "prets": False}}
    }

db = get_global_db()

# --- LOGIQUE DE NAVIGATION (RÔLES) ---
if 'role' not in st.session_state:
    st.title("🏰 Manoir Goorse")
    c1, c2 = st.columns(2)
    if c1.button("🔑 ADMIN"): st.session_state.role = "Admin_Login"; st.rerun()
    if c2.button("🎮 JOUEUR"): st.session_state.role = "Joueur_Config"; st.rerun()
    st.stop()

# --- INTERFACE ADMIN ---
if st.session_state.role == "Admin":
    st.title("🛡️ Dashboard Louis")
    if not db["game_started"]:
        if st.button("🚀 LANCER LA PARTIE"):
            db["game_started"] = True
            db["start_time"] = time.time()
            st.rerun()
    else:
        st.success("PARTIE EN COURS")
        # CALCUL DU TEMPS POUR L'ADMIN AUSSI
        elapsed = time.time() - db["start_time"]
        rem = max(0, (90 * 60) - elapsed)
        st.header(f"⏳ Temps Global : {int(rem//60):02d}:{int(rem%60):02d}")
        if st.button("🔴 RESET"):
            db["game_started"] = False
            st.rerun()
        time.sleep(1)
        st.rerun()

# --- INTERFACE JOUEUR (Le Chrono qui bouge) ---
elif "Joueur_" in st.session_state.role:
    if not db["game_started"]:
        st.title("⏳ Attente du signal...")
        st.info("Louis n'a pas encore lancé le chrono.")
        time.sleep(2)
        st.rerun()
    else:
        # --- LE SECRET DU CHRONO QUI BOUGE ---
        elapsed = time.time() - db["start_time"]
        total_seconds = 90 * 60
        remaining = max(0, total_seconds - elapsed)
        
        mins, secs = divmod(int(remaining), 60)
        
        # Affichage du Chrono
        st.markdown(f"""
            <div style="text-align: center; border: 5px solid #e67e22; padding: 20px; border-radius: 10px;">
                <h1 style="font-size: 80px; margin: 0; color: #e67e22;">{mins:02d}:{secs:02d}</h1>
                <p>TEMPS RESTANT</p>
            </div>
        """, unsafe_allow_stdio=True)

        # Actions de jeu
        st.write("---")
        code = st.text_input("Entrez un code secret :", key="game_code")
        if st.button("Valider"):
            if code == "8821": st.balloons()
            else: st.error("Code erroné")

        # FORCER LE RAFRAÎCHISSEMENT CHAQUE SECONDE
        if remaining > 0:
            time.sleep(1) # Attendre une seconde
            st.rerun()    # Relancer l'affichage
        else:
            st.error("TEMPS ÉCOULÉ !")

# --- LOGIN & CONFIG (Reste du code identique) ---
elif st.session_state.role == "Admin_Login":
    pwd = st.text_input("Mdp", type="password")
    if st.button("OK"):
        if pwd == "louis654321": st.session_state.role = "Admin"; st.rerun()
elif st.session_state.role == "Joueur_Config":
    team = st.radio("Equipe", ["Lumière", "Ombre"])
    if st.button("Rejoindre"):
        db["teams"][team]["prets"] = True
        st.session_state.role = f"Joueur_{team}"
        st.rerun()
