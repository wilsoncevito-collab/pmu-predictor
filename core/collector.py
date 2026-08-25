import sys
import os
from datetime import datetime

# Ajouter le chemin parent pour importer hkjc-api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import get_supabase
from core.models import Meeting, Race, Runner, Result

class DataCollector:
    def __init__(self):
        self.supabase = get_supabase()
    
    def collect_all(self):
        """Collecte les courses du jour et leurs résultats"""
        print("📡 Collecte des données du jour...")
        
        try:
            from hkjc_api import HorseRacingAPI
            api = HorseRacingAPI()
            
            # 1. Récupérer les réunions actives
            meetings = api.getActiveMeetings()
            print(f"   {len(meetings)} réunions trouvées")
            
            for meeting_data in meetings:
                venue_code = meeting_data.get('venueCode')
                meeting_date = meeting_data.get('raceDate')
                
                if not venue_code or not meeting_date:
                    continue
                
                # Créer ou récupérer la réunion
                meeting = Meeting.get_or_create(venue_code, meeting_date)
                print(f"   📋 Réunion {venue_code} - {meeting_date}")
                
                # 2. Récupérer toutes les courses
                all_races = api.getAllRaces()
                
                for meeting_races in all_races:
                    if meeting_races.get('venueCode') == venue_code:
                        for race in meeting_races.get('races', []):
                            race_no = race.get('raceNo')
                            runners = race.get('runners', [])
                            
                            # Sauvegarder la course
                            race_data = {
                                'meeting_id': meeting.id,
                                'race_no': race_no,
                                'race_name': race.get('raceName', ''),
                                'total_runners': len(runners)
                            }
                            
                            response = self.supabase.table('races').insert(race_data).execute()
                            race_id = response.data[0]['id']
                            
                            print(f"      Course #{race_no}: {len(runners)} partants")
                            
                            # 3. Sauvegarder les runners
                            for runner in runners:
                                runner_data = {
                                    'race_id': race_id,
                                    'runner_no': runner.get('runnerNo'),
                                    'horse_name': runner.get('horseName') or runner.get('name', ''),
                                    'rating': runner.get('internationalRating') or runner.get('rating'),
                                    'weight': runner.get('weight') or runner.get('handicapWeight'),
                                    'draw': runner.get('draw') or runner.get('barrierDrawNumber'),
                                    'trainer': runner.get('trainerName') or runner.get('trainer', {}).get('name_en'),
                                    'jockey': runner.get('jockeyName') or runner.get('jockey', {}).get('name_en'),
                                    'win_odds': runner.get('winOdds')
                                }
                                
                                self.supabase.table('runners').insert(runner_data).execute()
                            
                            # 4. Récupérer les résultats de la course
                            try:
                                result_data = api.getRaceResult(race_no)
                                if result_data and result_data.get('runners'):
                                    for r in result_data.get('runners', []):
                                        if r.get('position') == 1:
                                            winner_number = r.get('runnerNo')
                                            winner_name = r.get('horseName')
                                            
                                            # Sauvegarder le résultat
                                            Result.save_result(race_id, winner_number, winner_name)
                                            
                                            # Marquer le runner comme gagnant
                                            self.supabase.table('runners')\
                                                .update({'is_winner': True})\
                                                .eq('race_id', race_id)\
                                                .eq('runner_no', winner_number)\
                                                .execute()
                                            
                                            print(f"         🏆 Gagnant: {winner_name} (#{winner_number})")
                                            break
                            except Exception as e:
                                print(f"         ⚠️ Pas de résultat disponible: {e}")
            
            print("✅ Collecte terminée")
            return True
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    def collect_results_only(self):
        """Collecte uniquement les résultats des courses du jour"""
        print("📡 Collecte des résultats...")
        
        try:
            from hkjc_api import HorseRacingAPI
            api = HorseRacingAPI()
            
            # Récupérer toutes les courses du jour
            all_races = api.getAllRaces()
            
            for meeting in all_races:
                venue_code = meeting.get('venueCode')
                meeting_date = meeting.get('raceDate')
                
                # Récupérer la réunion
                meeting = Meeting.get_or_create(venue_code, meeting_date)
                
                for race in meeting.get('races', []):
                    race_no = race.get('raceNo')
                    
                    # Récupérer la course en base
                    response = self.supabase.table('races')\
                        .select('*')\
                        .eq('meeting_id', meeting.id)\
                        .eq('race_no', race_no)\
                        .execute()
                    
                    if not response.data:
                        continue
                    
                    race_id = response.data[0]['id']
                    
                    # Récupérer le résultat
                    try:
                        result_data = api.getRaceResult(race_no)
                        if result_data and result_data.get('runners'):
                            for r in result_data.get('runners', []):
                                if r.get('position') == 1:
                                    winner_number = r.get('runnerNo')
                                    winner_name = r.get('horseName')
                                    
                                    Result.save_result(race_id, winner_number, winner_name)
                                    
                                    self.supabase.table('runners')\
                                        .update({'is_winner': True})\
                                        .eq('race_id', race_id)\
                                        .eq('runner_no', winner_number)\
                                        .execute()
                                    
                                    print(f"   ✅ Course #{race_no}: {winner_name} gagne")
                                    break
                    except:
                        pass
            
            return True
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False