import streamlit as st
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Manoir Goorse PRO", layout="centered")

# --- MÉMOIRE PARTAGÉE (SYNCHRO RÉELLE) ---
@st.cache_resource
def get_global_db():
    return {
        "game_started": False,
        "start_time": None,
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
    
    st.write(f"Équipe Lumière : {'✅ PRÊT' if db['teams']['Lumière']['prets'] else '❌ ATTENTE'}")
    st.write(f"Équipe Ombre : {'✅ PRÊT' if db['teams']['Ombre']['prets'] else '❌ ATTENTE'}")
    
    if not db["game_started"]:
        if st.button("🚀 LANCER LA PARTIE", use_container_width=True):
            db["game_started"] = True
            db["start_time"] = time.time()
            st.rerun()
    else:
        # Affichage temps pour Admin
        elapsed = time.time() - db["start_time"]
        rem = max(0, (90 * 60) - elapsed)
        st.metric("Temps Global", f"{int(rem//60):02d}:{int(rem%60):02d}")
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
    if not db["game_started"]:
        st.title("⏳ Attente de Louis...")
        st.info("La partie va bientôt commencer. Préparez vos cartes !")
        time.sleep(2)
        st.rerun()
    else:
        # CALCUL DU TEMPS SÉCURISÉ
        try:
            elapsed = time.time() - db["start_time"]
            remaining = max(0, (90 * 60) - elapsed)
            mins, secs = divmod(int(remaining), 60)
            
            # Affichage du Chrono (HTML)
            st.markdown(f"""
                <div style="text-align: center; border: 5px solid #e67e22; padding: 20px; border-radius: 10px; background-color: #2c3e50; color: white;">
                    <h1 style="font-size: 60px; margin: 0;">{mins:02d}:{secs:02d}</h1>
                    <p>TEMPS RESTANT - EQUIPE {st.session_state.role.split('_')[1].upper()}</p>
                </div>
            """, unsafe_allow_stdio=True)
            
            st.write("---")
            
            # SAISIE DU CODE POUR LE JOUEUR
            code_input = st.text_input("Tapez un code d'objet ou de porte :", key="play_code")
            if st.button("VALIDER LE CODE"):
                # Exemple de logique de code
                if code_input == "8821":
                    st.balloons()
                    st.success("BRAVO ! Vous avez ouvert la porte finale !")
                elif code_input == "1234":
                    st.info("Le coffre s'ouvre... Vous trouvez un nouveau fragment de carte.")
                else:
                    st.error("Code erroné ou objet non trouvé.")
            
            # Refresh du chrono
            if remaining > 0:
                time.sleep(1)
                st.rerun()
        except Exception as e:
            st.error("Erreur de synchronisation... reconnexion au chrono.")
            time.sleep(1)
            st.rerun()

# --- GESTION LOGIN ADMIN ---
elif st.session_state.role == "Admin_Login":
    pwd = st.text_input("Code secret", type="password")
    if st.button("Entrer"):
        if pwd == "louis654321": st.session_state.role = "Admin"; st.rerun()
    if st.button("Retour"): del st.session_state.role; st.rerun()
