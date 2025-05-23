# src/ruapputfprap/ra_qrcode_window.py
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER, ROW, LEFT
import random

import qrcode
from PIL import Image as PILImage
import io

# ----- NOVA IMPORTAÇÃO -----
from .student_data_service import StudentDataService
# ---------------------------

class RAQRCodePresenter:
    def __init__(self, view_delegate, app_instance, window_manager):
        self.view = view_delegate
        self.app = app_instance
        self.window_manager = window_manager
        
        self.student_service = StudentDataService()
        
        self.current_student_ra = self.student_service.get_first_student_ra()
        if not self.current_student_ra:
            print("Nenhum aluno carregado do CSV, usando RA fictício.")
            self.current_student_ra = self._generate_fictitious_ra() 

    def _generate_fictitious_ra(self): # Mantido como fallback
        return str(random.randint(1000000, 9999999))

    def _generate_qr_image_bytes(self, data_text):
        if not data_text: return None
        try:
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=8, border=4) # box_size menor
            qr.add_data(data_text)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            return img_byte_arr.getvalue()
        except Exception as e:
            print(f"Erro ao gerar imagem QR Code: {e}")
            return None

    def _update_view_data(self):
        """Atualiza a view com o RA atual para o QR Code."""
        self.view.set_ra_for_qr(f"RA: {self.current_student_ra if self.current_student_ra else 'N/A'}")
        qr_image_bytes = self._generate_qr_image_bytes(self.current_student_ra)
        if qr_image_bytes:
            self.view.set_qrcode_image(qr_image_bytes)
        else:
            self.view.set_qrcode_placeholder_text("QR Code Indisponível")
        self.view.clear_student_details() # Limpa detalhes anteriores ao mostrar novo RA

    def handle_simulate_read_action(self, widget):
        """Simula a leitura do RA atual e busca os dados do aluno."""
        if not self.current_student_ra:
            self.view.show_info_dialog("Simulação Falhou", "Nenhum RA para simular.")
            self.view.clear_student_details()
            self.view.display_search_result("Nenhum RA para simular.")
            return

        student_info = self.student_service.find_student_by_ra(self.current_student_ra)
        
        if student_info:
            self.view.display_student_details(student_info)
            self.view.display_search_result(f"RA {self.current_student_ra} encontrado!")
            # Adiciona notificação no app principal
            if hasattr(self.app, 'notifi_utils') and hasattr(self.app.notifi_utils, 'adicionar_notificacao'):
                self.app.notifi_utils.adicionar_notificacao(f"RA {self.current_student_ra} ({student_info.get('NomeCompleto', '')}) verificado.")
        else:
            self.view.clear_student_details()
            self.view.display_search_result(f"RA {self.current_student_ra} NÃO encontrado na base de dados.")
            self.view.show_info_dialog("Resultado da Simulação", f"RA {self.current_student_ra} NÃO encontrado.")
        
    def handle_close_action(self, widget):
        self.view.close()

    def load_next_student(self, widget=None): # Novo método
        """Carrega o próximo aluno da lista para simulação."""
        students = self.student_service.get_all_students()
        if not students:
            self.current_student_ra = self._generate_fictitious_ra()
            self._update_view_data()
            return

        if self.current_student_ra:
            try:
                current_idx = [s['RA'] for s in students].index(self.current_student_ra)
                next_idx = (current_idx + 1) % len(students)
                self.current_student_ra = students[next_idx]['RA']
            except ValueError: # RA atual não está na lista (ex: fictício)
                self.current_student_ra = students[0]['RA']
        else: # Nenhum RA atual
            self.current_student_ra = students[0]['RA']
        
        self._update_view_data()
        print(f"Próximo RA para simulação: {self.current_student_ra}")


