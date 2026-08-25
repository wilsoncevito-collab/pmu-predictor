import { HorseRacingAPI } from 'hkjc-api';

async function testResults() {
    const horseAPI = new HorseRacingAPI();
    
    try {
        console.log('🔍 Test de récupération des résultats...');
        
        // Vérifier les méthodes disponibles
        console.log('Méthodes disponibles sur horseAPI:');
        console.log(Object.getOwnPropertyNames(Object.getPrototypeOf(horseAPI)));
        
        // Essayer de récupérer les courses
        const races = await horseAPI.getAllRaces();
        console.log(`\n📋 ${races?.length || 0} réunions trouvées`);
        
        if (races && races.length > 0) {
            const firstMeeting = races[0];
            if (firstMeeting.races && firstMeeting.races.length > 0) {
                const firstRace = firstMeeting.races[0];
                console.log(`\n🏇 Première course: #${firstRace.raceNo}`);
                console.log(`   Partants: ${firstRace.runners?.length || 0}`);
                
                // Essayer différentes méthodes pour récupérer les résultats
                try {
                    // Méthode 1: getRaceResult
                    console.log('\n📊 Essai getRaceResult...');
                    const result1 = await horseAPI.getRaceResult(firstRace.raceNo);
                    console.log('   Résultat:', JSON.stringify(result1, null, 2).substring(0, 300));
                } catch (e) {
                    console.log('   ❌ getRaceResult échoue:', e.message);
                }
                
                try {
                    // Méthode 2: getRaceOdds avec plus d'options
                    console.log('\n📊 Essai getRaceOdds avec RESULT...');
                    const result2 = await horseAPI.getRaceOdds(firstRace.raceNo, ['WIN', 'PLA', 'RESULT']);
                    console.log('   Résultat:', JSON.stringify(result2, null, 2).substring(0, 300));
                } catch (e) {
                    console.log('   ❌ getRaceOdds avec RESULT échoue:', e.message);
                }
            }
        }
        
    } catch (error) {
        console.error('Erreur:', error);
    }
}

testResults();