# Poner digerido.cl en línea

Guía completa, paso a paso, sin dar por sabido nada. Al final vas a tener
**https://digerido.cl** funcionando, y cada cambio que subas a GitHub se
publicará solo.

**Tiempo:** unos 40 minutos, más la espera del DNS (entre 10 minutos y 2 horas).

---

## Antes de empezar

Necesitás tener a mano:

- [ ] Acceso al panel de Hostinger (hPanel)
- [ ] Saber **dónde está registrado digerido.cl**: en Hostinger o en NIC Chile
      (los `.cl` a menudo se registran directo en NIC Chile). Lo resolvemos en
      el paso 2.
- [ ] Acceso a tu cuenta de GitHub, en el repositorio `lalrop/digeridoWeb`
- [ ] Una terminal en tu computador:
  - **Mac:** la app **Terminal** (Cmd+Espacio, escribí "terminal")
  - **Windows:** **PowerShell** (botón inicio, escribí "powershell")
  - **Linux:** la terminal que uses

### Cómo leer esta guía

- Los bloques con fondo gris son **comandos**: se copian y pegan tal cual.
- Cuando un comando dice `<algo>`, hay que **reemplazarlo** incluido los
  `<>`. Ejemplo: `ssh root@<IP>` → `ssh root@72.60.15.4`
- Después de cada comando importante digo **qué deberías ver**. Si ves otra
  cosa, andá a la sección «Si algo falla» al final.
- `sudo` significa "hacer esto como administrador". Es normal que lo pida.

### Qué vamos a construir

```
Vos hacés un cambio → lo subís a GitHub
                          ↓
                   GitHub Actions corre los tests y construye el sitio
                          ↓
                   Lo copia al VPS por SSH
                          ↓
                   Nginx lo sirve en https://digerido.cl
```

El VPS **no** construye el sitio: solo guarda archivos y los entrega. Por eso no
hace falta instalar Node ni nada de desarrollo ahí.

---

## Paso 1 · Crear la rama `main` en GitHub

**Por qué:** hoy el repositorio tiene una sola rama, llamada
`claude/digerido-project-skeleton-hy2w4j`. El sistema de despliegue automático
está configurado para publicar cuando algo llega a una rama llamada **`main`**,
que todavía no existe. Sin este paso, el despliegue nunca se dispara.

Abrí una terminal en tu computador y traé el proyecto:

```bash
cd ~
git clone https://github.com/lalrop/digeridoWeb.git
cd digeridoWeb
```

**Deberías ver:** `Cloning into 'digeridoWeb'...` y luego varias líneas de
progreso.

Ahora creá `main` a partir de lo que ya está hecho y subila:

```bash
git checkout -b main
git push -u origin main
```

**Deberías ver:** `* [new branch] main -> main`

Por último, decile a GitHub que `main` es la rama principal:

1. Andá a `https://github.com/lalrop/digeridoWeb/settings`
2. En la sección **Default branch**, apretá el ícono de las dos flechas (⇄)
3. Elegí **main** y confirmá

> **Nota:** al hacer el `push` a `main`, GitHub va a intentar desplegar y va a
> **fallar** — todavía no existen ni el servidor configurado ni las claves. Es
> esperado. Lo arreglamos en los pasos 4 a 6.

---

## Paso 2 · Apuntar digerido.cl a tu servidor

**Por qué:** un dominio es solo un nombre. Hay que decirle a internet a qué
servidor corresponde. Eso se hace con dos registros «A».

### 2.1 Anotá la IP de tu VPS

1. Entrá a **hPanel** → menú **VPS** → hacé clic en tu servidor
2. En la pantalla principal (**Overview** o **Panel**) aparece **IP address**
3. Anotala. Es algo como `72.60.15.4`

De acá en adelante, cada vez que escriba `<IP>` significa ese número.

### 2.2 Averiguá dónde se administra el DNS

Esto es lo que decide dónde poner los registros. En tu terminal:

```bash
whois digerido.cl | grep -i "nombre\|registrar\|name server\|nserver"
```

Si el comando no existe en tu sistema, entrá a
`https://www.nic.cl/registry/Whois.do` y buscá `digerido.cl`.

