import { HorseRacingAPI } from 'hkjc-api';
import fs from 'fs';

async function getResults() {
    const horseAPI = new HorseRacingAPI();
    
    try {
        console.log('🔍 Récupération des résultats des courses...');
        
        // Récupérer toutes les courses du jour
        const races = await horseAPI.getAllRaces();
        
        let allResults = [];
        
        for (const meeting of races || []) {
            for (const race of meeting.races || []) {
                // Récupérer les résultats de la course
                const result = await horseAPI.getRaceResult(race.raceNo);
                allResults.push({
                    meetingCode: meeting.venueCode,
                    raceDate: meeting.raceDate,
                    raceNo: race.raceNo,
                    result: result
                });
                console.log(`  ✅ Résultats course #${race.raceNo} récupérés`);
            }
        }
        
        // Sauvegarder les résultats
        fs.writeFileSync('resultats_courses.json', JSON.stringify(allResults, null, 2));
        console.log(`\n✅ Résultats sauvegardés dans "resultats_courses.json"`);
        
        // Afficher un résumé
        console.log('\n--- RÉSUMÉ DES RÉSULTATS ---');
        for (const r of allResults) {
            console.log(`Course ${r.raceNo} (${r.raceDate}): ${r.result?.runners?.length || 0} partants`);
        }
        
    } catch (error) {
        console.error('Erreur:', error);
    }
}

getResults();