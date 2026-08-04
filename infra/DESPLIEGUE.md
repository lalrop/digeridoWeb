# Desplegar digerido en un VPS de Hostinger

De cero a `https://tu-dominio` con deploy automático en cada push a `main`.

Son **seis pasos**, unos 20 minutos. Los pasos 1 y 2 son en el panel de
Hostinger; el resto por SSH y en GitHub.

---

## 0. Qué se va a montar

```
GitHub Actions (en cada push a main)
   ├─ tests de pipeline + build + Lighthouse
   └─ rsync → /var/www/digerido/releases/<sha>/
              └─ symlink atómico → /var/www/digerido/actual
                                    └─ Nginx sirve desde acá
```

Sin base de datos, sin backend, sin Docker. El sitio es HTML estático: un VPS
básico de Hostinger (1 vCPU / 4 GB) queda enorme para esto.

**El deploy es atómico.** Sube a un directorio nuevo y recién al final mueve un
symlink, así que no existe el instante con medio sitio subido. Y como conserva
las últimas cinco releases, volver atrás es cambiar un symlink, no reconstruir.

---

## 1. Elegir el dominio

Dos opciones, y conviene decidirla ahora porque queda en la config:

| Opción | Cuándo |
|---|---|
| Dominio propio (`digerido.cl`) | Es una publicación con identidad. Lo recomendado. |
| Subdominio de lo que ya tenés (`digerido.budgt.cl`) | Para probar sin comprar nada. |

Con el dominio decidido, cambialo en **un solo lugar** del repo:

```js
// apps/web/astro.config.mjs
site: 'https://digerido.cl',   // ← acá
```

Alimenta las URLs canónicas, el RSS, el sitemap y las imágenes OG. Si queda
mal, los enlaces que se compartan apuntan a otro lado.

---

## 2. Apuntar el DNS

En el panel de Hostinger → **Dominios → DNS / Nameservers**, creá dos registros
apuntando a la IP de tu VPS (la ves en **VPS → Overview**):

| Tipo | Nombre | Valor |
|---|---|---|
| A | `@` | `<IP del VPS>` |
| A | `www` | `<IP del VPS>` |

**Esperá a que propague antes del paso 4.** El certificado se valida por HTTP
contra el dominio, así que si el DNS todavía no resuelve, certbot falla. Para
comprobar:

```bash
dig +short digerido.cl        # tiene que devolver la IP del VPS
```

Suele tardar entre 5 minutos y una hora.

---

## 3. Entrar al VPS y clonar el repo

En **VPS → SSH access** están el usuario y la IP. Desde tu máquina:

```bash
ssh root@<IP-del-VPS>
```

Ya adentro:

```bash
apt-get update && apt-get install -y git
git clone https://github.com/lalrop/digeridoWeb.git /opt/digerido
cd /opt/digerido
```

> El repo en `/opt/digerido` es solo para tener los scripts de infraestructura a
> mano. El sitio **no** se construye en el VPS: lo construye GitHub Actions y
> llega por rsync. El VPS no necesita Node ni pnpm.

---

## 4. Correr el instalador

```bash
sudo ./infra/instalar-vps.sh digerido.cl deploy
```

Un solo comando, idempotente: si algo falla lo corregís y lo volvés a correr.

Hace lo siguiente:

1. instala nginx, certbot y rsync;
2. crea `/var/www/digerido/{releases,actual}` y el usuario `deploy`;
3. **detecta qué soporta este servidor** y genera la config acorde;
4. instala el vhost con tu dominio ya sustituido;
5. pide el certificado TLS a Let's Encrypt;
6. habilita `sudo` sin contraseña **solo** para `nginx -s reload`.

### Por qué detecta en vez de asumir

Tres cosas de la config de Nginx dependen del servidor, y ponerlas fijas hace
que Nginx **no arranque**:

- **`http2 on` existe desde nginx 1.25.1.** Ubuntu 24.04 trae 1.24, donde esa
  directiva no existe y http2 va en el `listen`. El instalador compara la
  versión y escribe la forma correcta.
- **Brotli no viene por defecto.** Es un módulo aparte (`libnginx-mod-brotli`,
  Ubuntu 24.04+). Si no está, el instalador deja solo gzip en vez de dejar una
  directiva que Nginx rechaza. Perdés ~15 % de compresión, nada más.
- **La anonimización de IP necesita un `map` en el contexto `http`,** no dentro
  del `server`. Va a `/etc/nginx/conf.d/`.

Al terminar imprime los cuatro secrets que necesita GitHub. Anotalos.

---

## 5. La clave SSH de deploy

GitHub Actions necesita entrar al VPS. Se usa una clave dedicada, **no** la tuya
personal: si se filtra, se revoca sin tocar tu acceso.

