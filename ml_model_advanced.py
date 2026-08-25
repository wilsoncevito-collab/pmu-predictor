import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
import joblib
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("🔬 PRÉDICTION DES GAGNANTS DE COURSES HIPPIQUES")
print("=" * 60)

# Lire les données
df = pd.read_csv('courses_with_results.csv')

# Nettoyer les données
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
df['win_odds'] = pd.to_numeric(df['win_odds'], errors='coerce')
df['weight'] = pd.to_numeric(df['weight'], errors='coerce')
df['draw'] = pd.to_numeric(df['draw'], errors='coerce')

# Supprimer les lignes avec des valeurs manquantes critiques
df_clean = df.dropna(subset=['rating', 'win_odds', 'weight', 'winner'])
print(f"📊 Données nettoyées: {len(df_clean)} chevaux")

# Créer des caractéristiques supplémentaires
print("\n🔧 Création des caractéristiques...")

# 1. Rating normalisé par course (performance relative)
df_clean['rating_normalized'] = df_clean.groupby('race_no')['rating'].transform(
    lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0
)

# 2. Cote normalisée par course
df_clean['odds_normalized'] = df_clean.groupby('race_no')['win_odds'].transform(
    lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0
)

# 3. Rang de la cote dans la course
df_clean['odds_rank'] = df_clean.groupby('race_no')['win_odds'].rank()

# 4. Rapport poids/rating
df_clean['weight_rating_ratio'] = df_clean['weight'] / df_clean['rating']

# 5. Position de départ (draw) normalisée
df_clean['draw_normalized'] = df_clean.groupby('race_no')['draw'].transform(
    lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0
)

# Encoder les variables catégorielles
le_trainer = LabelEncoder()
le_jockey = LabelEncoder()
le_sex = LabelEncoder()

df_clean['trainer_enc'] = le_trainer.fit_transform(df_clean['trainer'].fillna('unknown'))
df_clean['jockey_enc'] = le_jockey.fit_transform(df_clean['jockey'].fillna('unknown'))
df_clean['sex_enc'] = le_sex.fit_transform(df_clean['sex'].fillna('M'))

print(f"   - Entraîneurs: {len(le_trainer.classes_)}")
print(f"   - Jockeys: {len(le_jockey.classes_)}")

# Caractéristiques pour le modèle
features = [
    'rating',
    'rating_normalized',
    'win_odds',
    'odds_normalized',
    'odds_rank',
    'weight',
    'weight_rating_ratio',
    'draw',
    'draw_normalized',
    'trainer_enc',
    'jockey_enc',
    'sex_enc'
]

X = df_clean[features]
y = df_clean['winner']

# Standardiser les caractéristiques numériques
scaler = StandardScaler()
numeric_cols = ['rating', 'rating_normalized', 'win_odds', 'odds_normalized', 
                'odds_rank', 'weight', 'weight_rating_ratio', 'draw', 'draw_normalized']
X[numeric_cols] = scaler.fit_transform(X[numeric_cols])

# Séparer en train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\n📊 Données d'entraînement: {len(X_train)}")
print(f"📊 Données de test: {len(X_test)}")

# Entraîner plusieurs modèles
print("\n🤖 Entraînement des modèles...")

models = {
    'Logistic Regression': LogisticRegression(max_iter=1000, class_weight='balanced'),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
}

results = {}

for name, model in models.items():
    # Entraîner
    model.fit(X_train, y_train)
    
    # Prédire
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    # Évaluer
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_proba) if len(np.unique(y_test)) > 1 else 0
    
    results[name] = {
        'model': model,
        'accuracy': accuracy,
        'auc': auc
    }
    
    print(f"   {name}: Accuracy={accuracy:.2%}, AUC={auc:.2%}")

# Meilleur modèle
best_name = max(results, key=lambda x: results[x]['auc'])
best_model = results[best_name]['model']
print(f"\n🏆 Meilleur modèle: {best_name} (AUC={results[best_name]['auc']:.2%})")

# Importance des caractéristiques (pour Random Forest)
if best_name in ['Random Forest', 'Gradient Boosting']:
    print("\n🔑 Importance des caractéristiques:")
    importance = pd.DataFrame({
        'feature': features,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for _, row in importance.head(10).iterrows():
        print(f"   - {row['feature']}: {row['importance']:.2%}")

# Sauvegarder le modèle
print("\n💾 Sauvegarde du modèle...")
joblib.dump(best_model, 'best_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(le_trainer, 'trainer_encoder.pkl')
joblib.dump(le_jockey, 'jockey_encoder.pkl')
joblib.dump(le_sex, 'sex_encoder.pkl')
with open('features.txt', 'w') as f:
    f.write(','.join(features))

print(f"   ✅ Modèle sauvegardé: best_model.pkl")
print(f"   ✅ Scaler sauvegardé: scaler.pkl")
print(f"   ✅ Encodeurs sauvegardés")

# Afficher quelques prédictions
print("\n🔮 Exemples de prédictions:")
test_df = df_clean.iloc[X_test.index].copy()
test_df['predicted_winner'] = best_model.predict(X_test)
test_df['prediction_probability'] = best_model.predict_proba(X_test)[:, 1]

for i in range(min(5, len(test_df))):
    row = test_df.iloc[i]
    if row['winner'] == 1:
        print(f"   ✅ Gagnant: {row['horse_name']} (probabilité prédite: {row['prediction_probability']:.2%})")

print("\n" + "=" * 60)
print("📋 RÉSUMÉ:")
print(f"   Meilleur modèle: {best_name}")
print(f"   Précision: {results[best_name]['accuracy']:.2%}")
print(f"   AUC: {results[best_name]['auc']:.2%}")
print("=" * 60)