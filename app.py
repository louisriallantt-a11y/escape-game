import streamlit as st
import time

# Configuration de la page
st.set_page_config(page_title="Manoir Goorse PRO", layout="centered", page_icon="🕵️")

# --- INITIALISATION DE LA BASE DE DONNÉES PARTAGÉE ---
if 'db' not in st.session_state:
    st.session_state.db = {
        "game_started": False,
        "start_time": None,
        "messages": [],
        "teams_config": {
            "Lumière": {"membres": [], "prets": False},
            "Ombre": {"membres": [], "prets": False}
        }
    }

# --- PAGE DE SÉLECTION INITIALE (RÔLE) ---
if 'role' not in st.session_state:
    st.title("🏰 Bienvenue au Manoir Goorse")
    st.subheader("Veuillez sélectionner votre accès :")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 ACCÈS ADMINISTRATEUR", use_container_width=True):
            st.session_state.role = "Admin_Login"
            st.rerun()
    with col2:
        if st.button("🎮 REJOINDRE UNE ÉQUIPE", use_container_width=True):
            st.session_state.role = "Joueur_Config"
            st.rerun()
    st.stop()

# --- LOGIQUE DE CONNEXION ADMIN ---
if st.session_state.role == "Admin_Login":
    st.title("🛡️ Connexion Superviseur")
    pwd = st.text_input("Mot de passe secret", type="password")
    if st.button("Entrer"):
        if pwd == "louis654321":
            st.session_state.role = "Admin"
            st.rerun()
        else:
            st.error("Accès refusé.")
    if st.button("Retour"):
        del st.session_state.role
        st.rerun()

# --- LOGIQUE DE CONFIGURATION JOUEUR ---
elif st.session_state.role == "Joueur_Config":
    st.title("📝 Inscription de l'Équipe")
    
    equipe_choisie = st.radio("Sélectionnez votre camp :", ["Lumière", "Ombre"])
    nb_joueurs = st.number_input("Nombre de personnes dans l'équipe :", min_value=1, max_value=10, value=2)
    
    noms = []
    for i in range(int(nb_joueurs)):
        nom = st.text_input(f"Prénom du joueur {i+1} :", key=f"name_{i}")
        if nom: noms.append(nom)
    
    if st.button("Confirmer et Attendre le lancement"):
        if len(noms) == nb_joueurs:
            st.session_state.db["teams_config"][equipe_choisie]["membres"] = noms
            st.session_state.db["teams_config"][equipe_choisie]["prets"] = True
            st.session_state.role = f"Joueur_{equipe_choisie}"
            st.success("Configuration enregistrée ! Attendez que Louis lance la partie.")
            st.rerun()
        else:
            st.warning("Veuillez remplir tous les prénoms.")

# --- INTERFACE ADMIN (LOUIS) ---
elif st.session_state.role == "Admin":
    st.title("🛡️ Dashboard de Louis")
    
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"Équipe Lumière : {', '.join(st.session_state.db['teams_config']['Lumière']['membres'])}")
        st.write("Prêt : ", "✅" if st.session_state.db["teams_config"]["Lumière"]["prets"] else "❌")
    with c2:
        st.info(f"Équipe Ombre : {', '.join(st.session_state.db['teams_config']['Ombre']['membres'])}")
        st.write("Prêt : ", "✅" if st.session_state.db["teams_config"]["Ombre"]["prets"] else "❌")

    st.markdown("---")
    if not st.session_state.db["game_started"]:
        if st.button("🚀 LANCER LA PARTIE (90 MIN)", use_container_width=True):
            st.session_state.db["game_started"] = True
            st.session_state.db["start_time"] = time.time()
            st.rerun()
    else:
        st.success("PARTIE EN COURS")
        if st.button("🔴 RESET GÉNÉRAL"):
            st.session_state.db["game_started"] = False
            st.rerun()

# --- INTERFACE DE JEU (PENDANT LA PARTIE) ---
elif "Joueur_" in st.session_state.role:
    if not st.session_state.db["game_started"]:
        st.title("⏳ En attente...")
        st.write("Dès que Louis lancera le jeu, ton écran changera automatiquement.")
        time.sleep(2)
        st.rerun()
    else:
        # CHRONO
        elapsed = time.time() - st.session_state.db["start_time"]
        rem = max(0, (90 * 60) - elapsed)
        mins, secs = divmod(int(rem), 60)
        
        st.sidebar.title(f"⌛ {mins:02d}:{secs:02d}")
        st.title(f"🎮 Équipe {st.session_state.role.split('_')[1]}")
        
        # ACTIONS
        tab1, tab2 = st.tabs(["🧩 Résolution", "💬 Chat"])
        with tab1:
            code = st.text_input("Saisir un code secret :")
            if st.button("Valider"):
                if code == "8821": st.balloons()
                else: st.error("Code incorrect")
        
        with tab2:
            st.subheader("Messages reçus")
            for m in st.session_state.db["messages"]:
                st.write(m)
            msg = st.text_input("Envoyer un message à tous :")
            if st.button("Envoyer"):
                st.session_state.db["messages"].append(f"[{st.session_state.role.split('_')[1]}] : {msg}")
                st.rerun()
