import json
from http.server import BaseHTTPRequestHandler

def aplicar_operacao(a, b, operacao, mod=None):
    if operacao == "+":
        resultado = a + b
    elif operacao == "*":
        resultado = a * b
    else:
        return None
    
    if mod is not None:
        resultado %= mod
    return resultado

def fechado(grupo, operacao, mod):
    for a in grupo:
        for b in grupo:
            if aplicar_operacao(a, b, operacao, mod) not in grupo:
                return False
    return True

def identidade(grupo, operacao, mod):
    for e in grupo:
        if all(aplicar_operacao(a, e, operacao, mod) == a and 
               aplicar_operacao(e, a, operacao, mod) == a for a in grupo):
            return e
    return None

def inverso(grupo, operacao, elemento_identidade, mod):
    for a in grupo:
        if not any(aplicar_operacao(a, b, operacao, mod) == elemento_identidade and 
                  aplicar_operacao(b, a, operacao, mod) == elemento_identidade for b in grupo):
            return False
    return True

def teste_grupo(grupo, operacao, mod, nome):
    resultado = {
        "nome": nome,
        "elementos": grupo,
        "operacao": operacao,
        "modulo": mod,
        "testes": {},
        "eh_grupo": False,
        "identidade": None,
        "mensagens": []
    }
    
    resultado["testes"]["associatividade"] = True
    resultado["mensagens"].append("Associatividade: considerada verdadeira para + e *")
    
    eh_fechado = fechado(grupo, operacao, mod)
    resultado["testes"]["fechamento"] = eh_fechado
    resultado["mensagens"].append(
        "Fechamento: OK" if eh_fechado else "Fechamento: FALHOU"
    )
    
    e = identidade(grupo, operacao, mod)
    resultado["identidade"] = e
    resultado["testes"]["identidade"] = e is not None
    resultado["mensagens"].append(
        f"Identidade encontrada: {e}" if e is not None else "Identidade não encontrada"
    )
    
    if e is not None:
        tem_inversos = inverso(grupo, operacao, e, mod)
        resultado["testes"]["inversos"] = tem_inversos
        resultado["mensagens"].append(
            "Inversos: todos os elementos possuem" if tem_inversos else "Inversos: nem todos possuem"
        )
    else:
        resultado["testes"]["inversos"] = False
        resultado["mensagens"].append("Inversos: não testados (sem identidade)")
    
    if eh_fechado and e is not None and resultado["testes"]["inversos"]:
        resultado["eh_grupo"] = True
        resultado["mensagens"].append("✅ Resultado: o conjunto é um grupo")
    else:
        resultado["eh_grupo"] = False
        resultado["mensagens"].append("❌ Resultado: o conjunto NÃO é um grupo")
    
    return resultado

def teste_subgrupo(grupo_G, operacao_G, mod_G, grupo_H, operacao_H, mod_H, e_G, e_H):
    resultado = {
        "eh_subgrupo": False,
        "testes": {},
        "mensagens": []
    }
    
    resultado["mensagens"].append("Verificando se H é subgrupo de G...")
    
    contido = all(x in grupo_G for x in grupo_H)
    resultado["testes"]["contencao"] = contido
    resultado["mensagens"].append(
        "Todos os elementos de H estão em G" if contido else "H tem elementos que não estão em G"
    )
    
    fechado_H = fechado(grupo_H, operacao_H, mod_H)
    resultado["testes"]["fechamento_H"] = fechado_H
    resultado["mensagens"].append(
        "H é fechado na sua operação" if fechado_H else "H não é fechado"
    )
    
    mesma_operacao = operacao_G == operacao_H
    mesmo_modulo = mod_G == mod_H
    resultado["testes"]["mesma_operacao"] = mesma_operacao
    resultado["testes"]["mesmo_modulo"] = mesmo_modulo
    
    if not mesma_operacao:
        resultado["mensagens"].append("Operações diferentes em G e H")
    if not mesmo_modulo:
        resultado["mensagens"].append("Módulos diferentes em G e H")
    
    if e_H is None or e_H != e_G:
        resultado["testes"]["mesma_identidade"] = False
        resultado["mensagens"].append("H não contém a mesma identidade de G")
        resultado["testes"]["inversos_H"] = False
    else:
        resultado["testes"]["mesma_identidade"] = True
        resultado["mensagens"].append("H contém a mesma identidade de G")
        
        inverso_H = inverso(grupo_H, operacao_H, e_H, mod_H)
        resultado["testes"]["inversos_H"] = inverso_H
        resultado["mensagens"].append(
            "Todos os elementos de H têm inverso" if inverso_H else "Nem todos os elementos de H têm inverso"
        )
    
    if (contido and fechado_H and resultado["testes"]["mesma_identidade"] and 
        resultado["testes"]["inversos_H"] and mesma_operacao and mesmo_modulo):
        resultado["eh_subgrupo"] = True
        resultado["mensagens"].append("✅ Resultado: H é subgrupo de G")
    else:
        resultado["eh_subgrupo"] = False
        resultado["mensagens"].append("❌ Resultado: H NÃO é subgrupo de G")
    
    return resultado

def verificar_subgrupo(grupo_G, subgrupo_H, operacao):
    """Função principal que será chamada pelo handler"""
    # Assumindo que todos os parâmetros vêm no formato correto
    mod_G = None  # Por padrão, sem módulo
    mod_H = None
    
    # Testar os dois conjuntos
    resultado_G = teste_grupo(grupo_G, operacao, mod_G, "G")
    resultado_H = teste_grupo(subgrupo_H, operacao, mod_H, "H")
    
    # Testar se H é subgrupo de G
    resultado_subgrupo = teste_subgrupo(
        grupo_G, operacao, mod_G,
        subgrupo_H, operacao, mod_H,
        resultado_G["identidade"], resultado_H["identidade"]
    )
    
    return {
        "grupoG": resultado_G,
        "grupoH": resultado_H,
        "subgrupo": resultado_subgrupo
    }

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Ler o corpo da requisição
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extrair dados
            grupo_G = data.get("grupoG", {}).get("elementos", [])
            subgrupo_H = data.get("grupoH", {}).get("elementos", [])
            operacao_G = data.get("grupoG", {}).get("operacao")
            operacao_H = data.get("grupoH", {}).get("operacao")
            mod_G = data.get("grupoG", {}).get("modulo")
            mod_H = data.get("grupoH", {}).get("modulo")
            
            # Processar módulos
            if mod_G and mod_G != '':
                mod_G = int(mod_G)
            else:
                mod_G = None
                
            if mod_H and mod_H != '':
                mod_H = int(mod_H)
            else:
                mod_H = None
            
            # Testar os grupos
            resultado_G = teste_grupo(grupo_G, operacao_G, mod_G, "G")
            resultado_H = teste_grupo(subgrupo_H, operacao_H, mod_H, "H")
            
            # Testar subgrupo
            resultado_subgrupo = teste_subgrupo(
                grupo_G, operacao_G, mod_G,
                subgrupo_H, operacao_H, mod_H,
                resultado_G["identidade"], resultado_H["identidade"]
            )
            
            # Resposta de sucesso
            response_data = {
                "sucesso": True,
                "grupoG": resultado_G,
                "grupoH": resultado_H,
                "subgrupo": resultado_subgrupo
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            
        except Exception as e:
            # Resposta de erro
            error_response = {
                "sucesso": False,
                "erro": str(e)
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        # Lidar com requisições OPTIONS (CORS)
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()