En **tu máquina**:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/digerido-deploy -C "github actions → digerido" -N ""
```

Instalá la pública en el VPS:

```bash
ssh-copy-id -i ~/.ssh/digerido-deploy.pub deploy@<IP-del-VPS>
# si ssh-copy-id no está:
cat ~/.ssh/digerido-deploy.pub | ssh root@<IP> "cat >> /home/deploy/.ssh/authorized_keys"
```

Probá que funcione **antes** de seguir:

```bash
ssh -i ~/.ssh/digerido-deploy deploy@<IP-del-VPS> "echo ok && ls /var/www/digerido"
```

Y sacá la host key, que es lo que evita un man-in-the-middle en el deploy:

```bash
ssh-keyscan -t ed25519 digerido.cl
```

---

## 6. Cargar los secrets en GitHub

En **Settings → Secrets and variables → Actions → New repository secret**:

| Secret | Valor |
|---|---|
| `SSH_HOST` | la IP del VPS (o el dominio) |
| `SSH_USUARIO` | `deploy` |
| `SSH_CLAVE_PRIVADA` | el contenido **completo** de `~/.ssh/digerido-deploy`, incluidas las líneas `BEGIN`/`END` |
| `SSH_HOST_KEY` | la línea que devolvió `ssh-keyscan` |

Y creá el *environment* `produccion` en **Settings → Environments**: el job de
deploy lo referencia, y ahí podés exigir aprobación manual si más adelante
querés una puerta antes de publicar.

### Opcionales

| Secret | Para qué |
|---|---|
| `NTFY_URL` | avisos cuando una fuente cambia en origen (§13). Ej: `https://ntfy.sh/digerido-<algo-random>` |
| `LHCI_GITHUB_APP_TOKEN` | que Lighthouse comente los resultados en los PRs |

Sin `NTFY_URL` el chequeo semanal igual abre un issue; solo no manda push.

---

## 7. Desplegar

```bash
git checkout main
git merge claude/digerido-project-skeleton-hy2w4j
git push origin main
```

Mirá el progreso en la pestaña **Actions**. El pipeline corre cuatro jobs en
orden: `pipeline` → `web` → `lighthouse` → `desplegar`. El criterio de salida de
la Fase 0 es que todo eso termine en **menos de 3 minutos**.

Después:

```bash
curl -I https://digerido.cl
ssh deploy@<IP> "ls -l /var/www/digerido/actual"   # → apunta al sha del commit
```

---

## Operación

### Volver atrás

Un rollback es un symlink, no un deploy:

```bash
ssh deploy@<IP>
ls -1dt /var/www/digerido/releases/*        # las 5 últimas, más nueva primero
ln -sfn /var/www/digerido/releases/<sha-anterior> /var/www/digerido/actual.nuevo
mv -Tf /var/www/digerido/actual.nuevo /var/www/digerido/actual
```

Instantáneo y sin reconstruir nada.

### Renovación del certificado

Certbot instala su propio timer. Comprobá que esté activo:

```bash
systemctl list-timers | grep certbot
certbot renew --dry-run
```

### Logs

```bash
tail -f /var/log/nginx/digerido.access.log   # con la IP anonimizada
tail -f /var/log/nginx/digerido.error.log
```

### Analítica (opcional)

La CSP del vhost ya deja pasar `umami.<tu-dominio>`. Cuando levantes Umami,
descomentá el `<script>` en `apps/web/src/layouts/Base.astro` y poné el
`data-website-id`. Sin cookies, sin banner (§9).

---

## Si algo falla

| Síntoma | Causa habitual |
|---|---|
| `certbot` falla en el paso 4 | El DNS no propagó. `dig +short tu-dominio` tiene que dar la IP del VPS. |
| `nginx -t`: *unknown directive "brotli"* | El instalador no corrió, o se editó el vhost a mano. Volvé a correrlo. |
| `nginx -t`: *unknown variable "remote_addr_anon"* | Falta `/etc/nginx/conf.d/digerido-anonimizar-ip.conf`. Lo copia el instalador. |
| `nginx -t`: *unknown directive "http2"* | nginx < 1.25.1 con la config moderna. Volvé a correr el instalador: detecta la versión. |
| El job `desplegar` falla en `configurar ssh` | `SSH_CLAVE_PRIVADA` incompleta (faltan las líneas BEGIN/END) o `SSH_HOST_KEY` mal copiada. |
| `rsync`: *Permission denied* | `/var/www/digerido` no es del usuario `deploy`. `chown -R deploy:deploy /var/www/digerido`. |
| `sudo: a password is required` en el reload | Falta `/etc/sudoers.d/digerido-deploy`. Lo crea el instalador. |
| El sitio carga pero se ve con otra tipografía | Las fuentes de marca no están en `apps/web/public/fuentes/`. Ver el README. |
| El deploy pasa pero el sitio no cambia | Caché del navegador. El HTML se sirve con `must-revalidate`; probá con `curl -I`. |

### Seguridad mínima del VPS

Un VPS recién creado con SSH por contraseña recibe intentos de acceso desde el
primer día. Vale hacer esto una vez:

```bash
apt-get install -y ufw fail2ban
ufw allow OpenSSH && ufw allow 'Nginx Full' && ufw --force enable

# Con la clave de deploy ya probada, deshabilitá el acceso por contraseña:
sed -i 's/^#\?PasswordAuthentication .*/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl reload ssh
```

No lo hagas antes de confirmar que entrás por clave, o te quedás afuera.

---

## Lo que este despliegue deliberadamente no tiene

- **Sin Docker.** Servir HTML estático no necesita un runtime containerizado.
- **Sin Node en el VPS.** El build ocurre en CI; el servidor solo sirve archivos.
- **Sin base de datos.** Si alguna digestión necesita consultas dinámicas, §9
  dice: primero DuckDB-WASM en el cliente, y solo si eso falla, un endpoint.
- **Sin CDN.** Un sitio de 440 KB con caché `immutable` a un año no lo necesita
  todavía. Cuando el tráfico lo justifique, Cloudflare adelante de Nginx no
  requiere cambiar nada de esto.
