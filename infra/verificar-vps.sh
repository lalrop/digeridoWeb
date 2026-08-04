#!/usr/bin/env bash
#
# Diagnóstico del VPS. Dice qué está bien y qué falta, sin cambiar nada.
#
#   sudo ./infra/verificar-vps.sh digerido.cl
#
# Pensado para correr cuando algo no funciona y no está claro dónde mirar.
# Cada línea es una comprobación independiente: no se detiene en la primera que
# falla, porque lo útil es ver el cuadro completo.

set -uo pipefail

DOMINIO="${1:-digerido.cl}"
USUARIO_DEPLOY="${2:-deploy}"
RAIZ_WEB=/var/www/digerido

ok=0
fallas=0

si()  { printf '  \033[32m✓\033[0m %s\n' "$*"; ok=$((ok + 1)); }
no()  { printf '  \033[31m✗\033[0m %s\n' "$*"; fallas=$((fallas + 1)); }
info(){ printf '  \033[36m·\033[0m %s\n' "$*"; }
tit() { printf '\n\033[1m%s\033[0m\n' "$*"; }

echo "Diagnóstico de digerido en $(hostname) — dominio: $DOMINIO"

# ── DNS ─────────────────────────────────────────────────────────────────────
tit "DNS"
IP_LOCAL="$(hostname -I 2>/dev/null | awk '{print $1}')"
IP_PUBLICA="$(curl -fsS --max-time 5 https://api.ipify.org 2>/dev/null || echo '')"
info "IP de este servidor: ${IP_PUBLICA:-$IP_LOCAL}"

for nombre in "$DOMINIO" "www.$DOMINIO"; do
  RESUELVE="$(getent hosts "$nombre" 2>/dev/null | awk '{print $1}' | head -1)"
  if [[ -z "$RESUELVE" ]]; then
    no "$nombre no resuelve todavía (el DNS no propagó)"
  elif [[ "$RESUELVE" == "$IP_PUBLICA" || "$RESUELVE" == "$IP_LOCAL" ]]; then
    si "$nombre → $RESUELVE"
  else
    no "$nombre → $RESUELVE, pero este servidor es ${IP_PUBLICA:-$IP_LOCAL}"
  fi
done

# ── Nginx ───────────────────────────────────────────────────────────────────
tit "Nginx"
if ! command -v nginx &>/dev/null; then
  no "no está instalado — corré infra/instalar-vps.sh"
  # Sin nginx, el resto de este bloque solo produciría ruido.
  NGINX_AUSENTE=si
else
  si "instalado ($(nginx -v 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+'))"
  NGINX_AUSENTE=no
fi

for f in /etc/nginx/sites-enabled/digerido \
         /etc/nginx/snippets/digerido-http2.conf \
         /etc/nginx/snippets/digerido-compresion.conf \
         /etc/nginx/conf.d/digerido-anonimizar-ip.conf; do
  [[ -e "$f" ]] && si "existe $f" || no "falta $f — volvé a correr el instalador"
done

if [[ "$NGINX_AUSENTE" == no ]]; then
  if nginx -t &>/dev/null; then
    si "la configuración es válida (nginx -t)"
  else
    no "nginx -t falla:"
    nginx -t 2>&1 | sed 's/^/      /'
  fi

  if systemctl is-active --quiet nginx 2>/dev/null; then
    si "nginx está corriendo"
  else
    no "nginx NO está corriendo"
  fi
fi

if grep -q '^brotli on;' /etc/nginx/snippets/digerido-compresion.conf 2>/dev/null; then
  si "brotli activo"
else
  info "brotli no disponible en este sistema; se usa gzip (aceptable)"
fi

# ── Certificado ─────────────────────────────────────────────────────────────
tit "Certificado TLS"
CERT="/etc/letsencrypt/live/$DOMINIO/fullchain.pem"
if [[ -f "$CERT" ]]; then
  DIAS=$(( ( $(date -d "$(openssl x509 -enddate -noout -in "$CERT" | cut -d= -f2)" +%s) - $(date +%s) ) / 86400 ))
  if (( DIAS > 20 )); then
    si "válido, vence en $DIAS días"
  else
    no "vence en $DIAS días — revisá la renovación automática"
  fi
  if systemctl list-timers 2>/dev/null | grep -q certbot; then
    si "la renovación automática está programada"
  else
    no "no encuentro el timer de certbot"
  fi
