import streamlit as st
import time

# Configuration
st.set_page_config(page_title="Manoir Goorse PRO", layout="wide")

# --- INITIALISATION DES VARIABLES GLOBALES ---
# On utilise st.cache_resource pour simuler une petite base de données partagée
if 'db' not in st.session_state:
    st.session_state.db = {
        "game_started": False,
        "ready_lumiere": False,
        "ready_ombre": False,
        "start_time": None,
        "messages": []
    }

# --- SYSTÈME DE CONNEXION ---
if 'user' not in st.session_state:
    st.title("🔐 Accès Manoir Goorse")
    u = st.text_input("Identifiant")
    p = st.text_input("Mot de passe", type="password")
    if st.button("Connexion"):
        if u == "Louis" and p == "louis654321":
            st.session_state.user = "Admin"
            st.rerun()
        else:
            st.session_state.user = u
            st.rerun()
    st.stop()

# --- INTERFACE ADMIN (LOUIS) ---
if st.session_state.user == "Admin":
    st.title("🛡️ Dashboard de Louis")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 LANCER LA PARTIE MAINTENANT"):
            st.session_state.db["game_started"] = True
            st.session_state.db["start_time"] = time.time()
            st.success("Partie lancée !")
            
    with col2:
        if st.button("🔴 RESET TOUT"):
            st.session_state.db["game_started"] = False
            st.rerun()

    st.write("---")
    st.subheader("Discussion")
    msg = st.text_input("Message aux équipes")
    if st.button("Envoyer"):
        st.session_state.db["messages"].append(f"LOUIS : {msg}")

# --- INTERFACE JOUEURS ---
else:
    # AUTO-REFRESH : Cette ligne force l'app à vérifier le statut toutes les 3 secondes
    if not st.session_state.db["game_started"]:
        st.title(f"Bienvenue {st.session_state.user}")
        st.warning("Attente du lancement par Louis... L'écran s'actualisera tout seul.")
        time.sleep(3)
        st.rerun()
    else:
        st.title("🎮 LA PARTIE A COMMENCÉ !")
        
        # Calcul du temps
        elapsed = time.time() - st.session_state.db["start_time"]
        remaining = max(0, (90 * 60) - elapsed)
        mins, secs = divmod(int(remaining), 60)
        
        st.header(f"⏳ Temps restant : {mins:02d}:{secs:02d}")
        
        # Chat et Actions
        tab1, tab2 = st.tabs(["Actions", "Chat"])
        with tab1:
            st.write("Consultez vos cartes PDF !")
            code = st.text_input("Code secret")
            if st.button("Valider"):
                if code == "8821": st.success("GAGNÉ")
                else: st.error("Faux")
        
        with tab2:
            for m in st.session_state.db["messages"]:
                st.write(m)
            p_msg = st.text_input("Message")
            if st.button("Envoyer"):
                st.session_state.db["messages"].append(f"{st.session_state.user} : {p_msg}")
                st.rerun()
            
            player_msg = st.text_input("Ecrire à l'autre équipe...")
            if st.button("Envoyer"):
                send_message(st.session_state.logged_in, "Tous", player_msg)
                st.rerun()
