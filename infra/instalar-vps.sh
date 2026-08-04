#!/usr/bin/env bash
#
# Provisiona un VPS (Hostinger, Ubuntu/Debian) para servir digerido.
#
#   sudo ./infra/instalar-vps.sh digerido.cl deploy
#
# Idempotente: se puede correr de nuevo sin romper nada.
#
# Qué hace:
#   1. instala nginx, certbot y rsync
#   2. crea /var/www/digerido/{releases,actual} y el usuario de deploy
#   3. GENERA los snippets según lo que este servidor soporta de verdad:
#        · brotli, solo si el módulo existe
#        · `http2 on` o `listen ... http2`, según la versión de nginx
#        · el `map` de anonimización de IP, en el contexto http
#   4. instala el vhost con el dominio reemplazado
#   5. pide el certificado con certbot
#   6. habilita sudo sin contraseña SOLO para `nginx -s reload`
#
# Lo que NO hace: apuntar el DNS. Eso va en el panel de Hostinger, y tiene que
# estar propagado ANTES de correr esto, porque certbot valida por HTTP.

set -euo pipefail

DOMINIO="${1:-}"
USUARIO_DEPLOY="${2:-deploy}"
UMAMI_HOST="${UMAMI_HOST:-umami.${DOMINIO}}"

RAIZ_WEB=/var/www/digerido
DIR_SNIPPETS=/etc/nginx/snippets
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

rojo()  { printf '\033[31m%s\033[0m\n' "$*"; }
verde() { printf '\033[32m%s\033[0m\n' "$*"; }
info()  { printf '\033[36m▸\033[0m %s\n' "$*"; }

if [[ -z "$DOMINIO" ]]; then
  rojo "Uso: sudo $0 <dominio> [usuario-deploy]"
  rojo "Ej:  sudo $0 digerido.cl deploy"
  exit 1
fi

if [[ $EUID -ne 0 ]]; then
  rojo "Corré con sudo."
  exit 1
fi

# ── 1. Paquetes ─────────────────────────────────────────────────────────────
info "instalando paquetes"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq nginx certbot python3-certbot-nginx rsync

# El módulo brotli existe en Ubuntu 24.04+; en versiones anteriores no está y
# no vale la pena compilarlo: gzip cubre el caso, con ~15 % menos de ahorro.
TIENE_BROTLI=no
if apt-get install -y -qq libnginx-mod-brotli 2>/dev/null; then
  TIENE_BROTLI=si
  verde "  brotli disponible"
else
  info "  brotli no disponible en este sistema; se usa solo gzip"
fi

# ── 2. Directorios y usuario ────────────────────────────────────────────────
info "preparando $RAIZ_WEB"
mkdir -p "$RAIZ_WEB/releases" /var/www/certbot

if ! id "$USUARIO_DEPLOY" &>/dev/null; then
  # Sin shell de login interactivo y sin contraseña: solo entra por clave SSH.
  adduser --disabled-password --gecos "despliegue de digerido" "$USUARIO_DEPLOY"
  verde "  usuario $USUARIO_DEPLOY creado"
fi

# El usuario de deploy es dueño de las releases; nginx solo necesita leer.
chown -R "$USUARIO_DEPLOY:$USUARIO_DEPLOY" "$RAIZ_WEB"
chmod 755 "$RAIZ_WEB"
mkdir -p "/home/$USUARIO_DEPLOY/.ssh"
touch "/home/$USUARIO_DEPLOY/.ssh/authorized_keys"
chmod 700 "/home/$USUARIO_DEPLOY/.ssh"
chmod 600 "/home/$USUARIO_DEPLOY/.ssh/authorized_keys"
chown -R "$USUARIO_DEPLOY:$USUARIO_DEPLOY" "/home/$USUARIO_DEPLOY/.ssh"

# Un placeholder para que nginx arranque antes del primer deploy: sin esto, el
# symlink no existe y nginx falla el `nginx -t` por root inexistente.
if [[ ! -e "$RAIZ_WEB/actual" ]]; then
  mkdir -p "$RAIZ_WEB/releases/inicial"
  cat > "$RAIZ_WEB/releases/inicial/index.html" <<'HTML'
<!doctype html><html lang="es"><meta charset="utf-8">
<title>digerido</title>
<body style="font-family:system-ui;padding:3rem;max-width:40rem;margin:auto">
<h1>digerido</h1><p>Servidor listo. Esperando el primer despliegue.</p>
HTML
  ln -sfn "$RAIZ_WEB/releases/inicial" "$RAIZ_WEB/actual"
  chown -R "$USUARIO_DEPLOY:$USUARIO_DEPLOY" "$RAIZ_WEB"
  verde "  placeholder instalado"
fi

# ── 3. Snippets según lo que el servidor soporta ────────────────────────────
mkdir -p "$DIR_SNIPPETS"

# http2: la directiva `http2 on` existe desde nginx 1.25.1. Antes de eso hay que
# ponerlo en el `listen`, que es lo que hace el vhost por defecto. Usar la
# equivocada hace que nginx no arranque.
VERSION_NGINX="$(nginx -v 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')"
info "nginx $VERSION_NGINX"

version_mayor_o_igual() {
  printf '%s\n%s\n' "$2" "$1" | sort -V -C
}

if version_mayor_o_igual "$VERSION_NGINX" "1.25.1"; then
  cat > "$DIR_SNIPPETS/digerido-http2.conf" <<'CONF'
# nginx >= 1.25.1: http2 se activa con su propia directiva.
http2 on;
CONF
  verde "  http2: directiva moderna"
else
  cat > "$DIR_SNIPPETS/digerido-http2.conf" <<'CONF'