else
  no "no hay certificado para $DOMINIO"
fi

# ── Sitio ───────────────────────────────────────────────────────────────────
tit "Archivos del sitio"
if [[ -L "$RAIZ_WEB/actual" ]]; then
  DESTINO="$(readlink -f "$RAIZ_WEB/actual")"
  si "actual → $(basename "$DESTINO")"
  [[ -f "$DESTINO/index.html" ]] && si "index.html presente" || no "falta index.html"
  if [[ -f "$DESTINO/404.html" ]]; then
    si "404.html presente"
  else
    no "falta 404.html (el vhost lo referencia)"
  fi
  N=$(ls -1d "$RAIZ_WEB"/releases/*/ 2>/dev/null | wc -l)
  info "$N release(s) guardada(s)"
else
  no "$RAIZ_WEB/actual no es un symlink — ¿ya se desplegó alguna vez?"
fi

DUENO="$(stat -c '%U' "$RAIZ_WEB" 2>/dev/null || echo '?')"
[[ "$DUENO" == "$USUARIO_DEPLOY" ]] \
  && si "$RAIZ_WEB es de $USUARIO_DEPLOY" \
  || no "$RAIZ_WEB es de '$DUENO', debería ser '$USUARIO_DEPLOY' (rsync fallará)"

# ── Deploy ──────────────────────────────────────────────────────────────────
tit "Acceso de despliegue"
if id "$USUARIO_DEPLOY" &>/dev/null; then
  si "el usuario $USUARIO_DEPLOY existe"
  AUTH="/home/$USUARIO_DEPLOY/.ssh/authorized_keys"
  if [[ -s "$AUTH" ]]; then
    si "$(grep -c '^ssh-' "$AUTH" 2>/dev/null || echo 0) clave(s) autorizada(s)"
  else
    no "$AUTH está vacío — GitHub Actions no podrá entrar"
  fi
else
  no "el usuario $USUARIO_DEPLOY no existe"
fi

if [[ -f /etc/sudoers.d/digerido-deploy ]]; then
  si "sudo acotado para 'nginx -s reload'"
else
  no "falta /etc/sudoers.d/digerido-deploy (el último paso del deploy fallará)"
fi

# ── Respuesta real ──────────────────────────────────────────────────────────
tit "Respuesta HTTP"
for url in "http://$DOMINIO" "https://$DOMINIO"; do
  # Sin `|| echo`: curl ya imprime 000 cuando no conecta, y el fallback duplicaba el código.
  CODIGO="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 8 "$url" 2>/dev/null)"
  CODIGO="${CODIGO:-000}"
  case "$url:$CODIGO" in
    http://*:301) si "$url → 301 (redirige a HTTPS, correcto)" ;;
    https://*:200) si "$url → 200" ;;
    *:000) no "$url no responde" ;;
    *) no "$url → HTTP $CODIGO" ;;
  esac
done

# ── Firewall ────────────────────────────────────────────────────────────────
tit "Firewall"
if command -v ufw &>/dev/null && ufw status 2>/dev/null | grep -q "Status: active"; then
  si "ufw activo"
  ufw status 2>/dev/null | grep -qE "80|Nginx" && si "puerto 80/443 permitido" || no "Nginx podría estar bloqueado"
else
  info "ufw no está activo (ver el endurecimiento mínimo en DESPLIEGUE.md)"
fi

# ── Resumen ─────────────────────────────────────────────────────────────────
echo
if (( fallas == 0 )); then
  printf '\033[32m%s\033[0m\n' "Todo en orden: $ok comprobaciones pasaron."
else
  printf '\033[31m%s\033[0m\n' "$fallas problema(s) y $ok comprobaciones OK."
  echo "Buscá el síntoma en la tabla de infra/DESPLIEGUE.md."
  exit 1
fi
