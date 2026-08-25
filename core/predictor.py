import pandas as pd
import joblib
import os
import sys

# Ajouter le chemin parent pour importer le modèle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Predictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.features = []
        self.load_model()
    
    def load_model(self):
        """Charge le modèle entraîné"""
        # Chercher le modèle dans différents endroits
        possible_paths = [
            'best_model.pkl',
            'models/best_model.pkl',
            '../pipeline-pmu/best_model.pkl'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.model = joblib.load(path)
                print(f"✅ Modèle chargé depuis {path}")
                break
        
        if self.model is None:
            print("⚠️ Modèle non trouvé, utilisation d'un modèle simplifié")
            from sklearn.ensemble import RandomForestClassifier
            self.model = RandomForestClassifier()
            self.model.fit([[0, 0, 0, 0]], [0])
    
    def predict(self, runner_data):
        """Prédit la probabilité de victoire"""
        if self.model is None:
            return 0.5
        
        # Extraire les caractéristiques
        rating = float(runner_data.get('rating') or 0)
        win_odds = float(runner_data.get('win_odds') or 10)
        weight = float(runner_data.get('weight') or 120)
        draw = float(runner_data.get('draw') or 5)
        
        # Créer les caractéristiques
        features = {
            'rating': rating,
            'win_odds': win_odds,
            'weight': weight,
            'draw': draw,
            'odds_rank': 1,
            'rating_rank': 1,
            'weight_rating_ratio': weight / rating if rating > 0 else 0,
            'race_size': 10,
            'top3_rating': 1,
            'top3_odds': 1,
            'trainer_freq': 0.1,
            'jockey_freq': 0.1
        }
        
        df = pd.DataFrame([features])
        
        try:
            proba = self.model.predict_proba(df)[0][1]
            return proba
        except:
            return 0.5
    
    def get_bet_suggestion(self, runner_data, bankroll=100):
        """
        Suggère un pari basé sur la prédiction
        
        Retourne :
        - horse_name: nom du cheval
        - probability: probabilité prédite
        - odds: cote
        - value: valeur du pari (probabilité * cote - 1)
        - suggested_stake: mise suggérée (méthode de Kelly)
        - confidence: 'HIGH', 'MEDIUM', 'LOW'
        - recommendation: 'PLAY', 'CONSIDER', 'AVOID'
        """
        proba = self.predict(runner_data)
        odds = float(runner_data.get('win_odds') or 0)
        
        if odds == 0:
            return {
                'horse_name': runner_data.get('horse_name', ''),
                'probability': round(proba * 100, 2),
                'odds': odds,
                'value': 0,
                'suggested_stake': 0,
                'confidence': 'LOW',
                'recommendation': 'AVOID',
                'reason': 'Cote non disponible'
            }
        
        # Calculer la value
        value = (proba * odds) - 1
        
        # Calculer la mise suggérée (méthode de Kelly fractionnée)
        kelly = (proba * odds - 1) / (odds - 1) if odds > 1 else 0
        kelly = max(0, kelly)  # Pas de mise négative
        kelly_fraction = kelly * 0.25  # 25% de Kelly pour sécurité
        suggested_stake = min(bankroll * kelly_fraction, 5)  # Max 5€
        suggested_stake = max(suggested_stake, 0.50)  # Min 0.50€
        
        # Déterminer la confiance
        if proba > 0.70 and value > 0.10:
            confidence = 'HIGH'
            recommendation = 'PLAY'
            reason = f"Probabilité élevée ({proba*100:.0f}%) et bonne value ({value*100:.0f}%)"
        elif proba > 0.50 and value > 0.05:
            confidence = 'MEDIUM'
            recommendation = 'CONSIDER'
            reason = f"Value positive ({value*100:.0f}%) mais probabilité modérée"
        else:
            confidence = 'LOW'
            recommendation = 'AVOID'
            reason = f"Pas assez de value ({value*100:.0f}%)"
        
        return {
            'horse_name': runner_data.get('horse_name', ''),
            'probability': round(proba * 100, 2),
            'odds': odds,
            'value': round(value * 100, 1),
            'suggested_stake': round(suggested_stake, 2),
            'confidence': confidence,
            'recommendation': recommendation,
            'reason': reason
        }
    
    def get_best_bets(self, runners_data, bankroll=100, limit=3):
        """
        Retourne les meilleurs paris pour une course
        """
        suggestions = []
        
        for runner in runners_data:
            suggestion = self.get_bet_suggestion(runner, bankroll)
            if suggestion['recommendation'] != 'AVOID':
                suggestions.append(suggestion)
        
        # Trier par value décroissante
        suggestions.sort(key=lambda x: x['value'], reverse=True)
        
        return suggestions[:limit]