import { HorseRacingAPI } from 'hkjc-api';
import fs from 'fs';

async function getResultsDirect() {
    const horseAPI = new HorseRacingAPI();
    
    try {
        console.log('🔍 Récupération des résultats via GraphQL...');
        
        // Récupérer les meetings actifs
        const meetings = await horseAPI.getActiveMeetings();
        console.log(`📋 ${meetings.length} meetings actifs`);
        
        let allResults = [];
        
        for (const meeting of meetings) {
            console.log(`\n📅 Meeting: ${meeting.venueCode} - ${meeting.raceDate}`);
            
            // Récupérer les courses pour ce meeting
            const races = await horseAPI.getRaces({
                meetingId: meeting.id,
                raceDate: meeting.raceDate,
                venueCode: meeting.venueCode
            });
            
            // Alternative: utiliser getAllRaces() et filtrer
            if (!races || races.length === 0) {
                console.log('   ⚠️ Utilisation de getAllRaces()...');
                const allRaces = await horseAPI.getAllRaces();
                for (const m of allRaces) {
                    if (m.venueCode === meeting.venueCode && m.raceDate === meeting.raceDate) {
                        for (const race of m.races || []) {
                            // Pour chaque course, essayer de récupérer les résultats via l'API
                            const result = await getRaceResultsFromAPI(horseAPI, race.raceNo);
                            if (result) {
                                allResults.push({
                                    venueCode: meeting.venueCode,
                                    raceDate: meeting.raceDate,
                                    raceNo: race.raceNo,
                                    result: result
                                });
                            }
                        }
                    }
                }
            }
        }
        
        // Sauvegarder les résultats
        if (allResults.length > 0) {
            fs.writeFileSync('resultats_courses.json', JSON.stringify(allResults, null, 2));
            console.log(`\n✅ Résultats sauvegardés dans "resultats_courses.json"`);
            console.log(`   ${allResults.length} courses traitées`);
        } else {
            console.log('\n⚠️ Aucun résultat récupéré');
            // Créer un fichier vide
            fs.writeFileSync('resultats_courses.json', JSON.stringify([]));
        }
        
    } catch (error) {
        console.error('Erreur:', error);
    }
}

async function getRaceResultsFromAPI(api, raceNo) {
    try {
        // Essayer différentes approches
        const result = await api.getRaceResult(raceNo);
        return result;
    } catch (e) {
        // Si getRaceResult n'existe pas, essayer avec les cotes
        try {
            const odds = await api.getRaceOdds(raceNo, ['WIN']);
            // Les résultats peuvent être dans les cotes
            return { odds: odds, runners: [] };
        } catch (e2) {
            return null;
        }
    }
}

getResultsDirect();