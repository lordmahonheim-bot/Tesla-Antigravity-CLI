Ces artefacts peuvent contenir identifiants d'appareil, noms de réseaux, chemins,
journaux applicatifs et autres données privées. Ne pas les publier bruts. Conserver
localement, contrôler les accès et expurger avant transmission.

Pour capturer spécifiquement l'erreur -13 après cette collecte :
  adb -s IP:PORT logcat -c
  # reproduire l'erreur dans Netflix
  adb -s IP:PORT logcat -b all -v threadtime -d > netflix_repro_logcat.txt

L'effacement du logcat est une action destructive sur les anciens journaux ; il n'est
donc pas effectué automatiquement par ce script de collecte initiale.
