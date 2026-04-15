import streamlit as st
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Manoir Goorse PRO", layout="centered")

# --- MÉMOIRE PARTAGÉE (SYNCHRONISATION) ---
@st.cache_resource
def get_global_db():
    return {
        "game_started": False,
        "start_time": 0.0,
        "teams": {
            "Lumière": {"membres": "", "prets": False}, 
            "Ombre": {"membres": "", "prets": False}
        }
    }

db = get_global_db()

# --- INITIALISATION ÉTAT LOCAL ---
if 'show_cards' not in st.session_state:
    st.session_state.show_cards = False

# --- LOGIQUE DE NAVIGATION ---
if 'role' not in st.session_state:
    st.title("🏰 Bienvenue au Manoir Goorse")
    c1, c2 = st.columns(2)
    if c1.button("🔑 ACCÈS ADMIN"): st.session_state.role = "Admin_Login"; st.rerun()
    if c2.button("🎮 REJOINDRE ÉQUIPE"): st.session_state.role = "Joueur_Config"; st.rerun()
    st.stop()

# --- INTERFACE ADMIN (LOUIS) ---
if st.session_state.role == "Admin":
    st.title("🛡️ Dashboard de Louis")
    col_l, col_o = st.columns(2)
    with col_l:
        st.subheader("Équipe Lumière")
        st.write(f"Joueurs : **{db['teams']['Lumière']['membres']}**")
        st.write("Prêt :", "✅" if db['teams']['Lumière']['prets'] else "❌")
    with col_o:
        st.subheader("Équipe Ombre")
        st.write(f"Joueurs : **{db['teams']['Ombre']['membres']}**")
        st.write("Prêt :", "✅" if db['teams']['Ombre']['prets'] else "❌")
    
    st.divider()
    if not db["game_started"]:
        if st.button("🚀 LANCER LA PARTIE", use_container_width=True):
            db["start_time"] = time.time()
            db["game_started"] = True
            st.rerun()
    else:
        rem_admin = max(0, (90 * 60) - (time.time() - db["start_time"]))
        st.metric("⏳ CHRONO GLOBAL", f"{int(rem_admin//60):02d}:{int(rem_admin%60):02d}")
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
    eq = st.radio("Choisissez votre équipe :", ["Lumière", "Ombre"])
    noms = st.text_input("Prénoms des joueurs :")
    if st.button("Confirmer"):
        if noms:
            db["teams"][eq]["membres"] = noms
            db["teams"][eq]["prets"] = True
            st.session_state.role = f"Joueur_{eq}"
            st.rerun()

# --- INTERFACE DE JEU JOUEUR ---
elif "Joueur_" in st.session_state.role:
    equipe = st.session_state.role.split('_')[1]
    
    if not db["game_started"]:
        st.title(f"⏳ Équipe {equipe}")
        st.info("Attente du lancement par Louis...")
        time.sleep(2)
        st.rerun()
    else:
        # CALCUL TEMPS
        elapsed = time.time() - db["start_time"]
        remaining = max(0, (90 * 60) - elapsed)
        m, s = divmod(int(remaining), 60)
        
        st.title(f"🕵️ Équipe {equipe.upper()}")
        st.metric("TEMPS RESTANT", f"{m:02d}:{s:02d}")
        
        # --- L'HISTOIRE ---
        with st.expander("📖 L'AFFAIRE GOORSE (HISTOIRE)", expanded=True):
            st.write(f"""
            **Rapport de Mission :**
            Vous avez été envoyés par l'agence pour récupérer le prototype du Professeur Goorse. 
            Mais c'était un piège. Les portes se sont verrouillées et un mécanisme complexe 
            sépare vos deux groupes par un mur de verre blindé.
            
            **Votre mission :** Échanger vos informations pour désactiver les verrous. 
            L'équipe **Lumière** possède les codes de déchiffrement, mais l'équipe **Ombre** possède les outils pour les lire.
            """)

        # --- LES CARTES (FIXES) ---
        if st.button("🎴 Afficher/Masquer mes Cartes"):
            st.session_state.show_cards = not st.session_state.show_cards

        if st.session_state.show_cards:
            st.subheader("Vos indices actuels :")
            if equipe == "Lumière":
                st.warning("**CARTE L1 - Le Miroir de Goorse**")
                st.write("Le miroir semble vide, mais il réagit à une certaine longueur d'onde.")
                st.warning("**CARTE L2 - Dispositif Solaire**")
                st.write("Un cadran avec trois symboles. Seule l'autre équipe peut voir la position des aiguilles.")
            else:
                st.info("**CARTE O1 - Lampe de Blacklight**")
                st.write("L'ampoule émet une lumière UV. Essayez de la pointer vers les objets de l'autre équipe.")
                st.info("**CARTE O2 - Boîtier Mystère**")
                st.write("Contient un bouton. Une fois pressé, il envoie un code à l'autre équipe.")
            
            st.caption("Consultez le PDF 'Manoir_Goorse.pdf' pour les visuels complets.")

        st.divider()
        
        # ZONE DE CODE
        code = st.text_input("Saisir un code débloqué :", key="game_code")
        if st.button("Valider"):
            if code == "8821": st.balloons(); st.success("LA PORTE FINALE S'OUVRE !")
            elif code == "1234": st.info("Objet débloqué : La clé de cuivre.")
            else: st.error("Code erroné.")

        # RAFRAÎCHISSEMENT
        if remaining > 0:
            time.sleep(1)
            st.rerun()

# --- LOGIN ADMIN ---
elif st.session_state.role == "Admin_Login":
    p = st.text_input("Mdp", type="password")
    if st.button("OK"):
        if p == "louis654321": st.session_state.role = "Admin"; st.rerun()
    if st.button("Retour"): del st.session_state.role; st.rerun()
