import streamlit as st
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Manoir Goorse PRO", layout="centered")

# --- MÉMOIRE PARTAGÉE (SYNCHRO RÉELLE) ---
@st.cache_resource
def get_global_db():
    # Initialisation unique pour tous les utilisateurs
    return {
        "game_started": False,
        "start_time": 0,
        "messages": [],
        "teams": {"Lumière": {"prets": False}, "Ombre": {"prets": False}}
    }

db = get_global_db()

# --- INITIALISATION SESSION LOCALE ---
if 'role' not in st.session_state:
    st.title("🏰 Bienvenue au Manoir Goorse")
    c1, c2 = st.columns(2)
    if c1.button("🔑 ACCÈS ADMIN"): st.session_state.role = "Admin_Login"; st.rerun()
    if c2.button("🎮 REJOINDRE ÉQUIPE"): st.session_state.role = "Joueur_Config"; st.rerun()
    st.stop()

# --- LOGIQUE ADMIN (LOUIS) ---
if st.session_state.role == "Admin":
    st.title("🛡️ Dashboard de Louis")
    
    col_l, col_o = st.columns(2)
    col_l.metric("Lumière", "✅ PRÊT" if db['teams']['Lumière']['prets'] else "❌ ATTENTE")
    col_o.metric("Ombre", "✅ PRÊT" if db['teams']['Ombre']['prets'] else "❌ ATTENTE")
    
    if not db["game_started"]:
        if st.button("🚀 LANCER LA PARTIE", use_container_width=True):
            db["start_time"] = time.time()
            db["game_started"] = True
            st.rerun()
    else:
        # Calcul temps Admin
        rem_admin = max(0, (90 * 60) - (time.time() - db["start_time"]))
        st.header(f"⏳ GLOBAL : {int(rem_admin//60):02d}:{int(rem_admin%60):02d}")
        
        if st.button("🔴 RESET GÉNÉRAL"):
            db["game_started"] = False
            db["teams"]["Lumière"]["prets"] = False
            db["teams"]["Ombre"]["prets"] = False
            st.rerun()
        time.sleep(1)
        st.rerun()

# --- CONFIGURATION JOUEUR ---
elif st.session_state.role == "Joueur_Config":
    st.title("📝 Inscription")
    equipe = st.radio("Choisissez votre équipe :", ["Lumière", "Ombre"])
    if st.button("Valider l'équipe"):
        db["teams"][equipe]["prets"] = True
        st.session_state.role = f"Joueur_{equipe}"
        st.rerun()

# --- INTERFACE DE JEU JOUEUR ---
elif "Joueur_" in st.session_state.role:
    # On vérifie si la partie est lancée ET si le start_time est bien enregistré
    if not db["game_started"] or db["start_time"] == 0:
        st.title("⏳ Attente de Louis...")
        st.info("La partie va bientôt commencer. Préparez vos fiches !")
        time.sleep(2)
        st.rerun()
    else:
        # CALCUL DU TEMPS (Sécurisé : on s'assure que start_time est un nombre)
        now = time.time()
        elapsed = now - db["start_time"]
        remaining = max(0, (90 * 60) - elapsed)
        mins, secs = divmod(int(remaining), 60)
        
        # Affichage du Chrono
        st.markdown(f"""
            <div style="text-align: center; border: 5px solid #e67e22; padding: 20px; border-radius: 10px; background-color: #1a1a1a; color: #e67e22;">
                <h1 style="font-size: 70px; margin: 0;">{mins:02d}:{secs:02d}</h1>
                <p style="color: white;">ÉQUIPE {st.session_state.role.split('_')[1].upper()}</p>
            </div>
        """, unsafe_allow_stdio=True)
        
        st.write("---")
        
        # ZONE DE SAISIE DES CODES
        code_input = st.text_input("Entrez un code (ex: 8821) :", key="play_code")
        if st.button("VALIDER"):
            if code_input == "8821":
                st.balloons()
                st.success("FÉLICITATIONS ! Vous êtes sortis du Manoir !")
            elif code_input == "1234":
                st.info("Le tiroir s'ouvre... regardez la carte L2.")
            else:
                st.error("Code incorrect.")

        # Rafraîchissement automatique
        if remaining > 0:
            time.sleep(1)
            st.rerun()

# --- GESTION LOGIN ADMIN ---
elif st.session_state.role == "Admin_Login":
    pwd = st.text_input("Code secret", type="password")
    if st.button("Entrer"):
        if pwd == "louis654321": st.session_state.role = "Admin"; st.rerun()
    if st.button("Retour"): del st.session_state.role; st.rerun()
