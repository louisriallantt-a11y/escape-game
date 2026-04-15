import streamlit as st
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Manoir Goorse PRO", layout="centered")

# --- MÉMOIRE PARTAGÉE ---
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

# --- INITIALISATION SESSION ---
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
    with col_l:
        st.subheader("Équipe Lumière")
        st.write(f"Joueurs : **{db['teams']['Lumière']['membres'] if db['teams']['Lumière']['membres'] else 'En attente...'}**")
        st.write("Prêt :", "✅" if db['teams']['Lumière']['prets'] else "❌")
    
    with col_o:
        st.subheader("Équipe Ombre")
        st.write(f"Joueurs : **{db['teams']['Ombre']['membres'] if db['teams']['Ombre']['membres'] else 'En attente...'}**")
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
            db["teams"]["Lumière"]["membres"] = ""
            db["teams"]["Ombre"]["membres"] = ""
            st.rerun()
        time.sleep(1)
        st.rerun()

# --- CONFIGURATION JOUEUR ---
elif st.session_state.role == "Joueur_Config":
    st.title("📝 Inscription")
    eq = st.radio("Choisissez votre équipe :", ["Lumière", "Ombre"])
    noms_input = st.text_input("Prénoms des joueurs (ex: Jean et Marc) :")
    
    if st.button("Confirmer l'inscription"):
        if noms_input:
            db["teams"][eq]["membres"] = noms_input
            db["teams"][eq]["prets"] = True
            st.session_state.role = f"Joueur_{eq}"
            st.rerun()
        else:
            st.error("Merci d'entrer vos noms.")

# --- INTERFACE DE JEU JOUEUR ---
elif "Joueur_" in st.session_state.role:
    equipe_actuelle = st.session_state.role.split('_')[1]
    
    if not db["game_started"] or db["start_time"] <= 0:
        st.title(f"⏳ Équipe {equipe_actuelle}")
        st.info("Inscription réussie ! Louis va bientôt lancer le chrono.")
        time.sleep(2)
        st.rerun()
    else:
        # CALCULS
        remaining = max(0, (90 * 60) - (time.time() - db["start_time"]))
        m, s = divmod(int(remaining), 60)
        
        st.title(f"🕵️ Équipe {equipe_actuelle.upper()}")
        st.metric("TEMPS RESTANT", f"{m:02d}:{s:02d}")
        
        # SECTION HISTOIRE
        with st.expander("📖 Lire l'Histoire"):
            st.write("""
            Le Professeur Goorse a disparu en laissant derrière lui ce manoir piégé. 
            Une seule issue existe, mais elle nécessite la coordination parfaite entre l'ombre et la lumière.
            Le gaz neurotoxique sera libéré dans 90 minutes. Bonne chance.
            """)

        # SECTION CARTES (DYNAMIQUE)
        if st.button("🎴 Voir mes Cartes"):
            st.divider()
            if equipe_actuelle == "Lumière":
                st.info("**Carte L1 :** Le Miroir. Inscription invisible (besoin de la lampe UV de l'équipe Ombre).")
                st.info("**Carte L2 :** Le Code Solaire. Symboles : ☀️ ☁️ ⭐")
            else:
                st.info("**Carte O1 :** La Lampe UV. Permet de lire les miroirs (utile pour l'équipe Lumière).")
                st.info("**Carte O3 :** Le Code Lunaire. Symboles : 🌙 ☁️ ⚡")
        
        st.divider()
        
        # ZONE DE CODE
        code_res = st.text_input("Entrez un code :", key="game_input")
        if st.button("Valider"):
            if code_res == "8821": st.balloons(); st.success("LIBERTÉ !")
            else: st.error("Code erroné")

        if remaining > 0:
            time.sleep(1)
            st.rerun()

# --- LOGIN ADMIN ---
elif st.session_state.role == "Admin_Login":
    p = st.text_input("Mdp", type="password")
    if st.button("OK"):
        if p == "louis654321": st.session_state.role = "Admin"; st.rerun()
    if st.button("Retour"): del st.session_state.role; st.rerun()
