# src/ruapputfprap/student_data_service.py
import csv
from pathlib import Path

# Define o caminho para o arquivo CSV dentro do diretório da aplicação
# __file__ se refere ao arquivo student_data_service.py
# .parent se refere ao diretório src/ruapputfprap/
# Então, src/ruapputfprap/data/students.csv
APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
STUDENTS_CSV_PATH = DATA_DIR / "students.csv"

DEFAULT_STUDENTS_DATA = [
    {"RA": "2478498", "NomeCompleto": "Murilo Fontana Muniz", "SaldoRU": "28.50", "PeriodoCurso": "5º Período", "Sexo": "Masculino", "Curso": "Engenharia de Software", "StatusMatricula": "Ativo", "Email": "murilo.muniz@email.com"},
    {"RA": "1234567", "NomeCompleto": "Ana Clara Silva", "SaldoRU": "15.75", "PeriodoCurso": "3º Período", "Sexo": "Feminino", "Curso": "Design Digital", "StatusMatricula": "Ativo", "Email": "ana.silva@email.com"},
    {"RA": "9876543", "NomeCompleto": "Carlos Eduardo Pereira", "SaldoRU": "5.00", "PeriodoCurso": "7º Período", "Sexo": "Masculino", "Curso": "Engenharia Mecânica", "StatusMatricula": "Inativo", "Email": "carlos.pereira@email.com"},
    {"RA": "5566778", "NomeCompleto": "Beatriz Oliveira Almeida", "SaldoRU": "35.20", "PeriodoCurso": "2º Período", "Sexo": "Feminino", "Curso": "Arquitetura e Urbanismo", "StatusMatricula": "Ativo", "Email": "beatriz.almeida@email.com"},
    {"RA": "1122334", "NomeCompleto": "Lucas Gabriel Costa", "SaldoRU": "0.00", "PeriodoCurso": "1º Período", "Sexo": "Masculino", "Curso": "Sistemas de Informação", "StatusMatricula": "Trancado", "Email": "lucas.costa@email.com"},
]
CSV_HEADERS = ["RA", "NomeCompleto", "SaldoRU", "PeriodoCurso", "Sexo", "Curso", "StatusMatricula", "Email"]

class StudentDataService:
    def __init__(self):
        self._students_data = {}  # Dicionário para acesso rápido por RA
        self._ensure_students_csv()
        self.load_students_data()

    def _ensure_students_csv(self):
        """Garante que o diretório de dados e o arquivo CSV existam."""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True) # Cria o diretório /data se não existir
            if not STUDENTS_CSV_PATH.exists():
                print(f"Arquivo {STUDENTS_CSV_PATH} não encontrado. Criando com dados padrão...")
                with open(STUDENTS_CSV_PATH, mode='w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
                    writer.writeheader()
                    writer.writerows(DEFAULT_STUDENTS_DATA)
                print("Arquivo CSV criado com sucesso.")
        except Exception as e:
            print(f"Erro ao garantir/criar o arquivo CSV: {e}")


    def load_students_data(self):
        """Carrega os dados dos alunos do arquivo CSV."""
        try:
            with open(STUDENTS_CSV_PATH, mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                self._students_data = {row['RA']: row for row in reader}
            print(f"Dados de {len(self._students_data)} alunos carregados.")
            return True
        except FileNotFoundError:
            print(f"Erro: Arquivo {STUDENTS_CSV_PATH} não encontrado ao carregar.")
            self._students_data = {} # Garante que está vazio se não carregar
            return False
        except Exception as e:
            print(f"Erro ao carregar dados dos alunos: {e}")
            self._students_data = {}
            return False

    def find_student_by_ra(self, ra_to_find: str):
        """Busca um aluno pelo RA nos dados carregados."""
        return self._students_data.get(ra_to_find)

    def get_all_students(self):
        """Retorna uma lista de todos os alunos (dicionários)."""
        return list(self._students_data.values())

    def get_first_student_ra(self):
        """Retorna o RA do primeiro aluno na base, ou None se vazia."""
        if self._students_data:
            return next(iter(self._students_data.keys()))
        return None