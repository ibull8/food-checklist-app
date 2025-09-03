import streamlit as st
import pandas as pd
import gspread
from gspread_pandas import Spread, Client
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

# --- שם ה-Google Sheet שלכם ---
# חשוב: זהו השם של קובץ ה-Google Sheet שיצרתם
SPREADSHEET_NAME = "צ'קליסט טיול קולינרי" 

# --- התחברות ל-Google Sheets (פעם אחת בלבד) ---
@st.cache_resource
def get_gspread_client():
    """ מתחבר ל-Google Sheets באמצעות ה-Secrets של Streamlit """
    try:
        # Streamlit ממיר את ה-Secret לפורמט הנכון
        creds_json = dict(st.secrets["google_credentials"])
        client = gspread.service_account_from_dict(creds_json)
        return client
    except Exception as e:
        st.error("חיבור ל-Google Sheets נכשל. ודא שהגדרת את ה-Secrets נכון ושיתפת את הגיליון עם המייל של הרובוט.")
        st.stop()

client = get_gspread_client()

# --- ניהול נתונים ---
def get_spreadsheet(client):
    if not client:
        return None
    try:
        return client.open(SPREADSHEET_NAME)
    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"הקובץ בשם '{SPREADSHEET_NAME}' לא נמצא. ודא שיצרת אותו ושיתפת אותו עם הרובוט.")
        st.stop()

spreadsheet = get_spreadsheet(client)

@st.cache_data(ttl=60) # קורא את הנתונים מחדש כל 60 שניות
def get_data_from_sheet(_spreadsheet):
    """ טוען את ה-DataFrame מהגיליון או יוצר אותו אם הוא ריק """
    try:
        worksheet = _spreadsheet.worksheet("Data")
        df = pd.DataFrame(worksheet.get_all_records())
        # אם הגיליון ריק, ניצור את הנתונים הראשוניים
        if df.empty:
            df = initialize_local_data()
            save_data_to_sheet(_spreadsheet, df)
        return df
    except gspread.exceptions.WorksheetNotFound:
        df = initialize_local_data()
        save_data_to_sheet(_spreadsheet, df)
        return df
    except Exception as e:
        st.error("שגיאה בטעינת הנתונים מהגיליון.")
        st.exception(e)
        return pd.DataFrame() # החזרת DataFrame ריק במקרה של שגיאה

def save_data_to_sheet(_spreadsheet, df):
    """ שומר את ה-DataFrame כולו בחזרה לגיליון """
    if not _spreadsheet:
        st.warning("לא ניתן לשמור שינויים - אין חיבור ל-Google Sheets.")
        return
    try:
        worksheet = _spreadsheet.worksheet("Data")
        worksheet.clear()
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    except Exception as e:
        st.error("שגיאה בשמירת הנתונים לגיליון.")

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
if spreadsheet and 'food_df' not in st.session_state:
    st.session_state.food_df = get_data_from_sheet(spreadsheet)

# --- ממשק המשתמש ---
st.title("🌮 הטיול הקולינרי שלנו")
st.markdown("### צ'קליסט טעימות מסונכרן לבודפשט ולווינה")

if spreadsheet:
    if st.button("רענן נתונים 🔄"):
        st.cache_data.clear()
        st.session_state.food_df = get_data_from_sheet(spreadsheet)
        st.toast("הנתונים סונכרנו בהצלחה מה-Google Sheet!")

    tab_budapest, tab_vienna = st.tabs(["בודפשט 🇭🇺", "וינה 🇦🇹"])

    def create_food_checklist(city_name):
        if 'food_df' not in st.session_state or st.session_state.food_df.empty:
            st.warning("טוען נתונים, אנא המתן...")
            return

        city_df = st.session_state.food_df[st.session_state.food_df['עיר'] == city_name]
        
        for index, row in city_df.iterrows():
            # מציאת האינדקס המקורי ב-DataFrame הראשי
            original_index = st.session_state.food_df[st.session_state.food_df['שם המאכל'] == row['שם המאכל']].index[0]
            unique_key = f"{city_name}_{original_index}"
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                image_to_show = row.get('תמונה שלנו (URL)', '') or row.get('תמונה_מקרא', '')
                if image_to_show:
                    st.image(image_to_show, use_container_width=True)

            with col2:
                st.subheader(row['שם המאכל'])
                st.caption(f"המלצה: {row.get('המלצות', 'אין')}")
                
                tasted = st.checkbox("טעמנו ✔", value=bool(row['טעמנו']), key=f"tasted_{unique_key}")
                if tasted != bool(row['טעמנו']):
                    st.session_state.food_df.loc[original_index, 'טעמנו'] = tasted
                    save_data_to_sheet(spreadsheet, st.session_state.food_df)

                ilan_rating = st.slider("הדירוג של אילן:", 1, 5, value=int(row['דירוג אילן']), key=f"ilan_rating_{unique_key}")
                if ilan_rating != int(row['דירוג אילן']):
                    st.session_state.food_df.loc[original_index, 'דירוג אילן'] = ilan_rating
                    save_data_to_sheet(spreadsheet, st.session_state.food_df)

                mira_rating = st.slider("הדירוג של מירה:", 1, 5, value=int(row['דירוג מירה']), key=f"mira_rating_{unique_key}")
                if mira_rating != int(row['דירוג מירה']):
                    st.session_state.food_df.loc[original_index, 'דירוג מירה'] = mira_rating
                    save_data_to_sheet(spreadsheet, st.session_state.food_df)
                
                where_eaten = st.text_input("איפה אכלנו?", value=str(row['איפה אכלנו']), key=f"where_{unique_key}")
                if where_eaten != str(row['איפה אכלנו']):
                    st.session_state.food_df.loc[original_index, 'איפה אכלנו'] = where_eaten
                    save_data_to_sheet(spreadsheet, st.session_state.food_df)

                notes = st.text_area("הערות וטיפים", value=str(row['הערות']), key=f"notes_{unique_key}")
                if notes != str(row['הערות']):
                    st.session_state.food_df.loc[original_index, 'הערות'] = notes
                    save_data_to_sheet(spreadsheet, st.session_state.food_df)
                
                photo_url = st.text_input("הדבק קישור לתמונה (URL)", value=str(row.get('תמונה שלנו (URL)', '')), key=f"photo_url_{unique_key}")
                if photo_url != str(row.get('תמונה שלנו (URL)', '')):
                    st.session_state.food_df.loc[original_index, 'תמונה שלנו (URL)'] = photo_url
                    save_data_to_sheet(spreadsheet, st.session_state.food_df)
                    st.rerun()

            st.markdown("---")

    with tab_budapest:
        st.header("מאכלי חובה בבודפשט")
        create_food_checklist('בודפשט')

    with tab_vienna:
        st.header("מאכלי חובה בוינה")
        create_food_checklist('וינה')
else:
    st.warning("האפליקציה לא הצליחה להתחבר ל-Google Sheets. אנא בדוק את ההגדרות והרענון.")