Fijate en los **name servers** (o *servidores de nombre*):

| Si los name servers dicen… | Entonces el DNS se administra en… |
|---|---|
| `ns1.dns-parking.com` o algo con `hostinger` | **Hostinger** → seguí en 2.3-A |
| Cualquier otra cosa (NIC Chile u otro proveedor) | **Ahí** → seguí en 2.3-B |

### 2.3-A · Si el DNS está en Hostinger

1. hPanel → **Dominios** → hacé clic en `digerido.cl`
2. Buscá **DNS / Nameservers** (o **Zona DNS**)
3. Creá o editá estos dos registros:

| Tipo | Nombre | Apunta a | TTL |
|---|---|---|---|
| A | `@` | `<IP>` | 3600 |
| A | `www` | `<IP>` | 3600 |

Si ya existen registros A con otro valor, **editalos** en vez de agregar otro:
dos registros A con IPs distintas hacen que el sitio funcione a veces sí y a
veces no.

### 2.3-B · Si el DNS está en NIC Chile u otro proveedor

Tenés dos caminos. **El más simple** es delegar el DNS a Hostinger:

1. En hPanel → **Dominios** → `digerido.cl`, copiá los name servers que te da
   Hostinger (suelen ser `ns1.dns-parking.com` y `ns2.dns-parking.com`)
2. Entrá a `https://www.nic.cl` con tu cuenta → tu dominio → **Modificar
   servidores de nombre**
3. Reemplazá los actuales por los de Hostinger y guardá
4. Esperá la propagación y volvé a **2.3-A**

**O bien**, si preferís dejar el DNS donde está, creá los mismos dos registros A
del cuadro de 2.3-A en el panel de tu proveedor actual. El resultado es
idéntico.

### 2.4 Esperá y comprobá

Esto **no es inmediato**. Comprobá cada tanto:

```bash
nslookup digerido.cl
```

**Deberías ver** tu `<IP>` en la línea `Address:`. Mientras diga
`can't find` o muestre otra IP, seguí esperando.

> ⚠️ **No sigas al paso 4 hasta que esto funcione.** El certificado de seguridad
> (el candado del navegador) se valida contra el dominio, y si el DNS todavía no
> resuelve, falla.

---

## Paso 3 · Entrar al servidor

**Por qué:** hay que instalar el servidor web. Se hace por SSH, que es una
terminal remota: escribís en tu computador y se ejecuta allá.

### 3.1 Conseguí la contraseña de root

hPanel → **VPS** → tu servidor → buscá **SSH access** o **Root password**. Si no
la recordás, ahí mismo podés cambiarla.

### 3.2 Conectate

```bash
ssh root@<IP>
```

La primera vez pregunta:

```
The authenticity of host '...' can't be established.
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

Escribí `yes` y Enter. Después pide la contraseña de root.

> **Al escribir la contraseña no se ve nada**, ni asteriscos. Es normal:
> escribila completa y apretá Enter.

**Deberías ver** algo como `root@srv123456:~#`. Ese es el servidor: todo lo que
escribas de acá en adelante ocurre allá.

### 3.3 Traé el proyecto al servidor

```bash
apt-get update
apt-get install -y git
git clone https://github.com/lalrop/digeridoWeb.git /opt/digerido
cd /opt/digerido
```

**Deberías ver** `Cloning into '/opt/digerido'...` y terminar sin errores.

> Esto es solo para tener los scripts de instalación a mano. El sitio en sí no se
> construye acá.

---

## Paso 4 · Instalar y configurar todo

Un solo comando hace el resto:

```bash
sudo ./infra/instalar-vps.sh digerido.cl deploy
```

Toma dos o tres minutos. Va mostrando lo que hace:

```
▸ instalando paquetes
▸ preparando /var/www/digerido
  usuario deploy creado
  placeholder instalado
▸ nginx 1.24.0
  http2: en las líneas listen (nginx antiguo)
  snippets generados
▸ instalando vhost para digerido.cl
▸ pidiendo certificado para digerido.cl
▸ validando configuración
Listo. https://digerido.cl
```

