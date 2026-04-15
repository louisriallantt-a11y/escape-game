import streamlit as st
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Manoir Goorse - Officiel", layout="centered")

# --- MÉMOIRE PARTAGÉE ---
@st.cache_resource
def get_global_db():
    return {
        "game_started": False,
        "start_time": 0.0,
        "messages": [],
        "teams": {
            "Lumière": {"membres": "", "prets": False}, 
            "Ombre": {"membres": "", "prets": False}
        }
    }

db = get_global_db()

def send_msg(sender, receiver, text):
    if text:
        db["messages"].append({"from": sender, "to": receiver, "text": text, "time": time.strftime("%H:%M")})

# --- NAVIGATION ---
if 'role' not in st.session_state:
    st.title("🏰 Unlock! Le Manoir de Goorse")
    st.markdown("_Application de coordination pour deux équipes_")
    c1, c2 = st.columns(2)
    if c1.button("🔑 ADMIN"): st.session_state.role = "Admin_Login"; st.rerun()
    if c2.button("🎮 JOUEUR"): st.session_state.role = "Joueur_Config"; st.rerun()
    st.stop()

# --- INTERFACE ADMIN (LOUIS) ---
if st.session_state.role == "Admin":
    st.title("🛡️ Superviseur : Louis")
    
    col_l, col_o = st.columns(2)
    col_l.write(f"Lumière: **{db['teams']['Lumière']['membres']}** ({'✅' if db['teams']['Lumière']['prets'] else '❌'})")
    col_o.write(f"Ombre: **{db['teams']['Ombre']['membres']}** ({'✅' if db['teams']['Ombre']['prets'] else '❌'})")
    
    if db["game_started"]:
        rem = max(0, (90 * 60) - (time.time() - db["start_time"]))
        st.metric("⏳ TEMPS RESTANT", f"{int(rem//60):02d}:{int(rem%60):02d}")
        if st.button("🔴 RESET GÉNÉRAL"): db["game_started"] = False; st.rerun()
    elif st.button("🚀 LANCER L'AVENTURE", use_container_width=True):
        db["start_time"] = time.time(); db["game_started"] = True; st.rerun()

    st.divider()
    st.subheader("💬 Console de Communication")
    dest = st.radio("Destinataire :", ["Tous", "Lumière", "Ombre"], horizontal=True)
    msg_admin = st.text_input("Message ou Indice :")
    if st.button("Envoyer"):
        send_msg("LOUIS", dest, msg_admin); st.rerun()

    st.write("**Derniers messages :**")
    for m in reversed(db["messages"][-10:]):
        st.caption(f"[{m['time']}] {m['from']} ➡️ {m['to']}: {m['text']}")

    if db["game_started"]: time.sleep(2); st.rerun()

# --- CONFIGURATION JOUEUR ---
elif st.session_state.role == "Joueur_Config":
    st.title("📝 Inscription Équipe")
    eq = st.radio("Votre camp :", ["Lumière", "Ombre"])
    noms = st.text_input("Prénoms des joueurs :")
    if st.button("Rejoindre le Manoir"):
        if noms:
            db["teams"][eq]["membres"] = noms; db["teams"][eq]["prets"] = True
            st.session_state.role = f"Joueur_{eq}"; st.rerun()

# --- INTERFACE DE JEU JOUEUR ---
elif "Joueur_" in st.session_state.role:
    equipe = st.session_state.role.split('_')[1]
    autre = "Ombre" if equipe == "Lumière" else "Lumière"
    
    if not db["game_started"]:
        st.title(f"⏳ Équipe {equipe}")
        st.info("Préparez vos cartes... Louis va lancer le signal.")
        time.sleep(3); st.rerun()
    else:
        rem = max(0, (90 * 60) - (time.time() - db["start_time"]))
        st.metric("TEMPS", f"{int(rem//60):02d}:{int(rem%60):02d}")

        tab1, tab2 = st.tabs(["🧩 Énigmes & Codes", "💬 Talkie-Walkie"])

        with tab1:
            st.subheader(f"Mission : {equipe}")
            # Histoire basée sur le PDF
            st.write("Le Professeur Goorse vous a piégés. Vous devez réunir les 4 chiffres du code final.")
            
            with st.expander("📖 Vos indices de départ"):
                if equipe == "Lumière":
                    st.write("- **La bibliothèque :** Cherchez le livre rouge.")
                    st.write("- **Le miroir :** Il semble y avoir un chiffre caché, mais il faut plus de lumière.")
                else:
                    st.write("- **Le coffre-fort :** Il nécessite une clé que seule l'autre équipe peut voir.")
                    st.write("- **La lampe UV :** Elle révèle ce qui est invisible à l'œil nu.")

            # Saisie de codes
            code = st.text_input("Entrez un code trouvé (4 chiffres) :")
            if st.button("Vérifier le code"):
                # Logique basée sur la solution PDF
                if code == "8821":
                    st.balloons()
                    st.success("BRAVO ! Vous avez ouvert la grande porte. Vous êtes LIBRES !")
                elif code == "4592": # Exemple de code intermédiaire
                    st.info("Vous avez déverrouillé le tiroir secret. Donnez le chiffre '8' à l'autre équipe.")
                else:
                    st.error("Rien ne se passe... Recommencez.")

        with tab2:
            st.subheader("Communication")
            dest_j = st.selectbox("Envoyer à :", [autre, "LOUIS"])
            msg_j = st.text_input("Votre message...")
            if st.button("Envoyer"):
                send_msg(equipe, dest_j, msg_j); st.rerun()
            
            st.divider()
            for m in reversed(db["messages"]):
                if m["to"] in ["Tous", equipe] or m["from"] == equipe:
                    color = "#e67e22" if m["from"] == "LOUIS" else "white"
                    st.markdown(f"<p style='color:{color}'><b>[{m['time']}] {m['from']}</b> : {m['text']}</p>", unsafe_allow_html=True)

        if rem > 0: time.sleep(2); st.rerun()

# --- LOGIN ADMIN ---
elif st.session_state.role == "Admin_Login":
    p = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if p == "louis654321": st.session_state.role = "Admin"; st.rerun()
