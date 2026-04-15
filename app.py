import streamlit as st
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="Unlock! L'Île de Goorse", layout="centered", page_icon="🏝️")

# Style pour éviter le gris et rester dans l'ambiance "Aventure"
st.markdown("""
    <style>
    .stApp { background-color: #0b1a0b; color: #e0e0e0; }
    div[data-testid="stMetricValue"] { color: #f1c40f !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #1e3d1e; border-radius: 5px; color: white; }
    .emoji-badge { display: inline-block; background: #1e3d1e; padding: 5px 10px; border-radius: 5px; margin: 5px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DONNÉES AVEC PROGRESSION ---
@st.cache_resource
def get_db():
    return {
        "start": False, "t_zero": 0.0, "msgs": [],
        "teams": {
            "Désert (Jaune)": {
                "membres": "", 
                "objets": [],
                "salles_debloquees": ["Crash du Pilote"],
                "etape": 1
            }, 
            "Jungle (Vert)": {
                "membres": "", 
                "objets": [],
                "salles_debloquees": ["Repaire du Singe"],
                "etape": 1
            }
        }
    }

db = get_db()

# --- ÉNIGMES ET PROGRESSION (Type Unlock!) ---
ENIGMES = {
    "Désert (Jaune)": {
        "Crash du Pilote": {
            "description": "Vous trouvez une radio cassée et des débris de l'avion.",
            "énigmes": [
                {"id": 1, "titre": "Le Numéro d'Urgence", "texte": "Quel est le code SOS universel ?", "reponse": "123"}
            ],
            "objets": ["📻 Radio cassée", "🎟️ Billet d'avion"],
            "suivant": "Grotte du Crane"
        },
        "Grotte du Crane": {
            "description": "Une grotte avec un crâne et des hiéroglyphes anciens.",
            "énigmes": [
                {"id": 2, "titre": "Les 3 Symboles", "texte": "Soleil=1, Lune=2, Étoile=3. Quel nombre font-ils ensemble ?", "reponse": "123"}
            ],
            "objets": ["💀 Crâne doré", "🗺️ Parchemin"],
            "suivant": "Sphinx Final"
        },
        "Sphinx Final": {
            "description": "Le grand Sphinx garde la sortie de l'île.",
            "énigmes": [
                {"id": 3, "titre": "La Devinette du Sphinx", "texte": "Combinez vos indices avec l'équipe Jungle pour trouver le code !", "reponse": "7567"}
            ],
            "objets": ["👑 Couronne royale"],
            "suivant": None
        }
    },
    "Jungle (Vert)": {
        "Repaire du Singe": {
            "description": "Un ancien temple envahi par la jungle dense.",
            "énigmes": [
                {"id": 1, "titre": "Le Rituel Maya", "texte": "Quelle est la réponse à 20+16 ?", "reponse": "36"}
            ],
            "objets": ["🐵 Statuette du Singe", "🌿 Herbes rares"],
            "suivant": "Autel Caché"
        },
        "Autel Caché": {
            "description": "Un autel ancien avec des inscriptions sacrées.",
            "énigmes": [
                {"id": 2, "titre": "L'Ordre des Dieux", "texte": "Quel nombre vient immédiatement après 70 ?", "reponse": "71"}
            ],
            "objets": ["🏺 Vase antique", "💎 Gemme verte"],
            "suivant": "Trésor du Temple"
        },
        "Trésor du Temple": {
            "description": "Le cœur secret du temple contient les réponses finales.",
            "énigmes": [
                {"id": 3, "titre": "L'Énigme Finale", "texte": "Attendez le code du Sphinx (Équipe Désert) !", "reponse": "8821"}
            ],
            "objets": ["🎁 Trésor", "📜 Parchemin sacré"],
            "suivant": None
        }
    }
}

def debloquer_salle(equipe, code):
    """Débloque la salle suivante si le code est correct."""
    salle_actuelle = db['teams'][equipe]['salles_debloquees'][-1]
    enigme_data = ENIGMES[equipe][salle_actuelle]
    
    for enigme in enigme_data['énigmes']:
        if enigme['reponse'] == code:
            if enigme_data['suivant']:
                db['teams'][equipe]['salles_debloquees'].append(enigme_data['suivant'])
                db['teams'][equipe]['objets'].extend(enigme_data['objets'])
                db['teams'][equipe]['etape'] += 1
            return True, enigme
    return False, None

# --- INITIALISATION DE RÔLE ---
if 'role' not in st.session_state:
    st.session_state.role = None

# --- PAGE D'ACCUEIL ---
if st.session_state.role is None:
    st.title("🏝️ L'Île du Docteur Goorse")
    st.write("Votre avion s'est écrasé. Deux équipes, une île, 60 minutes pour s'échapper.")
    c1, c2 = st.columns(2)
    if c1.button("🔑 ADMIN"): st.session_state.role = "Admin_Login"; st.rerun()
    if c2.button("🎮 JOUEURS"): st.session_state.role = "Config"; st.rerun()

# --- INTERFACE ADMIN (LOUIS) ---
elif st.session_state.role == "Admin":
    st.title("🛡️ Superviseur : Louis")
    
    col_a, col_b = st.columns(2)
    desert_noms = db['teams']['Désert (Jaune)']['membres']
    jungle_noms = db['teams']['Jungle (Vert)']['membres']
    col_a.metric("Désert", f"Étape {db['teams']['Désert (Jaune)']['etape']}\n{desert_noms}" if desert_noms else "---")
    col_b.metric("Jungle", f"Étape {db['teams']['Jungle (Vert)']['etape']}\n{jungle_noms}" if jungle_noms else "---")

    if not db["start"]:
        if st.button("🚀 LANCER L'AVENTURE", use_container_width=True):
            db["t_zero"] = time.time(); db["start"] = True; st.rerun()
    else:
        rem = max(0, (60 * 60) - (time.time() - db["t_zero"]))
        st.metric("⏳ CHRONO GLOBAL", f"{int(rem//60):02d}:{int(rem%60):02d}")
        
        st.divider()
        st.subheader("📊 Progression des équipes")
        col_prog1, col_prog2 = st.columns(2)
        with col_prog1:
            st.write(f"**Désert :** {' → '.join(db['teams']['Désert (Jaune)']['salles_debloquees'])}")
        with col_prog2:
            st.write(f"**Jungle :** {' → '.join(db['teams']['Jungle (Vert)']['salles_debloquees'])}")
        
        st.divider()
        target = st.radio("Message à :", ["Tous", "Désert (Jaune)", "Jungle (Vert)"], horizontal=True)
        m_txt = st.text_input("Indice ou Message...")
        if st.button("📡 Diffuser"):
            db["msgs"].append({"f": "LOUIS", "t": target, "m": m_txt, "h": time.strftime("%H:%M")})
            st.rerun()
        
        if st.button("🔴 RESET TOUT"): 
            st.session_state.clear()
            st.rerun()
    
    time.sleep(3); st.rerun()

# --- INTERFACE JOUEUR ---
elif st.session_state.role.startswith("Joueur_"):
    mon_equipe = st.session_state.role.split('_')[1]
    autre_equipe = "Jungle (Vert)" if mon_equipe == "Désert (Jaune)" else "Désert (Jaune)"
    
    if not db["start"]:
        st.header(f"Équipe {mon_equipe}")
        st.info("Attente du signal de Louis...")
        time.sleep(3); st.rerun()
    else:
        rem = max(0, (60 * 60) - (time.time() - db["t_zero"]))
        m, s = divmod(int(rem), 60)
        
        st.metric("⏳ TEMPS RESTANT", f"{m:02d}:{s:02d}")
        
        salle_actuelle = db['teams'][mon_equipe]['salles_debloquees'][-1]
        st.subheader(f"📍 {salle_actuelle} (Étape {db['teams'][mon_equipe]['etape']}/3)")
        
        salle_info = ENIGMES[mon_equipe][salle_actuelle]
        st.write(salle_info['description'])
        
        tab1, tab2, tab3 = st.tabs(["🧩 ÉNIGME", "📦 INVENTAIRE", "📡 RADIO"])
        
        with tab1:
            enigme = salle_info['énigmes'][0]
            st.write(f"**{enigme['titre']}**")
            st.write(f"*{enigme['texte']}*")
            
            code = st.text_input("Votre réponse :", key=f"code_{salle_actuelle}")
            if st.button("✅ SOUMETTRE"):
                if code == enigme['reponse']:
                    success, _ = debloquer_salle(mon_equipe, code)
                    if success:
                        st.balloons()
                        st.success(f"✓ Correct ! Vous obtenez : {', '.join(salle_info['objets'])}")
                        if salle_info['suivant']:
                            st.info(f"→ Section suivante débloquée : **{salle_info['suivant']}**")
                        else:
                            st.success("🎉 Vous avez complété votre quête ! Attendez l'équipe Jungle.")
                        time.sleep(2); st.rerun()
                else:
                    st.error("❌ Incorrect. Cherchez un autre indice !")

        with tab2:
            st.write("**📦 Objets trouvés :**")
            if db['teams'][mon_equipe]['objets']:
                for obj in db['teams'][mon_equipe]['objets']:
                    st.markdown(f"<p class='emoji-badge'>{obj}</p>", unsafe_allow_html=True)
            else:
                st.write("_(Aucun objet trouvé pour le moment)_")

        with tab3:
            st.write(f"**📡 Communication avec l'équipe {autre_equipe}**")
            msg_j = st.text_input("Message...")
            if st.button("📤 Envoyer"):
                db["msgs"].append({"f": mon_equipe, "t": autre_equipe, "m": msg_j, "h": time.strftime("%H:%M")})
                st.rerun()
            
            st.divider()
            for m in reversed(db["msgs"]):
                if m["t"] in ["Tous", mon_equipe] or m["f"] == mon_equipe:
                    color = "#f1c40f" if m["f"] == "LOUIS" else "#ffffff"
                    st.markdown(f"<p style='color:{color}'><b>[{m['h']}] {m['f']}</b> : {m['m']}</p>", unsafe_allow_html=True)

        if rem > 0: time.sleep(3); st.rerun()
        else: st.error("⏳ TEMPS ÉCOULÉ ! Aventure terminée.")

# --- LOGIN ADMIN ---
elif st.session_state.role == "Admin_Login":
    pwd = st.text_input("Mot de passe", type="password")
    if st.button("🔓 ACCÈS"):
        if pwd == "louis654321": st.session_state.role = "Admin"; st.rerun()
    if st.button("← Retour"): st.session_state.role = None; st.rerun()
    
# --- CONFIG JOUEUR ---
elif st.session_state.role == "Config":
    st.title("📝 Inscription")
    choix = st.radio("Choisissez votre équipe :", ["Désert (Jaune)", "Jungle (Vert)"])
    noms = st.text_input("Vos prénoms :")
    if st.button("🚀 REJOINDRE"):
        if noms:
            db["teams"][choix]["membres"] = noms
            st.session_state.role = f"Joueur_{choix}"
            st.rerun()
        else:
            st.error("Merci d'entrer vos prénoms.")
    if st.button("← Retour"): st.session_state.role = None; st.rerun()