**Deberías ver** al final la línea verde `Listo. https://digerido.cl`, seguida de
un resumen con los datos que necesitaremos en el paso 6. **Dejá esa ventana
abierta** o copiá el resumen a un lado.

### Qué hizo, en castellano

1. Instaló **Nginx** (el servidor web), **certbot** (los certificados) y
   **rsync** (la copia de archivos).
2. Creó la carpeta `/var/www/digerido` y un usuario llamado `deploy`, que es el
   que va a usar GitHub. **No** usa root: si esa clave se filtrara, el daño
   posible es mucho menor.
3. **Detectó** qué soporta tu servidor y escribió la configuración acorde. Esto
   importa: tres directivas de Nginx dependen de la versión y de los módulos
   instalados, y con la variante equivocada Nginx **no arranca**. El script
   compara la versión en vez de suponer.
4. Pidió el certificado gratuito a Let's Encrypt. Es el candado del navegador, y
   se renueva solo.
5. Le dio al usuario `deploy` permiso de administrador **para un solo comando**
   (recargar Nginx) y nada más.

Ahora comprobá que quedó bien:

```bash
sudo ./infra/verificar-vps.sh digerido.cl
```

**Deberías ver** una lista de ✓ verdes y al final
`Todo en orden: N comprobaciones pasaron.`

Es esperado que haya **una** ✗ en «claves autorizadas»: eso es el paso 5.

Si abrís `https://digerido.cl` en el navegador vas a ver una página que dice
*«Servidor listo. Esperando el primer despliegue»*, con el candado cerrado. Eso
significa que el servidor funciona y falta conectar GitHub.

---

## Paso 5 · Darle a GitHub una llave del servidor

**Por qué:** GitHub necesita entrar al servidor para copiar el sitio. En vez de
darle una contraseña, se usa un par de claves: una privada (que guarda GitHub) y
una pública (que se instala en el servidor). Se crea una **exclusiva para esto**:
si algún día se filtra, se revoca sin afectar tu acceso personal.

### 5.1 Salí del servidor

```bash
exit
```

**Deberías ver** `logout` y volver al prompt de **tu computador**. Es importante:
los siguientes comandos van en tu máquina, no en el VPS.

### 5.2 Creá el par de claves

```bash
ssh-keygen -t ed25519 -f ~/.ssh/digerido-deploy -C "github actions digerido" -N ""
```

**Deberías ver** `Your identification has been saved in ...` y un dibujito de
cuadraditos (es normal, es una huella visual).

Quedan dos archivos:
- `~/.ssh/digerido-deploy` → la clave **privada**. Va a GitHub. No la compartas.
- `~/.ssh/digerido-deploy.pub` → la **pública**. Va al servidor.

### 5.3 Instalá la pública en el servidor

**En Mac o Linux:**

```bash
ssh-copy-id -i ~/.ssh/digerido-deploy.pub deploy@<IP>
```

Va a pedir la contraseña de root... y probablemente falle, porque el usuario
`deploy` no tiene contraseña. Si eso pasa, usá este método, que funciona
siempre (Mac, Linux y Windows):

```bash
ssh root@<IP> "cat >> /home/deploy/.ssh/authorized_keys" < ~/.ssh/digerido-deploy.pub
```

Pide la contraseña de **root** y no muestra nada al terminar. Eso es éxito.

### 5.4 Probá que funcione

Esto es importante: **si no funciona acá, tampoco va a funcionar en GitHub**.

```bash
ssh -i ~/.ssh/digerido-deploy deploy@<IP> "echo FUNCIONA && ls /var/www/digerido"
```

**Deberías ver:**

```
FUNCIONA
actual
releases
```

Si pide contraseña, la clave no quedó instalada: repetí 5.3.

### 5.5 Sacá la huella del servidor

Sirve para que GitHub verifique que se está conectando al servidor correcto y no
a un impostor. **Ojo:** tiene que ser contra la `<IP>`, no contra el dominio —
el despliegue se conecta a `$SSH_HOST` (la IP), y `known_hosts` solo sirve si
la huella quedó guardada bajo ese mismo nombre:

```bash
ssh-keyscan -t ed25519 <IP>
```

