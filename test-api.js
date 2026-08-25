import { HorseRacingAPI } from 'hkjc-api';
import fs from 'fs';

async function testPipeline() {
    const horseAPI = new HorseRacingAPI();

    try {
        // 1. Récupérer les réunions actives
        console.log('--- Récupération des réunions actives ---');
        const activeMeetings = await horseAPI.getActiveMeetings();
        console.log(`Nombre de réunions actives : ${activeMeetings.length}`);
        if (activeMeetings.length > 0) {
            console.log('Première réunion :', activeMeetings[0].venueCode, activeMeetings[0].raceDate);
        }

        // 2. Récupérer toutes les courses du jour
        console.log('\n--- Récupération des courses du jour ---');
        const races = await horseAPI.getAllRaces();
        
        // 3. SAUVEGARDER TOUTES LES DONNÉES DANS UN FICHIER JSON
        const dataToSave = {
            date: new Date().toISOString(),
            activeMeetings: activeMeetings,
            races: races
        };
        
        fs.writeFileSync('donnees_courses.json', JSON.stringify(dataToSave, null, 2));
        console.log('✅ Données sauvegardées dans "donnees_courses.json"');
        
        if (races && races.length > 0) {
            const firstMeeting = races[0];
            console.log(`Réunion : ${firstMeeting.venueCode} - ${firstMeeting.raceDate}`);
            console.log(`Nombre de courses : ${firstMeeting.races?.length || 0}`);

            if (firstMeeting.races && firstMeeting.races.length > 0) {
                const firstRace = firstMeeting.races[0];
                console.log(`- Course #${firstRace.raceNo} : ${firstRace.runners?.length || 0} partants`);
                console.log('  Exemple de partant :', firstRace.runners[0]?.horseName);
            }
        }

        // 4. Récupérer les cotes pour toutes les courses
        console.log('\n--- Récupération des cotes pour toutes les courses ---');
        const allOdds = [];
        const meetings = races || [];
        for (const meeting of meetings) {
            if (meeting.races) {
                for (const race of meeting.races) {
                    try {
                        const odds = await horseAPI.getRaceOdds(race.raceNo, ['WIN', 'PLA']);
                        allOdds.push({
                            meetingCode: meeting.venueCode,
                            raceDate: meeting.raceDate,
                            raceNo: race.raceNo,
                            odds: odds
                        });
                        console.log(`  ✅ Cotes course #${race.raceNo} récupérées`);
                    } catch (e) {
                        console.log(`  ❌ Erreur course #${race.raceNo}:`, e.message);
                    }
                }
            }
        }
        
        // 5. Sauvegarder les cotes séparément
        fs.writeFileSync('cotes_courses.json', JSON.stringify(allOdds, null, 2));
        console.log(`\n✅ ${allOdds.length} séries de cotes sauvegardées dans "cotes_courses.json"`);

        // 6. Afficher un résumé des données
        console.log('\n--- RÉSUMÉ DES DONNÉES ---');
        let totalRunners = 0;
        for (const meeting of races || []) {
            for (const race of meeting.races || []) {
                totalRunners += race.runners?.length || 0;
            }
        }
        console.log(`Total chevaux analysés : ${totalRunners}`);
        console.log(`Nombre de courses : ${allOdds.length}`);

    } catch (error) {
        console.error('Erreur lors du test :', error);
    }
}

testPipeline();