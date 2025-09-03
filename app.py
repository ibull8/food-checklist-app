<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>המסע הקולינרי המשותף: בודפשט ווינה</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Assistant:wght@400;600;700&display=swap" rel="stylesheet">
    <!-- Chosen Palette: Warm Earth Tones -->
    <!-- Application Structure Plan: The SPA is now a collaborative "Culinary Passport" using Firebase Firestore for real-time data synchronization. The structure remains a user-friendly single page with a dashboard and interactive cards. A shared list ID is displayed to ensure users are collaborating on the same document. This architecture elevates the app from a personal checklist to a shared, interactive experience, directly addressing the user's request for collaboration with "Mira". -->
    <!-- Visualization & Content Choices: Report Info: List of dishes for Budapest & Vienna. Goal: Collaboratively track tasted dishes. Viz/Presentation Method: 1) Donut charts (Chart.js) dynamically updated from Firestore data. 2) Interactive cards with real images. Justification: Real images significantly improve usability and appeal. Interaction: 1) City filters (JS). 2) Checkboxes now trigger Firestore updates (`updateDoc`), and the UI is updated in real-time for all users via an `onSnapshot` listener. This provides a seamless collaborative experience. Library/Method: Vanilla JS, Chart.js, Tailwind CSS, and Firebase SDK. -->
    <!-- CONFIRMATION: NO SVG graphics used. NO Mermaid JS used. -->
    <style>
        body {
            font-family: 'Assistant', sans-serif;
        }
        .chart-container {
            position: relative;
            width: 100%;
            max-width: 250px;
            margin-left: auto;
            margin-right: auto;
            height: 250px;
            max-height: 250px;
        }
        .food-card {
            transition: all 0.3s ease-in-out;
        }
        .food-card.tasted {
            opacity: 0.6;
            transform: scale(0.98);
        }
        .food-card.tasted .overlay {
            opacity: 1;
        }
        .overlay {
            transition: opacity 0.3s ease-in-out;
        }
        #loader {
            border: 8px solid #f3f3f3;
            border-top: 8px solid #a16207;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            animation: spin 1s linear infinite;
            position: absolute;
            top: 50%;
            left: 50%;
            margin-left: -30px;
            margin-top: -30px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body class="bg-stone-50 text-slate-800">

    <div id="loader"></div>

    <div id="app-content" class="container mx-auto p-4 md:p-8 max-w-7xl hidden">
        
        <header class="text-center mb-8">
            <h1 class="text-4xl md:text-5xl font-bold text-amber-800">המסע הקולינרי המשותף</h1>
            <p class="text-lg text-slate-600 mt-2">רשימת מאכלים שחובה לטעום בבודפשט ובווינה</p>
            <div class="mt-4 text-sm text-slate-500 bg-stone-100 inline-block px-3 py-1 rounded-full">
                מזהה רשימה משותפת: <span id="list-id" class="font-mono"></span>
            </div>
        </header>

        <nav class="flex justify-center gap-2 md:gap-4 mb-8">
            <button id="filter-all" class="filter-btn bg-amber-600 text-white py-2 px-5 rounded-full shadow-md hover:bg-amber-700 transition-colors">הכל</button>
            <button id="filter-budapest" class="filter-btn bg-white text-amber-800 py-2 px-5 rounded-full shadow-md hover:bg-stone-100 transition-colors">בודפשט 🇭🇺</button>
            <button id="filter-vienna" class="filter-btn bg-white text-amber-800 py-2 px-5 rounded-full shadow-md hover:bg-stone-100 transition-colors">וינה 🇦🇹</button>
        </nav>

        <section id="dashboard" class="mb-10 p-6 bg-white rounded-2xl shadow-sm">
             <h2 class="text-2xl font-bold text-center text-amber-800 mb-6">ההתקדמות שלנו</h2>
             <p class="text-center text-slate-600 mb-6 max-w-2xl mx-auto">כאן תוכלו לראות סיכום ויזואלי של החוויה הקולינרית שלכם. כל סימון מתעדכן בזמן אמת עבור כל המשתמשים ברשימה זו.</p>
            <div class="flex flex-col md:flex-row justify-center items-center gap-8">
                <div class="text-center">
                    <h3 class="text-xl font-semibold mb-2">בודפשט</h3>
                    <div class="chart-container">
                        <canvas id="budapestChart"></canvas>
                    </div>
                </div>
                <div class="text-center">
                    <h3 class="text-xl font-semibold mb-2">וינה</h3>
                    <div class="chart-container">
                        <canvas id="viennaChart"></canvas>
                    </div>
                </div>
            </div>
        </section>

        <main id="food-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
        </main>

    </div>

    <script type="module">
        import { initializeApp } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-app.js";
        import { getAuth, signInAnonymously, signInWithCustomToken } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-auth.js";
        import { getFirestore, doc, getDoc, setDoc, onSnapshot, updateDoc } from "https://www.gstatic.com/firebasejs/11.6.1/firebase-firestore.js";

        // For Codepen, replace this with your actual Firebase config object
        const firebaseConfig = {
          apiKey: "YOUR_API_KEY",
          authDomain: "YOUR_AUTH_DOMAIN",
          projectId: "YOUR_PROJECT_ID",
          storageBucket: "YOUR_STORAGE_BUCKET",
          messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
          appId: "YOUR_APP_ID"
        };
        
        const finalFirebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : firebaseConfig;
        const appIdForPath = finalFirebaseConfig.projectId || (typeof __app_id !== 'undefined' ? __app_id : 'default-app-id');

        const firebaseApp = initializeApp(finalFirebaseConfig);
        const auth = getAuth(firebaseApp);
        const db = getFirestore(firebaseApp);

        const loader = document.getElementById('loader');
        const appContent = document.getElementById('app-content');

        const initialFoodData = [
            { id: 1, name: 'גולאש (Gulyás)', city: 'budapest', description: 'מרק בשר וירקות עשיר ומתובל בפפריקה, נחשב למאכל הלאומי.', tasted: false, img: 'https://images.pexels.com/photos/10774535/pexels-photo-10774535.jpeg?auto=compress&cs=tinysrgb&w=800' },
            { id: 2, name: 'לאנגוש (Lángos)', city: 'budapest', description: 'בצק שטוח ומטוגן בשמן עמוק, מוגש בדרך כלל עם שמנת חמוצה וגבינה מגורדת.', tasted: false, img: 'https://images.pexels.com/photos/18943026/pexels-photo-18943026/free-photo-of-a-traditional-hungarian-street-food-dish-called-langos.jpeg?auto=compress&cs=tinysrgb&w=800' },
            { id: 3, name: 'קיורטוש (Kürtőskalács)', city: 'budapest', description: '"עוגת ארובה". מאפה שמרים מתוק בצורת גליל, מצופה בסוכר, קינמון או אגוזים.', tasted: false, img: 'https://images.pexels.com/photos/887853/pexels-photo-887853.jpeg?auto=compress&cs=tinysrgb&w=800' },
            { id: 4, name: 'פפריקש עוף (Csirkepaprikás)', city: 'budapest', description: 'תבשיל עוף ברוטב שמנת עשיר ומתובל בפפריקה מתוקה, מוגש לרוב עם בצקיות קטנות.', tasted: false, img: 'https://images.pexels.com/photos/6210876/pexels-photo-6210876.jpeg?auto=compress&cs=tinysrgb&w=800' },
            { id: 5, name: 'עוגת דובוש (Dobos Torta)', city: 'budapest', description: 'עוגת שכבות של טורט וקרם שוקולד, עם ציפוי קרמל קשיח מלמעלה.', tasted: false, img: 'https://images.pexels.com/photos/205961/pexels-photo-205961.jpeg?auto=compress&cs=tinysrgb&w=800' },
            { id: 6, name: 'כרוב ממולא (Töltött Káposzta)', city: 'budapest', description: 'עלי כרוב כבושים ממולאים בבשר טחון ואורז, מבושלים ברוטב עגבניות.', tasted: false, img: 'https://images.pexels.com/photos/5419233/pexels-photo-5419233.jpeg?auto=compress&cs=tinysrgb&w=800' },
            { id: 7, name: 'שניצל וינאי (Wiener Schnitzel)', city: 'vienna', description: 'פרוסת בשר עגל דקיקה מצופה בפירורי לחם ומטוגנת עד להזהבה. המאכל הכי מפורסם בווינה.', tasted: false, img: 'https://images.pexels.com/photos/106343/pexels-photo-106343.jpeg?auto=compress&cs=tinysrgb&w=800' },
            { id: 8, name: 'זאכרטורטה (Sachertorte)', city: 'vienna', description: 'עוגת שוקולד עשירה ודחוסה עם שכבה דקה של ריבת משמש, מצופה בגנאש שוקולד מבריק.', tasted: false, img: 'https://images.pexels.com/photos/4109998/pexels-photo-4109998.jpeg?auto=compress&cs=tinysrgb&w=800' },
            { id: 9, name: 'אפפלשטרודל (Apfelstrudel)', city: 'vienna', description: 'מאפה בצק עלים דקיק במילוי תפוחי עץ, צימוקים וקינמון. מוגש חם, לעיתים עם גלידת וניל.', tasted: false, img: 'https://images.pexels.com/photos/2205270/pexels-photo-2205270.jpeg?auto=compress&cs=tinysrgb&w=800' },
            { id: 10, name: 'טפלשפיץ (Tafelspitz)', city: 'vienna', description: 'נתח בקר המבושל בציר ירקות עד שהוא רך מאוד. מוגש באופן מסורתי עם רוטב חזרת ותפוחים.', tasted: false, img: 'https://images.pexels.com/photos/1251208/pexels-photo-1251208.jpeg?auto=compress&cs=tinysrgb&w=800' },
            { id: 11, name: 'קייזרשמארן (Kaiserschmarrn)', city: 'vienna', description: 'פנקייק עבה ורך שנקרא לחתיכות גסות, מקורמל עם סוכר וצימוקים, ומוגש עם רסק פירות.', tasted: false, img: 'https://images.pexels.com/photos/13107436/pexels-photo-13107436.jpeg?auto=compress&cs=tinysrgb&w=800' },
            { id: 12, name: 'נקניקיות וינאיות (Würstel)', city: 'vienna', description: 'מגוון נקניקיות איכותיות הנמכרות בדוכני רחוב ומוגשות בלחמנייה עם חרדל.', tasted: false, img: 'https://images.pexels.com/photos/806357/pexels-photo-806357.jpeg?auto=compress&cs=tinysrgb&w=800' }
        ];

        let foodData = [];
        const listId = "budapest-vienna-trip";
        // Simplified Firestore path to avoid potential permissions issues with deep nesting
        const listRef = doc(db, `culinary_lists/${listId}`);

        const foodGrid = document.getElementById('food-grid');
        const filterBtns = document.querySelectorAll('.filter-btn');
        let currentFilter = 'all';
        let budapestChart, viennaChart;

        const createChart = (ctx) => {
            return new Chart(ctx, {
                type: 'doughnut',
                data: { labels: ['טעמתי', 'נותר לטעום'], datasets: [{ data: [0, 0], backgroundColor: ['#92400e', '#f5f5f4'], borderColor: ['#ffffff'], borderWidth: 2, hoverOffset: 4 }] },
                options: { responsive: true, maintainAspectRatio: false, cutout: '70%', plugins: { legend: { display: false }, tooltip: { rtl: true, textDirection: 'rtl' } } }
            });
        };

        async function startApp() {
            try {
                if (typeof __initial_auth_token !== 'undefined') {
                    await signInWithCustomToken(auth, __initial_auth_token);
                } else {
                    await signInAnonymously(auth);
                }
                
                budapestChart = createChart(document.getElementById('budapestChart').getContext('2d'));
                viennaChart = createChart(document.getElementById('viennaChart').getContext('2d'));

                const docSnap = await getDoc(listRef);
                if (!docSnap.exists()) {
                    await setDoc(listRef, { items: initialFoodData });
                }

                onSnapshot(listRef, (doc) => {
                    const serverData = doc.data().items;
                    foodData = serverData.map(serverItem => {
                        const localItem = initialFoodData.find(i => i.id === serverItem.id);
                        return { ...serverItem, img: localItem ? localItem.img : serverItem.img };
                    });

                    renderApp();
                    loader.style.display = 'none';
                    appContent.classList.remove('hidden');
                });

            } catch (error) {
                console.error("Initialization Error:", error);
                loader.innerText = "Error loading app.";
            }
        }
        
        function renderApp() {
            document.getElementById('list-id').textContent = listId;
            renderCards();
            updateCharts();
        }

        const updateCharts = () => {
            if (!foodData.length || !budapestChart || !viennaChart) return;
            const cityData = foodData.reduce((acc, item) => {
                if (!acc[item.city]) acc[item.city] = { tasted: 0, total: 0 };
                acc[item.city].total++;
                if (item.tasted) acc[item.city].tasted++;
                return acc;
            }, {});

            budapestChart.data.datasets[0].data = [cityData.budapest.tasted, cityData.budapest.total - cityData.budapest.tasted];
            budapestChart.update();
            viennaChart.data.datasets[0].data = [cityData.vienna.tasted, cityData.vienna.total - cityData.vienna.tasted];
            viennaChart.update();
        };

        const renderCards = () => {
            foodGrid.innerHTML = '';
            const filteredData = foodData.filter(item => currentFilter === 'all' || item.city === currentFilter);
            filteredData.forEach(item => {
                const card = document.createElement('div');
                card.className = `food-card bg-white rounded-2xl shadow-md overflow-hidden relative ${item.tasted ? 'tasted' : ''}`;
                card.dataset.id = item.id;
                card.innerHTML = `
                    <div class="overlay absolute inset-0 bg-green-800 bg-opacity-70 flex items-center justify-center opacity-0 pointer-events-none">
                        <span class="text-white text-3xl font-bold">✓ טעמתי!</span>
                    </div>
                    <img src="${item.img}" alt="${item.name}" class="w-full h-48 object-cover" onerror="this.onerror=null;this.src='https://placehold.co/600x400/f5f5f4/44403c?text=Image+Not+Found';">
                    <div class="p-5">
                        <h3 class="text-xl font-bold text-amber-900">${item.name}</h3>
                        <p class="text-slate-600 mt-2 h-24">${item.description}</p>
                        <div class="mt-4">
                            <label class="flex items-center cursor-pointer">
                                <input type="checkbox" class="h-5 w-5 rounded border-gray-300 text-amber-600 focus:ring-amber-500" ${item.tasted ? 'checked' : ''}>
                                <span class="mr-3 text-slate-700 font-semibold">סמן כ"טעמתי"</span>
                            </label>
                        </div>
                    </div>
                `;
                foodGrid.appendChild(card);
            });
        };

        foodGrid.addEventListener('change', async (e) => {
            if (e.target.type === 'checkbox') {
                const card = e.target.closest('.food-card');
                const id = parseInt(card.dataset.id);
                const updatedFoodData = foodData.map(item => {
                    if (item.id === id) {
                        return { ...item, tasted: e.target.checked };
                    }
                    return item;
                });
                await updateDoc(listRef, { items: updatedFoodData });
            }
        });

        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                filterBtns.forEach(b => {
                    b.classList.remove('bg-amber-600', 'text-white');
                    b.classList.add('bg-white', 'text-amber-800');
                });
                btn.classList.add('bg-amber-600', 'text-white');
                btn.classList.remove('bg-white', 'text-amber-800');
                currentFilter = btn.id.replace('filter-', '');
                renderCards();
            });
        });

        startApp();
    </script>
</body>
</html>
