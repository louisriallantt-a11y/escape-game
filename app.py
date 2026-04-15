import streamlit as st
import time

# Configuration de la page
st.set_page_config(page_title="Manoir Goorse PRO", layout="centered", page_icon="🕵️")

# --- INITIALISATION SÉCURISÉE (C'est ici que l'erreur se corrige) ---
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

# --- PAGE DE SÉLECTION INITIALE ---
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
        nom = st.text_input(f"Prénom du joueur {i+1} :", key=f"name_input_{i}")
        if nom: noms.append(nom)
    
    if st.button("Confirmer et Attendre le lancement"):
        if len(noms) == int(nb_joueurs):
            # Sécurité supplémentaire pour éviter la KeyError
            if "teams_config" in st.session_state.db:
                st.session_state.db["teams_config"][equipe_choisie]["membres"] = noms
                st.session_state.db["teams_config"][equipe_choisie]["prets"] = True
                st.session_state.role = f"Joueur_{equipe_choisie}"
                st.success("Configuration enregistrée ! Attendez que Louis lance la partie.")
                st.rerun()
        else:
            st.warning(f"Veuillez remplir les {int(nb_joueurs)} prénoms.")

# --- INTERFACE ADMIN (LOUIS) ---
elif st.session_state.role == "Admin":
    st.title("🛡️ Dashboard de Louis")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Équipe Lumière")
        membres_l = st.session_state.db['teams_config']['Lumière']['membres']
        st.write(f"Joueurs : {', '.join(membres_l) if membres_l else 'Aucun'}")
        st.write("Statut : ", "✅" if st.session_state.db["teams_config"]["Lumière"]["prets"] else "❌")
    with c2:
        st.subheader("Équipe Ombre")
        membres_o = st.session_state.db['teams_config']['Ombre']['membres']
        st.write(f"Joueurs : {', '.join(membres_o) if membres_o else 'Aucun'}")
        st.write("Statut : ", "✅" if st.session_state.db["teams_config"]["Ombre"]["prets"] else "❌")

    st.markdown("---")
    if not st.session_state.db["game_started"]:
        if st.button("🚀 LANCER LA PARTIE", use_container_width=True):
            st.session_state.db["game_started"] = True
            st.session_state.db["start_time"] = time.time()
            st.rerun()
    else:
        st.success("🎮 PARTIE EN COURS")
        if st.button("🔴 RESET GÉNÉRAL"):
            # On vide tout proprement
            st.session_state.clear()
            st.rerun()

# --- INTERFACE DE JEU ---
elif "Joueur_" in st.session_state.role:
    if not st.session_state.db["game_started"]:
        st.title("⏳ En attente de Louis...")
        st.info("La partie n'a pas encore été lancée par l'administrateur.")
        time.sleep(3)
        st.rerun()
    else:
        # Affichage du jeu (Chrono, etc.)
        elapsed = time.time() - st.session_state.db["start_time"]
        rem = max(0, (90 * 60) - elapsed)
        mins, secs = divmod(int(rem), 60)
        
        st.sidebar.title(f"⌛ {mins:02d}:{secs:02d}")
        st.title(f"Équipe {st.session_state.role.split('_')[1]}")
        
        msg = st.text_input("Code ou Message :")
        if st.button("Valider / Envoyer"):
             st.session_state.db["messages"].append(f"{st.session_state.role}: {msg}")
             st.rerun()
