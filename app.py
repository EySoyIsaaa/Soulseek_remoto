import os
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

BASE_DIR = Path("/home/server/slskd/downloads").resolve()
APP_TOKEN = os.getenv("PRIVATE_DOWNLOADER_TOKEN", "cambia-este-token")

app = FastAPI(title="private-downloader")

MENU_PAGE = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Private Downloader</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin:0; background:#111; color:#eee; }
    .wrap { max-width:720px; margin:0 auto; padding:18px; }
    h1 { font-size:1.5rem; margin:8px 0 16px; }
    .card { display:block; text-decoration:none; color:#fff; background:#1c1c1c; border:1px solid #333; border-radius:16px; padding:18px; margin-bottom:14px; }
    .title { font-size:1.2rem; font-weight:700; margin-bottom:8px; }
    .desc { color:#bcbcbc; line-height:1.35; }
    .btn { margin-top:12px; display:inline-block; background:#2f80ed; border-radius:12px; padding:12px 16px; font-weight:700; }
  </style>
</head>
<body>
<div class="wrap">
  <h1>Private Downloader</h1>

  <a class="card" href="https://slskd.epicenterdsp.com" target="_blank" rel="noopener noreferrer">
    <div class="title">Buscar canciones</div>
    <div class="desc">Abre slskd completo para buscar y enviar descargas al servidor.</div>
    <div class="btn">Abrir slskd</div>
  </a>

  <a class="card" href="/downloads">
    <div class="title">Descargar canciones</div>
    <div class="desc">Descarga directamente a tu dispositivo los archivos temporales ya bajados.</div>
    <div class="btn">Ver descargas</div>
  </a>
</div>
</body>
</html>"""

DOWNLOADS_PAGE = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Private Downloader - Descargas</title>
  <style>
    :root { color-scheme: light dark; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; background:#111; color:#eee; }
    .wrap { max-width: 900px; margin: 0 auto; padding: 16px; }
    h1 { font-size: 1.4rem; margin: 8px 0 16px; }
    .bar { display:flex; gap:10px; margin-bottom: 14px; }
    button,input,a.back { font-size: 16px; border-radius: 12px; border:1px solid #444; padding: 12px; }
    input { flex: 1; background:#1e1e1e; color:#fff; }
    button { background:#2f80ed; color:#fff; font-weight:700; border:none; min-height:44px; }
    .secondary, a.back { background:#333; color:#fff; text-decoration:none; display:inline-flex; align-items:center; }
    .msg { margin: 8px 0 14px; color:#bbb; }
    .list { display:flex; flex-direction:column; gap:12px; }
    .card { background:#1b1b1b; border:1px solid #333; border-radius:14px; padding:12px; }
    .name { font-weight:700; word-break: break-word; }
    .meta { font-size:0.9rem; color:#aaa; margin:6px 0 10px; word-break: break-all; }
    .dl { width:100%; }
  </style>
</head>
<body>
<div class="wrap">
  <h1>Descargar canciones</h1>
  <div class="bar">
    <a class="back" href="/">Menú</a>
  </div>
  <div class="bar">
    <input id="token" placeholder="Token de acceso" />
    <button id="saveToken" class="secondary">Guardar</button>
  </div>
  <div class="bar">
    <button id="refresh">Actualizar</button>
  </div>
  <div id="msg" class="msg">Cargando...</div>
  <div id="list" class="list"></div>
</div>
<script>
const tokenInput = document.getElementById('token');
const msg = document.getElementById('msg');
const list = document.getElementById('list');
function formatSize(bytes){const u=['B','KB','MB','GB','TB'];let i=0,n=bytes;while(n>=1024&&i<u.length-1){n/=1024;i++;}return `${n.toFixed(i?1:0)} ${u[i]}`;}
function getToken(){return localStorage.getItem('pd_token')||'';}
function setToken(v){localStorage.setItem('pd_token',v);}
async function loadFiles(){
  const t=getToken();msg.textContent='Cargando archivos...';list.innerHTML='';
  const res=await fetch('/files',{headers:{'Authorization':`Bearer ${t}`}});
  if(res.status===401){msg.textContent='No autorizado. Revisa el token.';return;}
  if(!res.ok){msg.textContent='Error cargando archivos.';return;}
  const data=await res.json();
  if(!data.files.length){msg.textContent='No hay archivos disponibles ahora.';return;}
  msg.textContent=`${data.files.length} archivo(s) disponible(s).`;
  for(const f of data.files){
    const card=document.createElement('div');card.className='card';
    const dlUrl=`/download/${encodeURIComponent(f.path)}?token=${encodeURIComponent(t)}`;
    card.innerHTML=`<div class="name">${f.name}</div><div class="meta">Carpeta: ${f.folder||'/'}<br>Tamaño: ${formatSize(f.size)}</div><a href="${dlUrl}"><button class="dl">Descargar</button></a>`;
    list.appendChild(card);
  }
}
document.getElementById('saveToken').addEventListener('click',()=>{setToken(tokenInput.value.trim());loadFiles();});
document.getElementById('refresh').addEventListener('click',loadFiles);
tokenInput.value=getToken();loadFiles().catch(()=>{msg.textContent='Error de red.';});
</script>
</body>
</html>"""


def check_token(request: Request, token_query: str | None = None) -> None:
    auth = request.headers.get("Authorization", "")
    header_token = ""
    if auth.lower().startswith("bearer "):
        header_token = auth[7:].strip()
    token = token_query or header_token
    if token != APP_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


def secure_path(relative_path: str) -> Path:
    target = (BASE_DIR / relative_path).resolve()
    if not str(target).startswith(str(BASE_DIR) + os.sep):
        raise HTTPException(status_code=400, detail="Invalid path")
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return target


def iter_files():
    if not BASE_DIR.exists():
        return []
    files = []
    for p in BASE_DIR.rglob("*"):
        if p.is_file():
            rel = p.relative_to(BASE_DIR)
            files.append({
                "name": p.name,
                "folder": str(rel.parent) if str(rel.parent) != "." else "",
                "path": rel.as_posix(),
                "size": p.stat().st_size,
            })
    files.sort(key=lambda x: x["path"].lower())
    return files


@app.get("/", response_class=HTMLResponse)
def home():
    return MENU_PAGE


@app.get("/downloads", response_class=HTMLResponse)
def downloads_page():
    return DOWNLOADS_PAGE


@app.get("/files")
def list_files(request: Request):
    check_token(request)
    return JSONResponse({"files": iter_files()})


@app.get("/download/{file_path:path}")
def download(file_path: str, request: Request, token: str | None = None):
    check_token(request, token_query=token)
    path = secure_path(file_path)

    def file_iterator(chunk_size: int = 1024 * 1024):
        with path.open("rb") as f:
            while chunk := f.read(chunk_size):
                yield chunk

    filename = quote(path.name)
    headers = {
        "Content-Type": "application/octet-stream",
        "Content-Disposition": f"attachment; filename*=UTF-8''{filename}",
    }
    return StreamingResponse(file_iterator(), headers=headers, media_type="application/octet-stream")
