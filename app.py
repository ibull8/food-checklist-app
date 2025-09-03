import streamlit as st
import pandas as pd
import gspread
from PIL import Image
import io
import base64
import time
import json

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

# --- קבועים והגדרות ---
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

def ensure_columns_and_types(df):
    required_cols = {'תמונה_אישית_b64': ''}
    for col, default_value in required_cols.items():
        if col not in df.columns:
            df[col] = default_value
            
    # המרה חכמה של סוגי הנתונים אחרי טעינה
    df['טעמנו'] = df['טעמנו'].astype(str).str.strip().str.upper() == 'TRUE'
    df['דירוג אילן'] = pd.to_numeric(df['דירוג אילן'], errors='coerce').fillna(3).astype(int)
    df['דירוג מירה'] = pd.to_numeric(df['דירוג מירה'], errors='coerce').fillna(3).astype(int)
    
    # המרת עמודת ההמלצות מטקסט JSON לרשימה
    if 'המלצות' in df.columns:
        df['המלצות'] = df['המלצות'].apply(lambda x: json.loads(x) if isinstance(x, str) and x.startswith('[') else [])

    return df

# הפונקציה הזו רצה עכשיו בלי זיכרון מטמון
def get_data_from_sheet(_spreadsheet):
    try:
        worksheet = _spreadsheet.worksheet("Data")
        df = pd.DataFrame(worksheet.get_all_records())
        if df.empty:
            df = initialize_local_data()
            save_data_to_sheet(_spreadsheet, df)
        
        df = ensure_columns_and_types(df)
        return df
    except gspread.exceptions.WorksheetNotFound:
        df = initialize_local_data()
        save_data_to_sheet(_spreadsheet, df)
        df = ensure_columns_and_types(df) # ודא המרה גם כאן
        return df
    except Exception as e:
        st.error(f"שגיאה בטעינת הנתונים: {e}")
        return pd.DataFrame()

def save_data_to_sheet(_spreadsheet, df):
    try:
        worksheet = _spreadsheet.worksheet("Data")
        worksheet.clear()
        df_to_save = df.copy()
        # המרת עמודות לפורמט טקסט לפני שמירה
        df_to_save['טעמנו'] = df_to_save['טעמנו'].astype(str)
        df_to_save['המלצות'] = df_to_save['המלצות'].apply(lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) else x)
        worksheet.update([df_to_save.columns.values.tolist()] + df_to_save.values.tolist())
        return True
    except Exception as e:
        st.error(f"שגיאה בשמירת הנתונים: {e}")
        return False

def initialize_local_data():
    # ... (כל תוכן הפונקציה נשאר זהה) ...
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
            json.dumps([{'name': 'Gettó Gulyás', 'url': 'https://maps.app.goo.gl/P8fGq4S6oWp98Zz5A'}, {'name': 'Menza', 'url': 'https://maps.app.goo.gl/uXvY6hF3t9z19k8y6'}]),
            json.dumps([{'name': 'Retró Lángos Büfé', 'url': 'https://maps.app.goo.gl/3A74a7Kj5t9qN5qH8'}]),
            json.dumps([{'name': "Molnár's Kürtőskalács", 'url': 'https://maps.app.goo.gl/qL8h4T6P1tB1r8J67'}]),
            json.dumps([{'name': 'Gerbeaud Café', 'url': 'https://maps.app.goo.gl/s1Z6o3B6E5eX9kS28'}]),
            json.dumps([{'name': 'Paprika Jancsi', 'url': 'https://maps.app.goo.gl/e7xU4K7F8D9q8q8z8'}]),
            json.dumps([{'name': 'Csarnok Vendéglő', 'url': 'https://maps.app.goo.gl/X9y1M5z6N2Y9q9P47'}]),
            json.dumps([{'name': 'Bank3 Palacsinta Bár', 'url': 'https://maps.app.goo.gl/v5e9V3xG3z9W5kXw6'}]),
            json.dumps([{'name': 'Figlmüller', 'url': 'https://maps.app.goo.gl/FkG4R5z7w8q2X3P16'}]),
            json.dumps([{'name': 'Café Central', 'url': 'https://maps.app.goo.gl/vM6h4t5y7t8X9kYw6'}]),
            json.dumps([{'name': 'Hotel Sacher', 'url': 'https://maps.app.goo.gl/A9r4Y7t8z6X9kYw5'}]),
            json.dumps([{'name': 'Café Central', 'url': 'https://maps.app.goo.gl/vM6h4t5y7t8X9kYw6'}]),
            json.dumps([{'name': 'Plachutta Wollzeile', 'url': 'https://maps.app.goo.gl/z6h5R5z7w8q2X3P16'}]),
            json.dumps([{'name': 'Bitzinger Würstelstand', 'url': 'https://maps.app.goo.gl/b9Y6R5z7w8q2X3P16'}]),
            json.dumps([{'name': 'Gasthaus Pöschl', 'url': 'https://maps.app.goo.gl/n8X4R5z7w8q2X3P16'}])
        ],
        'טעמנו': [False] * 14, 'דירוג אילן': [3] * 14, 'דירוג מירה': [3] * 14, 'איפה אכלנו': [""] * 14,
        'הערות': [""] * 14, 'תמונה_אישית_b64': [""] * 14
    }
    df = pd.DataFrame(data)
    return df

