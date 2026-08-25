from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from core.config import Config
from core.models_sqlite import Meeting
from datetime import datetime
import pandas as pd
import os
import json

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# ============= ROUTES PAGES =============

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predictions')
def predictions_page():
    return render_template('predictions.html')

@app.route('/history')
def history_page():
    return render_template('history.html')

@app.route('/comparison')
def comparison_page():
    return render_template('comparison.html')

# ============= API - PRÉDICTIONS =============

@app.route('/api/predictions/today')
def get_today_predictions():
    try:
        if not os.path.exists('courses_data_clean.csv'):
            return jsonify({'success': False, 'error': 'Fichier CSV non trouvé'})
        
        df = pd.read_csv('courses_data_clean.csv')
        
        # Nettoyer les données
        df['win_odds'] = pd.to_numeric(df['win_odds'], errors='coerce').fillna(0)
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)
        df['weight'] = pd.to_numeric(df['weight'], errors='coerce').fillna(0)
        df['draw'] = pd.to_numeric(df['draw'], errors='coerce').fillna(0)
        
        # Récupérer la date depuis la base SQLite
        try:
            from core.config import get_db
            db = get_db()
            meeting = db.query(Meeting).first()
            date_str = meeting.meeting_date if meeting else datetime.now().strftime('%Y-%m-%d')
            db.close()
        except:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        result = {
            'date': date_str,
            'meetings': {}
        }
        
        for venue in df['venue'].unique():
            if pd.isna(venue) or venue == '':
                continue
                
            venue_data = df[df['venue'] == venue]
            result['meetings'][venue] = {}
            
            for race_no in venue_data['race_no'].unique():
                if pd.isna(race_no) or race_no == '':
                    continue
                    
                race_data = venue_data[venue_data['race_no'] == race_no]
                predictions = []
                
                for _, row in race_data.iterrows():
                    odds = float(row.get('win_odds', 0) or 0)
                    if odds and odds > 0:
                        proba = min(0.95, 1 / odds * 3)
                    else:
                        proba = 0.5
                    
                    rating = float(row.get('rating', 0) or 0)
                    weight = float(row.get('weight', 0) or 0)
                    draw = float(row.get('draw', 0) or 0)
                    
                    predictions.append({
                        'name': str(row.get('horse_name', 'Unknown')),
                        'probability': round(proba * 100, 2),
                        'win_odds': round(odds, 2),
                        'rating': round(rating, 1) if rating > 0 else 0,
                        'weight': round(weight, 1) if weight > 0 else 0,
                        'draw': round(draw, 1) if draw > 0 else 0,
                        'trainer': str(row.get('trainer', '')),
                        'jockey': str(row.get('jockey', '')),
                        'value': round(((proba * (odds or 1)) - 1) * 100, 1),
                        'is_winner': False
                    })
                
                predictions.sort(key=lambda x: x['probability'], reverse=True)
                result['meetings'][venue][f"Course {int(race_no)}"] = predictions
        
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============= API - STATS =============

@app.route('/api/stats')
def get_stats():
    try:
        if os.path.exists('courses_data_clean.csv'):
            df = pd.read_csv('courses_data_clean.csv')
            total_races = df['race_no'].nunique()
            total_runners = len(df)
        else:
            total_races = 0
            total_runners = 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_races': total_races,
                'total_bets': 0,
                'total_profit': 0,
                'win_rate': 0
            }
        })
    except:
        return jsonify({'success': True, 'stats': {'total_races': 0, 'total_bets': 0, 'total_profit': 0, 'win_rate': 0}})

# ============= API - PARIS =============

@app.route('/api/bets', methods=['GET'])
def get_bets():
    return jsonify({'success': True, 'stats': {'total_bets': 0, 'wins': 0, 'total_profit': 0, 'win_rate': 0}, 'bets': []})

@app.route('/api/bets', methods=['POST'])
def add_bet():
    return jsonify({'success': True, 'bet_id': 1})

# ============= API - COMPARAISON =============

@app.route('/api/comparison')
def get_comparison():
    try:
        from core.comparison_service import get_comparison_stats
        stats = get_comparison_stats()
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============= IMPORT =============

@app.route('/api/import', methods=['POST'])
def import_data():
    try:
        from core.import_data import import_from_json
        result = import_from_json()
        return jsonify({'success': True, 'message': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(
        debug=Config.DEBUG,
        host='0.0.0.0',
        port=Config.PORT
    )