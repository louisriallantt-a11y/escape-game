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

# --- LOGIQUE ADMIN ---
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
        # Affichage temps Admin simplifié (sans HTML complexe pour éviter les crashs)
        rem_admin = max(0, (90 * 60) - (time.time() - db["start_time"]))
        st.subheader(f"⏳ GLOBAL : {int(rem_admin//60):02d}:{int(rem_admin%60):02d}")
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
    # Vérification stricte du lancement
    if not db["game_started"] or db["start_time"] <= 0:
        st.title("⏳ Attente de Louis...")
        time.sleep(2)
        st.rerun()
    else:
        # CALCUL SÉCURISÉ
        now = time.time()
        start = db["start_time"]
        diff = now - start
        remaining = max(0, (90 * 60) - diff)
        
        m, s = divmod(int(remaining), 60)
        
        # TRANSFORMATION EN STRING AVANT LE MARKDOWN (Évite le TypeError)
        timer_text = f"{m:02d}:{s:02d}"
        team_name = st.session_state.role.split('_')[1].upper()

        # AFFICHAGE HTML SIMPLIFIÉ
        st.markdown(f"""
            <div style="background-color:#1a1a1a; padding:20px; border-radius:10px; border:4px solid #e67e22; text-align:center;">
                <h1 style="color:#e67e22; font-family:monospace; font-size:60px; margin:0;">{timer_text}</h1>
                <strong style="color:white;">EQUIPE {team_name}</strong>
            </div>
        """, unsafe_allow_stdio=True)
        
        st.write("---")
        
        # CODE INPUT
        res = st.text_input("Entrez un code :", key="play_input")
        if st.button("Valider"):
            if res == "8821": st.balloons(); st.success("Sortie débloquée !")
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
