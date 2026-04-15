import streamlit as st
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Manoir Goorse PRO", layout="centered")

# --- MÉMOIRE PARTAGÉE (SYNCHRONISATION RÉELLE) ---
@st.cache_resource
def get_global_db():
    # Ce dictionnaire sera le même pour TOUS les utilisateurs sur le serveur
    return {
        "game_started": False,
        "start_time": None,
        "messages": [],
        "teams": {"Lumière": {"membres": [], "prets": False}, 
                  "Ombre": {"membres": [], "prets": False}}
    }

db = get_global_db()

# --- INITIALISATION SESSION LOCALE ---
if 'role' not in st.session_state:
    st.title("🏰 Manoir Goorse")
    col1, col2 = st.columns(2)
    if col1.button("🔑 ADMIN"): st.session_state.role = "Admin_Login"; st.rerun()
    if col2.button("🎮 JOUEUR"): st.session_state.role = "Joueur_Config"; st.rerun()
    st.stop()

# --- LOGIQUE ADMIN ---
if st.session_state.role == "Admin_Login":
    pwd = st.text_input("Mdp", type="password")
    if st.button("OK"):
        if pwd == "louis654321": st.session_state.role = "Admin"; st.rerun()
    if st.button("Retour"): del st.session_state.role; st.rerun()

elif st.session_state.role == "Admin":
    st.title("🛡️ Dashboard Louis")
    st.write(f"Lumière: {'✅' if db['teams']['Lumière']['prets'] else '❌'}")
    st.write(f"Ombre: {'✅' if db['teams']['Ombre']['prets'] else '❌'}")
    
    if not db["game_started"]:
        if st.button("🚀 LANCER LA PARTIE POUR TOUS"):
            db["game_started"] = True
            db["start_time"] = time.time()
            st.rerun()
    else:
        st.success("PARTIE EN COURS")
        if st.button("🔴 RESET"):
            db["game_started"] = False
            db["teams"]["Lumière"]["prets"] = False
            db["teams"]["Ombre"]["prets"] = False
            st.rerun()

# --- LOGIQUE JOUEUR ---
elif st.session_state.role == "Joueur_Config":
    team = st.radio("Equipe", ["Lumière", "Ombre"])
    if st.button("Rejoindre"):
        db["teams"][team]["prets"] = True
        st.session_state.role = f"Joueur_{team}"
        st.rerun()

elif "Joueur_" in st.session_state.role:
    if not db["game_started"]:
        st.title("⏳ En attente de Louis...")
        st.info("L'écran s'actualisera quand Louis cliquera sur Lancer.")
        time.sleep(2) # Attendre 2 sec
        st.rerun()    # Forcer le rafraîchissement pour voir si db['game_started'] a changé
    else:
        st.title(f"🎮 JEU LANCÉ - Equipe {st.session_state.role.split('_')[1]}")
        # Calcul du temps
        elapsed = time.time() - db["start_time"]
        rem = max(0, (90 * 60) - elapsed)
        st.header(f"⏳ {int(rem//60):02d}:{int(rem%60):02d}")
        
        if st.button("Vérifier Code Final"):
            st.write("Entrez le code...")
