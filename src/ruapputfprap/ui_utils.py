import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

def criar_layout_principal(app):
    """Cria e retorna o layout principal do aplicativo."""
    # Container principal
    main_box = toga.Box(style=Pack(direction=COLUMN, padding=20))

    # Dias da semana em português
    dias_semana = [
        "Segunda-feira", "Terça-feira", "Quarta-feira",
        "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"
    ]
    dia_num = app.data_hoje.weekday()
    dia_semana = dias_semana[dia_num]

    # Cabeçalho com data
    app.date_label = toga.Label(
        f"📅 {dia_semana}, {app.data_hoje.strftime('%d/%m/%Y')}",
        style=Pack(
            padding_bottom=15,
            font_size=16,
            font_weight="bold",
            text_align="center"
        )
    )

    # Área de exibição de conteúdo
    app.data_display = toga.MultilineTextInput(
        readonly=True,
        style=Pack(flex=1, padding=10)
    )

    # Barra de botões
    button_box = toga.Box(style=Pack(direction=ROW, padding_bottom=15))

    app.cardapio_button = toga.Button(
        "🍽️ Cardápio de Hoje",
        on_press=app._mostrar_cardapio_hoje,
        style=Pack(padding=10, flex=1)
    )

    app.notif_button = toga.Button(
        "🔔 Notificações",
        on_press=app._mostrar_notificacoes,
        style=Pack(padding=10, flex=1, margin_left=10)
    )

    # Montagem da interface
    button_box.add(app.cardapio_button)
    button_box.add(app.notif_button)
    main_box.add(app.date_label)
    main_box.add(button_box)
    main_box.add(app.data_display)

    return main_box