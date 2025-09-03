import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import json

# --- הגדרות ראשוניות של האפליקציה ---
st.set_page_config(page_title="הטיול הקולינרי שלנו", page_icon="🌮", layout="wide")

# --- יישור לימין (RTL) ---
st.markdown("""
<style>
    html, body, [class*="st-"], .main { direction: rtl; text-align: right; }
    div[data-testid="stCheckbox"] { margin-left: 0; margin-right: -1rem; }
    div[data-testid="stSlider"] > label { text-align: right; }
</style>
""", unsafe_allow_html=True)

# --- התחברות ל-Firebase (פעם אחת בלבד) ---
def init_firestore():
    """ מתחבר ל-Firestore באמצעות ה-Secrets של Streamlit ופענוח Base64 """
    try:
        if not firebase_admin._apps:
            creds_dict = dict(st.secrets["firebase_credentials"])
            
            # --- התיקון עם Base64 ---
            # פענוח המפתח הפרטי מהקידוד
            private_key_b64 = creds_dict.pop("private_key_b64")
            decoded_key = base64.b64decode(private_key_b64).decode("utf-8")
            creds_dict["private_key"] = decoded_key
            
            creds = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(creds)
        return firestore.client()
    except Exception as e:
        st.error("חיבור ל-Firebase נכשל. ודא שהגדרת את ה-Secrets נכון ב-Streamlit Cloud.")
        st.exception(e)
        return None

db = init_firestore()
DOC_PATH = "checklist/budapest_vienna_trip"

# --- ניהול נתונים ---
@st.cache_data(ttl=60)
def get_data_from_firestore():
    """ טוען את ה-DataFrame מ-Firestore או יוצר אותו אם הוא לא קיים """
    if db is None:
        return initialize_local_data()

    doc_ref = db.collection("trips").document(DOC_PATH)
    try:
        doc = doc_ref.get()
        if doc.exists:
            data_dict = doc.to_dict()['data']
            return pd.DataFrame.from_records(data_dict)
        else:
            df = initialize_local_data()
            save_data_to_firestore(df)
            return df
    except Exception as e:
        st.error("שגיאה בטעינת הנתונים מ-Firestore.")
        st.exception(e)
        return initialize_local_data()

def save_data_to_firestore(df):
    """ שומר את ה-DataFrame כולו בחזרה ל-Firestore """
    if db is None:
        st.warning("לא ניתן לשמור שינויים - אין חיבור ל-Firebase.")
        return
    
    data_dict = {'data': df.to_dict('records')}
    db.collection("trips").document(DOC_PATH).set(data_dict)

def initialize_local_data():
    """ יוצר את ה-DataFrame הראשוני עם נתוני ברירת המחדל """
    data = {
        'עיר': ['בודפשט'] * 7 + ['וינה'] * 7,
        'שם המאכל': [
            'גולאש (Gulyás)', 'לאנגוש (Lángos)', 'קיורטוש (Kürtőskalács)', 'עוגת דובוש (Dobos Torta)',
            'פפריקש עוף (Csirkepaprikás)', 'כרוב ממולא (Töltött Káposzta)', 'פלאצ\'ינטה (Palacsinta)',
            'שניצל וינאי (Wiener Schnitzel)', 'אפפלשטרודל (Apfelstrudel)', 'זאכרטורטה (Sachertorte)',
            'קייזרשמארן (Kaiserschmarrn)', 'טפלשפיץ (Tafelspitz)', 'נקניקיות (Würstel)', 'קנודל (Knödel)'
        ],
        'תמונה_מקרא': [
            'https://images.pexels.com/photos/10774535/pexels-photo-10774535.jpeg?auto=compress&cs=tinysrgb&w=800', 'https://images.pexels.com/photos/18943026/pexels-photo-18943026/free-photo-of-a-traditional-hungarian-street-food-dish-called-langos.jpeg?auto=compress&cs=tinysrgb&w=800',
            'https://images.pexels.com/photos/887853/pexels-photo-887853.jpeg?auto=compress&cs=tinysrgb&w=800', 'https://images.pexels.com/photos/205961/pexels-photo-205961.jpeg?auto=compress&cs=tinysrgb&w=800',
            'https://images.pexels.com/photos/6210876/pexels-photo-6210876.jpeg?auto=compress&cs=tinysrgb&w=800', 'https://images.pexels.com/photos/5419233/pexels-photo-5419233.jpeg?auto=compress&cs=tinysrgb&w=800',
            'https://images.pexels.com/photos/14497685/pexels-photo-14497685.jpeg?auto=compress&cs=tinysrgb&w=800', 'https://images.pexels.com/photos/106343/pexels-photo-106343.jpeg?auto=compress&cs=tinysrgb&w=800',
            'https://images.pexels.com/photos/2205270/pexels-photo-2205270.jpeg?auto=compress&cs=tinysrgb&w=800', 'https://images.pexels.com/photos/4109998/pexels-photo-4109998.jpeg?auto=compress&cs=tinysrgb&w=800',
            'https://images.pexels.com/photos/13107436/pexels-photo-13107436.jpeg?auto=compress&cs=tinysrgb&w=800', 'https://images.pexels.com/photos/1251208/pexels-photo-1251208.jpeg?auto=compress&cs=tinysrgb&w=800',
            'https://images.pexels.com/photos/806357/pexels-photo-806357.jpeg?auto=compress&cs=tinysrgb&w=800', 'https://images.pexels.com/photos/13262933/pexels-photo-13262933.jpeg?auto=compress&cs=tinysrgb&w=800'
        ],
        'המלצות': [
            'Gettó Gulyás, Menza', 'Retró Lángos Büfé', 'Molnár\'s Kürtőskalács', 'Gerbeaud Café', 'Paprika Jancsi',
            'Csarnok Vendéglő', 'Bank3 Palacsinta Bár', 'Figlmüller', 'Café Central', 'Hotel Sacher',
            'Café Central', 'Plachutta Wollzeile', 'Bitzinger Würstelstand', 'Gasthaus Pöschl'
        ],
        'טעמנו': [False] * 14, 'דירוג אילן': [3] * 14, 'דירוג מירה': [3] * 14, 'איפה אכלנו': [""] * 14,
        'הערות': [""] * 14, 'תמונה שלנו (URL)': [""] * 14
    }
    return pd.DataFrame(data)

