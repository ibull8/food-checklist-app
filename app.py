import streamlit as st
import pandas as pd

# --- שלב 1: עדכון פרטי ה-GitHub שלך ---
# החלף את הערכים הבאים בשם המשתמש ובשם הריפוזיטורי שלך
GITHUB_USERNAME = "ibull8" # החלף בשם המשתמש שלך
GITHUB_REPO_NAME = "food-checklist-app" # החלף בשם הריפוזיטורי שלך

# --- הגדרות ראשוניות ---
st.set_page_config(page_title="הטיול הקולינרי שלנו", page_icon="🌮", layout="wide")
st.markdown("""<style> html, body, [class*="st-"], .main { direction: rtl; text-align: right; } </style>""", unsafe_allow_html=True)

def build_image_url(filename):
    return f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO_NAME}/main/images/{filename}"

@st.cache_data
def initialize_data():
    data = {
        'עיר': ['בודפשט'] * 7 + ['וינה'] * 7,
        'שם המאכל': [
            'גולאש (Gulyás)', 'לאנגוש (Lángos)', 'קיורטוש (Kürtőskalács)', 'עוגת דובוש (Dobos Torta)',
            'פפריקש עוף (Csirkepaprikás)', 'כרוב ממולא (Töltött Káposzta)', 'פלאצ\'ינטה (Palacsinta)',
            'שניצל וינאי (Wiener Schnitzel)', 'אפפלשטרודל (Apfelstrudel)', 'זאכרטורטה (Sachertorte)',
            'קייזרשמארן (Kaiserschmarrn)', 'טפלשפיץ (Tafelspitz)', 'נקניקיות (Würstel)', 'קנודל (Knödel)'
        ],
        # --- שלב 2: עדכון שמות קבצי התמונות ---
        # ודא שהשמות כאן תואמים בדיוק לשמות הקבצים שהעלית לתיקיית images
        'תמונה_קובץ': [
            'Gulyás.png', 'Lángos.png', 'Kürtőskalács.png', 'Dobos Torta.png', 'Csirkepaprikás.png',
            'Töltött Káposzta.png', 'Palacsinta.png', 'schnitzel.png', 'apfelstrudel.png',
            'sachertorte.png', 'kaiserschmarrn.png', 'tafelspitz.png', 'wurste.png', 'knodel.png'
        ],
        'המלצות': [
            'Gettó Gulyás, Menza', 'Retró Lángos Büfé', 'Molnár\'s Kürtőskalács', 'Gerbeaud Café', 'Paprika Jancsi',
            'Csarnok Vendéglő', 'Bank3 Palacsinta Bár', 'Figlmüller', 'Café Central', 'Hotel Sacher',
            'Café Central', 'Plachutta Wollzeile', 'Bitzinger Würstelstand', 'Gasthaus Pöschl'
        ],
    }
    df = pd.DataFrame(data)
    df['טעמנו'] = False
    df['דירוג אילן'] = 3
    df['דירוג מירה'] = 3
    df['איפה אכלנו'] = ""
    df['הערות'] = ""
    return df

if 'food_df' not in st.session_state:
    st.session_state.food_df = initialize_data()

st.title("🌮 הטיול הקולינרי שלנו")
st.markdown("### צ'קליסט טעימות לבודפשט ולווינה")

tab_budapest, tab_vienna = st.tabs(["בודפשט 🇭🇺", "וינה 🇦🇹"])

def create_food_checklist(city_name):
    city_df = st.session_state.food_df[st.session_state.food_df['עיר'] == city_name]
    for index, row in city_df.iterrows():
        unique_key = f"{city_name}_{index}"
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(build_image_url(row['תמונה_קובץ']), use_container_width=True)
        with col2:
            st.subheader(row['שם המאכל'])
            st.caption(f"המלצה: {row.get('המלצות', 'אין')}")
            st.session_state.food_df.loc[index, 'טעמנו'] = st.checkbox("טעמנו ✔", value=row['טעמנו'], key=f"tasted_{unique_key}")
            st.session_state.food_df.loc[index, 'דירוג אילן'] = st.slider("הדירוג של אילן:", 1, 5, value=row['דירוג אילן'], key=f"ilan_rating_{unique_key}")
            st.session_state.food_df.loc[index, 'דירוג מירה'] = st.slider("הדירוג של מירה:", 1, 5, value=row['דירוג מירה'], key=f"mira_rating_{unique_key}")
            st.session_state.food_df.loc[index, 'איפה אכלנו'] = st.text_input("איפה אכלנו?", value=row['איפה אכלנו'], key=f"where_{unique_key}")
            st.session_state.food_df.loc[index, 'הערות'] = st.text_area("הערות וטיפים", value=row['הערות'], key=f"notes_{unique_key}")
        st.markdown("---")

with tab_budapest:
    create_food_checklist('בודפשט')
with tab_vienna:
    create_food_checklist('וינה')

