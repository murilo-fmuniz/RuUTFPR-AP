import toga
from toga.style import Pack
from toga.style.pack import COLUMN

from .cardapio_utils import (
    gerar_data_aleatoria,
    garantir_cardapio_json,
    mostrar_cardapio
)

from . import notifi_utils 

from .ui_utils import criar_layout_principal

from .window_manager import WindowManager



class RUAppUTFPRAp(toga.App):
    """Aplicativo de cardápio do RU da UTFPR com notificações."""

    def __init__(self):
        super().__init__(
            formal_name="Cardápio RU UTFPR",
            app_id="br.edu.utfpr.rucardapio",
            app_name="RU UTFPR"
        )
        self.module_name = 'ruapputfprap' # Defina explicitamente o nome do seu pacote de app

        self.data_hoje = None
        self.data_display = None
        
        
        self.notifi_utils = notifi_utils

        self.window_manager = WindowManager(self)


    def startup(self):
        """Configura a interface inicial do aplicativo."""
        # Configura data aleatória dentro do período
        self.data_hoje = gerar_data_aleatoria()
        
        # Cria layout principal
        main_box = criar_layout_principal(self)
        
        # ----- BOTÃO PARA ABRIR A JANELA DE IDENTIFICAÇÃO -----
        btn_identificacao_aluno = toga.Button(
            "Identificação Aluno",
            on_press=self._abrir_janela_identificacao,
            style=Pack(padding_top=10, width=200) # Ajuste o estilo conforme necessário
        )
        main_box.add(btn_identificacao_aluno)
        # ------------------------------------------------------
        
        self.main_window = toga.MainWindow(
            title=self.formal_name,
            size=(400, 700)
        )
        self.main_window.content = main_box
        self.main_window.show()

        # Garante que o arquivo de cardápio existe
        garantir_cardapio_json()

    def _abrir_janela_identificacao(self, widget):
        # Usa o window_manager para abrir a janela especificada
        self.window_manager.open_window("ra_qrcode") # "ra_qrcode" corresponde ao nome do arquivo

    def _mostrar_cardapio_hoje(self, widget):
        """Exibe o cardápio do dia atual."""
        if not self.data_display:
            print("data_display não inicializado.")
            return
        resultado = mostrar_cardapio(self.data_hoje)
        self.data_display.value = resultado["mensagem"]
        
        if resultado["sucesso"]:
            self.notifi_utils.adicionar_notificacao( # Usando self.notifi_utils
                f"Usuário visualizou o cardápio de {self.data_hoje.strftime('%d/%m/%Y')}."
            )

    def _mostrar_notificacoes(self, widget):
        """Exibe as notificações recentes."""
        if not self.data_display:
            print("data_display não inicializado.")
            return
        resultado = self.notifi_utils.obter_notificacoes_formatadas(self.data_hoje) # Usando self.notifi_utils
        self.data_display.value = resultado["mensagem"]


def main():
    return RUAppUTFPRAp()