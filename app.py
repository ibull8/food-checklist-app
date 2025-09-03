import streamlit as st
import pandas as pd
import gspread
import json
from PIL import Image
import io
import base64

# --- הגדרות ראשוניות של האפליקציה ---
st.set_page_config(page_title="הטיול הקולינרי שלנו", page_icon="🥐", layout="wide")

# --- עיצוב ו-CSS ---
st.markdown("""
<style>
    /* הגדרות בסיס ומשתני צבע */
    :root {
        --primary-color: #78350f; /* Amber 800 */
        --background-color: #ffffff;
        --secondary-background-color: #f9fafb; /* Gray 50 */
        --text-color: #1f2937; /* Gray 800 */
        --secondary-text-color: #4b5563; /* Gray 600 */
        --accent-color: #f59e0b; /* Amber 500 */
        --border-color: #e5e7eb; /* Gray 200 */
    }

    /* מצב כהה (Dark Mode) */
    @media (prefers-color-scheme: dark) {
        :root {
            --primary-color: #f59e0b; /* Amber 500 */
            --background-color: #1f2937; /* Gray 800 */
            --secondary-background-color: #374151; /* Gray 700 */
            --text-color: #f9fafb; /* Gray 50 */
            --secondary-text-color: #d1d5db; /* Gray 300 */
            --accent-color: #fbbf24; /* Amber 400 */
            --border-color: #4b5563; /* Gray 600 */
        }
    }

    /* עיצוב כללי */
    html, body, [class*="st-"], .main {
        direction: rtl;
        text-align: right;
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    /* כותרות */
    h1, h2, h3 { color: var(--primary-color); }
    
    /* כרטיסיית מאכל */
    .food-card {
        border: 1px solid var(--border-color);
        border-radius: 1rem;
        padding: 1.5rem;
        background-color: var(--secondary-background-color);
        transition: box-shadow 0.3s ease;
    }
    .food-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
    }

    /* עיגול דירוג */
    .rating-badge {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 50%;
        background-color: var(--primary-color);
        color: var(--background-color);
        font-weight: bold;
        font-size: 1.1rem;
        margin-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- שם ה-Google Sheet שלכם ---
SPREADSHEET_NAME = "צ'קליסט טיול קולינרי" 

# --- התחברות ל-Google Sheets ---
@st.cache_resource
def get_gspread_client():
    try:
        creds_json = dict(st.secrets["google_credentials"])
        client = gspread.service_account_from_dict(creds_json)
        return client
    except Exception:
        st.error("חיבור ל-Google Sheets נכשל. ודא שהגדרת את ה-Secrets נכון ושיתפת את הגיליון עם המייל של הרובוט.")
        st.stop()

client = get_gspread_client()

# --- פונקציות לניהול נתונים ---
def get_spreadsheet(client):
    try:
        return client.open(SPREADSHEET_NAME)
    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"הקובץ בשם '{SPREADSHEET_NAME}' לא נמצא. ודא שיצרת אותו ושיתפת אותו עם הרובוט.")
        st.stop()

spreadsheet = get_spreadsheet(client)

def ensure_columns(df):
    """ מוודא שכל העמודות הנדרשות קיימות ב-DataFrame """
    required_cols = {
        'תמונה_אישית_b64': ''
    }
    for col, default_value in required_cols.items():
        if col not in df.columns:
            df[col] = default_value
    return df

@st.cache_data(ttl=60)
def get_data_from_sheet(_spreadsheet):
    try:
        worksheet = _spreadsheet.worksheet("Data")
        df = pd.DataFrame(worksheet.get_all_records())
        if df.empty:
            df = initialize_local_data()
            save_data_to_sheet(_spreadsheet, df)
        df = ensure_columns(df)
        return df
    except gspread.exceptions.WorksheetNotFound:
        df = initialize_local_data()
        save_data_to_sheet(_spreadsheet, df)
        df = ensure_columns(df)
        return df
    except Exception as e:
        st.error(f"שגיאה בטעינת הנתונים: {e}")
        return pd.DataFrame()

def save_data_to_sheet(_spreadsheet, df):
    try:
        worksheet = _spreadsheet.worksheet("Data")
        worksheet.clear()
        # המרה ל-str כדי למנוע שגיאות gspread עם סוגי נתונים
        df_str = df.astype(str)
        worksheet.update([df_str.columns.values.tolist()] + df_str.values.tolist())
    except Exception as e:
        st.error(f"שגיאה בשמירת הנתונים: {e}")

def initialize_local_data():
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
        'הערות': [""] * 14, 'תמונה_אישית_b64': [""] * 14
    }
    return pd.DataFrame(data)

# טעינת הנתונים
if spreadsheet and 'food_df' not in st.session_state:
    st.session_state.food_df = get_data_from_sheet(spreadsheet)

# --- ממשק המשתמש הראשי ---
st.title("🥐 הטיול הקולינרי שלנו")
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
            original_index = st.session_state.food_df[st.session_state.food_df['שם המאכל'] == row['שם המאכל']].index[0]
            unique_key = f"{city_name}_{original_index}"
            
            with st.container():
                st.markdown('<div class="food-card">', unsafe_allow_html=True)
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # הצגת תמונה אישית אם קיימת, אחרת תמונת ברירת מחדל
                    personal_image_b64 = row.get('תמונה_אישית_b64', '')
                    if personal_image_b64 and isinstance(personal_image_b64, str) and len(personal_image_b64) > 10:
                        try:
                            img_bytes = base64.b64decode(personal_image_b64)
                            st.image(img_bytes, use_container_width=True)
                        except Exception:
                             st.image(row['תמונה_מקרא'], use_container_width=True)
                    else:
                        st.image(row['תמונה_מקרא'], use_container_width=True)

                    uploaded_file = st.file_uploader("📸 העלה תמונה אישית", type=['png', 'jpg', 'jpeg'], key=f"uploader_{unique_key}")
                    if uploaded_file is not None:
                        # המרת תמונה ל-Base64
                        img = Image.open(uploaded_file)
                        buffered = io.BytesIO()
                        img.save(buffered, format=img.format or "PNG")
                        img_b64 = base64.b64encode(buffered.getvalue()).decode()
                        
                        st.session_state.food_df.loc[original_index, 'תמונה_אישית_b64'] = img_b64
                        save_data_to_sheet(spreadsheet, st.session_state.food_df)
                        st.toast(f"התמונה עבור {row['שם המאכל']} נשמרה!")
                        st.rerun()

                with col2:
                    st.subheader(row['שם המאכל'])
                    st.caption(f"המלצה: {row.get('המלצות', 'אין')}")
                    
                    # --- תיקון לבעיית ה-NameError ---
                    # המרה בטוחה של 'TRUE'/'FALSE' לערך בוליאני
                    current_tasted_bool = str(row['טעמנו']).strip().upper() == 'TRUE'
                    tasted = st.checkbox("טעמנו ✔", value=current_tasted_bool, key=f"tasted_{unique_key}")
                    
                    if tasted != current_tasted_bool:
                        st.session_state.food_df.loc[original_index, 'טעמנו'] = tasted
                        save_data_to_sheet(spreadsheet, st.session_state.food_df)

                    # סליידר דירוג משודרג
                    slider_col, badge_col = st.columns([4, 1])
                    with slider_col:
                        ilan_rating = st.slider("הדירוג של אילן:", 1, 5, value=int(row['דירוג אילן']), key=f"ilan_rating_{unique_key}")
                    with badge_col:
                        st.markdown(f'<div class="rating-badge">{ilan_rating}</div>', unsafe_allow_html=True)
                    if ilan_rating != int(row['דירוג אילן']):
                        st.session_state.food_df.loc[original_index, 'דירוג אילן'] = ilan_rating
                        save_data_to_sheet(spreadsheet, st.session_state.food_df)
                    
                    slider_col2, badge_col2 = st.columns([4, 1])
                    with slider_col2:
                         mira_rating = st.slider("הדירוג של מירה:", 1, 5, value=int(row['דירוג מירה']), key=f"mira_rating_{unique_key}")
                    with badge_col2:
                         st.markdown(f'<div class="rating-badge">{mira_rating}</div>', unsafe_allow_html=True)
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
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("---") # קו מפריד בין מאכלים

    with tab_budapest:
        create_food_checklist('בודפשט')

    with tab_vienna:
        create_food_checklist('וינה')
else:
    st.warning("האפליקציה לא הצליחה להתחבר ל-Google Sheets. אנא בדוק את ההגדרות והרענון.")

