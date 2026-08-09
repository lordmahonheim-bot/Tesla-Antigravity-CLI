-- Embryon de la table subagent_health pour la Vigilum Gateway V2.1
-- Cette table est destinée à être intégrée dans le Second Cerveau (Alexandria SQLite)
-- ou dans la base de données interne de l'Orchestrateur Tesla.

CREATE TABLE IF NOT EXISTS subagent_health (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,                  -- L'identifiant du sous-agent (ex: tesla-github-manager)
    last_invocation TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Dernière fois qu'il a été invoqué
    success_count INTEGER DEFAULT 0,         -- Nombre d'exécutions terminées par un CHECKPOINT:SUCCESS
    partial_count INTEGER DEFAULT 0,         -- Nombre d'exécutions terminées par un CHECKPOINT:PARTIAL
    failure_count INTEGER DEFAULT 0,         -- Nombre de crashs ou hard timeouts sans checkpoint
    consecutive_failures INTEGER DEFAULT 0,  -- Déclencheur du Circuit Breaker
    circuit_breaker_status TEXT DEFAULT 'CLOSED', -- CLOSED (OK), OPEN (BLOQUÉ), HALF_OPEN (RETRY)
    last_error_log TEXT                      -- Extrait du dernier log d'erreur ayant causé un crash
);

-- Index pour des recherches rapides par l'Orchestrateur lors du Pre-Flight
CREATE INDEX IF NOT EXISTS idx_agent_id ON subagent_health(agent_id);
