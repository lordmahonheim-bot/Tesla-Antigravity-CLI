#!/usr/bin/env python3
import os
import sqlite3
import xml.etree.ElementTree as ET
import zipfile
from html.parser import HTMLParser

import uvicorn
from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from starlette.middleware.cors import CORSMiddleware

HOST = os.environ.get("CALIBRE_SPARK_MCP_HOST", "127.0.0.1")
PORT = int(os.environ.get("CALIBRE_SPARK_MCP_PORT", "8081"))
TOKEN = os.environ.get("CALIBRE_SPARK_MCP_TOKEN", "no-oauth-required").strip()
TUNNEL_HOST = os.environ.get("CALIBRE_SPARK_TUNNEL_HOST", "").strip()

allowed_hosts = ["127.0.0.1", "127.0.0.1:*", "localhost", "localhost:*"]
allowed_origins = ["http://127.0.0.1:*", "http://localhost:*", "https://gemini.google.com"]
if TUNNEL_HOST:
    allowed_hosts += [TUNNEL_HOST, f"{TUNNEL_HOST}:*"]
    allowed_origins.append(f"https://{TUNNEL_HOST}")

security = TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    allowed_hosts=allowed_hosts,
    allowed_origins=allowed_origins,
)

mcp = MCPServer(
    "Calibre SPARK Gateway",
    instructions="Gateway dédié à la bibliothèque Calibre pour Google SPARK."
)

LIB_PATH = os.path.expanduser("~/Bibliothèque calibre")
DB_PATH = os.path.join(LIB_PATH, "metadata.db")

class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.chunks = []
    def handle_data(self, data):
        self.chunks.append(data)
    def get_text(self):
        return "".join(self.chunks).strip()

def get_db(mode: str = "ro") -> sqlite3.Connection:
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Base de données introuvable : {DB_PATH}")
    return sqlite3.connect(f"file:{os.path.abspath(DB_PATH)}?mode={mode}", uri=True, timeout=15.0)

@mcp.tool()
def search_books(query: str = "", author: str = "", tag: str = "", limit: int = 20) -> str:
    """Recherche des livres dans la bibliothèque Calibre par titre, résumé, auteur ou tag."""
    conn = get_db()
    c = conn.cursor()
    sql = """
    SELECT b.id, b.title, b.author_sort, 
           (SELECT group_concat(t.name, ', ') FROM books_tags_link btl JOIN tags t ON btl.tag = t.id WHERE btl.book = b.id),
           (SELECT group_concat(d.format, ', ') FROM data d WHERE d.book = b.id)
    FROM books b WHERE 1=1
    """
    params = []
    if query:
        sql += " AND (lower(b.title) LIKE ? OR b.id IN (SELECT book FROM comments WHERE lower(text) LIKE ?))"
        params.extend([f"%{query.lower()}%", f"%{query.lower()}%"])
    if author:
        sql += " AND lower(b.author_sort) LIKE ?"
        params.append(f"%{author.lower()}%")
    if tag:
        sql += " AND b.id IN (SELECT btl.book FROM books_tags_link btl JOIN tags t ON btl.tag = t.id WHERE lower(t.name) LIKE ?)"
        params.append(f"%{tag.lower()}%")
    sql += " ORDER BY b.title ASC LIMIT ?"
    params.append(limit)
    rows = c.execute(sql, params).fetchall()
    conn.close()
    if not rows: return "Aucun livre trouvé correspondant aux critères."
    return "\n".join([f"ID {r[0]}: « {r[1]} » par {r[2]} | Formats: {r[4] or 'Aucun'} | Tags: {r[3] or 'Aucun'}" for r in rows])

@mcp.tool()
def get_book_details(book_id: int) -> str:
    """Récupère les métadonnées complètes d'un livre (résumé, ISBN, tags, formats)."""
    conn = get_db()
    c = conn.cursor()
    b = c.execute("SELECT id, title, author_sort, path, pubdate FROM books WHERE id = ?", (book_id,)).fetchone()
    if not b:
        conn.close()
        return f"Erreur : Aucun livre avec ID {book_id}."
    comm = c.execute("SELECT text FROM comments WHERE book = ?", (book_id,)).fetchone()
    summary = comm[0] if comm and comm[0] else "Aucun résumé disponible."
    p = HTMLTextExtractor(); p.feed(summary)
    tags = [t[0] for t in c.execute("SELECT t.name FROM tags t JOIN books_tags_link btl ON t.id = btl.tag WHERE btl.book = ?", (book_id,)).fetchall()]
    idents = [f"{i[0].upper()}: {i[1]}" for i in c.execute("SELECT type, val FROM identifiers WHERE book = ?", (book_id,)).fetchall()]
    fmts = [f"{f[0]} ({f[2]//1024} Ko)" for f in c.execute("SELECT format, name, uncompressed_size FROM data WHERE book = ?", (book_id,)).fetchall()]
    conn.close()
    return f"=== FICHE LIVRE (ID: {b[0]}) ===\nTitre   : {b[1]}\nAuteur  : {b[2]}\nDate    : {b[4] or 'Inconnue'}\nTags    : {', '.join(tags) if tags else 'Aucun'}\nIdent.  : {', '.join(idents) if idents else 'Aucun'}\nFormats : {', '.join(fmts) if fmts else 'Aucun'}\n\n--- RÉSUMÉ ---\n{p.get_text()}"

