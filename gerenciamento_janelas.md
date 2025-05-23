# Entendendo o Gerenciamento de Janelas e Eventos no Aplicativo

Este documento explica como o sistema de gerenciamento de janelas (`WindowManager`) funciona em nosso aplicativo Toga, permitindo abrir, fechar e reabrir janelas de funcionalidades de forma organizada.

## Componente Chave: `WindowManager`

O `WindowManager` é uma classe central projetada para lidar com todas as janelas secundárias do seu aplicativo.

- **Propósito**: Centralizar a criação, exibição e o rastreamento de janelas. Evitar a duplicação de janelas (se desejado para certos tipos) e gerenciar o ciclo de vida delas de forma limpa.
- **Rastreamento**: Ele utiliza um dicionário interno chamado `self.open_windows`. Este dicionário armazena as instâncias das janelas Toga que estão atualmente abertas, usando um `window_type` (um nome string único para cada tipo de janela) como chave.
  ```python
  # Exemplo de como as janelas são rastreadas:
  # self.open_windows = {
  #     "ra_qrcode": <objeto toga.Window da janela RA/QRCode>,
  #     "settings": <objeto toga.Window da janela de Configurações>
  # }


Abrindo uma Janela (WindowManager.open_window)
Quando você solicita a abertura de uma janela (ex: self.window_manager.open_window("meu_tipo_de_janela")):

Verificação Inicial: O WindowManager primeiro verifica se uma janela do tipo window_type já está em self.open_windows.

Se a Janela Já Estiver Rastreada (e supostamente aberta):

Ele tenta chamar o método .show() na instância da janela existente. Isso deve trazer a janela para frente e dar foco a ela se já estiver visível, ou reexibi-la se estiver apenas oculta (comportamento pode variar um pouco entre backends Toga).
Tratamento de Erro para Janelas "Mortas": Se a chamada a .show() falhar (por exemplo, porque a janela foi fechada pelo sistema operacional e o objeto Toga interno não é mais válido), o WindowManager captura essa exceção. Ele então remove a referência "morta" de self.open_windows. Isso é crucial, pois permite que, na próxima tentativa de abrir essa janela, ela seja recriada do zero.
Se a Janela Não Estiver Rastreada (ou foi removida por ser "morta"):

Importação Dinâmica: O WindowManager usa importlib.import_module() para carregar dinamicamente o módulo Python associado ao window_type. Por convenção, se window_type é "meu_tipo", ele procura por um arquivo meu_tipo_window.py dentro do seu pacote de aplicativo (ex: src/ruapputfprap/meu_tipo_window.py).
Função de Fábrica: Espera-se que cada módulo de janela (meu_tipo_window.py) forneça uma função chamada create_and_show_window(app_instance, window_manager, **kwargs). Esta função é responsável por:
Criar a interface da janela (widgets Toga, layout).
Criar a instância de toga.Window.
Chamar .show() na nova janela Toga.
Retornar a instância de toga.Window criada.
Armazenamento e Callback on_close:
A nova instância de toga.Window retornada é armazenada em self.open_windows.
O WindowManager então anexa seu próprio manipulador de eventos (_manager_on_close_wrapper) ao evento on_close da nova janela Toga. Este wrapper é fundamental para o rastreamento.
Se a janela criada já tinha um manipulador on_close definido por si mesma (para sua própria limpeza, por exemplo), o WindowManager tenta preservá-lo e chamá-lo de dentro do _manager_on_close_wrapper.
Fechando uma Janela (Ação do Usuário - Botão 'X')
Quando o usuário clica no botão 'X' da janela do sistema operacional:

O Toga detecta essa ação e invoca o manipulador de eventos on_close que está atualmente anexado à janela.
No nosso caso, este é o _manager_on_close_wrapper definido pelo WindowManager.
Dentro do _manager_on_close_wrapper:
Primeiro, ele chama o manipulador on_close original que a janela poderia ter (se foi preservado), permitindo que a janela realize qualquer limpeza específica que precise.
Crucialmente: Ele remove a referência da janela do dicionário self.open_windows do WindowManager (usando del self.open_windows[window_type]). Isso informa ao WindowManager que esta instância específica da janela não está mais ativa ou rastreada.
A documentação do Toga especifica que se um handler on_close é fornecido, ele é responsável por realizar o fechamento. No nosso wrapper, o foco principal é o de-rastreamento. A destruição real do objeto Toga e seus recursos nativos é gerenciada pelo framework Toga após a conclusão do handler on_close.
Reabrindo uma Janela
O usuário clica no botão/menu que aciona a abertura da janela novamente.
O método WindowManager.open_window("meu_tipo_de_janela") é chamado.
Como a janela foi removida de self.open_windows pelo _manager_on_close_wrapper quando foi fechada, a verificação if window_type in self.open_windows: será False.
Consequentemente, o WindowManager prossegue para criar uma nova instância da janela, seguindo a lógica de "Se a Janela Não Estiver Rastreada" descrita acima.
É assim que o "reabrir" funciona: não é a mesma instância da janela que reaparece, mas uma nova é criada, garantindo um estado limpo.

Chave para o Funcionamento da Reabertura
O ponto mais crítico para que a reabertura funcione corretamente é a execução bem-sucedida do callback on_close (nosso _manager_on_close_wrapper) que remove a janela do dicionário de rastreamento do WindowManager. Se isso acontecer de forma confiável, o sistema permitirá que novas instâncias sejam criadas sob demanda. Os prints que adicionamos ao console ajudam a verificar se esse fluxo está ocorrendo como esperado.


---

## Arquivo 2: `como_adicionar_novas_janelas.md`

```markdown
# Guia: Adicionando Novas Janelas ao Aplicativo

