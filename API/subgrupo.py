import json
from http.server import BaseHTTPRequestHandler
from subgrupo import verificar_subgrupo  # importa sua função

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        body = self.rfile.read(content_length)
        data = json.loads(body)

        grupo_G = data.get("grupo_G", [])
        subgrupo_H = data.get("subgrupo_H", [])
        operacao = data.get("operacao")

        resultado = verificar_subgrupo(grupo_G, subgrupo_H, operacao)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"resultado": resultado}).encode())
