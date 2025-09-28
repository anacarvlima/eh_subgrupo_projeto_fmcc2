import json
from subgrupo import verificar_subgrupo

def handler(request):
    try:
        data = request.get_json()

        grupo_G = data.get("grupoG", {}).get("elementos", [])
        subgrupo_H = data.get("grupoH", {}).get("elementos", [])
        operacao = data.get("grupoG", {}).get("operacao")

        resultado = verificar_subgrupo(grupo_G, subgrupo_H, operacao)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "sucesso": True,
                "grupoG": resultado.get("grupoG", {}),
                "grupoH": resultado.get("grupoH", {}),
                "subgrupo": resultado.get("subgrupo", {})
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "sucesso": False,
                "erro": str(e)
            })
        }
