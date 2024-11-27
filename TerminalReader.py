import serial
import threading
import sys

class TerminalReader:
    def __init__(self, port, baudrate=115200, timeout=1):
        """
        Inicializa a conexão serial com os parâmetros especificados.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None
        self.running = True  # Controla o loop principal

    def connect(self):
        """
        Tenta estabelecer conexão com a porta serial.
        Caso falhe, oferece a opção de tentar novamente ou sair.
        """
        while True:
            try:
                self.connection = serial.Serial(
                    port=self.port,
                    baudrate=self.baudrate,
                    timeout=self.timeout,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS
                )
                print(f"Conectado à porta {self.port} com baudrate {self.baudrate}.")
                return True
            except serial.SerialException as e:
                print(f"Erro ao conectar na porta {self.port}: {e}")
                retry = input("Deseja tentar novamente? (s/n): ").strip().lower()
                if retry != 's':
                    print("Encerrando o programa.")
                    return False

    def read_distance(self):
        """
        Lê uma linha da porta serial e retorna a distância medida.
        """
        if self.connection and self.connection.is_open:
            try:
                line = self.connection.readline().decode('utf-8').strip()
                if line:
                    print(f"Dados recebidos: {line}")
                    return float(line)  # Converte para float se os dados forem numéricos
            except ValueError:
                print("Erro ao converter os dados recebidos para número.")
            except Exception as e:
                print(f"Erro durante a leitura: {e}")
        else:
            print("Conexão não estabelecida ou fechada.")
        return None

    def close(self):
        """
        Fecha a conexão serial.
        """
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("Conexão serial encerrada.")

    def stop(self):
        """
        Interrompe a execução do programa.
        """
        self.running = False


# Função para monitorar o "botão de segurança"
def monitorar_botao(terminal):
    print("Pressione 'q' e Enter para encerrar o programa a qualquer momento.")
    while terminal.running:
        comando = input()
        if comando.lower() == 'q':
            terminal.stop()
            print("Encerrando por comando do botão de segurança...")
            break


# Exemplo de uso:
if __name__ == "__main__":
    print("Configuração da porta serial:")
    porta = input("Insira o nome da porta (ex.: COM3): ").strip()
    try:
        baudrate = int(input("Insira o baudrate (ex.: 115200): ").strip())
        timeout = float(input("Insira o timeout em segundos (ex.: 1): ").strip())
    except ValueError:
        print("Valores inválidos! Usando configurações padrão (COM3, 115200, timeout 1s).")
        porta = "COM3"
        baudrate = 115200
        timeout = 1

    terminal = TerminalReader(port=porta, baudrate=baudrate, timeout=timeout)

    if terminal.connect():
        # Iniciar monitoramento do botão de segurança em uma thread separada
        botao_thread = threading.Thread(target=monitorar_botao, args=(terminal,))
        botao_thread.daemon = True  # Thread será finalizada quando o programa principal encerrar
        botao_thread.start()

        try:
            while terminal.running:
                distancia = terminal.read_distance()
                if distancia is not None:
                    print(f"Distância medida: {distancia} metros")
        except KeyboardInterrupt:
            print("\nFinalizando...")
        finally:
            terminal.close()
