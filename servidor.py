#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor de registro para el evento.

La laptop guarda todos los registros y la tableta se conecta por WiFi
(por ejemplo, el hotspot de un celular; no se gastan datos).

Uso:  doble clic en "iniciar.bat" (Windows)  o  python3 servidor.py
No necesita instalar nada además de Python 3.
"""
import base64
import json
import os
import re
import shutil
import socket
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PORT = 8000
BASE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(BASE, "registro-evento.html")
DIR = os.path.join(BASE, "registros")
IMG = os.path.join(DIR, "imagenes")
DB = os.path.join(DIR, "datos.json")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

lock = threading.Lock()
state = {"version": int(time.time()), "registros": [], "uids": {}}


def cargar():
    os.makedirs(IMG, exist_ok=True)
    if os.path.exists(DB):
        with open(DB, encoding="utf-8") as f:
            state["registros"] = json.load(f).get("registros", [])
    state["uids"] = {r["uid"]: r["folio"] for r in state["registros"] if r.get("uid")}


def guardar():
    tmp = DB + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"registros": state["registros"]}, f, ensure_ascii=False, indent=1)
    os.replace(tmp, DB)


def publico(r):
    return {k: r.get(k) for k in ("folio", "nombre", "telefono", "fecha", "firma")}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def responder(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def json(self, obj, code=200):
        self.responder(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self):
        u = urlparse(self.path)
        if u.path in ("/", "/index.html", "/registro-evento.html"):
            with open(HTML, "rb") as f:
                return self.responder(200, f.read(), "text/html; charset=utf-8")
        if u.path == "/api/registros":
            v = parse_qs(u.query).get("v", [""])[0]
            with lock:
                if v == str(state["version"]):
                    return self.json({"changed": False, "version": state["version"]})
                return self.json({"changed": True, "version": state["version"],
                                  "registros": [publico(r) for r in state["registros"]]})
        m = re.fullmatch(r"/api/img/(\d+)\.png", u.path)
        if m:
            p = os.path.join(IMG, m.group(1) + ".png")
            if os.path.exists(p):
                with open(p, "rb") as f:
                    return self.responder(200, f.read(), "image/png")
        self.json({"error": "no encontrado"}, 404)

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 3_000_000:
            return self.json({"error": "muy grande"}, 413)
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return self.json({"error": "json"}, 400)
        path = urlparse(self.path).path

        if path == "/api/registro":
            uid = str(body.get("uid") or "")[:40]
            nombre = str(body.get("nombre") or "")[:150]
            tel = re.sub(r"\D", "", str(body.get("telefono") or ""))[:15]
            fecha = str(body.get("fecha") or "")[:40]
            img = body.get("img") or ""
            with lock:
                if uid and uid in state["uids"]:          # reintento: ya lo teníamos
                    return self.json({"folio": state["uids"][uid]})
                folio = max([r["folio"] for r in state["registros"]], default=0) + 1
                firma = False
                if isinstance(img, str) and img.startswith("data:image/png;base64,"):
                    with open(os.path.join(IMG, f"{folio}.png"), "wb") as f:
                        f.write(base64.b64decode(img.split(",", 1)[1]))
                    firma = True
                rec = {"folio": folio, "nombre": nombre, "telefono": tel, "fecha": fecha, "firma": firma, "uid": uid}
                state["registros"].append(rec)
                if uid:
                    state["uids"][uid] = folio
                state["version"] += 1
                guardar()
            print(f"  [OK] #{folio:<4} {nombre or '(escrito a mano)':<35} {tel}   total: {len(state['registros'])}")
            return self.json({"folio": folio})

        if path == "/api/borrar":
            try:
                folio = int(body.get("folio"))
            except (TypeError, ValueError):
                return self.json({"error": "folio"}, 400)
            with lock:
                state["registros"] = [r for r in state["registros"] if r["folio"] != folio]
                p = os.path.join(IMG, f"{folio}.png")
                if os.path.exists(p):
                    os.remove(p)
                state["version"] += 1
                guardar()
            print(f"  [BORRADO] #{folio}")
            return self.json({"ok": True})

        if path == "/api/borrar-todo":
            with lock:
                ts = time.strftime("%Y%m%d_%H%M%S")
                if state["registros"]:            # respaldo por si acaso
                    shutil.copy(DB, os.path.join(DIR, f"respaldo_{ts}.json"))
                    shutil.move(IMG, os.path.join(DIR, f"imagenes_respaldo_{ts}"))
                    os.makedirs(IMG, exist_ok=True)
                state["registros"], state["uids"] = [], {}
                state["version"] += 1
                guardar()
            print(f"  [BORRADO TODO] respaldo guardado en registros/respaldo_{ts}.json")
            return self.json({"ok": True})

        self.json({"error": "no encontrado"}, 404)


def ips_locales():
    ips = set()
    try:
        ips.update(socket.gethostbyname_ex(socket.gethostname())[2])
    except OSError:
        pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ips.add(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    return sorted(i for i in ips if not i.startswith("127.") and not i.startswith("169.254."))


def main():
    if not os.path.exists(HTML):
        print("No encuentro registro-evento.html. Ponlo en la misma carpeta que servidor.py")
        input("Enter para salir...")
        return
    cargar()
    try:
        srv = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    except OSError:
        print(f"El puerto {PORT} esta ocupado. Quiza el servidor ya esta abierto en otra ventana.")
        input("Enter para salir...")
        return
    ips = ips_locales()
    print("=" * 60)
    print("   SERVIDOR DE REGISTRO - ENCENDIDO")
    print("=" * 60)
    print(f"   Registros guardados: {len(state['registros'])}")
    print("   En la TABLETA abre Chrome y escribe:")
    for ip in ips or ["(no hay red: conecta la laptop al WiFi/hotspot)"]:
        print(f"        http://{ip}:{PORT}")
    print("   En esta LAPTOP el panel se abre solo (PIN 2811).")
    print("   Los datos se guardan en la carpeta 'registros'.")
    print("   NO cierres esta ventana durante el evento.")
    print("=" * 60)
    threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{PORT}/#panel")).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor apagado. Los datos quedaron guardados.")


if __name__ == "__main__":
    main()
