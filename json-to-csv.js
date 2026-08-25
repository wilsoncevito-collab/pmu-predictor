import fs from 'fs';

// Lire les fichiers JSON
const racesData = JSON.parse(fs.readFileSync('donnees_courses.json', 'utf8'));
const oddsData = JSON.parse(fs.readFileSync('cotes_courses.json', 'utf8'));

// Fonction pour trouver les cotes d'un cheval dans une course
function findOddsForRunner(oddsList, raceNo, runnerNo) {
    const raceOdds = oddsList.find(o => {
        return String(o.raceNo) === String(raceNo);
    });
    
    if (!raceOdds || !raceOdds.odds) return { win: null, pla: null };
    
    let winOdds = null;
    let plaOdds = null;
    
    if (raceOdds.odds.WIN && Array.isArray(raceOdds.odds.WIN)) {
        const found = raceOdds.odds.WIN.find(w => String(w.runnerNo) === String(runnerNo));
        if (found) winOdds = found.odds;
    }
    
    if (raceOdds.odds.PLA && Array.isArray(raceOdds.odds.PLA)) {
        const found = raceOdds.odds.PLA.find(p => String(p.runnerNo) === String(runnerNo));
        if (found) plaOdds = found.odds;
    }
    
    return { win: winOdds, pla: plaOdds };
}

// Fonction pour extraire les données d'un runner avec les bons noms de champs
function extractRunnerData(runner, raceNo, date, venue, oddsData) {
    // Utiliser les vrais noms de champs trouvés dans la structure
    const horseName = runner.horseName || runner.name || runner.runnerName || '';
    const runnerNo = runner.runnerNo || runner.number || '';
    const draw = runner.draw || runner.drawNo || runner.barrier || '';
    const weight = runner.weight || runner.imposedWeight || runner.carryWeight || '';
    const rating = runner.internationalRating || runner.rating || runner.currentRating || '';
    const age = runner.age || runner.horseAge || '';
    const sex = runner.sex || runner.gender || runner.horseSex || '';
    const trainer = runner.trainerName || runner.trainer || runner.trainerNameEn || '';
    const jockey = runner.jockeyName || runner.jockey || runner.rider || runner.jockeyNameEn || '';
    
    // Récupérer les cotes
    const odds = findOddsForRunner(oddsData, raceNo, runnerNo);
    
    return {
        date: date || '',
        venue: venue || '',
        raceNo: raceNo || '',
        horseName: horseName,
        runnerNo: runnerNo,
        draw: draw,
        weight: weight,
        rating: rating,
        age: age,
        sex: sex,
        trainer: trainer,
        jockey: jockey,
        winOdds: odds.win || '',
        placeOdds: odds.pla || ''
    };
}

// Construire le CSV
let csvLines = [];
let headers = [
    'date','venue','race_no','horse_name','horse_number',
    'draw','weight','rating','age','sex',
    'trainer','jockey','win_odds','place_odds'
];
csvLines.push(headers.join(','));

console.log('🔍 Extraction des données...');

// Parcourir toutes les courses
const meetings = racesData.races || [];
let totalRunners = 0;
let debugCount = 0;

for (const meeting of meetings) {
    const date = meeting.raceDate || '';
    const venue = meeting.venueCode || '';
    
    // Vérifier si meeting.races existe
    const races = meeting.races || [];
    
    for (const race of races) {
        const raceNo = race.raceNo || '';
        const runners = race.runners || [];
        
        for (const runner of runners) {
            const data = extractRunnerData(runner, raceNo, date, venue, oddsData);
            
            // Debug : afficher les 5 premiers chevaux
            if (debugCount < 5 && data.horseName) {
                console.log(`  🐴 Cheval #${debugCount + 1}: ${data.horseName} (Rating: ${data.rating}, Cote: ${data.winOdds})`);
                debugCount++;
            }
            
            // Ne pas inclure les lignes vides
            if (data.horseName || data.runnerNo) {
                const row = [
                    data.date,
                    data.venue,
                    data.raceNo,
                    `"${data.horseName}"`,
                    data.runnerNo,
                    data.draw,
                    data.weight,
                    data.rating,
                    data.age,
                    data.sex,
                    `"${data.trainer}"`,
                    `"${data.jockey}"`,
                    data.winOdds,
                    data.placeOdds
                ];
                csvLines.push(row.join(','));
                totalRunners++;
            }
        }
    }
}

// Sauvegarder le CSV
fs.writeFileSync('courses_data.csv', csvLines.join('\n'));
console.log(`\n✅ CSV créé avec ${totalRunners} lignes (chevaux)`);
console.log(`📁 Fichier : courses_data.csv`);

// Afficher un aperçu
console.log('\n--- APERÇU DES 5 PREMIÈRES LIGNES ---');
for (let i = 0; i < Math.min(6, csvLines.length); i++) {
    console.log(csvLines[i]);
}

console.log('\n✨ Félicitations ! Vos données sont maintenant prêtes pour l\'analyse.');