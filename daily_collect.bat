@echo off
echo ========================================
echo 📡 COLLECTE QUOTIDIENNE PMU
echo ========================================
echo.

echo 📥 Collecte des données...
node test-api.js

echo 📊 Import dans la base...
python -c "from core.import_data import import_from_json; print(import_from_json())"

echo 📊 Mise à jour du CSV...
python -c "import pandas as pd; df=pd.read_csv('courses_data.csv'); df['venue']=df['venue'].fillna('S4'); df['race_no']=pd.to_numeric(df['race_no'], errors='coerce').fillna(1).astype(int); df.to_csv('courses_data_clean.csv', index=False); print('✅ CSV mis à jour')"

echo.
echo ✅ Collecte terminée !
echo.
pause