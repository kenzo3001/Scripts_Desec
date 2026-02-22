#!/usr/bin/env bash
set -euo pipefail

# ==============================
# CONFIG: ajuste aqui
# ==============================

# Onde procurar (adicione/remova caminhos conforme seu servidor)
SEARCH_ROOTS=(
  /etc
  /opt
  /usr/local/etc
  /var/www
  /srv
  /home
)

# Nomes exatos de arquivos importantes (adicione os seus)
TARGET_FILES=(
  "nginx.conf"
  "apache2.conf"
  "httpd.conf"
  "php.ini"
  "my.cnf"
  "mariadb.cnf"
  "postgresql.conf"
  "pg_hba.conf"
  "redis.conf"
  "sshd_config"
  "docker-compose.yml"
  ".env"
)

# Padrões (glob) para achar configs comuns (adicione/remova)
TARGET_GLOBS=(
  "*.conf"
  "*.cnf"
  "*.ini"
  "*.yml"
  "*.yaml"
  "*.toml"
  "*.json"
  "*.properties"
  "*.env"
)

# Se você quiser filtrar por conteúdo (ex.: "password", "DB_HOST"), coloque aqui.
# Deixe vazio para não fazer busca por conteúdo.
CONTENT_PATTERNS=(
  # "DB_HOST"
  # "password"
)

# Arquivo de saída (relatório)
OUTFILE="config_paths_$(hostname)_$(date +%F_%H%M%S).txt"

# Excluir diretórios barulhentos (find -path ... -prune)
EXCLUDE_DIRS=(
  "/proc"
  "/sys"
  "/dev"
  "/run"
  "/tmp"
  "/var/lib/docker"
  "/var/snap"
)

# ==============================
# FUNÇÕES
# ==============================
build_prune_expr() {
  local expr=()
  for d in "${EXCLUDE_DIRS[@]}"; do
    expr+=( -path "$d" -o -path "$d/*" )
  done
  # Remove o último -o
  unset 'expr[${#expr[@]}-1]'
  printf '%s\0' "${expr[@]}"
}

print_header() {
  {
    echo "=== Config discovery report ==="
    echo "Host: $(hostname -f 2>/dev/null || hostname)"
    echo "Date: $(date -Is)"
    echo "User: $(id -un) (uid=$(id -u))"
    echo "Search roots: ${SEARCH_ROOTS[*]}"
    echo "Excluded dirs: ${EXCLUDE_DIRS[*]}"
    echo
  } >> "$OUTFILE"
}

# ==============================
# MAIN
# ==============================
: > "$OUTFILE"
print_header

echo "[*] Gerando expressão de exclusão..."
mapfile -d '' PRUNE_EXPR < <(build_prune_expr)

echo "[*] Procurando por nomes exatos de arquivos..."
{
  echo "=== Exact filename matches ==="
  for root in "${SEARCH_ROOTS[@]}"; do
    [ -d "$root" ] || continue
    for f in "${TARGET_FILES[@]}"; do
      find "$root" \
        \( "${PRUNE_EXPR[@]}" \) -prune -o \
        -type f -name "$f" -print 2>/dev/null
    done
  done | sort -u
  echo
} >> "$OUTFILE"

echo "[*] Procurando por padrões (globs)..."
{
  echo "=== Glob pattern matches ==="
  for root in "${SEARCH_ROOTS[@]}"; do
    [ -d "$root" ] || continue
    for g in "${TARGET_GLOBS[@]}"; do
      find "$root" \
        \( "${PRUNE_EXPR[@]}" \) -prune -o \
        -type f -name "$g" -print 2>/dev/null
    done
  done | sort -u
  echo
} >> "$OUTFILE"

if [ "${#CONTENT_PATTERNS[@]}" -gt 0 ]; then
  echo "[*] Procurando por conteúdo dentro de arquivos (pode demorar)..."
  {
    echo "=== Content matches (ripgrep) ==="
    if command -v rg >/dev/null 2>&1; then
      # ripgrep (mais rápido)
      for root in "${SEARCH_ROOTS[@]}"; do
        [ -d "$root" ] || continue
        for pat in "${CONTENT_PATTERNS[@]}"; do
          rg -n --hidden --no-messages \
            --glob '!.git/*' \
            --glob '!**/node_modules/**' \
            --glob '!**/vendor/**' \
            "$pat" "$root" 2>/dev/null || true
        done
      done
    else
      # fallback grep
      for root in "${SEARCH_ROOTS[@]}"; do
        [ -d "$root" ] || continue
        for pat in "${CONTENT_PATTERNS[@]}"; do
          grep -RIn --binary-files=without-match \
            --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=vendor \
            "$pat" "$root" 2>/dev/null || true
        done
      done
    fi
    echo
  } >> "$OUTFILE"
fi

echo "[+] Pronto. Relatório gerado em: $OUTFILE"
echo "[+] Para ver rapidamente só os caminhos: grep -E '^/' \"$OUTFILE\" | head"