# nginx < 1.25.1: `http2 on` no existe todavía. En esta versión http2 se activa
# en el `listen`, así que acá no va nada y el vhost necesita `listen 443 ssl
# http2`. El instalador ya ajustó las líneas listen de digerido.conf.
CONF
  verde "  http2: en las líneas listen (nginx antiguo)"
fi

# Compresión
{
  echo "# Generado por infra/instalar-vps.sh"
  echo
  if [[ "$TIENE_BROTLI" == si ]]; then
    cat <<'CONF'
brotli            on;
brotli_comp_level 6;
brotli_static     on;
brotli_types      text/plain text/css text/xml application/javascript
                  application/json application/xml image/svg+xml
                  application/rss+xml font/woff2;
CONF
  else
    echo "# brotli no disponible en este servidor: solo gzip."
  fi
  cat <<'CONF'

gzip            on;
gzip_vary       on;
gzip_comp_level 6;
gzip_min_length 256;
gzip_proxied    any;
gzip_types      text/plain text/css text/xml application/javascript
                application/json application/xml image/svg+xml
                application/rss+xml;
CONF
} > "$DIR_SNIPPETS/digerido-compresion.conf"

# El `map` de anonimización va en el contexto http → conf.d/
cp "$AQUI/nginx/snippets/digerido-anonimizar-ip.conf" /etc/nginx/conf.d/
verde "  snippets generados"

# ── 4. Vhost ───────────────────────────────────────────────────────────────
info "instalando vhost para $DOMINIO"
VHOST=/etc/nginx/sites-available/digerido
sed -e "s/DOMINIO/$DOMINIO/g" -e "s/UMAMI_HOST/$UMAMI_HOST/g" \
  "$AQUI/nginx/digerido.conf" > "$VHOST"

# nginx antiguo: http2 va en el listen.
if ! version_mayor_o_igual "$VERSION_NGINX" "1.25.1"; then
  sed -i 's/^\(\s*listen \(\[::\]:\)\?443 ssl\);$/\1 http2;/' "$VHOST"
fi

ln -sfn "$VHOST" /etc/nginx/sites-enabled/digerido
rm -f /etc/nginx/sites-enabled/default

# ── 5. Certificado ─────────────────────────────────────────────────────────
# El vhost referencia los .pem, así que `nginx -t` falla hasta que existan.
# Se arranca con una config mínima en HTTP, se pide el cert y recién después se
# valida el vhost completo.
if [[ ! -d "/etc/letsencrypt/live/$DOMINIO" ]]; then
  info "pidiendo certificado para $DOMINIO"
  rm -f /etc/nginx/sites-enabled/digerido
  cat > /etc/nginx/sites-available/digerido-acme <<CONF
server {
    listen 80;
    server_name $DOMINIO www.$DOMINIO;
    root /var/www/certbot;
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
}
CONF
  ln -sfn /etc/nginx/sites-available/digerido-acme /etc/nginx/sites-enabled/
  nginx -t && systemctl reload nginx

  # `--webroot` en vez del plugin de nginx: no toca la config, así el vhost
  # definitivo queda exactamente como lo dejó el repo.
  certbot certonly --webroot -w /var/www/certbot \
    -d "$DOMINIO" -d "www.$DOMINIO" \
    --non-interactive --agree-tos --register-unsafely-without-email \
    || { rojo "certbot falló. ¿El DNS de $DOMINIO ya apunta a este servidor?"; exit 1; }

  rm -f /etc/nginx/sites-enabled/digerido-acme
  ln -sfn "$VHOST" /etc/nginx/sites-enabled/digerido
fi

# certbot instala estos dos si usó el plugin de nginx; con --webroot hay que
# asegurarse de que existan, porque el vhost los incluye.
[[ -f /etc/letsencrypt/options-ssl-nginx.conf ]] || \
  curl -fsSL https://raw.githubusercontent.com/certbot/certbot/main/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf \
    -o /etc/letsencrypt/options-ssl-nginx.conf
[[ -f /etc/letsencrypt/ssl-dhparams.pem ]] || \
  openssl dhparam -out /etc/letsencrypt/ssl-dhparams.pem 2048

# ── 6. sudo acotado para el reload del deploy ──────────────────────────────
# El workflow corre `sudo nginx -s reload` para purgar la caché de /data/.
# Se habilita ESE comando y nada más: sudo total para un usuario de CI es una
# escalada de privilegios esperando ocurrir.
cat > /etc/sudoers.d/digerido-deploy <<CONF
$USUARIO_DEPLOY ALL=(root) NOPASSWD: /usr/sbin/nginx -s reload
CONF
chmod 440 /etc/sudoers.d/digerido-deploy
visudo -c -f /etc/sudoers.d/digerido-deploy >/dev/null

# ── Verificación ───────────────────────────────────────────────────────────
info "validando configuración"
nginx -t
systemctl reload nginx
systemctl enable nginx --quiet

echo
verde "Listo. https://$DOMINIO"
echo
cat <<RESUMEN
Secrets que hay que cargar en GitHub (Settings → Secrets → Actions):

  SSH_HOST          $(hostname -I | awk '{print $1}')
  SSH_USUARIO       $USUARIO_DEPLOY
  SSH_CLAVE_PRIVADA la clave privada cuyo .pub agregues a
                    /home/$USUARIO_DEPLOY/.ssh/authorized_keys
  SSH_HOST_KEY      la salida de:
                    ssh-keyscan -t ed25519 $DOMINIO

Falta:
  · agregar la clave pública de deploy a authorized_keys
  · confirmar que astro.config.mjs tenga site: 'https://$DOMINIO'
RESUMEN