Este guia descreve como adicionar novas funcionalidades em janelas separadas ao seu aplicativo, utilizando o `WindowManager` existente.

## Introdução

O `WindowManager` foi projetado para facilitar a adição de novas janelas independentes. Cada nova "funcionalidade" que merece sua própria janela seguirá um padrão semelhante ao que usamos para a `ra_qrcode_window`.

## Passo a Passo para Adicionar uma Nova Janela

Suponha que você queira criar uma nova janela para "Configurações" (o `window_type` seria `"settings"`).

### Passo 1: Criar o Arquivo do Módulo da Janela

Crie um novo arquivo Python na sua pasta de código fonte (`src/ruapputfprap/`).

- **Convenção de Nomenclatura**: `SEU_TIPO_DE_JANELA_window.py`.
  - Exemplo: `src/ruapputfprap/settings_window.py`

O "tipo de janela" (`settings` no exemplo) é a string que você usará para identificá-la no `WindowManager`.

### Passo 2: Implementar a View e a Lógica da Janela

Dentro do seu novo arquivo (ex: `settings_window.py`), você normalmente definirá classes para a View (interface) e para o Presenter (lógica), similar ao padrão MVP (Model-View-Presenter) que adaptamos.

**Exemplo de Estrutura para `settings_window.py`:**

