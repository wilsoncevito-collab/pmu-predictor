import { HorseRacingAPI } from 'hkjc-api';
import fs from 'fs';

async function getFavoritesCorrect() {
    const horseAPI = new HorseRacingAPI();
    
    try {
        console.log('🔍 Récupération des favoris...');
        
        // Récupérer toutes les courses
        const races = await horseAPI.getAllRaces();
        console.log(`📋 ${races?.length || 0} réunions trouvées`);
        
        let allResults = [];
        
        for (const meeting of races || []) {
            console.log(`\n📅 Meeting: ${meeting.venueCode} - ${meeting.raceDate}`);
            
            for (const race of meeting.races || []) {
                console.log(`   Course #${race.raceNo}: ${race.runners?.length || 0} partants`);
                
                try {
                    // Récupérer les cotes WIN
                    const odds = await horseAPI.getRaceOdds(race.raceNo, ['WIN']);
                    
                    let favoriteNo = null;
                    let favoriteOdds = null;
                    let favoriteName = null;
                    let isHotFavorite = false;
                    
                    // Chercher le favori dans la réponse
                    if (odds && odds.WIN && odds.WIN.length > 0) {
                        // Parcourir les cotes pour trouver le favori
                        for (const odd of odds.WIN) {
                            // Vérifier si c'est le favori
                            if (odd.hotFavourite === true) {
                                favoriteNo = odd.runnerNo || odd.runnerNumber || odd.no;
                                favoriteOdds = odd.oddsValue || odd.odds;
                                isHotFavorite = true;
                                break;
                            }
                        }
                        
                        // Si pas de hotFavourite, prendre la plus petite cote
                        if (!favoriteNo && odds.WIN.length > 0) {
                            let minOdds = Infinity;
                            for (const odd of odds.WIN) {
                                const currentOdds = parseFloat(odd.oddsValue || odd.odds || Infinity);
                                if (currentOdds < minOdds) {
                                    minOdds = currentOdds;
                                    favoriteNo = odd.runnerNo || odd.runnerNumber || odd.no;
                                    favoriteOdds = currentOdds;
                                }
                            }
                        }
                    }
                    
                    // Trouver le nom du cheval favori
                    if (favoriteNo) {
                        for (const runner of race.runners || []) {
                            if (String(runner.runnerNo || runner.no) === String(favoriteNo)) {
                                favoriteName = runner.horseName || runner.name || runner.name_en || '';
                                break;
                            }
                        }
                    }
                    
                    allResults.push({
                        venueCode: meeting.venueCode,
                        raceDate: meeting.raceDate,
                        raceNo: race.raceNo,
                        favoriteNumber: favoriteNo,
                        favoriteName: favoriteName,
                        favoriteOdds: favoriteOdds,
                        isHotFavorite: isHotFavorite,
                        totalRunners: race.runners?.length || 0
                    });
                    
                    console.log(`      Favori: #${favoriteNo} - ${favoriteName} (cote ${favoriteOdds})${isHotFavorite ? ' 🔥' : ''}`);
                    
                } catch (e) {
                    console.log(`      ⚠️ Erreur: ${e.message}`);
                    allResults.push({
                        venueCode: meeting.venueCode,
                        raceDate: meeting.raceDate,
                        raceNo: race.raceNo,
                        favoriteNumber: null,
                        favoriteName: null,
                        favoriteOdds: null,
                        isHotFavorite: false,
                        totalRunners: race.runners?.length || 0
                    });
                }
            }
        }
        
        // Sauvegarder les résultats
        fs.writeFileSync('resultats_courses.json', JSON.stringify(allResults, null, 2));
        console.log(`\n✅ Résultats sauvegardés dans "resultats_courses.json"`);
        
        // Compter les favoris trouvés
        const withFavorites = allResults.filter(r => r.favoriteNumber !== null);
        console.log(`   Favoris identifiés: ${withFavorites.length}/${allResults.length}`);
        
    } catch (error) {
        console.error('Erreur:', error);
    }
}

getFavoritesCorrect();