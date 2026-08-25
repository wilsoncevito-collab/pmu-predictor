import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score, log_loss
from sklearn.linear_model import LogisticRegression
import joblib
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("🔬 PRÉDICTION DES GAGNANTS (VERSION CORRIGÉE)")
print("=" * 60)

# Lire les données
df = pd.read_csv('courses_with_results.csv')

# Nettoyer les données
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
df['win_odds'] = pd.to_numeric(df['win_odds'], errors='coerce')
df['weight'] = pd.to_numeric(df['weight'], errors='coerce')
df['draw'] = pd.to_numeric(df['draw'], errors='coerce')

# Supprimer les lignes avec des valeurs manquantes
df_clean = df.dropna(subset=['rating', 'win_odds', 'weight', 'winner'])
print(f"📊 Données: {len(df_clean)} chevaux, {df_clean['race_no'].nunique()} courses")

# Créer des caractéristiques
print("\n🔧 Création des caractéristiques...")

# 1. Rang de la cote dans la course (1 = favori)
df_clean['odds_rank'] = df_clean.groupby('race_no')['win_odds'].rank(method='dense')

# 2. Rang du rating dans la course
df_clean['rating_rank'] = df_clean.groupby('race_no')['rating'].rank(method='dense', ascending=False)

# 3. Ratio poids/rating
df_clean['weight_rating_ratio'] = df_clean['weight'] / df_clean['rating']

# 4. Taille de la course
df_clean['race_size'] = df_clean.groupby('race_no')['race_no'].transform('count')

# 5. Si le cheval est dans le top 3 des ratings
df_clean['top3_rating'] = df_clean['rating_rank'].apply(lambda x: 1 if x <= 3 else 0)

# 6. Si le cheval est dans le top 3 des cotes
df_clean['top3_odds'] = df_clean['odds_rank'].apply(lambda x: 1 if x <= 3 else 0)

# Encoder les variables catégorielles avec gestion des valeurs rares
def encode_with_frequency(series):
    """Encode les valeurs avec leur fréquence"""
    freq = series.value_counts() / len(series)
    return series.map(freq)

df_clean['trainer_freq'] = encode_with_frequency(df_clean['trainer'].fillna('unknown'))
df_clean['jockey_freq'] = encode_with_frequency(df_clean['jockey'].fillna('unknown'))

# Caractéristiques pour le modèle
features = [
    'rating',
    'win_odds',
    'weight',
    'draw',
    'odds_rank',
    'rating_rank',
    'weight_rating_ratio',
    'race_size',
    'top3_rating',
    'top3_odds',
    'trainer_freq',
    'jockey_freq'
]

X = df_clean[features]
y = df_clean['winner']

print(f"\n📊 Caractéristiques: {len(features)}")
print(f"   Target: {y.sum()} gagnants sur {len(y)}")

# Séparer en train/test (en gardant les courses ensemble)
unique_races = df_clean['race_no'].unique()
np.random.seed(42)
train_races = np.random.choice(unique_races, size=int(0.8 * len(unique_races)), replace=False)
test_races = [r for r in unique_races if r not in train_races]

train_idx = df_clean['race_no'].isin(train_races)
test_idx = df_clean['race_no'].isin(test_races)

X_train, X_test = X[train_idx], X[test_idx]
y_train, y_test = y[train_idx], y[test_idx]

print(f"\n📊 Entraînement: {len(X_train)} chevaux ({len(train_races)} courses)")
print(f"📊 Test: {len(X_test)} chevaux ({len(test_races)} courses)")

# Standardiser
scaler = StandardScaler()
numeric_cols = ['rating', 'win_odds', 'weight', 'draw', 'weight_rating_ratio']
X_train_scaled = X_train.copy()
X_test_scaled = X_test.copy()
X_train_scaled[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
X_test_scaled[numeric_cols] = scaler.transform(X_test[numeric_cols])

# Entraîner le modèle
print("\n🤖 Entraînement du modèle Random Forest...")

model = RandomForestClassifier(
    n_estimators=50,
    max_depth=5,
    min_samples_split=10,
    min_samples_leaf=5,
    class_weight='balanced',
    random_state=42
)

model.fit(X_train_scaled, y_train)

# Évaluer
y_pred = model.predict(X_test_scaled)
y_proba = model.predict_proba(X_test_scaled)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_proba)

print(f"\n📈 PERFORMANCE:")
print(f"   Précision (Accuracy): {accuracy:.2%}")
print(f"   AUC: {auc:.2%}")
print(f"   Log Loss: {log_loss(y_test, y_proba):.4f}")

# Importance des caractéristiques
print("\n🔑 IMPORTANCE DES CARACTÉRISTIQUES:")
importance = pd.DataFrame({
    'feature': features,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

for _, row in importance.head(10).iterrows():
    print(f"   - {row['feature']}: {row['importance']:.2%}")

# Validation croisée
print("\n📊 Validation croisée (5 folds):")
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=cv, scoring='accuracy')
print(f"   Score moyen: {cv_scores.mean():.2%} (+/- {cv_scores.std():.2%})")

# Sauvegarder
print("\n💾 Sauvegarde du modèle...")
joblib.dump(model, 'best_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
with open('features.txt', 'w') as f:
    f.write(','.join(features))

print("   ✅ Modèle sauvegardé")

# Afficher quelques prédictions
print("\n🔮 Exemples sur le jeu de test:")
test_df = df_clean[test_idx].copy()
test_df['pred_proba'] = y_proba
test_df['predicted'] = y_pred

# Afficher les prédictions pour quelques courses
for race in test_races[:2]:
    race_data = test_df[test_df['race_no'] == race]
    print(f"\n   Course {race}:")
    for _, row in race_data.sort_values('pred_proba', ascending=False).head(3).iterrows():
        actual = "🏆" if row['winner'] == 1 else ""
        print(f"      {row['horse_name']}: {row['pred_proba']:.2%} (Cote: {row['win_odds']}) {actual}")

print("\n" + "=" * 60)