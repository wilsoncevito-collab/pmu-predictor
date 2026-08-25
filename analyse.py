import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Lire le CSV
df = pd.read_csv('courses_data.csv')

print("=" * 60)
print("ANALYSE DES DONNÉES DES COURSES HIPPIQUES")
print("=" * 60)

# Informations générales
print(f"\n📊 STATISTIQUES GÉNÉRALES:")
print(f"   - Nombre total de chevaux: {len(df)}")
print(f"   - Nombre de courses uniques: {df['race_no'].nunique()}")
print(f"   - Nombre de chevaux uniques: {df['horse_name'].nunique()}")
print(f"   - Nombre d'entraîneurs uniques: {df['trainer'].nunique()}")
print(f"   - Nombre de jockeys uniques: {df['jockey'].nunique()}")

# Statistiques des cotes
print(f"\n📈 STATISTIQUES DES COTES (WIN_ODDS):")
win_odds = pd.to_numeric(df['win_odds'], errors='coerce')
print(f"   - Moyenne: {win_odds.mean():.2f}")
print(f"   - Médiane: {win_odds.median():.2f}")
print(f"   - Minimum: {win_odds.min():.2f}")
print(f"   - Maximum: {win_odds.max():.2f}")
print(f"   - Écart-type: {win_odds.std():.2f}")

# Statistiques des ratings
print(f"\n🏆 STATISTIQUES DES RATINGS:")
ratings = pd.to_numeric(df['rating'], errors='coerce')
print(f"   - Moyenne: {ratings.mean():.2f}")
print(f"   - Médiane: {ratings.median():.2f}")
print(f"   - Minimum: {ratings.min():.2f}")
print(f"   - Maximum: {ratings.max():.2f}")

# Top 5 des entraîneurs avec le plus de chevaux
print(f"\n👨‍🏫 TOP 5 DES ENTRAÎNEURS:")
top_trainers = df['trainer'].value_counts().head(5)
for trainer, count in top_trainers.items():
    print(f"   - {trainer}: {count} chevaux")

# Top 5 des jockeys avec le plus de chevaux
print(f"\n🏇 TOP 5 DES JOCKEYS:")
top_jockeys = df['jockey'].value_counts().head(5)
for jockey, count in top_jockeys.items():
    print(f"   - {jockey}: {count} chevaux")

# Distribution des cotes (graphique)
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
win_odds_clean = win_odds.dropna()
win_odds_clean = win_odds_clean[win_odds_clean < 50]  # Filtrer les valeurs extrêmes
plt.hist(win_odds_clean, bins=30, edgecolor='black', alpha=0.7, color='blue')
plt.title('Distribution des cotes (WIN)')
plt.xlabel('Cote')
plt.ylabel('Nombre de chevaux')
plt.grid(True, alpha=0.3)

plt.subplot(1, 2, 2)
ratings_clean = ratings.dropna()
plt.hist(ratings_clean, bins=20, edgecolor='black', alpha=0.7, color='green')
plt.title('Distribution des ratings')
plt.xlabel('Rating')
plt.ylabel('Nombre de chevaux')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('analyse_courses.png', dpi=150)
print(f"\n📊 Graphiques sauvegardés dans 'analyse_courses.png'")

# Relation entre rating et cote
plt.figure(figsize=(8, 6))
valid_data = df.dropna(subset=['rating', 'win_odds'])
valid_data['rating'] = pd.to_numeric(valid_data['rating'], errors='coerce')
valid_data['win_odds'] = pd.to_numeric(valid_data['win_odds'], errors='coerce')
valid_data = valid_data.dropna()
valid_data = valid_data[valid_data['win_odds'] < 50]

plt.scatter(valid_data['rating'], valid_data['win_odds'], alpha=0.5)
plt.xlabel('Rating')
plt.ylabel('Cote (WIN)')
plt.title('Relation entre Rating et Cote')
plt.grid(True, alpha=0.3)
plt.savefig('rating_vs_cote.png', dpi=150)
print(f"📊 Graphique 'rating_vs_cote.png' sauvegardé")

# Sauvegarder un résumé
summary = {
    'total_chevaux': len(df),
    'total_courses': df['race_no'].nunique(),
    'moyenne_cote': win_odds.mean(),
    'moyenne_rating': ratings.mean(),
    'top_entraineur': top_trainers.index[0] if len(top_trainers) > 0 else '',
    'top_jockey': top_jockeys.index[0] if len(top_jockeys) > 0 else ''
}

print("\n" + "=" * 60)
print("📋 RÉSUMÉ:")
print(f"   Total chevaux: {summary['total_chevaux']}")
print(f"   Total courses: {summary['total_courses']}")
print(f"   Cote moyenne: {summary['moyenne_cote']:.2f}")
print(f"   Rating moyen: {summary['moyenne_rating']:.2f}")
print("=" * 60)

# Exporter les données nettoyées pour le machine learning
df_clean = df.copy()
df_clean['win_odds'] = pd.to_numeric(df_clean['win_odds'], errors='coerce')
df_clean['rating'] = pd.to_numeric(df_clean['rating'], errors='coerce')
df_clean = df_clean.dropna(subset=['win_odds', 'rating'])
df_clean.to_csv('courses_data_clean.csv', index=False)
print(f"\n💾 Données nettoyées sauvegardées dans 'courses_data_clean.csv'")