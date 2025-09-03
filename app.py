import streamlit as st
import pandas as pd
from io import BytesIO

# הגדרות ראשוניות של העמוד
st.set_page_config(
    page_title="הטיול הקולינרי שלנו",
    page_icon="🌮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- יישור לימין (RTL) ---
st.markdown("""
<style>
    html, body, [class*="st-"], .main {
        direction: rtl;
        text-align: right;
    }
    /* התאמות קטנות למראה הצ'קבוקס והסליידרים ב-RTL */
    div[data-testid="stCheckbox"] {
        margin-left: 0;
        margin-right: -1rem;
    }
    div[data-testid="stSlider"] > label {
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# --- ניהול נתונים ושמירת מצב (Session State) ---

def initialize_data():
    """
    יוצר את רשימת המאכלים הראשונית ומכין אותה לשמירה במצב הסשן.
    הפונקציה רצה פעם אחת בלבד בתחילת השימוש באפליקציה.
    """
    data = {
        'עיר': ['בודפשט'] * 7 + ['וינה'] * 7,
        'שם המאכל': [
            'גולאש (Gulyás)', 'לאנגוש (Lángos)', 'קיורטוש (Kürtőskalács)', 
            'עוגת דובוש (Dobos Torta)', 'פפריקש עוף (Csirkepaprikás)', 'כרוב ממולא (Töltött Káposzta)', 
            'פלאצ\'ינטה (Palacsinta)',
            'שניצל וינאי (Wiener Schnitzel)', 'אפפלשטרודל (Apfelstrudel)', 'זאכרטורטה (Sachertorte)',
            'קייזרשמארן (Kaiserschmarrn)', 'טפלשפיץ (Tafelspitz)', 'נקניקיות (Würstel)', 
            'קנודל (Knödel)'
        ],
        'תמונה_מקרא': [ # שיניתי את שם העמודה כדי למנוע בלבול
            'https://images.pexels.com/photos/10774535/pexels-photo-10774535.jpeg?auto=compress&cs=tinysrgb&w=800',
            'https://images.pexels.com/photos/18943026/pexels-photo-18943026/free-photo-of-a-traditional-hungarian-street-food-dish-called-langos.jpeg?auto=compress&cs=tinysrgb&w=800',
            'https://images.pexels.com/photos/887853/pexels-photo-887853.jpeg?auto=compress&cs=tinysrgb&w=800',
            'https://images.pexels.com/photos/205961/pexels-photo-205961.jpeg?auto=compress&cs=tinysrgb&w=800',
            'https://images.pexels.com/photos/6210876/pexels-photo-6210876.jpeg?auto=compress&cs=tinysrgb&w=800',
            'https://images.pexels.com/photos/5419233/pexels-photo-5419233.jpeg?auto=compress&cs=tinysrgb&w=800',
            'https://images.pexels.com/photos/14497685/pexels-photo-14497685.jpeg?auto=compress&cs=tinysrgb&w=800',
            'https://images.pexels.com/photos/106343/pexels-photo-106343.jpeg?auto=compress&cs=tinysrgb&w=800',
            'https://images.pexels.com/photos/2205270/pexels-photo-2205270.jpeg?auto=compress&cs=tinysrgb&w=800',
            'https://images.pexels.com/photos/4109998/pexels-photo-4109998.jpeg?auto=compress&cs=tinysrgb&w=800',
            'https://images.pexels.com/photos/13107436/pexels-photo-13107436.jpeg?auto=compress&cs=tinysrgb&w=800',
            'https://images.pexels.com/photos/1251208/pexels-photo-1251208.jpeg?auto=compress&cs=tinysrgb&w=800',
            'https://images.pexels.com/photos/806357/pexels-photo-806357.jpeg?auto=compress&cs=tinysrgb&w=800',
            'https://images.pexels.com/photos/13262933/pexels-photo-13262933.jpeg?auto=compress&cs=tinysrgb&w=800'
        ],
        'המלצות': [
            'Gettó Gulyás, Menza', 'Retró Lángos Büfé', 'Molnár\'s Kürtőskalács',
            'Gerbeaud Café, Ruszwurm Cukrászda', 'Paprika Jancsi Restaurant', 'Csarnok Vendéglő',
            'Bank3 Palacsinta Bár',
            'Figlmüller, Schnitzelwirt', 'Café Central, Café Landtmann', 'Hotel Sacher, Demel',
            'Café Central, Heuriger 10er Marie', 'Plachutta Wollzeile', 'Bitzinger Würstelstand',
            'Gasthaus Pöschl'
        ]
    }
    df = pd.DataFrame(data)
    # הוספת עמודות לשמירת המצב של כל רכיב אינטראקטיבי
    df['טעמנו'] = False
    df['דירוג אילן'] = 3
    df['דירוג מירה'] = 3
    df['איפה אכלנו'] = ""
    df['הערות'] = ""
    df['תמונה שלנו (URL)'] = "" # עמודה ייעודית לקישור
    df['תמונה שהועלתה'] = [None] * len(df) # עמודה לשמירת התמונות שהמשתמש מעלה
    return df

# טעינת הנתונים לתוך ה-session state אם הם לא קיימים שם
if 'food_df' not in st.session_state:
    st.session_state.food_df = initialize_data()

# --- ממשק המשתמש ---

st.title("🌮 הטיול הקולינרי שלנו")
st.markdown("### צ'קליסט טעימות אינטראקטיבי לבודפשט ולווינה")

tab_budapest, tab_vienna = st.tabs(["בודפשט 🇭🇺", "וינה 🇦🇹"])

def create_food_checklist(city_name):
    """
    פונקציה ליצירת התצוגה של כל המאכלים והרכיבים האינטראקטיביים.
    """
    # סינון ה-DataFrame לפי העיר הנבחרת
    city_df = st.session_state.food_df[st.session_state.food_df['עיר'] == city_name]
    
    for index, row in city_df.iterrows():
        unique_key = f"{city_name}_{index}"
        
        col1, col2 = st.columns([1, 2])
        
        with col1: # עמודת התמונה
            # לוגיקת בחירת התמונה להצגה: קישור > תמונה שהועלתה > תמונת ברירת מחדל
            image_to_show = row['תמונה_מקרא'] # ברירת מחדל
            if row['תמונה שהועלתה'] is not None:
                image_to_show = row['תמונה שהועלתה']
            if row['תמונה שלנו (URL)']:
                image_to_show = row['תמונה שלנו (URL)']
            
            st.image(image_to_show, use_container_width=True)
            
            uploaded_file = st.file_uploader("החלף תמונה מקובץ", type=['png', 'jpg', 'jpeg'], key=f"uploader_{unique_key}")
            if uploaded_file:
                # קריאת התמונה שהועלתה ושמירתה במצב הסשן
                st.session_state.food_df.at[index, 'תמונה שהועלתה'] = uploaded_file.getvalue()
                # אם מעלים קובץ, נקה את הקישור כדי למנוע בלבול
                st.session_state.food_df.at[index, 'תמונה שלנו (URL)'] = ""
                st.rerun()

        with col2: # עמודת המידע והאינטראקציה
            st.subheader(row['שם המאכל'])
            st.caption(f"המלצה: {row['המלצות']}")
            
            st.session_state.food_df.at[index, 'טעמנו'] = st.checkbox("טעמנו ✔", value=row['טעמנו'], key=f"tasted_{unique_key}")
            
            st.session_state.food_df.at[index, 'דירוג אילן'] = st.slider("הדירוג של אילן:", 1, 5, value=row['דירוג אילן'], key=f"ilan_rating_{unique_key}", format="%d כוכבים")
            st.session_state.food_df.at[index, 'דירוג מירה'] = st.slider("הדירוג של מירה:", 1, 5, value=row['דירוג מירה'], key=f"mira_rating_{unique_key}", format="%d כוכבים")
            
            st.session_state.food_df.at[index, 'איפה אכלנו'] = st.text_input("איפה אכלנו?", value=row['איפה אכלנו'], key=f"where_{unique_key}")
            st.session_state.food_df.at[index, 'הערות'] = st.text_area("הערות וטיפים", value=row['הערות'], key=f"notes_{unique_key}")
            
            # שדה ייעודי להדבקת קישור לתמונה
            url_input = st.text_input("הדבק קישור לתמונה (URL)", value=row['תמונה שלנו (URL)'], key=f"photo_url_{unique_key}")
            if url_input != row['תמונה שלנו (URL)']:
                st.session_state.food_df.at[index, 'תמונה שלנו (URL)'] = url_input
                # אם מדביקים קישור, נקה את התמונה שהועלתה
                st.session_state.food_df.at[index, 'תמונה שהועלתה'] = None
                st.rerun()

        st.markdown("---")
        
    # טופס להוספת מאכל חדש
    with st.expander("הוסף מאכל חדש 🥐"):
        with st.form(key=f"add_food_form_{city_name}", clear_on_submit=True):
            new_name = st.text_input("שם המאכל")
            new_recommendations = st.text_input("המלצות")
            new_url = st.text_input("הדבק קישור לתמונה (URL)")
            new_image_file = st.file_uploader("או העלה תמונה למאכל החדש", type=['png', 'jpg', 'jpeg'])
            
            submitted = st.form_submit_button("הוסף לרשימה")
            if submitted and new_name:
                image_bytes = new_image_file.getvalue() if new_image_file else None
                
                new_row = pd.DataFrame([{
                    'עיר': city_name,
                    'שם המאכל': new_name,
                    'תמונה_מקרא': 'https://placehold.co/800x800/EEE/31343C?text=My+Photo', # תמונה זמנית
                    'המלצות': new_recommendations,
                    'טעמנו': False, 'דירוג אילן': 3, 'דירוג מירה': 3, 'איפה אכלנו': "", 'הערות': "", 
                    'תמונה שלנו (URL)': new_url,
                    'תמונה שהועלתה': image_bytes
                }])
                
                st.session_state.food_df = pd.concat([st.session_state.food_df, new_row], ignore_index=True)
                st.success(f"'{new_name}' נוסף בהצלחה לרשימה!")
                st.rerun()

with tab_budapest:
    st.header("מאכלי חובה בבודפשט")
    create_food_checklist('בודפשט')

with tab_vienna:
    st.header("מאכלי חובה בוינה")
    create_food_checklist('וינה')

