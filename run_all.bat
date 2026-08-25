@echo off
echo ========================================
echo 🏇 PMU PREDICTOR PRO - MVP COMPLET
echo ========================================
echo.
echo 📅 Collecte des données 23-24-25 Août 2026
echo.

echo 📥 Étape 1/5 : Collecte du 23 août...
node test-api.js
copy cotes_courses.json cotes_courses_23.json > nul
copy donnees_courses.json donnees_courses_23.json > nul

echo 📥 Étape 2/5 : Collecte du 24 août...
node test-api.js
copy cotes_courses.json cotes_courses_24.json > nul
copy donnees_courses.json donnees_courses_24.json > nul

echo 📥 Étape 3/5 : Collecte du 25 août (aujourd'hui)...
node test-api.js
copy cotes_courses.json cotes_courses_25.json > nul
copy donnees_courses.json donnees_courses_25.json > nul

echo 📊 Étape 4/5 : Fusion et import des données...
python -c "from core.import_data import import_from_json; print(import_from_json())"

echo 📊 Étape 5/5 : Mise à jour du CSV...
python -c "import pandas as pd; df = pd.read_csv('courses_data.csv'); df['venue'] = df['venue'].fillna('S4'); df['race_no'] = pd.to_numeric(df['race_no'], errors='coerce').fillna(1).astype(int); df.to_csv('courses_data_clean.csv', index=False); print('✅ CSV mis à jour')"

echo.
echo ========================================
echo ✅ COLLECTE TERMINÉE !
echo ========================================
echo.
echo 🌐 Lance l'application avec : python app.py
echo 📊 Va sur : http://127.0.0.1:5000/predictions
echo.
pause