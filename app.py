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
        "messages": [], # Liste de dict: {"from": str, "to": str, "text": str, "time": str}
        "teams": {
            "Lumière": {"membres": "", "prets": False}, 
            "Ombre": {"membres": "", "prets": False}
        }
    }

db = get_global_db()

# --- FONCTION D'ENVOI DE MESSAGE ---
def send_msg(sender, receiver, text):
    if text:
        db["messages"].append({
            "from": sender,
            "to": receiver,
            "text": text,
            "time": time.strftime("%H:%M")
        })

# --- NAVIGATION ---
if 'role' not in st.session_state:
    st.title("🏰 Système Manoir Goorse")
    c1, c2 = st.columns(2)
    if c1.button("🔑 ADMIN"): st.session_state.role = "Admin_Login"; st.rerun()
    if c2.button("🎮 JOUEUR"): st.session_state.role = "Joueur_Config"; st.rerun()
    st.stop()

# --- INTERFACE ADMIN (LOUIS) ---
if st.session_state.role == "Admin":
    st.title("🛡️ Dashboard de Louis")
    
    # Statut des équipes
    col_l, col_o = st.columns(2)
    col_l.write(f"Lumière: **{db['teams']['Lumière']['membres']}** ({'✅' if db['teams']['Lumière']['prets'] else '❌'})")
    col_o.write(f"Ombre: **{db['teams']['Ombre']['membres']}** ({'✅' if db['teams']['Ombre']['prets'] else '❌'})")
    
    # Chrono & Reset
    if db["game_started"]:
        rem = max(0, (90 * 60) - (time.time() - db["start_time"]))
        st.metric("⏳ CHRONO", f"{int(rem//60):02d}:{int(rem%60):02d}")
        if st.button("🔴 RESET"): db["game_started"] = False; st.rerun()
    elif st.button("🚀 LANCER LA PARTIE", use_container_width=True):
        db["start_time"] = time.time(); db["game_started"] = True; st.rerun()

    st.divider()

    # SECTION MESSAGERIE ADMIN
    st.subheader("💬 Centre de Communication (Louis)")
    dest = st.radio("Envoyer à :", ["Tous", "Lumière", "Ombre"], horizontal=True)
    msg_admin = st.text_input("Votre message secret ou indice :")
    if st.button("Diffuser le message"):
        send_msg("LOUIS", dest, msg_admin)
        st.rerun()

    st.write("**Historique de tous les échanges :**")
    for m in reversed(db["messages"]):
        st.caption(f"[{m['time']}] {m['from']} ➡️ {m['to']}: {m['text']}")

    if db["game_started"]: time.sleep(2); st.rerun()

# --- INTERFACE JOUEUR ---
elif "Joueur_" in st.session_state.role:
    equipe_actuelle = st.session_state.role.split('_')[1]
    autre_equipe = "Ombre" if equipe_actuelle == "Lumière" else "Lumière"
    
    if not db["game_started"]:
        st.title(f"⏳ Équipe {equipe_actuelle}")
        st.info("Attente du signal de Louis...")
        time.sleep(3); st.rerun()
    else:
        rem = max(0, (90 * 60) - (time.time() - db["start_time"]))
        st.metric("TEMPS RESTANT", f"{int(rem//60):02d}:{int(rem%60):02d}")

        tab_jeu, tab_chat = st.tabs(["🧩 Jeu & Cartes", "💬 Messagerie"])

        with tab_jeu:
            if st.button("🎴 Voir mes Cartes"):
                st.session_state.show_cards = not st.session_state.get('show_cards', False)
            if st.session_state.get('show_cards'):
                st.info("Indices : " + ("Cartes L1, L2" if equipe_actuelle == "Lumière" else "Cartes O1, O2"))
            
            code = st.text_input("Saisir un code :")
            if st.button("Valider"):
                if code == "8821": st.balloons(); st.success("BRAVO !")
                else: st.error("Code erroné")

        with tab_chat:
            st.subheader(f"Chat Équipe {equipe_actuelle}")
            
            # Envoi de message
            dest_joueur = st.selectbox("Destinataire :", [autre_equipe, "LOUIS"])
            msg_joueur = st.text_input("Votre message...")
            if st.button("Envoyer"):
                send_msg(equipe_actuelle, dest_joueur, msg_joueur)
                st.rerun()

            # Affichage des messages filtrés
            st.write("---")
            for m in reversed(db["messages"]):
                # On voit les messages pour "Tous", ou ceux qui nous sont destinés, ou ceux qu'on a envoyés
                if m["to"] == "Tous" or m["to"] == equipe_actuelle or m["from"] == equipe_actuelle:
                    color = "orange" if m["from"] == "LOUIS" else "white"
                    st.markdown(f"<span style='color:{color}'>**[{m['time']}] {m['from']}** : {m['text']}</span>", unsafe_allow_html=True)

        if rem > 0: time.sleep(2); st.rerun()

# --- CONFIG & LOGIN (Reste du code inchangé) ---
elif st.session_state.role == "Joueur_Config":
    st.title("Inscriptions")
    eq = st.radio("Equipe", ["Lumière", "Ombre"])
    noms = st.text_input("Prénoms :")
    if st.button("Confirmer"):
        db["teams"][eq]["membres"] = noms; db["teams"][eq]["prets"] = True
        st.session_state.role = f"Joueur_{eq}"; st.rerun()
elif st.session_state.role == "Admin_Login":
    p = st.text_input("Mdp", type="password")
    if st.button("OK"):
        if p == "louis654321": st.session_state.role = "Admin"; st.rerun()