**Deberías ver** una línea larga que empieza con `<IP> ssh-ed25519 AAAA…`.
Copiala **completa** (ignorá las líneas que empiezan con `#`).

---

## Paso 6 · Guardar los datos en GitHub

**Por qué:** GitHub necesita la IP, el usuario y la clave, pero eso no puede
estar escrito en el código. Se guardan como *secrets*: valores cifrados que solo
ve el proceso de despliegue.

### 6.1 Cargá los cuatro secrets

Andá a:

```
https://github.com/lalrop/digeridoWeb/settings/secrets/actions
```

Apretá **New repository secret** y creá estos cuatro, uno por uno. **El nombre
tiene que ser exacto**, en mayúsculas:

| Name | Secret (el valor) |
|---|---|
| `SSH_HOST` | tu `<IP>`, por ejemplo `72.60.15.4` |
| `SSH_USUARIO` | `deploy` |
| `SSH_CLAVE_PRIVADA` | el contenido **completo** del archivo `~/.ssh/digerido-deploy` |
| `SSH_HOST_KEY` | la línea que copiaste en 5.5 |

Para ver el contenido de la clave privada y copiarlo:

```bash
cat ~/.ssh/digerido-deploy
```

**Copiá todo**, desde `-----BEGIN OPENSSH PRIVATE KEY-----` hasta
`-----END OPENSSH PRIVATE KEY-----` **incluidas esas dos líneas** y el salto de
línea final. Es el error más habitual: pegar solo el medio no sirve.

### 6.2 Creá el entorno `produccion`

1. Andá a `https://github.com/lalrop/digeridoWeb/settings/environments`
2. **New environment**
3. Nombre: `produccion` (sin tilde, tal cual)
4. **Configure environment** y guardá

El proceso de despliegue lo referencia por nombre. Más adelante, si querés que
cada publicación necesite tu aprobación manual, se activa acá.

### 6.3 Opcionales

No hacen falta para publicar:

| Secret | Para qué |
|---|---|
| `NTFY_URL` | Aviso al teléfono cuando un organismo reemplaza un documento. Andá a `https://ntfy.sh`, inventá un nombre difícil de adivinar y usá `https://ntfy.sh/ese-nombre` |
| `LHCI_GITHUB_APP_TOKEN` | Que el informe de rendimiento aparezca como comentario en los cambios |

Sin `NTFY_URL`, el chequeo semanal igual abre un *issue* en GitHub. Solo no te
manda notificación.

---

## Paso 7 · Publicar

Ya está todo. Sacá el despliegue que había fallado en el paso 1:

1. Andá a `https://github.com/lalrop/digeridoWeb/actions`
2. Hacé clic en la ejecución que falló (la de arriba, con ✗ roja)
3. Botón **Re-run all jobs**, arriba a la derecha

**Deberías ver** cuatro etapas ponerse verdes en orden:

```
✓ tests de pipeline      (los datos cuadran)
✓ build y presupuesto    (el sitio se construye y no pesa de más)
✓ lighthouse             (velocidad y accesibilidad)
✓ desplegar al VPS       (copia al servidor)
```

Toma unos 3 minutos. Cuando termine, abrí **https://digerido.cl**.

Y confirmá desde el servidor que quedó apuntando al commit correcto:

```bash
ssh deploy@<IP> "ls -l /var/www/digerido/actual"
```

**Deberías ver** una flecha a una carpeta con un nombre largo de letras y
números: ese es el identificador del commit publicado.

### De acá en adelante

Cada vez que quieras publicar un cambio:

```bash
cd ~/digeridoWeb
git add -A
git commit -m "describí qué cambiaste"
git push
```

Y listo. En tres minutos está en línea. Si algún test falla, **no se publica**:
el sitio en vivo queda intacto.

---

## Operación diaria

### Si algo salió mal y querés volver atrás

Volver a la versión anterior es instantáneo, no hay que reconstruir nada:

```bash
ssh deploy@<IP>
ls -1dt /var/www/digerido/releases/*/          # las 5 últimas, la más nueva primero
ln -sfn /var/www/digerido/releases/<la-anterior> /var/www/digerido/actual.nuevo
mv -Tf /var/www/digerido/actual.nuevo /var/www/digerido/actual
```

