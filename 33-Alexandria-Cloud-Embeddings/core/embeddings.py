#!/usr/bin/env python3
import time
from abc import ABC, abstractmethod
import numpy as np
from google import genai
from google.genai import errors

class EmbeddingProvider(ABC):
    @abstractmethod
    def generate_embeddings(self, texts: list[str]) -> list[np.ndarray]:
        """Génère une liste de vecteurs d'embeddings normalisés L2 pour une liste de textes."""
        pass

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Version ou nom du modèle d'embedding utilisé."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Dimension des vecteurs générés."""
        pass


class GeminiEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "models/gemini-embedding-001", dimension: int = 768):
        self._model_name = model_name
        self._dimension = dimension
        # Le client utilise la variable d'environnement GEMINI_API_KEY par défaut
        self.client = genai.Client()

    @property
    def model_version(self) -> str:
        return f"{self._model_name}:{self._dimension}"

    @property
    def dimension(self) -> int:
        return self._dimension

    def _normalize_l2(self, vec: list[float]) -> np.ndarray:
        arr = np.array(vec, dtype=np.float32)
        norm = np.linalg.norm(arr)
        if norm > 0:
            arr = arr / norm
        return arr

    def generate_embeddings(self, texts: list[str]) -> list[np.ndarray]:
        if not texts:
            return []

        # Division en batchs de 96
        batch_size = 96
        batches = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]
        all_embeddings = []

        from typing import Any, cast

        for batch in batches:
            success = False
            last_err = None
            # Retry exponentiel 3x (1s, 2s, 4s)
            for attempt in range(3):
                try:
                    response = self.client.models.embed_content(
                        model=self._model_name,
                        contents=cast(Any, batch)
                    )
                    # Récupérer les vecteurs
                    if response and response.embeddings:
                        for e in response.embeddings:
                            if e.values is not None:
                                all_embeddings.append(self._normalize_l2(e.values))
                            else:
                                raise ValueError("L'un des vecteurs retournes par l'API Gemini est None")
                        success = True
                        break
                    else:
                        raise ValueError("Réponse d'embedding vide de l'API Gemini")
                except errors.APIError as e:
                    last_err = e
                    # Code 429 est typiquement le Rate Limit
                    wait_time = (2 ** attempt)
                    print(f"[-] Erreur API Gemini (Attempt {attempt+1}/3): {e}. Attente de {wait_time}s...")
                    time.sleep(wait_time)
                except Exception as e:
                    last_err = e
                    wait_time = (2 ** attempt)
                    print(f"[-] Erreur inattendue Gemini (Attempt {attempt+1}/3): {e}. Attente de {wait_time}s...")
                    time.sleep(wait_time)

            if not success:
                # Si tous les retries ont échoué, on lève l'exception pour que l'appelant
                # bascule en mode dégradé (stockage dans pending_embeddings).
                raise ConnectionError(f"Echec persistant de generation d'embeddings via Gemini API : {last_err}")

        return all_embeddings


class MockEmbeddingProvider(EmbeddingProvider):
    """Provider factice utile pour les tests ou le mode offline."""
    def __init__(self, dimension: int = 768):
        self._dimension = dimension

    @property
    def model_version(self) -> str:
        return f"mock-embedding:{self._dimension}"

    @property
    def dimension(self) -> int:
        return self._dimension

    def generate_embeddings(self, texts: list[str]) -> list[np.ndarray]:
        # Retourne des vecteurs aléatoires normalisés
        res = []
        for _ in texts:
            vec = np.random.randn(self._dimension).astype(np.float32)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            res.append(vec)
        return res
