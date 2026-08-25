@app.route('/api/predictions/today')
def get_today_predictions():
    try:
        from core.models_sqlite import Meeting, Race, Runner
        from core.config import get_db
        
        db = get_db()
        
        # Récupérer la dernière réunion
        meeting = db.query(Meeting).order_by(Meeting.meeting_date.desc()).first()
        
        if not meeting:
            return jsonify({'success': False, 'error': 'Aucune réunion trouvée'})
        
        result = {
            'date': meeting.meeting_date,
            'meetings': {}
        }
        
        # Récupérer les courses
        races = db.query(Race).filter(Race.meeting_id == meeting.id).all()
        
        for race in races:
            runners = db.query(Runner).filter(Runner.race_id == race.id).all()
            predictions = []
            
            for runner in runners:
                odds = runner.win_odds or 0
                if odds and odds > 0:
                    proba = min(0.95, 1 / odds * 3)
                else:
                    proba = 0.5
                
                predictions.append({
                    'name': runner.horse_name or 'Unknown',
                    'probability': round(proba * 100, 2),
                    'win_odds': round(odds, 2),
                    'rating': runner.rating or 0,
                    'weight': runner.weight or 0,
                    'draw': runner.draw or 0,
                    'trainer': runner.trainer or '',
                    'jockey': runner.jockey or '',
                    'value': round(((proba * (odds or 1)) - 1) * 100, 1),
                    'is_winner': runner.is_winner or False
                })
            
            predictions.sort(key=lambda x: x['probability'], reverse=True)
            result['meetings'][meeting.venue_code] = result['meetings'].get(meeting.venue_code, {})
            result['meetings'][meeting.venue_code][f"Course {race.race_no}"] = predictions
        
        db.close()
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})