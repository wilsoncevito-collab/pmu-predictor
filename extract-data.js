import fs from 'fs';

// Lire le fichier JSON
const rawData = fs.readFileSync('donnees_courses.json', 'utf8');
const data = JSON.parse(rawData);

// Fonction pour trouver récursivement toutes les courses
function findAllRaces(obj) {
    let races = [];
    
    if (!obj || typeof obj !== 'object') return races;
    
    if (Array.isArray(obj)) {
        for (const item of obj) {
            races = races.concat(findAllRaces(item));
        }
        return races;
    }
    
    // Vérifier si c'est une course (a des runners)
    if (obj.runners && Array.isArray(obj.runners) && obj.runners.length > 0) {
        const raceNo = obj.raceNo || obj.no || obj.raceNumber || '';
        const date = obj.raceDate || obj.date || obj.meetingDate || '';
        const venue = obj.venueCode || obj.venue || obj.meetingVenue || '';
        
        races.push({
            raceNo: raceNo,
            date: date,
            venue: venue,
            runners: obj.runners
        });
    }
    
    // Parcourir les propriétés de l'objet
    for (const key of Object.keys(obj)) {
        const value = obj[key];
        if (value && typeof value === 'object') {
            races = races.concat(findAllRaces(value));
        }
    }
    
    return races;
}

// Fonction pour extraire les données d'un runner
function extractRunnerData(runner, raceNo, date, venue) {
    // Extraire le nom du cheval
    let horseName = '';
    if (runner.name_en) horseName = runner.name_en;
    else if (runner.name_ch) horseName = runner.name_ch;
    else if (runner.horseName) horseName = runner.horseName;
    
    // Numéro du cheval
    const runnerNo = runner.no || runner.runnerNo || runner.number || runner.saddleClothNo || '';
    
    // Tirage (barrier draw)
    const draw = runner.barrierDrawNumber || runner.draw || runner.barrier || '';
    
    // Poids
    const weight = runner.handicapWeight || runner.weight || runner.imposedWeight || '';
    
    // Rating
    let rating = runner.internationalRating || runner.rating || runner.currentRating || '';
    if (rating === '' || rating === '-') rating = '';
    
    // Âge - peut être extrait du nom ou d'un champ
    let age = runner.age || runner.horseAge || '';
    
    // Sexe
    let sex = runner.sex || runner.gender || runner.horseSex || '';
    
    // Entraîneur
    let trainer = '';
    if (runner.trainer) {
        if (typeof runner.trainer === 'object') {
            trainer = runner.trainer.name_en || runner.trainer.name_ch || '';
        } else {
            trainer = runner.trainer;
        }
    }
    if (!trainer) trainer = runner.trainerName || '';
    
    // Jockey
    let jockey = '';
    if (runner.jockey) {
        if (typeof runner.jockey === 'object') {
            jockey = runner.jockey.name_en || runner.jockey.name_ch || '';
        } else {
            jockey = runner.jockey;
        }
    }
    if (!jockey) jockey = runner.jockeyName || runner.rider || '';
    
    // Cote (si disponible)
    const winOdds = runner.winOdds || runner.odds || '';
    
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
        winOdds: winOdds
    };
}

// Trouver toutes les courses
console.log('🔍 Recherche des courses dans le JSON...');
const foundRaces = findAllRaces(data);
console.log(`✅ ${foundRaces.length} courses trouvées\n`);

// Construire le CSV
let csvLines = [];
let headers = [
    'date','venue','race_no','horse_name','horse_number',
    'draw','weight','rating','age','sex',
    'trainer','jockey','win_odds'
];
csvLines.push(headers.join(','));

let totalRunners = 0;
let debugCount = 0;

for (const race of foundRaces) {
    const raceNo = race.raceNo;
    const date = race.date;
    const venue = race.venue;
    const runners = race.runners || [];
    
    console.log(`📋 Course ${raceNo} - ${runners.length} partants`);
    
    for (const runner of runners) {
        const data = extractRunnerData(runner, raceNo, date, venue);
        
        // Debug: afficher les 5 premiers chevaux
        if (debugCount < 5 && data.horseName) {
            console.log(`  🐴 Cheval ${data.runnerNo}: ${data.horseName} (Entr: ${data.trainer}, Jock: ${data.jockey})`);
            debugCount++;
        }
        
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
                data.winOdds
            ];
            csvLines.push(row.join(','));
            totalRunners++;
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