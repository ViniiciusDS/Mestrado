import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports
import subprocess
import threading

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Interface de Testes - Projeto")
        self.geometry("800x600")
        self.setup_ui()

    def setup_ui(self):
        """Configura a interface gráfica"""

        # Título
        tk.Label(self, text="Software de Testes de Campo", font=("Helvetica", 16)).pack(pady=10)

        # Portas COM
        com_frame = tk.LabelFrame(self, text="Portas COM Disponíveis")
        com_frame.pack(pady=10, fill=tk.X, padx=10)

        tk.Label(com_frame, text="Selecionar Porta:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.com_list = ttk.Combobox(com_frame, state="readonly", width=40)
        self.com_list.grid(row=0, column=1, padx=5, pady=5)
        self.update_com_ports()

        tk.Button(com_frame, text="Atualizar Portas", command=self.update_com_ports).grid(row=0, column=2, padx=5, pady=5)

        # Opções de Teste
        test_frame = tk.LabelFrame(self, text="Opções de Teste")
        test_frame.pack(pady=10, fill=tk.X, padx=10)

        tk.Label(test_frame, text="Selecionar Teste:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.test_selector = ttk.Combobox(test_frame, state="readonly", width=40)
        self.test_selector["values"] = [
            "Teste Completo (APS014)", 
            "TWR Calibration", 
            "Candidate Delay Generator", 
            "Candidate Evaluator",
            "TerminalReader"
        ]
        self.test_selector.grid(row=0, column=1, padx=5, pady=5)
        self.test_selector.bind("<<ComboboxSelected>>", self.display_parameters)

        # Parâmetros de Entrada
        self.params_frame = tk.LabelFrame(self, text="Parâmetros de Entrada")
        self.params_frame.pack(pady=10, fill=tk.X, padx=10)

        self.param_widgets = []

        # Botões para execução
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Executar Teste", command=self.run_test).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Limpar Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=5)

        # Área de Logs
        logs_frame = tk.LabelFrame(self, text="Logs de Execução")
        logs_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=10)

        self.logs_text = tk.Text(logs_frame, wrap="word", height=15)
        self.logs_text.pack(pady=5, fill=tk.BOTH, expand=True)

    def update_com_ports(self):
        """Atualiza a lista de portas COM disponíveis"""
        ports = serial.tools.list_ports.comports()
        com_list = [f"{port.device} - {port.description}" for port in ports]
        self.com_list["values"] = com_list
        if com_list:
            self.com_list.current(0)

    def display_parameters(self, event):
        """Exibe os parâmetros específicos para o teste selecionado"""
        for widget in self.param_widgets:
            widget.destroy()
        self.param_widgets = []

        selected_test = self.test_selector.get()
        if selected_test == "Teste Completo (APS014)":
            self.add_parameter("Porta COM", "COM3")
            self.add_parameter("Baudrate", "115200")
            self.add_parameter("Timeout (s)", "1")
            self.add_parameter("Número de Tags", "2")
            self.add_parameter("Número de Âncoras", "2")
            self.add_parameter("Matriz Euclidiana (ex.: [[0,1],[1,0]])", "[[0, 1.0, 1.5], [1.0, 0, 2.0], [1.5, 2.0, 0]]")
        elif selected_test == "TWR Calibration":
            self.add_parameter("Porta COM", "COM3")
            self.add_parameter("Baudrate", "115200")
            self.add_parameter("Timeout (s)", "1")
        elif selected_test == "Candidate Delay Generator":
            self.add_parameter("Atraso Inicial (s)", "513e-9")
            self.add_parameter("Limite de Perturbação (s)", "0.2e-9")
            self.add_parameter("Número de Iterações", "100")
        elif selected_test == "Candidate Evaluator":
            self.add_parameter("Erro Máximo Aceitável", "1e-6")
        elif selected_test == "TerminalReader": 
            self.add_parameter("Porta COM", "COM3")
            self.add_parameter("Baudrate", "115200")
            self.add_parameter("Timeout (s)", "1")

    def add_parameter(self, label, default_value):
        """Adiciona um campo para entrada de parâmetro"""
        row = len(self.param_widgets) // 2
        label_widget = tk.Label(self.params_frame, text=label)
        label_widget.grid(row=row, column=0, padx=5, pady=5, sticky="w")
        entry_widget = tk.Entry(self.params_frame)
        entry_widget.insert(0, default_value)
        entry_widget.grid(row=row, column=1, padx=5, pady=5)
        self.param_widgets.append(label_widget)
        self.param_widgets.append(entry_widget)

    def run_test(self):
        """Executa o teste selecionado e trata falhas de conexão."""
        selected_test = self.test_selector.get()
        params = [widget.get() for widget in self.param_widgets if isinstance(widget, tk.Entry)]
        self.log(f"Executando: {selected_test} com parâmetros: {params}")

        # Executar TerminalReader em uma thread separada para evitar travamentos
        if selected_test == "TerminalReader":
            threading.Thread(target=self.run_terminal_reader, args=(params,)).start()
            return

        try:
            if selected_test == "Teste Completo (APS014)":
                result = subprocess.run(["python", "APS014.py"] + params, check=True)
            elif selected_test == "TWR Calibration":
                result = subprocess.run(["python", "TWRCalibration.py"] + params, check=True)
            elif selected_test == "Candidate Delay Generator":
                subprocess.run(["python", "CandidateDelayGenerator.py"] + params, check=True)
            elif selected_test == "Candidate Evaluator":
                subprocess.run(["python", "CandidateEvaluator.py"] + params, check=True)

            print(f"DEBUG: Código de saída do teste: {result.returncode}")

            if result.returncode == 1:
                self.ask_retry()

        except subprocess.CalledProcessError as e:
            print(f"DEBUG: Erro na execução do teste: {e}")
            self.ask_retry()

    def run_terminal_reader(self, params):
        """Executa o TerminalReader em uma thread separada."""
        try:
            result = subprocess.run(["python", "TerminalReader.py"] + params, check=True)
            print(f"DEBUG: Código de saída do TerminalReader: {result.returncode}")

            if result.returncode == 1:
                self.ask_retry()

        except subprocess.CalledProcessError as e:
            print(f"DEBUG: Erro ao executar TerminalReader: {e}")
            self.ask_retry()

    def ask_retry(self):
        """Pergunta ao usuário se deseja tentar novamente após falha de conexão"""
        retry = messagebox.askyesno("Erro de Conexão", "Não foi possível conectar à porta COM. Deseja tentar novamente?")
        if retry:
            self.run_test()  # Tenta novamente o teste

    def log(self, message):
        """Adiciona uma mensagem à área de logs"""
        self.logs_text.insert(tk.END, message + "\n")
        self.logs_text.see(tk.END)

    def clear_logs(self):
        """Limpa a área de logs"""
        self.logs_text.delete(1.0, tk.END)

if __name__ == "__main__":
    app = GUI()
    app.mainloop()