# טעינת הנתונים בפעם הראשונה
if 'food_df' not in st.session_state:
    st.session_state.food_df = get_data_from_firestore()

# --- ממשק המשתמש ---
st.title("🌮 הטיול הקולינרי שלנו")
st.markdown("### צ'קליסט טעימות מסונכרן לבודפשט ולווינה")

if db:
    if st.button("רענן נתונים 🔄"):
        st.cache_data.clear()
        st.session_state.food_df = get_data_from_firestore()
        st.toast("הנתונים סונכרנו בהצלחה!")

tab_budapest, tab_vienna = st.tabs(["בודפשט 🇭🇺", "וינה 🇦🇹"])

def create_food_checklist(city_name):
    # ודא שהנתונים קיימים ב-session_state
    if 'food_df' not in st.session_state:
        st.warning("טוען נתונים, אנא המתן...")
        return

    city_df = st.session_state.food_df[st.session_state.food_df['עיר'] == city_name]
    
    for index, row in city_df.iterrows():
        unique_key = f"{city_name}_{index}"
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            image_to_show = row.get('תמונה שלנו (URL)', '') or row.get('תמונה_מקרא', '')
            if image_to_show:
                st.image(image_to_show, width='stretch')

        with col2:
            st.subheader(row['שם המאכל'])
            st.caption(f"המלצה: {row.get('המלצות', 'אין')}")
            
            tasted = st.checkbox("טעמנו ✔", value=row['טעמנו'], key=f"tasted_{unique_key}")
            if tasted != row['טעמנו']:
                st.session_state.food_df.loc[index, 'טעמנו'] = tasted
                save_data_to_firestore(st.session_state.food_df)

            ilan_rating = st.slider("הדירוג של אילן:", 1, 5, value=row['דירוג אילן'], key=f"ilan_rating_{unique_key}")
            if ilan_rating != row['דירוג אילן']:
                st.session_state.food_df.loc[index, 'דירוג אילן'] = ilan_rating
                save_data_to_firestore(st.session_state.food_df)

            mira_rating = st.slider("הדירוג של מירה:", 1, 5, value=row['דירוג מירה'], key=f"mira_rating_{unique_key}")
            if mira_rating != row['דירוג מירה']:
                st.session_state.food_df.loc[index, 'דירוג מירה'] = mira_rating
                save_data_to_firestore(st.session_state.food_df)
            
            where_eaten = st.text_input("איפה אכלנו?", value=row['איפה אכלנו'], key=f"where_{unique_key}")
            if where_eaten != row['איפה אכלנו']:
                st.session_state.food_df.loc[index, 'איפה אכלנו'] = where_eaten
                save_data_to_firestore(st.session_state.food_df)

            notes = st.text_area("הערות וטיפים", value=row['הערות'], key=f"notes_{unique_key}")
            if notes != row['הערות']:
                st.session_state.food_df.loc[index, 'הערות'] = notes
                save_data_to_firestore(st.session_state.food_df)
            
            photo_url = st.text_input("הדבק קישור לתמונה (URL)", value=row.get('תמונה שלנו (URL)', ''), key=f"photo_url_{unique_key}")
            if photo_url != row.get('תמונה שלנו (URL)', ''):
                st.session_state.food_df.loc[index, 'תמונה שלנו (URL)'] = photo_url
                save_data_to_firestore(st.session_state.food_df)
                st.rerun()

        st.markdown("---")

with tab_budapest:
    st.header("מאכלי חובה בבודפשט")
    create_food_checklist('בודפשט')

with tab_vienna:
    st.header("מאכלי חובה בוינה")
    create_food_checklist('וינה')

