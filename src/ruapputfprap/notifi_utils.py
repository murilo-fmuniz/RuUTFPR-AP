import os
import json
import datetime

def get_notificacoes_path():
    return os.path.join(os.path.dirname(__file__), "data", "notificacoes.json")

def inicializar_notificacoes():
    path = get_notificacoes_path()
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"notificacoes": []}, f, indent=4, ensure_ascii=False)

def carregar_notificacoes():
    path = get_notificacoes_path()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("notificacoes", [])

def adicionar_notificacao(texto):
    path = get_notificacoes_path()
    data = {"notificacoes": carregar_notificacoes()}
    
    nova = {
        "data": datetime.datetime.now().isoformat(),
        "mensagem": texto
    }
    data["notificacoes"].append(nova)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def obter_notificacoes_por_data(data_referencia, limite=5):
    notificacoes = carregar_notificacoes()
    notificacoes_filtradas = [
        n for n in notificacoes
        if datetime.datetime.fromisoformat(n["data"]).date() == data_referencia
    ]
    notificacoes_filtradas.sort(key=lambda x: x["data"], reverse=True)
    return notificacoes_filtradas[:limite]

def obter_notificacoes_formatadas(data_referencia):
    try:
        notificacoes = obter_notificacoes_por_data(data_referencia)
        
        if not notificacoes:
            return {
                "sucesso": True,
                "mensagem": "Nenhuma notificação recente."
            }

        formatted = ["🔔 Últimas Notificações", ""]
        for notif in notificacoes:
            data = datetime.datetime.fromisoformat(notif["data"])
            formatted.append(
                f"⏰ {data.strftime('%d/%m %H:%M')} - {notif['mensagem']}"
            )
        
        return {
            "sucesso": True,
            "mensagem": "\n".join(formatted)
        }

    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": f"⚠️ Erro ao carregar notificações:\n{str(e)}"
        }