# --- ניהול מצב (Session State) ---
# קוראים את הנתונים פעם אחת בתחילת הריצה
if 'food_df' not in st.session_state:
    st.session_state.food_df = get_data_from_sheet(spreadsheet)

# --- ממשק המשתמש הראשי ---
st.title("🥐 הטיול הקולינרי שלנו")
st.markdown("### צ'קליסט טעימות מסונכרן לבודפשט ולווינה")

# יוצרים עותק לעבודה כדי לזהות שינויים
df_modified = st.session_state.food_df.copy()

tab_budapest, tab_vienna = st.tabs(["בודפשט 🇭🇺", "וינה 🇦🇹"])

def create_food_checklist(city_name, dataframe):
    city_df = dataframe[dataframe['עיר'] == city_name]
    
    for index, row in city_df.iterrows():
        unique_key = f"{city_name}_{index}"
        
        with st.container():
            st.markdown('<div class="food-card">', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 2])
            
            with col1:
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
                    img = Image.open(uploaded_file)
                    img.thumbnail((600, 600)) 
                    buffered = io.BytesIO()
                    img_format = img.format if img.format in ['JPEG', 'PNG'] else 'PNG'
                    img.save(buffered, format=img_format)
                    img_b64 = base64.b64encode(buffered.getvalue()).decode()
                    dataframe.loc[index, 'תמונה_אישית_b64'] = img_b64

            with col2:
                st.subheader(row['שם המאכל'])
                
                recommendations = row.get('המלצות', [])
                if recommendations and isinstance(recommendations, list):
                    rec_md = "📍 **המלצות:** "
                    links = [f"[{rec['name']}]({rec['url']})" for rec in recommendations if isinstance(rec, dict)]
                    if links:
                        rec_md += ", ".join(links)
                        st.markdown(rec_md, unsafe_allow_html=True)

                dataframe.loc[index, 'טעמנו'] = st.checkbox("טעמנו ✔", value=bool(row['טעמנו']), key=f"tasted_{unique_key}")
                
                slider_col, badge_col = st.columns([4, 1])
                with slider_col:
                    dataframe.loc[index, 'דירוג אילן'] = st.slider("הדירוג של אילן:", 1, 5, value=int(row['דירוג אילן']), key=f"ilan_rating_{unique_key}")
                with badge_col:
                    st.markdown(f'<div class="rating-badge">{dataframe.loc[index, "דירוג אילן"]}</div>', unsafe_allow_html=True)
                
                slider_col2, badge_col2 = st.columns([4, 1])
                with slider_col2:
                    dataframe.loc[index, 'דירוג מירה'] = st.slider("הדירוג של מירה:", 1, 5, value=int(row['דירוג מירה']), key=f"mira_rating_{unique_key}")
                with badge_col2:
                    st.markdown(f'<div class="rating-badge">{dataframe.loc[index, "דירוג מירה"]}</div>', unsafe_allow_html=True)
                
                dataframe.loc[index, 'איפה אכלנו'] = st.text_input("איפה אכלנו?", value=str(row['איפה אכלנו']), key=f"where_{unique_key}")
                dataframe.loc[index, 'הערות'] = st.text_area("הערות וטיפים", value=str(row['הערות']), key=f"notes_{unique_key}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")

with tab_budapest:
    create_food_checklist('בודפשט', df_modified)

with tab_vienna:
    create_food_checklist('וינה', df_modified)

# --- לוגיקת סנכרון פשוטה וישירה ---
if not st.session_state.food_df.equals(df_modified):
    st.session_state.food_df = df_modified.copy()
    with st.spinner("☁️ שומר שינויים..."):
        if save_data_to_sheet(spreadsheet, st.session_state.food_df):
            st.success("✅ השינויים נשמרו!")
            time.sleep(1)
            st.rerun()
        else:
            st.error("שגיאה בשמירה.")

