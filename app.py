import streamlit as st
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Manoir Goorse PRO", layout="centered", page_icon="🕵️")

# --- STYLE CSS (Pour éviter le gris et faire joli) ---
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: white; }
    [data-testid="stMetricValue"] { color: #e67e22 !important; font-size: 50px !important; }
    .stAlert { background-color: #1e1e1e; border: 1px solid #e67e22; }
    </style>
    """, unsafe_allow_html=True)

# --- MÉMOIRE PARTAGÉE ---
@st.cache_resource
def get_db():
    return {
        "start": False, "time": 0.0, "msgs": [],
        "teams": {"Lumière": {"p": "", "ready": False}, "Ombre": {"p": "", "ready": False}}
    }

db = get_db()

# --- NAVIGATION ---
if 'role' not in st.session_state:
    st.title("🏰 UNLOCK : L'île de Goorse")
    st.image("https://cdn.svc.asmodee.net/production-spacecowboys/uploads/2019/02/Goorse_Box_3D.png", width=300)
    c1, c2 = st.columns(2)
    if c1.button("🔑 LOUIS (ADMIN)"): st.session_state.role = "Admin_Login"; st.rerun()
    if c2.button("🎮 JOUEURS"): st.session_state.role = "Config"; st.rerun()
    st.stop()

# --- INTERFACE ADMIN ---
if st.session_state.role == "Admin":
    st.title("🛡️ Contrôle Louis")
    
    # Dashboard rapide
    col_l, col_o = st.columns(2)
    col_l.metric("Lumière", db['teams']['Lumière']['p'] if db['teams']['Lumière']['p'] else "---")
    col_o.metric("Ombre", db['teams']['Ombre']['p'] if db['teams']['Ombre']['p'] else "---")
    
    if not db["start"]:
        if st.button("🚀 LANCER L'AVENTURE", use_container_width=True):
            db["time"] = time.time(); db["start"] = True; st.rerun()
    else:
        rem = max(0, (90 * 60) - (time.time() - db["time"]))
        st.metric("CHRONO", f"{int(rem//60):02d}:{int(rem%60):02d}")
        if st.button("🔴 RESET"): db["start"] = False; st.rerun()

    st.divider()
    # Chat Admin
    target = st.radio("Destinataire", ["Tous", "Lumière", "Ombre"], horizontal=True)
    m_text = st.text_input("Message / Indice")
    if st.button("Envoyer"):
        db["msgs"].append({"f": "LOUIS", "t": target, "m": m_text, "h": time.strftime("%H:%M")})
        st.rerun()

    # Voir les messages des joueurs
    st.write("**Derniers échanges :**")
    for m in reversed(db["msgs"][-5:]):
        st.caption(f"{m['h']} - {m['f']} ➡️ {m['t']}: {m['m']}")
    
    time.sleep(2); st.rerun()

# --- INTERFACE JOUEUR ---
elif "Joueur_" in st.session_state.role:
    eq = st.session_state.role.split('_')[1]
    
    if not db["start"]:
        st.header(f"Équipe {eq}")
        st.info("Attente du signal de départ...")
        time.sleep(2); st.rerun()
    else:
        rem = max(0, (90 * 60) - (time.time() - db["time"]))
        m, s = divmod(int(rem), 60)
        
        # Chrono Pro
        st.metric("TEMPS RESTANT", f"{m:02d}:{s:02d}")

        t1, t2 = st.tabs(["🧩 ÉNIGMES", "💬 CHAT"])
        
        with t1:
            # SECTION HISTOIRE & IMAGES
            if eq == "Lumière":
                st.subheader("☀️ Vos indices de Jour")
                st.image("https://img.vavel.com/b/unlock-kids-1.jpg", caption="Le Manoir au grand jour")
                st.write("**Indice :** Le code final est caché derrière le miroir du salon.")
            else:
                st.subheader("🌙 Vos indices d'Ombre")
                st.image("https://www.ludovox.fr/wp-content/uploads/2017/02/Unlock-3.jpg", caption="Les secrets de la nuit")
                st.write("**Indice :** Votre lampe UV permet de voir les chiffres que l'autre équipe ne voit pas.")

            # SAISIE CODE
            code = st.text_input("Entrez un code (4 chiffres) :", key="code")
            if st.button("Valider"):
                if code == "8821": st.balloons(); st.success("BRAVO ! VOUS ÊTES LIBRES !")
                elif code == "7567": st.info("Code de l'avion trouvé ! 10 min de bonus !")
                else: st.error("Rien ne se passe...")

        with t2:
            # CHAT SIMPLIFIÉ
            msg = st.text_input("Message à l'autre équipe :")
            if st.button("Envoyer"):
                dest = "Ombre" if eq == "Lumière" else "Lumière"
                db["msgs"].append({"f": eq, "t": dest, "m": msg, "h": time.strftime("%H:%M")})
                st.rerun()
            
            for m in reversed(db["msgs"]):
                if m["t"] in ["Tous", eq] or m["f"] == eq:
                    st.write(f"**{m['f']}** : {m['m']}")

        if rem > 0:
            time.sleep(2); st.rerun()

# --- LOGIN & CONFIG ---
elif st.session_state.role == "Admin_Login":
    p = st.text_input("Mot de passe", type="password")
    if st.button("OK"):
        if p == "louis654321": st.session_state.role = "Admin"; st.rerun()
elif st.session_state.role == "Config":
    st.title("Inscription")
    eq = st.radio("Equipe", ["Lumière", "Ombre"])
    noms = st.text_input("Vos prénoms")
    if st.button("GO"):
        db["teams"][eq]["p"] = noms; st.session_state.role = f"Joueur_{eq}"; st.rerun()
