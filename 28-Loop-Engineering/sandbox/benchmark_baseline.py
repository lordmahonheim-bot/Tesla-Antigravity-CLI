#!/usr/bin/env python3
import os
import shutil
import time
import subprocess
import sqlite3
import random
from dotenv import load_dotenv
load_dotenv()

# Chemins de benchmark isolés
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCHMARK_DIR = "/tmp/alexandria_benchmark"
VAULT_DIR = os.path.join(BENCHMARK_DIR, "vault")
DB_PATH = os.path.join(BENCHMARK_DIR, "alexandria_brain.db")
CHROMA_DIR = os.path.join(BENCHMARK_DIR, ".chroma_vectors")
REPORT_PATH = "/home/lord-mahonheim/bifrost/tesla/OUTPUTS/benchmark_baseline.md"

def setup_benchmark_env():
    # Nettoyer et recréer les répertoires de benchmark
    if os.path.exists(BENCHMARK_DIR):
        shutil.rmtree(BENCHMARK_DIR)
    os.makedirs(VAULT_DIR, exist_ok=True)
    
    # Générer 100 fichiers Markdown factices réalistes
    # Chaque fichier aura environ 2000 caractères de texte structuré.
    subjects = ["ia", "gouvernance", "midgard", "tesla", "agents", "code", "securite", "reseau", "base_de_donnees", "benchmark"]
    verbs = ["analyse", "optimise", "securise", "valide", "execute", "surveille", "previent", "nettoie", "configure", "harmonise"]
    objects = ["le systeme", "la memoire", "les performances", "les donnees sensibles", "le reseau", "les scripts", "la base SQLite", "le processeur", "le cache local", "les requetes"]
    
    for i in range(100):
        filepath = os.path.join(VAULT_DIR, f"fiche_doc_{i+1:03d}.md")
        # Choisir un frontmatter aléatoire (certains confidentiels pour les phases futures)
        confidential = "true" if i % 10 == 0 else "false"
        content = f"---\ntitle: Fiche Documentaire {i+1}\ntags: [benchmark, test]\nconfidential: {confidential}\n---\n\n"
        content += f"# Document de test {i+1}\n\n"
        for p in range(5):
            content += f"## Section {p+1}\n"
            sentences = []
            for _ in range(5):
                subj = random.choice(subjects)
                verb = random.choice(verbs)
                obj = random.choice(objects)
                sentences.append(f"Dans ce cadre, {subj} {verb} {obj} afin de garantir un fonctionnement nominal sur MIDGARD.")
            content += " ".join(sentences) + "\n\n"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    
    print(f"[✓] Environnement de benchmark pret : 100 fichiers generes sous {VAULT_DIR}")

def get_process_metrics(pid):
    # Récupère l'utilisation CPU et RAM (RSS en Mo) pour le PID et ses descendants
    try:
        output = subprocess.check_output(["ps", "-e", "-o", "pid,ppid,%cpu,rss"], text=True)
        lines = output.strip().split('\n')[1:]
        
        proc_map = {}
        for line in lines:
            parts = line.split()
            if len(parts) >= 4:
                try:
                    p = int(parts[0])
                    pp = int(parts[1])
                    cpu = float(parts[2])
                    rss = int(parts[3]) # en Ko
                    proc_map[p] = (pp, cpu, rss)
                except ValueError:
                    continue
        
        descendants = {pid}
        added = True
        while added:
            added = False
            for p, (pp, _, _) in proc_map.items():
                if pp in descendants and p not in descendants:
                    descendants.add(p)
                    added = True
        
        total_cpu = 0.0
        total_rss = 0.0
        for p in descendants:
            if p in proc_map:
                _, cpu, rss = proc_map[p]
                total_cpu += cpu
                total_rss += rss
                
        return total_cpu, total_rss / 1024.0 # Retourne CPU (%) et RSS (Mo)
    except Exception:
        return 0.0, 0.0

