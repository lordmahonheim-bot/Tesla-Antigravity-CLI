# Étude de Faisabilité : Intégration de VOICE-TESLA avec Google Colab

**Mission** : Capturer l'audio d'un microphone depuis un notebook Google Colab et l'utiliser pour un traitement STT (Speech-to-Text).

## 1. Méthodes JavaScript/HTML5 (WebRTC, MediaRecorder API)
Colab tournant dans un environnement cloud (backend sur les serveurs Google), le code Python n'a pas accès direct aux périphériques matériels locaux (microphone, webcam). La solution consiste à créer un "pont" via le navigateur en exécutant du JavaScript dans la cellule de sortie.

La méthode la plus robuste repose sur :
1. L'utilisation de `navigator.mediaDevices.getUserMedia({ audio: true })` pour demander l'accès au microphone au sein du navigateur (requiert l'autorisation explicite de l'utilisateur).
2. L'utilisation de l'API `MediaRecorder` pour capturer le flux audio généré.
3. L'envoi des données vers le backend Python via `google.colab.output.eval_js`.

## 2. Streaming vs Enregistrement Complet
L'architecture de Colab pose certaines limites quant au streaming :

* **Enregistrement complet (Batch)** : C'est la méthode la plus fiable. Le script JS enregistre l'audio pendant une durée déterminée ou jusqu'à ce que l'utilisateur clique sur un bouton "Stop", puis convertit le Blob audio en chaîne encodée en base64. Cette chaîne est retournée au code Python de façon synchrone via l'appel `eval_js`.
* **Streaming en temps réel** : `google.colab.output.eval_js` est bloquant et conçu pour retourner une valeur unique une fois la promesse JS résolue. Pour simuler un streaming :
    * On peut utiliser une boucle de captures courtes (ex: 2 secondes) en appelant répétitivement JS, mais la latence et les coupures peuvent dégrader la qualité du STT.
    * Le "vrai" streaming nécessiterait d'établir un canal bidirectionnel (WebSockets, WebRTC Data Channels, ou via l'API Jupyter de communication frontend/backend), ce qui est nettement plus complexe à mettre en œuvre proprement sur Colab en raison de l'isolation réseau et des proxies.

## 3. Solutions existantes (Exemples de Code)

Un pattern Python/JS très courant sur GitHub pour l'enregistrement complet est le suivant :

```python
from IPython.display import Javascript, display
from google.colab import output
from base64 import b64decode

# Injection du JS pour l'enregistrement
RECORD_JS = """
const sleep = time => new Promise(resolve => setTimeout(resolve, time));
const b2text = blob => new Promise(resolve => {
  const reader = new FileReader();
  reader.onloadend = e => resolve(e.srcElement.result);
  reader.readAsDataURL(blob);
});
var record = time => new Promise(async resolve => {
  stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  recorder = new MediaRecorder(stream);
  chunks = [];
  recorder.ondataavailable = e => chunks.push(e.data);
  recorder.start();
  await sleep(time); // Attend 'time' ms
  recorder.onstop = async () => {
    blob = new Blob(chunks);
    text = await b2text(blob);
    resolve(text);
  };
  recorder.stop();
});
"""

def record_audio(seconds=5):
    display(Javascript(RECORD_JS))
    # Exécute JS, l'utilisateur devra autoriser le micro
    print(f"Enregistrement en cours pour {seconds} secondes...")
    s = output.eval_js('record(%d)' % (seconds * 1000))
    # Retourne les données en base64. Index 1 = data après "data:audio/webm;base64,"
    b = b64decode(s.split(',')[1])
    return b

# Utilisation
audio_bytes = record_audio(5)
with open('enregistrement.webm', 'wb') as f:
    f.write(audio_bytes)
```

## 4. Limites et Contraintes

1. **Format Audio** : Le format par défaut généré par `MediaRecorder` dans Chrome est le `audio/webm` (généralement avec codec Opus). La plupart des modèles STT (comme Whisper ou Google STT) peuvent avoir besoin de WAV PCM. Il sera donc indispensable de transcoder l'audio côté Python (ex: via `ffmpeg-python` ou `pydub`).
2. **Latence** : Il y a un léger décalage entre l'exécution de la cellule et le moment où l'enregistrement débute effectivement, à cause du temps de rendu et des éventuelles demandes de permission.
3. **Permissions Colab** : Le navigateur redemande souvent l'autorisation d'accès au micro lors du premier lancement du bloc JS, ce qui peut rendre complexe une exécution entièrement automatisée sans "Human in the loop". Une bonne pratique consiste à injecter un bouton HTML Start/Stop.
4. **Limites de `eval_js`** : La méthode est adaptée pour de petits payloads (quelques mégas). Un enregistrement très long pourrait saturer la limite de taille d'échange entre le front et le backend Jupyter.
