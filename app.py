import streamlit as st
import pandas as pd

# הגדרות ראשוניות של העמוד
st.set_page_config(
    page_title="הטיול הקולינרי שלנו",
    page_icon="🌮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- הגדרת הנתונים ---
# יצירת DataFrame עם כל המידע על המאכלים
def load_data():
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
        'תמונה': [
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
    return pd.DataFrame(data)

df = load_data()

# --- ממשק המשתמש ---

st.title("🌮 הטיול הקולינרי שלנו")
st.markdown("### צ'קליסט טעימות אינטראקטיבי לבודפשט ולווינה")

# יצירת לשוניות (טאבים) לכל עיר
tab_budapest, tab_vienna = st.tabs(["בודפשט 🇭🇺", "וינה 🇦🇹"])

def create_food_checklist(city_df, city_name):
    """
    פונקציה ליצירת התצוגה של כל המאכלים בעיר מסוימת
    """
    # כותרות הטבלה
    col_header_1, col_header_2, col_header_3, col_header_4, col_header_5 = st.columns([2, 1, 1.5, 1.5, 2])
    with col_header_1:
        st.markdown("**המאכל**")
    with col_header_2:
        st.markdown("**טעמנו?**")
    with col_header_3:
        st.markdown("**הדירוג של אילן**")
    with col_header_4:
        st.markdown("**הדירוג של מירה**")
    with col_header_5:
        st.markdown("**פרטים נוספים**")
    st.markdown("---")


    # לולאה על כל המאכלים בעיר
    for index, row in city_df.iterrows():
        # יצירת מזהה ייחודי לכל מאכל כדי לשמור את המידע שלו
        unique_key = f"{city_name}_{index}"
        
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1.5, 1.5, 2])
        
        with col1:
            st.image(row['תמונה'], width=150)
            st.subheader(row['שם המאכל'])
            st.caption(f"המלצה: {row['המלצות']}")

        with col2:
            # צ'קבוקס
            tasted = st.checkbox("✔", key=f"tasted_{unique_key}")

        with col3:
            # דירוג כוכבים (סליידר)
            ilan_rating = st.slider("דרג:", 1, 5, 3, key=f"ilan_rating_{unique_key}", format="%d כוכבים")

        with col4:
            mira_rating = st.slider("דרגי:", 1, 5, 3, key=f"mira_rating_{unique_key}", format="%d כוכבים")
        
        with col5:
            # שדות טקסט להערות
            where_ate = st.text_input("איפה אכלנו?", key=f"where_{unique_key}")
            notes = st.text_area("הערות וטיפים", key=f"notes_{unique_key}")
            our_photo = st.text_input("קישור לתמונה שלנו", key=f"photo_{unique_key}")

        st.markdown("---")


# יצירת התוכן עבור הלשונית של בודפשט
with tab_budapest:
    st.header("מאכלי חובה בבודפשט")
    create_food_checklist(df[df['עיר'] == 'בודפשט'], 'budapest')

# יצירת התוכן עבור הלשונית של וינה
with tab_vienna:
    st.header("מאכלי חובה בוינה")
    create_food_checklist(df[df['עיר'] == 'וינה'], 'vienna')
