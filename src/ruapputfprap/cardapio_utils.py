import os
import json
import datetime
import random

# Constantes
DATE_RANGE_START = datetime.date(2025, 5, 22)
DATE_RANGE_END = datetime.date(2025, 6, 6)

def get_cardapio_path():
    """Retorna o caminho completo para o arquivo de cardápio"""
    return os.path.join(os.path.dirname(__file__), "data", "cardapio.json")

def gerar_data_aleatoria():
    """Gera uma data aleatória dentro do intervalo definido."""
    delta = (DATE_RANGE_END - DATE_RANGE_START).days
    return DATE_RANGE_START + datetime.timedelta(days=random.randint(0, delta))

def gerar_cardapio_padrao():
    """Gera um cardápio padrão caso não exista"""
    path = get_cardapio_path()
    dias_semana = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado"]
    pratos = [
        "Arroz, feijão, bife acebolado, salada verde",
        "Macarrão ao sugo, frango grelhado, legumes cozidos",
        "Strogonoff de frango, arroz, batata palha, cenoura ralada",
        "Feijoada, arroz, couve refogada, laranja",
        "Escondidinho de carne, arroz integral, beterraba",
        "Peixe empanado, purê de batata, arroz, salada de alface",
        "Lasanha de legumes, arroz, brócolis no vapor",
        "Risoto de frango, salada de rúcula, pão de alho",
        "Torta salgada, arroz branco, salada de repolho",
        "Carne de panela, mandioca cozida, arroz, vinagrete"
    ]

    cardapio = {}
    for dia in dias_semana:
        cardapio[dia] = {
            "almoço": random.choice(pratos)
        }
        if dia != "sábado":
            cardapio[dia]["jantar"] = random.choice(pratos)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cardapio, f, indent=4, ensure_ascii=False)

def garantir_cardapio_json():
    """Garante que o arquivo JSON de cardápio existe ou cria um novo."""
    path = get_cardapio_path()
    if not os.path.exists(path):
        gerar_cardapio_padrao()

def carregar_cardapio():
    """Carrega o cardápio do arquivo JSON"""
    path = get_cardapio_path()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def mostrar_cardapio(data):
    """Retorna o cardápio formatado para a data especificada"""
    try:
        if not (DATE_RANGE_START <= data <= DATE_RANGE_END):
            return {
                "sucesso": False,
                "mensagem": "Fora do período de exibição de cardápio (22/05 a 06/06)."
            }

        dias_semana_pt = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
        dia_num = data.weekday()
        dia_semana = dias_semana_pt[dia_num]

        cardapio = carregar_cardapio()

        if dia_semana not in cardapio:
            return {
                "sucesso": True,
                "mensagem": "RU fechado hoje (domingo ou feriado)."
            }

        refeicoes = cardapio[dia_semana]
        formatted = [
            f"📅 Cardápio - {data.strftime('%d/%m/%Y')}",
            f"📌 {dia_semana.capitalize()}-feira",
            ""
        ]
        
        for tipo, menu in refeicoes.items():
            formatted.append(f"🍽️ {tipo.capitalize()}:")
            formatted.append(f"   {menu}")
            formatted.append("")

        return {
            "sucesso": True,
            "mensagem": "\n".join(formatted).strip()
        }

    except Exception as e:
        return {
            "sucesso": False,
            "mensagem": f"⚠️ Erro ao carregar cardápio:\n{str(e)}"
        }