@mcp.tool()
def read_book_content(book_id: int, max_characters: int = 60000, start_offset: int = 0) -> str:
    """Extrait le contenu textuel d'un livre EPUB à partir de son ID."""
    conn = get_db()
    c = conn.cursor()
    row = c.execute("SELECT b.path, d.name FROM books b JOIN data d ON b.id = d.book WHERE b.id = ? AND d.format = 'EPUB'", (book_id,)).fetchone()
    conn.close()
    if not row: return f"Aucun fichier EPUB pour l'ID {book_id}."
    epub_file = os.path.join(LIB_PATH, row[0], f"{row[1]}.epub")
    if not os.path.exists(epub_file): return f"EPUB introuvable ({epub_file})."
    try:
        parts = []
        with zipfile.ZipFile(epub_file, 'r') as z:
            root = ET.fromstring(z.read("META-INF/container.xml"))
            opf_path = next(e.attrib.get("full-path", "") for e in root.iter() if e.tag.endswith("rootfile"))
            opf_dir = os.path.dirname(opf_path)
            o_root = ET.fromstring(z.read(opf_path))
            manifest = {e.attrib.get("id"): os.path.normpath(os.path.join(opf_dir, e.attrib.get("href"))).replace("\\", "/")
                        for e in o_root.iter() if e.tag.endswith("item") and ("html" in e.attrib.get("media-type","") or "xml" in e.attrib.get("media-type",""))}
            spine = [e.attrib.get("idref") for e in o_root.iter() if e.tag.endswith("itemref") and e.attrib.get("idref")]
            for sid in spine:
                href = manifest.get(sid)
                if not href: continue
                try:
                    p = HTMLTextExtractor(); p.feed(z.read(href).decode("utf-8", errors="ignore"))
                    t = p.get_text()
                    if t: parts.append(t)
                except Exception: pass
        full = "\n\n".join(parts)
        sub = full[start_offset:start_offset + max_characters]
        return f"[EPUB ID {book_id} : {start_offset} à {start_offset + len(sub)} sur {len(full)} caractères]\n\n" + sub
    except Exception as e:
        return f"Erreur EPUB : {e}"

@mcp.tool()
def batch_update_books(updates: list[dict]) -> str:
    """
    Met à jour en masse les métadonnées des livres (titre, auteur).
    
    La liste `updates` doit contenir des dictionnaires avec :
    - 'id' (int, requis): l'identifiant du livre.
    - 'title' (str, optionnel): le nouveau titre du livre.
    - 'author_sort' (str, optionnel): le nom de l'auteur utilisé pour le tri (ex: "Nom, Prénom").
    
    Cette opération est sécurisée (requêtes préparées) mais peut échouer si l'interface
    graphique de Calibre est actuellement ouverte (verrouillage de la base de données).
    """
    if not updates:
        return "Aucune mise à jour fournie."

    try:
        conn = get_db(mode="rw")
        c = conn.cursor()
        
        updated_count = 0
        for update in updates:
            book_id = update.get("id")
            if not book_id:
                continue
            
            fields = []
            params = []
            if "title" in update:
                fields.append("title = ?")
                params.append(update["title"])
            if "author_sort" in update:
                fields.append("author_sort = ?")
                params.append(update["author_sort"])
            
            if not fields:
                continue
            
            query = f"UPDATE books SET {', '.join(fields)} WHERE id = ?"
            params.append(book_id)
            
            c.execute(query, tuple(params))
            if c.rowcount > 0:
                updated_count += 1
                
        conn.commit()
        conn.close()
        return f"Mise à jour réussie : {updated_count} livre(s) modifié(s)."
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e).lower():
            return "Erreur : La base de données est verrouillée. L'interface graphique de Calibre est probablement ouverte. Veuillez la fermer et réessayer."
        return f"Erreur de base de données : {e}"
    except Exception as e:
        return f"Erreur inattendue lors de la mise à jour : {e}"

class BearerAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
            
        if scope["method"] == "OPTIONS":
            return await self.app(scope, receive, send)
            
        if TOKEN and TOKEN.lower() != "no-oauth-required":
            headers = dict(scope.get("headers", []))
            auth = headers.get(b"authorization", b"").decode("utf-8", errors="ignore")
            if auth != f"Bearer {TOKEN}":
                await send({
                    "type": "http.response.start",
                    "status": 401,
                    "headers": [(b"content-type", b"application/json")]
                })
                await send({
                    "type": "http.response.body",
                    "body": b'{"error": "unauthorized"}'
                })
                return
                
        return await self.app(scope, receive, send)

raw_app = mcp.streamable_http_app(transport_security=security, stateless_http=True, streamable_http_path="/")
cors_app = CORSMiddleware(
    raw_app,
    allow_origins=["https://gemini.google.com"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app = BearerAuthMiddleware(cors_app)

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
