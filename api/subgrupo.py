import json
from subgrupo import verificar_subgrupo  # sua função de lógica

def handler(request):
    try:
        data = request.get_json()  # Vercel converte o corpo POST para dict

        grupo_G = data.get("grupoG", {}).get("elementos", [])
        subgrupo_H = data.get("grupoH", {}).get("elementos", [])
        operacao = data.get("grupoG", {}).get("operacao")  # ou subgrupo

        resultado = verificar_subgrupo(grupo_G, subgrupo_H, operacao)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"resultado": resultado, "sucesso": True})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"sucesso": False, "erro": str(e)})
        }
