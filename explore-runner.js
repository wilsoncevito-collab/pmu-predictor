import fs from 'fs';

// Lire le fichier JSON
const rawData = fs.readFileSync('donnees_courses.json', 'utf8');
const data = JSON.parse(rawData);

// Fonction pour trouver le premier runner
function findFirstRunner(obj, path = '') {
    if (!obj || typeof obj !== 'object') return null;
    
    if (Array.isArray(obj)) {
        for (let i = 0; i < obj.length; i++) {
            const result = findFirstRunner(obj[i], `${path}[${i}]`);
            if (result) return result;
        }
        return null;
    }
    
    // Si c'est un objet avec runners, prendre le premier
    if (obj.runners && Array.isArray(obj.runners) && obj.runners.length > 0) {
        return {
            runner: obj.runners[0],
            path: `${path}.runners[0]`,
            raceNo: obj.raceNo || obj.no || '',
            date: obj.raceDate || obj.date || '',
            venue: obj.venueCode || obj.venue || ''
        };
    }
    
    // Parcourir les propriétés
    for (const key of Object.keys(obj)) {
        const result = findFirstRunner(obj[key], `${path}.${key}`);
        if (result) return result;
    }
    
    return null;
}

// Fonction pour explorer récursivement un objet et afficher toutes les clés
function exploreObject(obj, prefix = '', maxDepth = 3) {
    if (!obj || typeof obj !== 'object' || maxDepth === 0) {
        if (typeof obj === 'string' && obj.length > 50) {
            console.log(`${prefix} "${obj.substring(0, 50)}..."`);
        } else {
            console.log(`${prefix} ${obj}`);
        }
        return;
    }
    
    if (Array.isArray(obj)) {
        console.log(`${prefix} [Tableau de ${obj.length} éléments]`);
        if (obj.length > 0 && typeof obj[0] === 'object') {
            exploreObject(obj[0], `${prefix}[0]`, maxDepth - 1);
        }
        return;
    }
    
    const keys = Object.keys(obj);
    console.log(`${prefix} { ${keys.join(', ')} }`);
    
    // Afficher les 10 premières propriétés importantes
    const importantKeys = keys.filter(k => 
        !k.startsWith('_') && 
        !['id', 'status', 'lastUpdateTime'].includes(k)
    );
    
    for (const key of importantKeys.slice(0, 10)) {
        const value = obj[key];
        if (value && typeof value === 'object') {
            console.log(`${prefix}  ${key}:`);
            exploreObject(value, `${prefix}    `, maxDepth - 1);
        } else if (typeof value === 'string' && value.length > 0) {
            const display = value.length > 30 ? value.substring(0, 30) + '...' : value;
            console.log(`${prefix}  ${key}: "${display}"`);
        } else if (typeof value === 'number') {
            console.log(`${prefix}  ${key}: ${value}`);
        }
    }
}

// Trouver un runner
console.log('🔍 Recherche d\'un runner dans les données...\n');
const result = findFirstRunner(data);

if (result) {
    console.log(`✅ Runner trouvé dans la course ${result.raceNo} (${result.date} - ${result.venue})`);
    console.log(`   Chemin: ${result.path}\n`);
    console.log('=== STRUCTURE COMPLÈTE DU RUNNER ===');
    exploreObject(result.runner, '', 2);
    
    // Sauvegarder le runner complet
    fs.writeFileSync('runner_complet.json', JSON.stringify(result.runner, null, 2));
    console.log('\n📁 Runner complet sauvegardé dans "runner_complet.json"');
    console.log('   Ouvrez ce fichier pour voir toutes les propriétés.');
    
    // Afficher les propriétés qui pourraient contenir le nom
    console.log('\n=== RECHERCHE DU NOM DU CHEVAL ===');
    const allKeys = [];
    function collectKeys(obj, prefix = '') {
        if (!obj || typeof obj !== 'object') return;
        if (Array.isArray(obj)) {
            if (obj.length > 0) collectKeys(obj[0], `${prefix}[0]`);
            return;
        }
        for (const key of Object.keys(obj)) {
            const fullKey = prefix ? `${prefix}.${key}` : key;
            allKeys.push(fullKey);
            if (obj[key] && typeof obj[key] === 'object' && !Array.isArray(obj[key])) {
                collectKeys(obj[key], fullKey);
            }
        }
    }
    collectKeys(result.runner);
    
    const nameKeys = allKeys.filter(k => 
        k.toLowerCase().includes('name') || 
        k.toLowerCase().includes('horse') ||
        k.toLowerCase().includes('nom')
    );
    console.log('Clés pouvant contenir le nom:');
    for (const key of nameKeys) {
        const value = evalKey(result.runner, key);
        console.log(`  ${key}: "${value}"`);
    }
    
    // Afficher les propriétés qui pourraient contenir le nom du trainer
    console.log('\nClés pouvant contenir le nom du trainer:');
    const trainerKeys = allKeys.filter(k => 
        k.toLowerCase().includes('trainer') || 
        k.toLowerCase().includes('entraineur')
    );
    for (const key of trainerKeys) {
        const value = evalKey(result.runner, key);
        console.log(`  ${key}: "${value}"`);
    }
    
} else {
    console.log('❌ Aucun runner trouvé dans les données');
}

function evalKey(obj, path) {
    const parts = path.split('.');
    let current = obj;
    for (const part of parts) {
        if (current === null || current === undefined) return '';
        if (typeof current === 'object' && current[part] !== undefined) {
            current = current[part];
        } else {
            return '';
        }
    }
    if (typeof current === 'object' && current !== null) {
        return JSON.stringify(current).substring(0, 100);
    }
    return String(current);
}