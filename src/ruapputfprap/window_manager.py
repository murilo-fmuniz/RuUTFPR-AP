# src/ruapputfprap/window_manager.py
import toga
import importlib
import traceback # Mantenha esta importação

class WindowManager:
    def __init__(self, app_instance):
        self.app = app_instance
        self.open_windows = {}
        print("WindowManager: Inicializado.")

    def open_window(self, window_type: str, **kwargs):
        print(f"\nWindowManager: ---- Tentando abrir janela do tipo: {window_type} ----")
        print(f"WindowManager: Janelas atualmente rastreadas: {list(self.open_windows.keys())}")

        if window_type in self.open_windows:
            window_instance = self.open_windows[window_type]
            print(f"WindowManager: Janela '{window_type}' encontrada no rastreamento. ID da Instância: {id(window_instance)}.")
            try:
                print(f"WindowManager: Tentando .show() na instância existente de '{window_type}'.")
                window_instance.show()
                print(f"WindowManager: Chamada .show() bem-sucedida para '{window_type}'. A janela deve estar visível/focada.")
                return window_instance
            except Exception as e:
                print(f"WindowManager: EXCEÇÃO durante .show() para '{window_type}' existente (ID: {id(window_instance)}): {type(e).__name__} - {e}")
                print(f"WindowManager: Assumindo que a instância (ID: {id(window_instance)}) não é mais válida. Removendo do rastreamento.")
                del self.open_windows[window_type]
                print(f"WindowManager: '{window_type}' removida. Janelas rastreadas: {list(self.open_windows.keys())}. Prosseguindo para criar nova instância.")
        else:
            print(f"WindowManager: Janela do tipo '{window_type}' NÃO encontrada no rastreamento. Será criada uma nova instância.")

        print(f"WindowManager: Importando módulo e criando nova janela para '{window_type}'.")
        window_module_name = f".{window_type}_window"
        try:
            module = importlib.import_module(window_module_name, package=self.app.module_name)
            if hasattr(module, "create_and_show_window"):
                new_toga_window = module.create_and_show_window(self.app, self, **kwargs)
                if new_toga_window and isinstance(new_toga_window, toga.Window):
                    print(f"WindowManager: Nova janela '{window_type}' (ID: {id(new_toga_window)}) criada e mostrada.")
                    self.open_windows[window_type] = new_toga_window
                    
                    original_on_close_handler = getattr(new_toga_window, '_original_on_close_handler', None)
                    if not original_on_close_handler and hasattr(new_toga_window, 'on_close'):
                        current_on_close = new_toga_window.on_close
                        if not (hasattr(current_on_close, '__name__') and current_on_close.__name__ == '_manager_on_close_wrapper'):
                             new_toga_window._original_on_close_handler = current_on_close
                    
                    def _manager_on_close_wrapper(window, **kw):
                        print(f"WindowManager: Callback _manager_on_close_wrapper para '{window_type}' (ID da Janela de Origem: {id(window)}) iniciado.")
                        
                        original_handler = getattr(window, '_original_on_close_handler', None)
                        if callable(original_handler):
                            print(f"WindowManager: Chamando _original_on_close_handler para '{window_type}'.")
                            original_handler(window)

                        # Verifica se a janela a ser removida é de fato a que está no dicionário
                        if self.open_windows.get(window_type) == window:
                            print(f"WindowManager: Removendo '{window_type}' (ID: {id(window)}) do rastreamento devido ao on_close.")
                            del self.open_windows[window_type]
                            print(f"WindowManager: '{window_type}' removida. Janelas rastreadas agora: {list(self.open_windows.keys())}")
                        else:
                            print(f"WindowManager AVISO: '{window_type}' (ID: {id(window)}) on_close chamado, mas não encontrada no rastreamento ou instância não corresponde.")
                            print(f"WindowManager DEBUG: Instância rastreada para '{window_type}' é ID: {id(self.open_windows.get(window_type)) if self.open_windows.get(window_type) else 'Nenhuma'}")

                    new_toga_window.on_close = _manager_on_close_wrapper
                    return new_toga_window
                else:
                    error_msg = f"Função 'create_and_show_window' em {window_module_name} não retornou uma toga.Window válida."
                    print(f"Erro Crítico (WindowManager): {error_msg}") # Mudado para print
                    # self.app.main_window.error_dialog("Erro de Criação de Janela", error_msg) # Comentado
            else:
                error_msg = f"Módulo {window_module_name} não possui 'create_and_show_window'."
                print(f"Erro Crítico (WindowManager): {error_msg}") # Mudado para print
                # self.app.main_window.error_dialog("Erro de Carregamento", error_msg) # Comentado
        
        except ImportError as e_import:
            error_msg = f"Módulo para '{window_type}' ({window_module_name}) não encontrado: {e_import}"
            print(f"Erro Crítico de Importação (WindowManager): {error_msg}") # Mudado para print
            traceback.print_exc()
            # self.app.main_window.error_dialog("Erro de Importação", error_msg) # Comentado

        except Exception as e_geral: # Erro durante a criação da janela
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!! WindowManager: ERRO INESPERADO ORIGINAL CAPTURADO (durante import/create) !!!")
            print(f"!!! Tipo da Exceção Original: {type(e_geral)}")
            print(f"!!! Argumentos da Exceção Original: {e_geral.args}")
            print("!!! Traceback Original Completo:")
            traceback.print_exc()
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            # error_msg = f"Erro ao criar/abrir janela '{window_type}': {e_geral}"
            # try:
            # self.app.main_window.error_dialog("Erro Inesperado (Ver Console para Detalhes)", error_msg) # Comentado
            # except Exception as dialog_e:
            # print(f"!!! WindowManager: FATAL - Erro ao tentar exibir o diálogo de erro do Toga! Detalhes: {dialog_e}")
            # print(f"!!! WindowManager: A mensagem de erro original era: {error_msg}")
            
        return None

    def close_window(self, window_type: str):
        # ... (método close_window como antes, talvez adicionar prints também) ...
        if window_type in self.open_windows:
            window_instance = self.open_windows[window_type]
            print(f"WindowManager: Fechando programaticamente a janela '{window_type}' (ID: {id(window_instance)}).")
            try:
                window_instance.close()
            except Exception as e:
                print(f"WindowManager: Erro ao fechar programaticamente '{window_type}': {e}. Tentando remover do rastreamento.")
                del self.open_windows[window_type] # Remove se o close() falhar
        else:
            print(f"WindowManager: Janela do tipo '{window_type}' não encontrada para fechar programaticamente.")


    def get_window(self, window_type: str):
        return self.open_windows.get(window_type)