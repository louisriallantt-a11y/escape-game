import streamlit as st
import time

# Configuration de la page
st.set_page_config(page_title="Manoir Goorse PRO", layout="wide", page_icon="🕵️")

# Initialisation de la base de données fictive (Session State)
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
    st.session_state.ready = {"Lumière": False, "Ombre": False}
    st.session_state.names = {"Lumière": "", "Ombre": ""}
    st.session_state.start_time = None
    st.session_state.messages = []
    st.session_state.logs = []

# --- FONCTION DE MESSAGERIE ---
def send_message(sender, recipient, text):
    st.session_state.messages.append({
        "time": time.strftime("%H:%M"),
        "from": sender,
        "to": recipient,
        "text": text
    })

# --- SYSTÈME DE CONNEXION ---
if 'logged_in' not in st.session_state:
    st.title("🔐 Accès au Système Goorse")
    role = st.selectbox("Rôle", ["Joueur", "Administrateur"])
    user_id = st.text_input("Identifiant")
    pwd = st.text_input("Mot de passe", type="password")
    
    if st.button("Connexion"):
        if role == "Administrateur" and user_id == "Louis" and pwd == "louis654321":
            st.session_state.logged_in = "Admin"
            st.rerun()
        elif role == "Joueur" and user_id:
            st.session_state.logged_in = user_id
            st.rerun()
        else:
            st.error("Identifiants incorrects")
    st.stop()

# --- INTERFACE ADMIN (LOUIS) ---
if st.session_state.logged_in == "Admin":
    st.title("🛡️ Dashboard Superviseur - Louis")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Lumière", "PRÊT" if st.session_state.ready["Lumière"] else "Attente", delta_color="normal")
    col2.metric("Ombre", "PRÊT" if st.session_state.ready["Ombre"] else "Attente")
    col3.write(f"Noms : {st.session_state.names['Lumière']} & {st.session_state.names['Ombre']}")

    if not st.session_state.game_started:
        if st.button("🚀 LANCER LA PARTIE POUR TOUS", use_container_width=True):
            st.session_state.game_started = True
            st.session_state.start_time = time.time()
            st.rerun()
    else:
        st.success("La partie est en cours !")

    st.markdown("---")
    st.subheader("💬 Console de Communication")
    target = st.radio("Destinataire :", ["Tous", "Lumière", "Ombre"])
    admin_msg = st.text_input("Envoyer une consigne ou un indice...")
    if st.button("Diffuser"):
        send_message("ADMIN", target, admin_msg)

# --- INTERFACE JOUEURS ---
else:
    st.title(f"🏰 Manoir Goorse")
    
    if not st.session_state.game_started:
        st.info("Configuration de l'équipe")
        team = st.radio("Votre équipe :", ["Lumière", "Ombre"])
        name = st.text_input("Votre prénom :")
        if st.button("Prêt !"):
            st.session_state.ready[team] = True
            st.session_state.names[team] = name
            st.success("En attente du signal de Louis...")
    
    else:
        # Chrono
        elapsed = time.time() - st.session_state.start_time
        remaining = max(0, (90 * 60) - elapsed)
        mins, secs = divmod(int(remaining), 60)
        
        st.sidebar.header(f"⏳ {mins:02d}:{secs:02d}")
        st.sidebar.progress(remaining / (90 * 60))

        tab_play, tab_chat = st.tabs(["🧩 Énigmes", "💬 Communication"])

        with tab_play:
            st.subheader("Vérification de code")
            code_guess = st.text_input("Entrez un code :")
            if st.button("Vérifier"):
                if code_guess == "8821":
                    st.balloons()
                    st.success("LIBERTÉ ! Vous avez gagné !")
                else:
                    st.error("Code erroné.")

        with tab_chat:
            st.subheader("Chat Inter-Équipes")
            # Affichage des messages
            for m in st.session_state.messages:
                if m["to"] in ["Tous", st.session_state.names.get("Lumière"), st.session_state.names.get("Ombre")] or m["from"] == "ADMIN":
                    st.write(f"**[{m['time']}] {m['from']}** : {m['text']}")
            
            player_msg = st.text_input("Ecrire à l'autre équipe...")
            if st.button("Envoyer"):
                send_message(st.session_state.logged_in, "Tous", player_msg)
                st.rerun()
