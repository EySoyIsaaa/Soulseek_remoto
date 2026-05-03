# private-downloader

Web privada y ligera para listar/descargar archivos de `slskd` sin exponer `slskd` directamente a internet.

## Qué hace
- Backend FastAPI en `0.0.0.0:8000`.
- Frontend simple (HTML/CSS/JS) optimizado para móvil/PC.
- Lista archivos recursivos de `/home/server/slskd/downloads`.
- Descarga forzada (`application/octet-stream` + `attachment`).
- Auth por token (`PRIVATE_DOWNLOADER_TOKEN`).
- Limpieza automática: borra archivos >15 min y carpetas vacías.

## Instalación
```bash
cd /home/server/slskd/private-downloader
chmod +x install.sh
./install.sh
```

## Uso
1. Configura token en `/home/server/slskd/private-downloader/.env`.
2. Reinicia servicio:
```bash
sudo systemctl restart private-downloader.service
```
3. Abre en LAN:
- `http://10.0.0.45:8000`

## Endpoints
- `GET /` -> frontend
- `GET /files` -> JSON de archivos (requiere Bearer token)
- `GET /download/{path}?token=...` -> descarga forzada

## Seguridad aplicada
- Validación anti path traversal.
- Nunca permite salir de `/home/server/slskd/downloads`.
- No expone `slskd` (`5030`) al exterior.
- Solo expón, si hace falta, el puerto `8000` + token.

## Acceso remoto recomendado

### Opción A (recomendada): Tailscale
1. Instala Tailscale en servidor y cliente.
2. Inicia sesión en ambos con misma tailnet.
3. Verifica IP Tailscale del servidor:
```bash
tailscale ip -4
```
4. Accede desde fuera por:
- `http://<IP_TAILSCALE_DEL_SERVIDOR>:8000`

**Importante:** no abrir puerto 5030 en router/firewall.

### Opción B (opcional): Cloudflare Tunnel
1. Instala `cloudflared` en servidor.
2. Crea túnel autenticado y DNS público.
3. En configuración del túnel, apunta **solo** a:
- `http://127.0.0.1:8000`
4. Protege acceso con Cloudflare Access (además del token interno).

Ejemplo de `config.yml`:
```yaml
tunnel: private-downloader
credentials-file: /home/server/.cloudflared/<ID>.json

ingress:
  - hostname: descargas.tudominio.com
    service: http://127.0.0.1:8000
  - service: http_status:404
```

## Operación
- Estado servicio:
```bash
sudo systemctl status private-downloader.service
```
- Logs:
```bash
journalctl -u private-downloader.service -f
```
- Cron limpieza:
```bash
crontab -l
```
