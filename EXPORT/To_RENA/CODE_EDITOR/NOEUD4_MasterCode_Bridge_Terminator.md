# Bridge Python : Antigravity CLI <-> Google AI Studio dans Terminator

Ce document présente l'implémentation d'un script Python léger servant de "hook" ou "bridge" pour connecter Google AI Studio à Antigravity CLI v1.2.7, pensé pour être exécuté dans un panneau Terminator.

## Script Bridge (`agy_ai_bridge.py`)

Ce script interroge le modèle Gemini via AI Studio, récupère le code généré, le sauvegarde temporairement et l'exécute via Antigravity CLI.

```python
#!/usr/bin/env python3
import os
import subprocess
import sys
import google.generativeai as genai

def setup_ai_studio():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[!] Erreur: GEMINI_API_KEY non définie dans l'environnement.")
        sys.exit(1)
    genai.configure(api_key=api_key)
    # Configuration du modèle
    return genai.GenerativeModel('gemini-1.5-pro')

def run_antigravity_cli(file_path):
    print(f"[*] Exécution de {file_path} via Antigravity CLI v1.2.7...")
    try:
        # Remplacer 'antigravity' par le chemin absolu si nécessaire
        result = subprocess.run(['antigravity', 'run', file_path], 
                                capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"[!] Erreur d'exécution AGY :\n{e.stderr}"
    except FileNotFoundError:
        return "[!] Erreur : Antigravity CLI n'est pas installé ou n'est pas dans le PATH."

def main():
    if len(sys.argv) < 2:
        print("Usage: agy_ai_bridge.py <votre prompt pour générer du code AGY>")
        sys.exit(1)
    
    prompt = sys.argv[1]
    prompt_complet = f"Génère uniquement du code compatible Antigravity CLI v1.2.7 pour accomplir la tâche suivante : {prompt}. Ne fournis pas de markdown, juste le code."
    
    model = setup_ai_studio()
    
    print("[*] Envoi de la requête à Google AI Studio...")
    response = model.generate_content(prompt_complet)
    generated_code = response.text.strip()
    
    # Nettoyage éventuel des balises markdown si le modèle en génère quand même
    if generated_code.startswith("```"):
        generated_code = "\n".join(generated_code.split("\n")[1:-1])
        
    script_path = "/tmp/generated_ai_script.agy"
    with open(script_path, "w") as f:
        f.write(generated_code)
    
    print("[*] Code généré avec succès. Début de l'exécution locale sur MIDGARD.")
    output = run_antigravity_cli(script_path)
    
    print("\n" + "="*40)
    print("RÉSULTAT DE L'EXÉCUTION ANTIGRAVITY")
    print("="*40)
    print(output)

if __name__ == "__main__":
    main()
```

## Configuration Terminator

Pour utiliser ce script efficacement dans Terminator :
1. Rendez le script exécutable : `chmod +x agy_ai_bridge.py`
2. Assurez-vous que la variable d'environnement `GEMINI_API_KEY` est définie dans votre `.bashrc` ou `.zshrc`.
3. Dans Terminator, vous pouvez séparer la fenêtre (`Ctrl+Shift+O` ou `Ctrl+Shift+E`).
4. Dans l'un des panneaux, utilisez la commande : `./agy_ai_bridge.py "Créer une fonction qui calcule la suite de Fibonacci"`

Cette approche permet de visualiser les outputs locaux directement dans le panneau Terminator actif, créant un pipeline transparent entre l'idéation dans le cloud (AI Studio) et l'exécution locale sécurisée sur MIDGARD.
