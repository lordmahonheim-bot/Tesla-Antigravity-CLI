#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                 TESLA EXIT CODES LIBRARY                                    ║
# ║              Codes de sortie standardisés pour l'écosystème Tesla           ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

# ═══════════════════════════════════════════════════════════════════════════════
# CODES DE SUCCÈS
# ═══════════════════════════════════════════════════════════════════════════════

EXIT_SUCCESS=0                    # Succès
EXIT_PASS=0                       # Vérification Passed

# ═══════════════════════════════════════════════════════════════════════════════
# CODES D'ÉCHEC GÉNÉRIQUES
# ═══════════════════════════════════════════════════════════════════════════════

EXIT_GENERAL_ERROR=1              # Erreur générale
EXIT_VALIDATION_FAILED=1          # Échec de validation
EXIT_BLOCKED=1                    # Bloqué par sécurité

# ═══════════════════════════════════════════════════════════════════════════════
# CODES SPÉCIFIQUES TESLA
# ═══════════════════════════════════════════════════════════════════════════════

EXIT_INVALID_SCHEMA=64            # Schéma YAML/JSON invalide
EXIT_INVALID_SIGNATURE=65         # Signature HMAC invalide
EXIT_TESLA_ROOT_NOT_FOUND=66       # TESLA_ROOT introuvable
EXIT_DEPENDENCY_MISSING=69        # Dépendance manquante (jq, rg, etc.)

EXIT_SECRET_DETECTED=100          # Secret/token détecté
EXIT_SCOPE_VIOLATION=101          # Violation de périmètre
EXIT_PROJECT_STATE_DESYNC=102     # PROJECT_STATE désynchronisé
EXIT_MARBLE_CERT_MISSING=103      # Marble Certificate absent
EXIT_BASELINE_DRIFT=104           # Baseline drift détecté
EXIT_UNKNOWN_STATE=105            # État non vérifiable (≠ PASS)

EXIT_AUTH_EXPIRED=110             # Autorisation expirée
EXIT_AUTH_MISSING=111             # Autorisation manquante
EXIT_FORCE_PUSH_BLOCKED=112       # Force-push non autorisé

EXIT_RETRY_EXCEEDED=120          # Max retries dépassé
EXIT_CIRCUIT_BREAKER_OPEN=121    # Circuit breaker déclenché
EXIT_ESCALATION_REQUIRED=130     # Escalade vers Mahonheim requise

# ═══════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES
# ═══════════════════════════════════════════════════════════════════════════════

# Obtenir la description d'un code de sortie
exit_code_description() {
    local code="$1"
    case "$code" in
        0)    echo "SUCCESS" ;;
        1)    echo "FAILURE (generic)" ;;
        64)   echo "INVALID_SCHEMA" ;;
        65)   echo "INVALID_SIGNATURE" ;;
        66)   echo "TESLA_ROOT_NOT_FOUND" ;;
        69)   echo "DEPENDENCY_MISSING" ;;
        100)  echo "SECRET_DETECTED" ;;
        101)  echo "SCOPE_VIOLATION" ;;
        102)  echo "PROJECT_STATE_DESYNC" ;;
        103)  echo "MARBLE_CERT_MISSING" ;;
        104)  echo "BASELINE_DRIFT" ;;
        105)  echo "UNKNOWN_STATE" ;;
        110)  echo "AUTH_EXPIRED" ;;
        111)  echo "AUTH_MISSING" ;;
        112)  echo "FORCE_PUSH_BLOCKED" ;;
        120)  echo "RETRY_EXCEEDED" ;;
        121)  echo "CIRCUIT_BREAKER_OPEN" ;;
        130)  echo "ESCALATION_REQUIRED" ;;
        *)    echo "UNKNOWN_CODE" ;;
    esac
}

# Afficher un message d'erreur formaté
exit_with_message() {
    local code="$1"
    local message="$2"
    
    echo "╔═══════════════════════════════════════════════════════════════╗"
    printf "║ %-60s ║\n" "$(exit_code_description $code)"
    echo "╠═══════════════════════════════════════════════════════════════╣"
    printf "║ %-60s ║\n" "$message"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    
    exit "$code"
}

# Export
export -f exit_code_description exit_with_message
export EXIT_SUCCESS EXIT_PASS
export EXIT_GENERAL_ERROR EXIT_VALIDATION_FAILED EXIT_BLOCKED
export EXIT_INVALID_SCHEMA EXIT_INVALID_SIGNATURE EXIT_TESLA_ROOT_NOT_FOUND EXIT_DEPENDENCY_MISSING
export EXIT_SECRET_DETECTED EXIT_SCOPE_VIOLATION EXIT_PROJECT_STATE_DESYNC EXIT_MARBLE_CERT_MISSING
export EXIT_BASELINE_DRIFT EXIT_UNKNOWN_STATE
export EXIT_AUTH_EXPIRED EXIT_AUTH_MISSING EXIT_FORCE_PUSH_BLOCKED
export EXIT_RETRY_EXCEEDED EXIT_CIRCUIT_BREAKER_OPEN EXIT_ESCALATION_REQUIRED
