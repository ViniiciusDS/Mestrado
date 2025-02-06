import serial
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

    def connect(self):
        """
        Tenta estabelecer conexão com a porta serial.
        Caso falhe, retorna False para que a interface possa tratar o erro.
        """
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
            return False  # Retorna False para que a interface capture

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
        return None

    def close(self):
        """
        Fecha a conexão serial.
        """
        if self.connection and self.connection.is_open:
            self.connection.close()
            print("Conexão serial encerrada.")

# Teste local do módulo
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: TerminalReader.py <porta> <baudrate> <timeout>")
        sys.exit(1)

    port = sys.argv[1]
    baudrate = int(sys.argv[2])
    timeout = float(sys.argv[3])

    reader = TerminalReader(port, baudrate, timeout)

    if reader.connect():
        distance = reader.read_distance()
        if distance is not None:
            print(f"Distância lida: {distance:.2f} m")
        reader.close()
    else:
        print("Erro ao conectar na porta serial.")
        sys.exit(1)  # Retorna erro para a interface