### Revisar que todo siga bien

```bash
ssh root@<IP> "cd /opt/digerido && sudo ./infra/verificar-vps.sh digerido.cl"
```

Vale correrlo una vez al mes, o cuando algo se comporte raro.

### Ver quién visita

```bash
ssh root@<IP> "tail -f /var/log/nginx/digerido.access.log"
```

Las IPs aparecen con el último número en cero: el sitio no guarda direcciones
completas.

### El certificado

Se renueva solo. Para comprobarlo:

```bash
ssh root@<IP> "certbot renew --dry-run"
```

**Deberías ver** `Congratulations, all simulated renewals succeeded`.

---

## Si algo falla

Corré primero el diagnóstico, que suele señalar exactamente el problema:

```bash
ssh root@<IP> "cd /opt/digerido && sudo ./infra/verificar-vps.sh digerido.cl"
```

| Lo que ves | Qué pasa | Cómo se arregla |
|---|---|---|
| `certbot` falla en el paso 4 | El DNS no propagó todavía | `nslookup digerido.cl` tiene que devolver tu IP. Esperá y volvé a correr el instalador. |
| `Permission denied (publickey)` al hacer `ssh deploy@` | La clave pública no llegó al servidor | Repetí el paso 5.3 con el método `cat >>`. |
| El paso «configurar ssh» falla en GitHub | `SSH_CLAVE_PRIVADA` incompleta | Volvé a copiar el archivo entero, con las líneas `BEGIN` y `END`. |
| `Host key verification failed` | `SSH_HOST_KEY` mal copiada, o sacada contra el dominio en vez de la `<IP>` | Volvé a correr `ssh-keyscan -t ed25519 <IP>` (contra la IP, no `digerido.cl`) y pegá la línea completa. |
| `rsync: Permission denied` | La carpeta no es del usuario `deploy` | `ssh root@<IP> "chown -R deploy:deploy /var/www/digerido"` |
| `sudo: a password is required` | Falta el permiso acotado | Volvé a correr el instalador. |
| `nginx: unknown directive "brotli"` | Se editó la configuración a mano | Volvé a correr el instalador: genera solo lo que el servidor soporta. |
| `nginx: unknown variable "remote_addr_anon"` | Falta un archivo en `/etc/nginx/conf.d/` | Volvé a correr el instalador. |
| El sitio carga sin estilos o con otra tipografía | Faltan las fuentes de marca | Es esperado por ahora: no van en el repositorio por licencia. Ver el README. |
| El despliegue dice ✓ pero el sitio no cambia | Caché del navegador | Probá `curl -I https://digerido.cl` o abrí una ventana privada. |
| No aparece nada en la pestaña Actions | Los workflows están deshabilitados | En **Settings → Actions → General**, elegí *Allow all actions*. |

### Seguridad mínima del servidor

Un VPS nuevo recibe intentos de acceso desde el primer día. Vale hacer esto una
vez, **después** de confirmar que el paso 5.4 funciona:

```bash
ssh root@<IP>
apt-get install -y ufw fail2ban
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable
```

Y, solo si ya entrás por clave sin problemas, desactivá el ingreso por
contraseña:

```bash
sed -i 's/^#\?PasswordAuthentication .*/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl reload ssh
```

> ⚠️ No hagas esto último antes de comprobar que entrás por clave, o te quedás
> afuera de tu propio servidor.

---

## Lo que este despliegue no tiene, a propósito

- **Sin Docker.** Servir archivos estáticos no necesita contenedores.
- **Sin Node en el servidor.** El sitio se construye en GitHub; el VPS entrega
  archivos y nada más. Menos que mantener y menos que pueda romperse.
- **Sin base de datos.** Si alguna digestión llega a necesitar consultas
  dinámicas, primero se intenta resolver en el navegador del lector.
- **Sin CDN.** Un sitio de 440 KB con caché de un año no lo necesita todavía.
  Cuando el tráfico lo justifique, poner Cloudflare adelante no requiere cambiar
  nada de esto.
