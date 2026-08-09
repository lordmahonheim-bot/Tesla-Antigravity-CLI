import re
import base64
import json

base64_path = '/home/lord-mahonheim/bifrost/tesla/OUTPUTS/Synergy/N1/arcanis_base64_assets.md'
html_out_path = '/home/lord-mahonheim/bifrost/tesla/Cluedo/manuel_cluedo.html'

def extract_base64():
    with open(base64_path, 'r') as f:
        content = f.read()
    
    assets = {}
    matches = re.finditer(r'## Asset: `(.*?)`\n.*?\n.*?\n.*?\n```text\n(.*?)\n```', content, re.DOTALL)
    for m in matches:
        name = m.group(1)
        data = m.group(2).strip()
        assets[name] = data
    return assets

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cluedo - Le Jeu des Grands Détectives</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Inter:wght@400;500;600&family=Playfair+Display:ital,wght@0,600;1,600&display=swap');

        :root {
            --bg-main: #0E1428;
            --bg-panel: rgba(20, 28, 50, 0.85);
            --gold: #C9A961;
            --gold-hover: #e0c279;
            --red-blood: #6b1d1d;
            --text-main: #f0ead6;
            --font-title: 'Cinzel', serif;
            --font-body: 'Inter', sans-serif;
            --font-story: 'Playfair Display', serif;
        }

        body {
            margin: 0;
            background-color: var(--bg-main);
            color: var(--text-main);
            font-family: var(--font-body);
            overflow-x: hidden;
            background-image: radial-gradient(circle at center, #1a2340 0%, #0E1428 100%);
            background-attachment: fixed;
        }

        /* Navbar */
        nav {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(14, 20, 40, 0.95);
            backdrop-filter: blur(10px);
            z-index: 1000;
            display: flex;
            justify-content: center;
            padding: 15px 0;
            border-bottom: 2px solid var(--gold);
        }
        
        .nav-links {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            justify-content: center;
        }

        .nav-btn {
            background: none;
            border: 1px solid transparent;
            color: var(--gold);
            font-family: var(--font-title);
            font-size: 1.1rem;
            cursor: pointer;
            padding: 5px 15px;
            transition: all 0.3s ease;
        }

        .nav-btn:hover, .nav-btn.active {
            border-bottom: 2px solid var(--gold);
            text-shadow: 0 0 10px rgba(201, 169, 97, 0.5);
        }

        /* Hero Section */
        .hero {
            height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding-top: 60px;
        }
        
        .hero h1 {
            font-family: var(--font-title);
            font-size: 5rem;
            color: var(--gold);
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 10px;
            text-shadow: 0 0 20px rgba(201, 169, 97, 0.3);
        }
        
        .hero h2 {
            font-family: var(--font-story);
            font-size: 2rem;
            margin-top: 10px;
            font-weight: normal;
        }
        
        .invitation {
            background: #f0ead6;
            color: #1a1a2e;
            padding: 30px;
            max-width: 600px;
            margin: 40px auto;
            border: 3px double #1a1a2e;
            font-family: var(--font-story);
            font-size: 1.2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            position: relative;
        }

        .cta-btn {
            background: var(--gold);
            color: #000;
            border: none;
            padding: 15px 30px;
            font-size: 1.2rem;
            font-family: var(--font-title);
            font-weight: bold;
            cursor: pointer;
            border-radius: 5px;
            transition: all 0.3s ease;
            text-decoration: none;
        }
        
        .cta-btn:hover {
            background: var(--gold-hover);
            box-shadow: 0 0 20px rgba(201, 169, 97, 0.6);
            transform: translateY(-2px);
        }

        /* Content Sections */
        .section-container {
            display: none;
            padding: 100px 20px 50px;
            max-width: 1200px;
            margin: 0 auto;
            min-height: calc(100vh - 150px);
            animation: fadeIn 0.5s ease-in-out;
        }

        .section-container.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        h2.section-title {
            font-family: var(--font-title);
            color: var(--gold);
            font-size: 2.5rem;
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 1px solid rgba(201, 169, 97, 0.3);
            padding-bottom: 10px;
        }

        /* Interactive Grid */
        .grid-3 {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
        }

        /* 3D Flip Cards for Suspects */
        .flip-card {
            background-color: transparent;
            height: 400px;
            perspective: 1000px;
            cursor: pointer;
        }
        .flip-card-inner {
            position: relative;
            width: 100%;
            height: 100%;
            text-align: center;
            transition: transform 0.8s;
            transform-style: preserve-3d;
        }
        .flip-card:hover .flip-card-inner {
            transform: rotateY(180deg);
        }
        .flip-card-front, .flip-card-back {
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.5);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 20px;
            box-sizing: border-box;
        }
        .flip-card-front {
            background: var(--bg-panel);
            border: 2px solid var(--gold);
        }
        .flip-card-back {
            background: var(--text-main);
            color: #1a1a2e;
            transform: rotateY(180deg);
            border: 2px solid var(--red-blood);
        }
        .flip-card-back p {
            font-size: 0.95rem;
            text-align: justify;
        }

        /* Accordions */
        .accordion {
            background: var(--bg-panel);
            color: var(--text-main);
            cursor: pointer;
            padding: 18px;
            width: 100%;
            text-align: left;
            border: 1px solid var(--gold);
            outline: none;
            transition: 0.4s;
            font-family: var(--font-title);
            font-size: 1.2rem;
            margin-top: 10px;
        }
        .accordion.active, .accordion:hover {
            background: rgba(201, 169, 97, 0.2);
        }
        .panel {
            padding: 0 18px;
            background-color: rgba(0, 0, 0, 0.3);
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.2s ease-out;
            border-left: 1px solid var(--gold);
            border-right: 1px solid var(--gold);
        }
        .panel p { margin: 15px 0; }

        /* Detective Sheet */
        .detective-sheet {
            background: #fff;
            color: #000;
            padding: 20px;
            border-radius: 5px;
            font-family: monospace;
            max-width: 800px;
            margin: 0 auto;
        }
        .sheet-table {
            width: 100%;
            border-collapse: collapse;
        }
        .sheet-table th, .sheet-table td {
            border: 1px solid #000;
            padding: 8px;
            text-align: center;
        }
        .sheet-table th:first-child, .sheet-table td:first-child {
            text-align: left;
            font-weight: bold;
        }
        .sheet-input {
            width: 30px;
            border: none;
            text-align: center;
            font-family: monospace;
            background: transparent;
        }

        /* Box Cover BG */
        .box-cover-bg {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: url('{{BOX_COVER}}');
            background-size: cover;
            background-position: center;
            opacity: 0.1;
            z-index: -1;
            pointer-events: none;
        }
        
        .clue-card {
            background: #f0ead6;
            color: #1a1a2e;
            border: 2px solid var(--gold);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            cursor: pointer;
            transition: transform 0.3s;
        }
        .clue-card:hover {
            transform: scale(1.05);
            box-shadow: 0 0 15px var(--gold);
        }
        
        .dice-container {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin: 40px 0;
        }
        .dice {
            width: 100px;
            height: 100px;
            background: white;
            color: black;
            font-size: 3rem;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.5);
            cursor: pointer;
            transition: transform 0.5s;
        }
        .dice.roll {
            animation: shake 0.5s;
        }
        @keyframes shake {
            0% { transform: rotate(0deg); }
            25% { transform: rotate(15deg); }
            50% { transform: rotate(0deg); }
            75% { transform: rotate(-15deg); }
            100% { transform: rotate(0deg); }
        }
        
        /* Modal */
        .modal {
            display: none;
            position: fixed;
            z-index: 2000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.8);
        }
        .modal-content {
            background-color: var(--bg-main);
            margin: 15% auto;
            padding: 30px;
            border: 2px solid var(--gold);
            width: 80%;
            max-width: 600px;
            text-align: center;
        }
        .close {
            color: var(--gold);
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="box-cover-bg"></div>
    <nav>
        <div class="nav-links">
            <button class="nav-btn active" onclick="showTab('tab-enquete')">L'Enquête</button>
            <button class="nav-btn" onclick="showTab('tab-dossier')">Le Dossier</button>
            <button class="nav-btn" onclick="showTab('tab-manoir')">Le Manoir</button>
            <button class="nav-btn" onclick="showTab('tab-protocole')">Le Protocole</button>
            <button class="nav-btn" onclick="showTab('tab-preuve')">La Preuve</button>
            <button class="nav-btn" onclick="showTab('tab-labo')">Le Laboratoire</button>
            <button class="nav-btn" onclick="showTab('tab-biblio')">La Bibliothèque</button>
            <button class="nav-btn" onclick="showTab('tab-academie')">L'Académie</button>
        </div>
    </nav>

    <!-- TAB: L'ENQUÊTE -->
    <div id="tab-enquete" class="section-container active">
        <div class="hero">
            <h1>CLUEDO</h1>
            <h2>Le jeu des grands détectives</h2>
            <p style="font-family: var(--font-title); color: var(--red-blood); font-size: 1.5rem; letter-spacing: 2px;">L'un d'eux est coupable : personne n'est innocent.</p>
            
            <div class="invitation">
                <p>« M. Mat Lenoir demande de lui faire l'honneur de votre compagnie pour un dîner privé dans son manoir historique Tudor. Hors d'œuvres servis au coucher du soleil, dîner servi à 20 h. Votre présence est d'ores et déjà confirmée. »</p>
            </div>
            
            <p style="font-size: 1.2rem; color: #aaa;">8+ | 2-6 joueurs | ~45 min | Hasbro © 2023</p>
            
            <button class="accordion" style="max-width: 800px; margin-top: 40px; text-align: center;">Ouvrir le dossier (La Nuit du Meurtre) ▼</button>
            <div class="panel" style="max-width: 800px; text-align: justify; font-family: var(--font-story);">
                <p>Six invités soigneusement sélectionnés arrivent au manoir Tudor, la demeure familiale de Mat Lenoir, dit le Macchabé, après avoir reçu une mystérieuse invitation. Pendant le dîner, Lenoir annonce son projet de construction d'un hôtel de luxe extravagant et démesuré, à l'endroit même d'un parc populaire de la ville. Tout le monde s'y oppose, mais Lenoir révèle ensuite qu'il a des informations pour tous les faire chanter et les forcer à l'aider. S'ils refusent, leurs secrets seront révélés. Peu de temps après, il s'excuse et les invités se dispersent pour digérer la nouvelle. Un cri retentit. Les invités découvrent Lenoir, assassiné.</p>
                <p style="text-align: center; color: var(--gold); font-size: 1.5rem;"><strong>C'est maintenant à vous d'élucider le mystère.</strong></p>
                <div style="text-align: center; font-size: 1.3rem; margin: 30px 0;">
                    <p><strong>QUI</strong> a tué Mat Lenoir ?</p>
                    <p>avec **QUELLE** arme ?</p>
                    <p>et **OÙ** ?</p>
                </div>
            </div>
        </div>
    </div>

    <!-- TAB: LE DOSSIER -->
    <div id="tab-dossier" class="section-container">
        <h2 class="section-title">Les Suspects</h2>
        <div class="grid-3">
            <div class="flip-card">
                <div class="flip-card-inner">
                    <div class="flip-card-front" style="color: #ff4d4d;">
                        <h1 style="font-size: 4rem; margin:0;">🎭</h1>
                        <h2>Mlle Rose</h2>
                        <p>Pion Rouge</p>
                    </div>
                    <div class="flip-card-back">
                        <h3>Mlle Rose</h3>
                        <p>Bourgeoise, à première vue. En réalité, c'est une journaliste d'investigation particulièrement intelligente. Écrivant sous le pseudonyme de « Cyan », elle a fait mettre des mafieux en prison et a causé la ruine de héros locaux. Personne n'est à l'abri de sa plume, vu que personne ne sait qui elle est. À l'exception de Mat Lenoir, qui a justement besoin d'une bonne critique sur son nouvel hôtel.</p>
                    </div>
                </div>
            </div>
            <div class="flip-card">
                <div class="flip-card-inner">
                    <div class="flip-card-front" style="color: #ffd633;">
                        <h1 style="font-size: 4rem; margin:0;">🎭</h1>
                        <h2>Col. Moutarde</h2>
                        <p>Pion Jaune</p>
                    </div>
                    <div class="flip-card-back">
                        <h3>Col. Moutarde</h3>
                        <p>Héros de guerre décoré, avec de nombreux récits de batailles passées et d'évasions miraculeuses. C'est un homme d'action qui a l'expérience nécessaire pour agir. En tant que membre respecté de l'armée, sa crédibilité pourrait facilement faire pencher l'opinion publique en faveur de Lenoir, surtout si cela signifie que personne ne découvre qu'en fait, il n'a jamais combattu pendant la bataille pour laquelle il a reçu sa médaille la plus prestigieuse.</p>
                    </div>
                </div>
            </div>
            <div class="flip-card">
                <div class="flip-card-inner">
                    <div class="flip-card-front" style="color: #33cc33;">
                        <h1 style="font-size: 4rem; margin:0;">🎭</h1>
                        <h2>M. le Maire Olive</h2>
                        <p>Pion Vert</p>
                    </div>
                    <div class="flip-card-back">
                        <h3>M. le Maire Olive</h3>
                        <p>Le sympathique maire du Comté Coloris qui a toujours un bon mot à dire. Il se prépare pour sa réélection, mais cela ne l'inquiète pas : même ses adversaires ont du mal à le détester. Il n'y a qu'un seul point qui peut ternir son dossier impeccable : un don reçu d'une importante famille de criminels qui lui a permis de sauver sa campagne. Lenoir lui a assuré que personne ne le découvrirait... tant qu'il contribue à modifier la zone du parc où Lenoir a l'intention de faire construire son hôtel.</p>
                    </div>
                </div>
            </div>
            <div class="flip-card">
                <div class="flip-card-inner">
                    <div class="flip-card-front" style="color: #3399ff;">
                        <h1 style="font-size: 4rem; margin:0;">🎭</h1>
                        <h2>Maître Pervenche</h2>
                        <p>Pion Bleu</p>
                    </div>
                    <div class="flip-card-back">
                        <h3>Maître Pervenche</h3>
                        <p>Avocate tenace, elle sait exactement comment gérer une salle, que ce soit dans un tribunal ou non. Son succès lui a apporté un statut important qu'elle n'hésite pas à afficher. Lenoir sait que rien ne peut l'arrêter quand il s'agit de gagner un procès, pas même l'utilisation de faux témoins, un fait qu'il serait ravi de révéler si elle refuse de le représenter dans les négociations pour son hôtel.</p>
                    </div>
                </div>
            </div>
            <div class="flip-card">
                <div class="flip-card-inner">
                    <div class="flip-card-front" style="color: #b366ff;">
                        <h1 style="font-size: 4rem; margin:0;">🎭</h1>
                        <h2>Prof. Violet</h2>
                        <p>Pion Violet</p>
                    </div>
                    <div class="flip-card-back">
                        <h3>Prof. Violet</h3>
                        <p>Un professeur d'antiquités extrêmement perspicace. Son incroyable attention aux détails l'aide à identifier les contrefaçons, et parfois même à en fabriquer. Seul Lenoir sait que sa contrefaçon la plus convaincante est le doctorat de Violet, trônant fièrement au-dessus de son bureau. Avec une bonne motivation, le professeur pourrait probablement fabriquer n'importe quelle contrefaçon, même un acte de propriété prouvant que Lenoir a des droits sur le parc où il a l'intention de construire son hôtel.</p>
                    </div>
                </div>
            </div>
            <div class="flip-card">
                <div class="flip-card-inner">
                    <div class="flip-card-front" style="color: #ffffff;">
                        <h1 style="font-size: 4rem; margin:0;">🎭</h1>
                        <h2>Cheffe Leblanc</h2>
                        <p>Pion Blanc</p>
                    </div>
                    <div class="flip-card-back">
                        <h3>Cheffe Leblanc</h3>
                        <p>Cheffe prometteuse et ambitieuse avec de nouvelles idées. Elle dirige les cuisines de Lenoir depuis des années, mais elle trouve que son menu peu original limite sa créativité et elle rêve d'ouvrir son propre restaurant. Son plan repose sur son talent, sa persévérance... et l'argent qu'elle a soutiré à Mat Lenoir, mais celui-ci le sait depuis le début. Deux choix s'offrent à elle : gérer ingratement le restaurant de l'hôtel de Lenoir, ou faire face aux accusations.</p>
                    </div>
                </div>
            </div>
        </div>
        
        <h2 class="section-title" style="margin-top: 60px;">Les Armes</h2>
        <div class="grid-3" style="text-align: center;">
            <div class="clue-card" onclick="alert('Le Chandelier en bronze massif plaqué or 24 carats.')">
                <h1 style="font-size: 3rem; margin: 0;">🕯️</h1>
                <h3>Chandelier</h3>
            </div>
            <div class="clue-card" onclick="alert('Outil de plomberie en acier forgé de 30 cm.')">
                <h1 style="font-size: 3rem; margin: 0;">🔧</h1>
                <h3>Clé anglaise</h3>
            </div>
            <div class="clue-card" onclick="alert('Corde de chanvre tressé de marine de 2 mètres.')">
                <h1 style="font-size: 3rem; margin: 0;">🪢</h1>
                <h3>Corde</h3>
            </div>
            <div class="clue-card" onclick="alert('Conduit de plomberie lourd en plomb gris mat.')">
                <h1 style="font-size: 3rem; margin: 0;">🏏</h1>
                <h3>Barre de fer</h3>
            </div>
            <div class="clue-card" onclick="alert('Arme de poing de collection à barillet 6 coups.')">
                <h1 style="font-size: 3rem; margin: 0;">🔫</h1>
                <h3>Révolver</h3>
            </div>
            <div class="clue-card" onclick="alert('Lame en acier damassé de 15 cm avec garde ciselée.')">
                <h1 style="font-size: 3rem; margin: 0;">🗡️</h1>
                <h3>Poignard</h3>
            </div>
        </div>
    </div>

    <!-- TAB: LE MANOIR -->
    <div id="tab-manoir" class="section-container">
        <h2 class="section-title">Les Pièces du Manoir</h2>
        <div class="grid-3">
            <div class="clue-card"><h3>🛋️ Salon (Passage vers Jardin)</h3><p>L'air y est lourd, saturé de tabac froid.</p></div>
            <div class="clue-card"><h3>🍳 Cuisine (Passage vers Bureau)</h3><p>Une lumière blafarde se reflète sur le marbre blanc.</p></div>
            <div class="clue-card"><h3>🎱 Salle de billard</h3><p>Le pas est étouffé par les tapis d'Orient.</p></div>
            <div class="clue-card"><h3>🌿 Jardin d'hiver (Passage vers Salon)</h3><p>La pluie frappe frénétiquement les vitraux gothiques.</p></div>
            <div class="clue-card"><h3>🍽️ Salle à manger</h3><p>C'est ici que le piège s'est refermé.</p></div>
            <div class="clue-card"><h3>📚 Bibliothèque</h3><p>Un silence de cathédrale, lourd des secrets de tomes anciens.</p></div>
            <div class="clue-card"><h3>💼 Bureau (Passage vers Cuisine)</h3><p>La froideur du pouvoir et de la manipulation.</p></div>
            <div class="clue-card"><h3>🚪 Entrée</h3><p>Le grand escalier double plonge vers vous.</p></div>
            <div class="clue-card"><h3>🎉 Salle de réception</h3><p>C'est ici que le cri strident a déchiré la nuit.</p></div>
        </div>
    </div>

    <!-- TAB: LE PROTOCOLE -->
    <div id="tab-protocole" class="section-container">
        <h2 class="section-title">Mise en place</h2>
        <button class="accordion">Étape 1. Les Pions</button>
        <div class="panel"><p>Placez les six pions sur leurs cases de couleur correspondantes du plateau de jeu. Tous les pions doivent s'y trouver, même s'il y a moins de 6 joueurs. Choisissez votre personnage.</p></div>
        <button class="accordion">Étape 2. Les Armes</button>
        <div class="panel"><p>Placez aléatoirement chaque arme dans une pièce différente.</p></div>
        <button class="accordion">Étape 3. Les Indices</button>
        <div class="panel"><p>Séparez les 29 cartes Indice des autres cartes. Mélangez la pile de cartes Indice et placez-la face cachée à côté du plateau.</p></div>
        <button class="accordion">Étape 4 & 5. L'Étui Confidentiel</button>
        <div class="panel"><p>Séparez les autres cartes en 3 piles : personnages, armes et pièces. Mélangez chaque pile. Prenez la carte du dessus de chaque pile et glissez-la discrètement dans l'étui confidentiel sans que personne ne la voie. C'est le mystère que vous allez devoir résoudre !</p></div>
        <button class="accordion">Étape 6 & 7. Distribution</button>
        <div class="panel"><p>Mélangez les cartes restantes, puis distribuez-les toutes aux joueurs. Détachez une feuille du carnet de détective pour chaque joueur.</p></div>
        <button class="accordion">Étape 8. Cochez !</button>
        <div class="panel"><p>Regardez vos cartes en secret et cochez les suspects, les armes et les pièces sur votre feuille. Aucun d'eux ne peut être dans l'étui confidentiel ! Gardez votre feuille et vos cartes secrètes.</p></div>

        <h2 class="section-title" style="margin-top: 50px;">Place au Jeu</h2>
        <button class="accordion">Action 1 — Déplacez votre pion</button>
        <div class="panel">
            <p>Lancez les dés. Vous pouvez vous déplacer au maximum du nombre de cases indiqué par le lancer de dés. (La loupe rouge compte comme un 1.) Si vous entrez dans une pièce, émettez une hypothèse.</p>
            <p><strong>Cartes Indice (icône loupe 🔍) :</strong> Si vous avez obtenu l'icône de loupe, piochez une carte Indice, lisez-la à haute voix et suivez ses instructions. Remettez-la ensuite au-dessous de la pile.</p>
        </div>
        <button class="accordion">Action 2 — Émettez une hypothèse</button>
        <div class="panel">
            <p>Si vous entrez dans une pièce, dites : « Est-ce (un personnage), avec (une arme), dans (la pièce où vous êtes) ».</p>
            <p>Déplacez le pion suspect et l'arme dans la pièce. Le joueur situé à votre gauche vous montre secrètement une des cartes incluses dans votre hypothèse, s'il en a une. Cochez la carte qu'on vous a montrée sur votre feuille de détective. Vous savez qu'elle n'est pas dans l'étui.</p>
        </div>
        <div class="invitation" style="border-color: var(--red-blood); margin-top: 30px;">
            <h3 style="color: var(--red-blood); text-align: center;">COMMENT GAGNER (L'Accusation Finale)</h3>
            <p>Dès que vous pensez avoir résolu le mystère, portez une accusation ! Vous ne pouvez porter qu'une seule accusation par partie.</p>
            <p>1. Dites « J'accuse (un personnage), avec (une arme), dans (une pièce) ».</p>
            <p>2. Regardez discrètement dans l'étui confidentiel.</p>
            <p style="text-align: center; font-weight: bold; font-size: 1.4rem;">Si c'est exact : Vous gagnez !<br>Si c'est faux : Vous êtes éliminé !</p>
        </div>
    </div>

    <!-- TAB: LA PREUVE (INDICES & FEUILLE) -->
    <div id="tab-preuve" class="section-container">
        <h2 class="section-title">Feuille de Détective Interactive</h2>
        <div class="detective-sheet">
            <table class="sheet-table" id="detectiveTable">
                <tr>
                    <th>CLUEDO</th>
                    <th><input type="text" class="sheet-input" placeholder="J1"></th>
                    <th><input type="text" class="sheet-input" placeholder="J2"></th>
                    <th><input type="text" class="sheet-input" placeholder="J3"></th>
                    <th><input type="text" class="sheet-input" placeholder="J4"></th>
                    <th><input type="text" class="sheet-input" placeholder="J5"></th>
                </tr>
                <!-- SUSPECTS -->
                <tr style="background: #e0e0e0;"><td colspan="6" style="text-align: left; font-weight: bold;">QUI ? (Suspects)</td></tr>
                <tr><td>Mlle Rose</td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td></tr>
                <tr><td>Col. Moutarde</td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td></tr>
                <tr><td>M. le Maire Olive</td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td></tr>
                <tr><td>Maître Pervenche</td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td></tr>
                <tr><td>Prof. Violet</td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td></tr>
                <tr><td>Cheffe Leblanc</td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td></tr>
                <!-- ARMES -->
                <tr style="background: #e0e0e0;"><td colspan="6" style="text-align: left; font-weight: bold;">AVEC QUOI ? (Armes)</td></tr>
                <tr><td>Chandelier</td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td></tr>
                <tr><td>Clé anglaise</td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td></tr>
                <tr><td>Corde</td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td></tr>
                <tr><td>Barre de fer</td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td></tr>
                <tr><td>Révolver</td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td></tr>
                <tr><td>Poignard</td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td></tr>
                <!-- PIECES -->
                <tr style="background: #e0e0e0;"><td colspan="6" style="text-align: left; font-weight: bold;">OÙ ? (Pièces)</td></tr>
                <tr><td>Salon</td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td></tr>
                <tr><td>Cuisine</td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td></tr>
                <tr><td>Salle de billard</td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td></tr>
                <tr><td>Jardin d'hiver</td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td></tr>
                <tr><td>Salle à manger</td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td></tr>
                <tr><td>Bibliothèque</td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td></tr>
                <tr><td>Bureau</td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td></tr>
                <tr><td>Entrée</td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td></tr>
                <tr><td>Salle de réception</td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td><td onclick="toggleCell(this)"></td></tr>
            </table>
            <button onclick="resetSheet()" style="margin-top: 15px; padding: 5px 15px; cursor: pointer;">Réinitialiser la feuille</button>
        </div>
    </div>

    <!-- TAB: LE LABORATOIRE -->
    <div id="tab-labo" class="section-container">
        <h2 class="section-title">Laboratoire & Simulateur</h2>
        
        <div style="text-align: center;">
            <h3>Lanceur de Dés 3D</h3>
            <div class="dice-container">
                <div class="dice" id="dice1" onclick="rollDice()">⚀</div>
                <div class="dice" id="dice2" onclick="rollDice()">🔍</div>
            </div>
            <p id="dice-result">Cliquez sur les dés pour les lancer !</p>
        </div>
    </div>
    
    <!-- TAB: LA BIBLIOTHEQUE -->
    <div id="tab-biblio" class="section-container">
        <h2 class="section-title">FAQ et Situations Spéciales</h2>
        <button class="accordion">Puis-je émettre une hypothèse sans être dans une pièce ?</button>
        <div class="panel"><p>Non, vous devez être dans une pièce.</p></div>
        <button class="accordion">Que se passe-t-il si mon pion est déplacé par l'hypothèse d'un autre joueur ?</button>
        <div class="panel"><p>Vous êtes maintenant dans cette pièce. À votre prochain tour, vous pouvez y émettre une hypothèse ou la quitter.</p></div>
        <button class="accordion">Puis-je nommer une pièce différente de celle où je me trouve ?</button>
        <div class="panel"><p>Non, pour une hypothèse vous devez nommer la pièce où vous êtes. Pour une accusation, vous pouvez nommer n'importe quelle pièce.</p></div>
        <button class="accordion">Si je me trompe lors de mon Accusation Finale, suis-je totalement éliminé ?</button>
        <div class="panel"><p>Vous êtes éliminé de la course à la victoire : vous ne pouvez plus vous déplacer, ni émettre d'hypothèse. Cependant, vous devez garder vos cartes et continuer à les montrer secrètement aux autres enquêteurs. Vous devenez un simple "témoin".</p></div>
    </div>

    <!-- TAB: L'ACADEMIE -->
    <div id="tab-academie" class="section-container">
        <h2 class="section-title">L'Académie des Détectives</h2>
        <div class="invitation">
            <h3 style="color: var(--red-blood);">L'Art de la Déduction</h3>
            <p><strong>Le Théorème de l'Intersection :</strong> Ne regardez pas seulement ce que les autres vous montrent, observez ce qu'ils montrent aux autres.</p>
            <p><strong>L'Interrogatoire Ciblé :</strong> Pour forcer la main d'un adversaire, formulez une hypothèse en utilisant deux cartes que vous possédez déjà et une que vous cherchez à valider.</p>
        </div>
        <div class="invitation">
            <h3 style="color: var(--red-blood);">Techniques de Bluff</h3>
            <p><strong>L'Auto-Accusation :</strong> Formulez une hypothèse impliquant le personnage que vous jouez et l'arme que vous détenez. Vos adversaires seront déconcertés.</p>
            <p><strong>La Rétention d'Information :</strong> Si vous possédez plusieurs cartes demandées dans une hypothèse, montrez toujours la même.</p>
        </div>
    </div>

    <script>
        function showTab(tabId) {
            document.querySelectorAll('.section-container').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
            
            document.getElementById(tabId).classList.add('active');
            event.target.classList.add('active');
            window.scrollTo(0, 0);
        }

        // Accordion functionality
        var acc = document.getElementsByClassName("accordion");
        for (var i = 0; i < acc.length; i++) {
            acc[i].addEventListener("click", function() {
                this.classList.toggle("active");
                var panel = this.nextElementSibling;
                if (panel.style.maxHeight) {
                    panel.style.maxHeight = null;
                } else {
                    panel.style.maxHeight = panel.scrollHeight + "px";
                } 
            });
        }

        // Detective Sheet
        function toggleCell(cell) {
            if(cell.innerText === "") cell.innerText = "✗";
            else if(cell.innerText === "✗") cell.innerText = "✓";
            else cell.innerText = "";
        }
        
        function resetSheet() {
            var cells = document.querySelectorAll("#detectiveTable td[onclick]");
            cells.forEach(c => c.innerText = "");
        }

        // Dice Roller
        function rollDice() {
            const faces = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'];
            const d1 = document.getElementById('dice1');
            const d2 = document.getElementById('dice2');
            
            d1.classList.add('roll');
            d2.classList.add('roll');
            
            setTimeout(() => {
                let v1 = Math.floor(Math.random() * 6);
                let v2 = Math.floor(Math.random() * 6);
                
                d1.innerText = faces[v1];
                d2.innerText = (v2 === 5) ? '🔍' : faces[v2];
                
                let sum = (v1 + 1) + (v2 === 5 ? 1 : v2 + 1);
                let text = "Vous pouvez avancer de " + sum + " cases.";
                if (v2 === 5) text += " N'oubliez pas de piocher une carte Indice !";
                
                document.getElementById('dice-result').innerText = text;
                
                d1.classList.remove('roll');
                d2.classList.remove('roll');
            }, 500);
        }
    </script>
</body>
</html>
"""

def build():
    assets = extract_base64()
    box_cover = assets.get('Documentation/MANUS/cluedo2023_documentation/cluedo2023/assets/box_cover.jpg', '')
    
    html = HTML_TEMPLATE.replace('{{BOX_COVER}}', box_cover)
    
    with open(html_out_path, 'w') as f:
        f.write(html)
    print(f"Successfully wrote HTML to {html_out_path}")

if __name__ == '__main__':
    build()
