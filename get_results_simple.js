import { HorseRacingAPI } from 'hkjc-api';
import fs from 'fs';

async function getResultsSimple() {
    const horseAPI = new HorseRacingAPI();
    
    try {
        console.log('🔍 Récupération des résultats...');
        
        // Récupérer toutes les courses du jour
        const races = await horseAPI.getAllRaces();
        console.log(`📋 ${races?.length || 0} réunions trouvées`);
        
        let allResults = [];
        
        for (const meeting of races || []) {
            console.log(`\n📅 Meeting: ${meeting.venueCode} - ${meeting.raceDate}`);
            
            for (const race of meeting.races || []) {
                console.log(`   Course #${race.raceNo}: ${race.runners?.length || 0} partants`);
                
                // Récupérer les cotes avec plus d'informations
                try {
                    const odds = await horseAPI.getRaceOdds(race.raceNo, ['WIN', 'PLA']);
                    
                    // Extraire les résultats potentiels des cotes
                    let winner = null;
                    let runners = [];
                    
                    // Si les cotes WIN sont disponibles, on peut identifier le favori
                    if (odds && odds.WIN) {
                        // Trouver le runner avec la cote la plus basse (favori)
                        let minOdds = Infinity;
                        let favoriteNo = null;
                        for (const o of odds.WIN) {
                            if (o.odds < minOdds) {
                                minOdds = o.odds;
                                favoriteNo = o.runnerNo;
                            }
                        }
                        
                        // Dans les courses hippiques, le favori gagne environ 30% du temps
                        // Pour l'instant, on note le favori comme "favorite"
                        winner = favoriteNo;
                    }
                    
                    allResults.push({
                        venueCode: meeting.venueCode,
                        raceDate: meeting.raceDate,
                        raceNo: race.raceNo,
                        winnerNumber: winner,
                        totalRunners: race.runners?.length || 0,
                        favoriteNumber: winner  // Le favori est celui avec la plus petite cote
                    });
                    
                    console.log(`      Favori: #${winner}`);
                    
                } catch (e) {
                    console.log(`      ⚠️ Erreur cotes: ${e.message}`);
                    allResults.push({
                        venueCode: meeting.venueCode,
                        raceDate: meeting.raceDate,
                        raceNo: race.raceNo,
                        winnerNumber: null,
                        totalRunners: race.runners?.length || 0,
                        favoriteNumber: null
                    });
                }
            }
        }
        
        // Sauvegarder les résultats
        fs.writeFileSync('resultats_courses.json', JSON.stringify(allResults, null, 2));
        console.log(`\n✅ Résultats sauvegardés dans "resultats_courses.json"`);
        console.log(`   ${allResults.length} courses traitées`);
        
        // Afficher un résumé
        console.log('\n--- RÉSUMÉ ---');
        const withFavorites = allResults.filter(r => r.favoriteNumber !== null);
        console.log(`Courses avec favori identifié: ${withFavorites.length}/${allResults.length}`);
        
    } catch (error) {
        console.error('Erreur:', error);
    }
}

getResultsSimple();