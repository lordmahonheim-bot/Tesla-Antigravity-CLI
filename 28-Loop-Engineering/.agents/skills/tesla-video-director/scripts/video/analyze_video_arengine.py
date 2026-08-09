import os
import sys
import time
from pathlib import Path
from google import genai
from google.genai import types

def analyze_video(video_path: str, output_path: str):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY missing.")
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)
    
    print(f"Uploading {video_path}...")
    video_file = client.files.upload(file=video_path)
    print(f"Uploaded as {video_file.name}. Waiting for processing...")
    
    while video_file.state and video_file.state.name == "PROCESSING":
        time.sleep(5)
        video_file = client.files.get(name=video_file.name)
        
    if video_file.state.name == "FAILED":
        print("File processing failed.")
        sys.exit(1)
        
    print("File processed. Sending prompt for AREngine report...")
    
    prompt = """Tu es Tesla Video Director. Analyse le contenu de cette vidéo en respectant scrupuleusement le standard AREngine (Analytical Report Engine).
    L'objectif de l'analyse est: "Rédiger un rapport analytique de haut niveau sur le contenu de cette vidéo (qu'est-ce qui est montré, expliqué, etc.)."
    Génère les 13 blocs AREngine (Bloc 0 au Bloc 12) détaillés, incluant les faits observés, le fact-checking, les recommandations, etc.
    Ne renvoie que le rapport complet en Markdown. Ne rajoute rien en dehors des blocs."""
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[video_file, prompt]
    )
    
    with open(output_path, "w") as f:
        f.write(response.text)
        
    print(f"Report written to {output_path}")

if __name__ == "__main__":
    analyze_video("/home/lord-mahonheim/Vidéos/Obsidian Graph.mp4", "/home/lord-mahonheim/bifrost/tesla/OUTPUTS/AREngine_Obsidian_Graph_Content_Analysis.md")
