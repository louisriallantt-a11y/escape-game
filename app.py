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
        "messages": [],
        "teams": {"Lumière": {"prets": False}, "Ombre": {"prets": False}}
    }

db = get_global_db()

# --- INITIALISATION SESSION ---
if 'role' not in st.session_state:
    st.title("🏰 Manoir Goorse")
    c1, c2 = st.columns(2)
    if c1.button("🔑 ADMIN"): st.session_state.role = "Admin_Login"; st.rerun()
    if c2.button("🎮 JOUEUR"): st.session_state.role = "Joueur_Config"; st.rerun()
    st.stop()

# --- LOGIQUE ADMIN (LOUIS) ---
if st.session_state.role == "Admin":
    st.title("🛡️ Dashboard Louis")
    col_l, col_o = st.columns(2)
    col_l.metric("Lumière", "✅" if db['teams']['Lumière']['prets'] else "❌")
    col_o.metric("Ombre", "✅" if db['teams']['Ombre']['prets'] else "❌")
    
    if not db["game_started"]:
        if st.button("🚀 LANCER", use_container_width=True):
            db["start_time"] = time.time()
            db["game_started"] = True
            st.rerun()
    else:
        rem_admin = max(0, (90 * 60) - (time.time() - db["start_time"]))
        st.metric("⏳ CHRONO GLOBAL", f"{int(rem_admin//60):02d}:{int(rem_admin%60):02d}")
        if st.button("🔴 RESET"):
            db["game_started"] = False
            st.rerun()
        time.sleep(1)
        st.rerun()

# --- CONFIGURATION JOUEUR ---
elif st.session_state.role == "Joueur_Config":
    st.title("📝 Inscription")
    eq = st.radio("Equipe :", ["Lumière", "Ombre"])
    if st.button("Valider"):
        db["teams"][eq]["prets"] = True
        st.session_state.role = f"Joueur_{eq}"
        st.rerun()

# --- INTERFACE DE JEU JOUEUR ---
elif "Joueur_" in st.session_state.role:
    if not db["game_started"] or db["start_time"] <= 0:
        st.title("⏳ Attente de Louis...")
        st.info("Le chrono n'est pas encore lancé.")
        time.sleep(2)
        st.rerun()
    else:
        # CALCULS
        remaining = max(0, (90 * 60) - (time.time() - db["start_time"]))
        m, s = divmod(int(remaining), 60)
        
        # AFFICHAGE NATIF (SANS HTML POUR ÉVITER LE TYPEERROR)
        st.title(f"🕵️ ÉQUIPE {st.session_state.role.split('_')[1].upper()}")
        st.metric("TEMPS RESTANT", f"{m:02d}:{s:02d}")
        
        st.divider()
        
        # ZONE DE CODE
        with st.container():
            res = st.text_input("Entrez un code secret :", key="play_input")
            if st.button("Valider le code"):
                if res == "8821": 
                    st.balloons()
                    st.success("SORTIE DÉBLOQUÉE !")
                elif res == "1234":
                    st.warning("Indice : Regardez sous la table.")
                else: 
                    st.error("Code erroné")

        # RAFRAÎCHISSEMENT
        if remaining > 0:
            time.sleep(1)
            st.rerun()
        else:
            st.error("TEMPS ÉCOULÉ !")

# --- LOGIN ADMIN ---
elif st.session_state.role == "Admin_Login":
    p = st.text_input("Mdp", type="password")
    if st.button("OK"):
        if p == "louis654321": st.session_state.role = "Admin"; st.rerun()
    if st.button("Retour"): del st.session_state.role; st.rerun()