```python
# src/ruapputfprap/settings_window.py
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW # Importe o que precisar

# (Opcional) Classe Presenter para a lógica da janela de configurações
class SettingsPresenter:
    def __init__(self, view, app_instance, window_manager):
        self.view = view
        self.app = app_instance
        self.window_manager = window_manager
        print("SettingsPresenter inicializado")
        # Carregue configurações, defina estado inicial, etc.

    def handle_save_settings(self, widget):
        print("Configurações salvas (simulado)")
        # Pegue os valores dos widgets da view (self.view.algum_input.value)
        # Salve as configurações (ex: em um arquivo JSON, ou usando um serviço)
        self.view.show_confirmation("Salvo!", "Configurações atualizadas.")
        # self.view.close() # Opcional: fechar após salvar

    def handle_close_window(self, widget):
        self.view.close()

# Classe View para a interface da janela de configurações
class SettingsView:
    def __init__(self, app_instance, window_manager, **kwargs): # kwargs pode ser usado para passar dados
        self.app = app_instance
        self.window_manager = window_manager
        self.presenter = SettingsPresenter(self, app_instance, window_manager)

        self.toga_window = toga.Window(
            title="Configurações",
            size=(350, 400)
        )
        # Opcional: definir um handler on_close para limpeza específica desta janela
        # self.toga_window.on_close = self.my_custom_on_close_logic 

        self._build_ui()
        # O presenter pode carregar dados nos campos da UI aqui se necessário,
        # ou isso pode ser feito no show() da view.

    def _build_ui(self):
        # Crie seus widgets Toga aqui
        self.some_setting_input = toga.TextInput(placeholder="Ex: Alguma Configuração")
        save_button = toga.Button("Salvar", on_press=self.presenter.handle_save_settings)
        close_button = toga.Button("Fechar", on_press=self.presenter.handle_close_window)

        main_box = toga.Box(
            style=Pack(direction=COLUMN, padding=20),
            children=[
                toga.Label("Opções Gerais:", style=Pack(font_weight='bold')),
                self.some_setting_input,
                save_button,
                close_button
            ]
        )
        self.toga_window.content = main_box

    def show(self):
        self.toga_window.show()

    def close(self):
        self.toga_window.close() # Isso irá acionar o on_close do WindowManager

    def show_confirmation(self, title, message):
        self.toga_window.info_dialog(title, message)

    # Exemplo de handler on_close específico da janela (opcional)
    # def my_custom_on_close_logic(self, window, **kwargs):
    #     print("SettingsView: Lógica de limpeza específica ao fechar.")
    #     # IMPORTANTE: Se você definir este, o WindowManager o chamará.
    #     # Você NÃO precisa chamar window.close() aqui normalmente,
    #     # a menos que queira interromper o fechamento sob certas condições
    #     # (o que é mais complexo e não coberto pelo on_close do Toga diretamente).

# Passo 3: Criar a Função de Fábrica `create_and_show_window`

# Esta função é o ponto de entrada que o WindowManager usará.
def create_and_show_window(app_instance, window_manager, **kwargs):
    view = SettingsView(app_instance, window_manager, **kwargs)
    view.show()
    return view.toga_window # ESSENCIAL: Retornar a instância de toga.Window
Passo 3: (Já incluído acima) Função de Fábrica
Cada módulo de janela DEVE ter uma função:
def create_and_show_window(app_instance, window_manager, **kwargs):
Esta função deve instanciar sua View (que por sua vez pode instanciar seu Presenter), chamar .show() na janela Toga da view, e crucialmente, retornar a instância de toga.Window (ex: return view.toga_window).

Passo 4: Acionar a Abertura da Nova Janela
No seu app.py (ou em qualquer outro lugar onde você tenha acesso à instância self.window_manager da sua aplicação principal):

Adicione um Botão ou Comando de Menu:
Python

# Em app.py, dentro da sua classe principal (ex: RUAppUTFPRAp)
# No método startup() ou onde você constrói sua UI principal:

# ...
# self.window_manager = WindowManager(self) # Já deve existir no __init__
# ...

# def _abrir_janela_configuracoes(self, widget):
#     self.window_manager.open_window("settings") # "settings" deve corresponder ao nome do arquivo/tipo

# ...
# btn_settings = toga.Button("Configurações", on_press=self._abrir_janela_configuracoes)
# seu_layout_principal.add(btn_settings)
Certifique-se de que o string passado para open_window (ex: "settings") corresponda à parte do nome do arquivo do módulo da janela (ex: settings_window.py -> tipo "settings").

Passo 5: Serviços de Dados (Se Necessário)
Se sua nova janela precisar interagir com dados persistentes (ler/salvar arquivos, etc.), crie ou utilize um módulo de serviço dedicado, similar ao student_data_service.py. O Presenter da sua nova janela seria responsável por usar este serviço.

Passo 6: Dependências no pyproject.toml
Se a sua nova janela introduzir dependências de bibliotecas Python que ainda não estão no seu projeto, adicione-as às seções requires apropriadas no seu arquivo pyproject.toml e rode briefcase dev -d (ou briefcase update -d).