class RAQRCodeView:
    def __init__(self, app_instance, window_manager):
        self.app = app_instance
        self.window_manager = window_manager
        self.toga_window = toga.Window(
            title="Identificação Aluno via QR Code",
            size=(420, 650) # Aumentar tamanho para mais detalhes
        )
        self.presenter = RAQRCodePresenter(self, app_instance, window_manager)
        self._build_ui()

    def _build_ui(self):
        self.qr_image_view = toga.ImageView(style=Pack(width=150, height=150, padding_bottom=5))
        self.qr_code_status_label = toga.Label("Gerando QR Code...", style=Pack(text_align=CENTER, padding_bottom=10, font_size=9))
        self.ra_for_qr_label = toga.Label("RA: ", style=Pack(padding_bottom=10, font_size=12, text_align=CENTER, font_weight='bold'))

        style_label_campo = Pack(text_align=LEFT, padding_right=5, width=100, font_weight='bold') # padding_right para separar do valor
        style_label_valor = Pack(text_align=LEFT, flex=1)

        self.nome_label = toga.Label("---", style=style_label_valor)
        self.saldo_label = toga.Label("---", style=style_label_valor)
        self.periodo_label = toga.Label("---", style=style_label_valor)
        self.sexo_label = toga.Label("---", style=style_label_valor)
        self.curso_label = toga.Label("---", style=style_label_valor)
        self.status_label = toga.Label("---", style=style_label_valor)
        self.email_label = toga.Label("---", style=style_label_valor)
        
        details_box = toga.Box(style=Pack(direction=COLUMN, padding_top=10), children=[
            # CORREÇÃO: direction=LEFT alterado para direction=ROW
            toga.Box(style=Pack(direction=ROW, padding_bottom=2), children=[toga.Label("Nome:", style=style_label_campo), self.nome_label]),
            toga.Box(style=Pack(direction=ROW, padding_bottom=2), children=[toga.Label("Saldo RU:", style=style_label_campo), self.saldo_label]),
            toga.Box(style=Pack(direction=ROW, padding_bottom=2), children=[toga.Label("Período:", style=style_label_campo), self.periodo_label]),
            toga.Box(style=Pack(direction=ROW, padding_bottom=2), children=[toga.Label("Sexo:", style=style_label_campo), self.sexo_label]),
            toga.Box(style=Pack(direction=ROW, padding_bottom=2), children=[toga.Label("Curso:", style=style_label_campo), self.curso_label]),
            toga.Box(style=Pack(direction=ROW, padding_bottom=2), children=[toga.Label("Status:", style=style_label_campo), self.status_label]),
            toga.Box(style=Pack(direction=ROW, padding_bottom=2), children=[toga.Label("Email:", style=style_label_campo), self.email_label]),
        ])

        self.search_result_label = toga.Label("Clique em 'Simular Leitura' para verificar o RA.", style=Pack(padding_top=15, text_align=CENTER, font_style='italic'))
        
        simulate_button = toga.Button("Simular Leitura do RA", on_press=self.presenter.handle_simulate_read_action, style=Pack(padding_top=20, width=220, background_color='lightgreen'))
        next_student_button = toga.Button("Próximo Aluno (Simulação)", on_press=self.presenter.load_next_student, style=Pack(padding_top=5, width=220))
        close_button = toga.Button("Fechar", on_press=self.presenter.handle_close_action, style=Pack(padding_top=10, width=120))

        main_box = toga.Box(
            style=Pack(direction=COLUMN, padding=20, alignment=CENTER),
            children=[
                toga.Label("Leitor de Identificação (Simulado)", style=Pack(font_size=16, padding_bottom=10, text_align=CENTER)),
                self.qr_image_view,
                self.qr_code_status_label,
                self.ra_for_qr_label,
                details_box,
                self.search_result_label,
                simulate_button,
                next_student_button,
                close_button
            ]
        )
        self.toga_window.content = main_box

    def set_ra_for_qr(self, text):
        self.ra_for_qr_label.text = text

    def set_qrcode_image(self, image_bytes):
        if image_bytes:
            self.qr_image_view.image = toga.Image(data=image_bytes)
            self.qr_code_status_label.text = "" 
            self.qr_code_status_label.style.update(height=0, padding=0)
        else:
            self.set_qrcode_placeholder_text("Falha ao carregar QR Code.")

    def set_qrcode_placeholder_text(self, text):
        self.qr_image_view.image = None 
        self.qr_code_status_label.text = text
        self.qr_code_status_label.style.update(height=None, padding_bottom=10) # Garante que o texto de status seja visível

    def display_student_details(self, student_info: dict):
        self.nome_label.text = student_info.get("NomeCompleto", "N/A")
        saldo_ru = student_info.get("SaldoRU", "N/A")
        try:
            self.saldo_label.text = f"R$ {float(saldo_ru):.2f}" if saldo_ru != "N/A" else "N/A"
        except ValueError:
            self.saldo_label.text = saldo_ru # Mantém como está se não for um número válido
            
        self.periodo_label.text = student_info.get("PeriodoCurso", "N/A")
        self.sexo_label.text = student_info.get("Sexo", "N/A")
        self.curso_label.text = student_info.get("Curso", "N/A")
        self.status_label.text = student_info.get("StatusMatricula", "N/A")
        self.email_label.text = student_info.get("Email", "N/A")


    def clear_student_details(self):
        self.nome_label.text = "---"
        self.saldo_label.text = "---"
        self.periodo_label.text = "---"
        self.sexo_label.text = "---"
        self.curso_label.text = "---"
        self.status_label.text = "---"
        self.email_label.text = "---"

    def display_search_result(self, message: str):
        self.search_result_label.text = message
        
    def show_info_dialog(self, title, message):
        self.toga_window.info_dialog(title, message)

    def show(self):
        self.toga_window.show()
        self.presenter._update_view_data() # Atualiza o RA e QR ao mostrar
        self.clear_student_details() # Garante que detalhes estejam limpos inicialmente

    def close(self):
        self.toga_window.close()

def create_and_show_window(app_instance, window_manager, **kwargs):
    view = RAQRCodeView(app_instance, window_manager)
    view.show()
    return view.toga_window