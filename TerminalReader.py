import serial

class TerminalReader:
    def __init__(self, port, baudrate=115200, timeout=1):
        """
        Inicializa a conexão serial com os parâmetros especificados.
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None

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

# Exemplo de uso:
if __name__ == "__main__":
    terminal = TerminalReader(port='COM3')  # Substitua COM3 pela porta apropriada
    if terminal.connect():
        try:
            while True:
                distancia = terminal.read_distance()
                if distancia is not None:
                    print(f"Distância medida: {distancia} metros")
        except KeyboardInterrupt:
            print("\nFinalizando...")
        finally:
            terminal.close()