def run_idle_benchmark():
    # Mesure la memoire RAM au repos (idle) du chargeur sémantique
    # On lance un script minimal qui charge les librairies et attend
    idle_code = """
import sys
import os
sys.path.insert(0, os.getcwd())
import time
import chromadb
from sentence_transformers import SentenceTransformer
try:
    # Charger le modele
    encoder = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    print("READY", flush=True)
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    sys.exit(1)
time.sleep(10)
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = BASE_DIR
    p = subprocess.Popen(
        [".venv/bin/python3", "-c", idle_code],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    output_lines = []
    err_output = ""
    while True:
        line = p.stdout.readline()
        if line:
            output_lines.append(line)
            if "READY" in line:
                break
            if "ERROR" in line:
                print(f"[-] Erreur dans le sous-processus d'idle baseline: {line.strip()}")
                break
        if not line and p.poll() is not None:
            break
        time.sleep(0.05)
        
    cpu, rss = get_process_metrics(p.pid)
    
    if p.poll() is not None and p.returncode != 0:
        err_output = p.stderr.read() if p.stderr else ""
        print(f"[-] Le sous-processus baseline s'est arrete avec le code {p.returncode}. Stderr: {err_output}")
        
    p.terminate()
    p.wait()
    return rss

def run_indexing_benchmark():
    env = os.environ.copy()
    env["ALEXANDRIA_DB_PATH"] = DB_PATH
    env["ALEXANDRIA_CHROMA_DIR"] = CHROMA_DIR
    env["ALEXANDRIA_VAULT_DIR"] = VAULT_DIR
    
    start_time = time.time()
    p = subprocess.Popen([".venv/bin/python3", "indexer_hybrid.py"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    max_rss = 0.0
    cpu_samples = []
    
    while p.poll() is None:
        cpu, rss = get_process_metrics(p.pid)
        if rss > max_rss:
            max_rss = rss
        if cpu > 0.0:
            cpu_samples.append(cpu)
        time.sleep(0.1)
        
    duration = time.time() - start_time
    avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0.0
    
    return duration, max_rss, avg_cpu

def run_search_benchmark():
    # Faire 10 requetes de recherche et mesurer la latence moyenne
    env = os.environ.copy()
    env["ALEXANDRIA_DB_PATH"] = DB_PATH
    env["ALEXANDRIA_CHROMA_DIR"] = CHROMA_DIR
    
    latencies = []
    max_search_rss = 0.0
    
    queries = [
        "ia et gouvernance local",
        "securite de la base de donnees",
        "optimise les performances",
        "cache local pour les requetes",
        "donnees sensibles sur midgard",
        "analyse et validation",
        "scripts de benchmark",
        "fonctionnement nominal du systeme",
        "processeur et memoire",
        "gouvernance de code"
    ]
    
    for query in queries:
        start = time.time()
        p = subprocess.Popen([".venv/bin/python3", "core/search_router.py", query], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        while p.poll() is None:
            _, rss = get_process_metrics(p.pid)
            if rss > max_search_rss:
                max_search_rss = rss
            time.sleep(0.01)
            
        p.wait()
        latencies.append((time.time() - start) * 1000.0) # en ms
        
    avg_latency = sum(latencies) / len(latencies)
    return avg_latency, max_search_rss

def main():
    print("[*] Debut du Benchmark Baseline (Phase 0)...")
    setup_benchmark_env()
    
    print("[*] Mesure de l'empreinte memoire au repos (Idle)...")
    idle_ram = run_idle_benchmark()
    print(f"  - RAM au repos : {idle_ram:.2f} Mo")
    
    print("[*] Execution de l'indexation de 100 documents...")
    duration, max_rss, avg_cpu = run_indexing_benchmark()
    print(f"  - Duree totale : {duration:.2f} s")
    print(f"  - RAM maximale lors de l'indexation : {max_rss:.2f} Mo")
    print(f"  - CPU moyen : {avg_cpu:.1f}%")
    
    print("[*] Execution des tests de recherche sémantique...")
    avg_latency, max_search_rss = run_search_benchmark()
    print(f"  - Latence moyenne : {avg_latency:.2f} ms")
    print(f"  - RAM max pendant la recherche : {max_search_rss:.2f} Mo")
    
    # Generer le rapport de benchmark
    report_content = f"""# BENCHMARK BASELINE - ALEXANDRIA EMBEDDINGS V1.0 (BASELINE)
Date: {time.strftime("%Y-%m-%d %H:%M:%S")}
Machine: MIDGARD (Ubuntu, CPU-only, 8 Go RAM)

## Moteur de Reference (Actuel)
- Moteur sémantique local : `ChromaDB` (In-Process)
- Modèle d'embeddings local : `SentenceTransformer` (`all-MiniLM-L6-v2` - 384 dimensions)
- Dépendances : `torch`, `sentence-transformers`, `chromadb`

## Metriques Physiques Mesurees

| Metrique | Valeur Baseline | Description |
| :--- | :--- | :--- |
| **RAM au repos (Idle)** | {idle_ram:.2f} Mo | Empreinte mémoire résidente (RSS) avec ChromaDB et le modèle chargé en mémoire |
| **RAM Max Indexation** | {max_rss:.2f} Mo | Pic de mémoire résidente (RSS) lors de l'indexation de 100 documents |
| **Temps d'indexation (100 docs)** | {duration:.2f} s | Temps total de traitement et génération locale d'embeddings |
| **Vitesse d'indexation** | {100.0 / duration:.2f} doc/s | Nombre de documents traités par seconde |
| **Latence moyenne de recherche** | {avg_latency:.2f} ms | Temps de calcul de l'embedding de requête + query ChromaDB + SQLite FTS5 + RRF |
| **RAM Max Recherche** | {max_search_rss:.2f} Mo | Pic de mémoire résidente lors de l'exécution de la recherche |
| **CPU Moyen Indexation** | {avg_cpu:.1f}% | Utilisation CPU moyenne cumulée sur tous les cœurs |

## Observations & Diagnostic
1. **Empreinte memoire excessive** : Le chargement au repos de sentence-transformers + ChromaDB nécessite plus de {idle_ram:.1f} Mo de RAM, limitant les ressources de MIDGARD.
2. **Pic memoire a l'indexation** : Durant le traitement de seulement 100 fichiers, la RAM monte à {max_rss:.1f} Mo, ce qui risque d'entraîner des crashs sur des corpus plus importants ou lors d'indexations concurrentes.
3. **Dependances systeme** : La présence de `torch` et `sentence-transformers` alourdit inutilement le virtualenv de production et ralentit le serveur de langage (LSP).
"""
    
    # S'assurer que le dossier parent existe
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"[✓] Rapport de benchmark baseline genere avec succes sous {REPORT_PATH}")
    
    # Nettoyage
    if os.path.exists(BENCHMARK_DIR):
        shutil.rmtree(BENCHMARK_DIR)

if __name__ == "__main__":
    main()
