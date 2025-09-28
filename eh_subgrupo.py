from flask import Flask, request, jsonify
from flask_cors import CORS

# Criando a aplicação Flask
app = Flask(__name__)
CORS(app)  # Libera acesso da API para outras origens (evita erro de CORS no front)

# Função que aplica a operação escolhida (+ ou *) entre dois elementos
# Se o usuário passou um módulo, o resultado é reduzido por ele
def aplicar_operacao(a, b, operacao, mod=None):
    if operacao == "+":
        resultado = a + b
    elif operacao == "*":
        resultado = a * b
    else:
        return None  # Se for operação inválida, devolve None
    
    if mod is not None:
        resultado %= mod  # Aplica módulo se foi definido
    return resultado

# Verifica se o conjunto é fechado: ou seja, toda operação entre elementos
# gera um resultado que também pertence ao conjunto
def fechado(grupo, operacao, mod):
    for a in grupo:
        for b in grupo:
            if aplicar_operacao(a, b, operacao, mod) not in grupo:
                return False
    return True

# Procura o elemento identidade: aquele que não altera nenhum elemento
# quando usado na operação
def identidade(grupo, operacao, mod):
    for e in grupo:
        if all(aplicar_operacao(a, e, operacao, mod) == a and 
               aplicar_operacao(e, a, operacao, mod) == a for a in grupo):
            return e
    return None

# Testa se cada elemento do grupo tem um inverso
# (ou seja, alguém que “cancele” o efeito da operação e leve de volta para a identidade)
def inverso(grupo, operacao, elemento_identidade, mod):
    for a in grupo:
        if not any(aplicar_operacao(a, b, operacao, mod) == elemento_identidade and 
                  aplicar_operacao(b, a, operacao, mod) == elemento_identidade for b in grupo):
            return False
    return True

# Função que roda todos os testes e monta o relatório
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
    
    # Associatividade: assumimos que sempre é verdadeira para + e *
    resultado["testes"]["associatividade"] = True
    resultado["mensagens"].append("Associatividade: considerada verdadeira para + e *")
    
    # Testando fechamento
    eh_fechado = fechado(grupo, operacao, mod)
    resultado["testes"]["fechamento"] = eh_fechado
    resultado["mensagens"].append(
        "Fechamento: OK" if eh_fechado else "Fechamento: FALHOU"
    )
    
    # Testando identidade
    e = identidade(grupo, operacao, mod)
    resultado["identidade"] = e
    resultado["testes"]["identidade"] = e is not None
    resultado["mensagens"].append(
        f"Identidade encontrada: {e}" if e is not None else "Identidade não encontrada"
    )
    
    # Testando inversos
    if e is not None:
        tem_inversos = inverso(grupo, operacao, e, mod)
        resultado["testes"]["inversos"] = tem_inversos
        resultado["mensagens"].append(
            "Inversos: todos os elementos possuem" if tem_inversos else "Inversos: nem todos possuem"
        )
    else:
        resultado["testes"]["inversos"] = False
        resultado["mensagens"].append("Inversos: não testados (sem identidade)")
    
    # Resultado final: é grupo se passou em todos os testes
    if eh_fechado and e is not None and resultado["testes"]["inversos"]:
        resultado["eh_grupo"] = True
        resultado["mensagens"].append("✅ Resultado: o conjunto é um grupo")
    else:
        resultado["eh_grupo"] = False
        resultado["mensagens"].append("❌ Resultado: o conjunto NÃO é um grupo")
    
    return resultado

# Testa se H é subgrupo de G
def teste_subgrupo(grupo_G, operacao_G, mod_G, grupo_H, operacao_H, mod_H, e_G, e_H):
    resultado = {
        "eh_subgrupo": False,
        "testes": {},
        "mensagens": []
    }
    
    resultado["mensagens"].append("Verificando se H é subgrupo de G...")
    
    # H precisa estar contido em G
    contido = all(x in grupo_G for x in grupo_H)
    resultado["testes"]["contencao"] = contido
    resultado["mensagens"].append(
        "Todos os elementos de H estão em G" if contido else "H tem elementos que não estão em G"
    )
    
    # Fechamento em H
    fechado_H = fechado(grupo_H, operacao_H, mod_H)
    resultado["testes"]["fechamento_H"] = fechado_H
    resultado["mensagens"].append(
        "H é fechado na sua operação" if fechado_H else "H não é fechado"
    )
    
    # Operação e módulo precisam ser iguais
    mesma_operacao = operacao_G == operacao_H
    mesmo_modulo = mod_G == mod_H
    resultado["testes"]["mesma_operacao"] = mesma_operacao
    resultado["testes"]["mesmo_modulo"] = mesmo_modulo
    
    if not mesma_operacao:
        resultado["mensagens"].append("Operações diferentes em G e H")
    if not mesmo_modulo:
        resultado["mensagens"].append("Módulos diferentes em G e H")
    
    # Identidade e inversos
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
    
    # Conclusão
    if (contido and fechado_H and resultado["testes"]["mesma_identidade"] and 
        resultado["testes"]["inversos_H"] and mesma_operacao and mesmo_modulo):
        resultado["eh_subgrupo"] = True
        resultado["mensagens"].append("✅ Resultado: H é subgrupo de G")
    else:
        resultado["eh_subgrupo"] = False
        resultado["mensagens"].append("❌ Resultado: H NÃO é subgrupo de G")
    
    return resultado

# Endpoint principal da API: recebe os dados de G e H e devolve os testes
@app.route('/verificar_grupos', methods=['POST'])
def verificar_grupos():
    try:
        data = request.json
        
        # Extrair dados do grupo G
        elementos_G = data['grupoG']['elementos']
        operacao_G = data['grupoG']['operacao']
        mod_G = int(data['grupoG']['modulo']) if data['grupoG']['modulo'] not in ['', None] else None
        
        # Extrair dados do grupo H
        elementos_H = data['grupoH']['elementos']
        operacao_H = data['grupoH']['operacao']
        mod_H = int(data['grupoH']['modulo']) if data['grupoH']['modulo'] not in ['', None] else None
        
        # Testar os dois conjuntos separadamente
        resultado_G = teste_grupo(elementos_G, operacao_G, mod_G, "G")
        resultado_H = teste_grupo(elementos_H, operacao_H, mod_H, "H")
        
        # Testar se H é subgrupo de G
        resultado_subgrupo = teste_subgrupo(
            elementos_G, operacao_G, mod_G,
            elementos_H, operacao_H, mod_H,
            resultado_G["identidade"], resultado_H["identidade"]
        )
        
        return jsonify({
            "sucesso": True,
            "grupoG": resultado_G,
            "grupoH": resultado_H,
            "subgrupo": resultado_subgrupo
        })
        
    except Exception as e:
        return jsonify({
            "sucesso": False,
            "erro": f"Ocorreu um erro ao processar os dados: {str(e)}"
        }), 400

# Endpoint de teste rápido para saber se a API está rodando
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "msg": "API rodando direitinho 🚀"})

if __name__ == '__main__':
    print("API do Verificador de Grupos iniciada")
    print("Rodando em: http://localhost:5000")
    print("Endpoint principal: POST /verificar_grupos")
    print("Health check: GET /health")
    app.run(host='0.0.0.0', port=5000, debug=True)
