#!/usr/bin/env bash
# Copia las skills propias de .agents/skills/ (el original) a .claude/skills/,
# que es la única carpeta que lee Claude Code. No se usan enlaces simbólicos
# porque se rompen en Windows (ver docs/adr/0004).
#
# Uso:   bash scripts/sincronizar-skills.sh           # sincroniza
#        bash scripts/sincronizar-skills.sh --check   # solo comprueba (sale con 1 si hay diferencias)
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ "${1:-}" == "--check" ]]; then
  if diff -r .agents/skills .claude/skills > /dev/null; then
    echo "OK: .claude/skills es idéntica a .agents/skills"
  else
    echo "DESINCRONIZADO: ejecuta 'bash scripts/sincronizar-skills.sh'" >&2
    exit 1
  fi
  exit 0
fi

rm -rf .claude/skills
mkdir -p .claude
cp -R .agents/skills .claude/skills
echo "Sincronizado: .agents/skills -> .claude/skills"
