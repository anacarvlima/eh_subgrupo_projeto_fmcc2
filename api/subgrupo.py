import json
from subgrupo import verificar_subgrupo  # sua função de lógica

def handler(request):
    # request.body contém os dados enviados pelo frontend
    data = request.get_json()  # Vercel passa JSON como dicionário

    grupo_G = data.get("grupo_G", [])
    subgrupo_H = data.get("subgrupo_H", [])
    operacao = data.get("operacao")

    resultado = verificar_subgrupo(grupo_G, subgrupo_H, operacao)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"resultado": resultado})
    }
