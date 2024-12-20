import numpy as np
from TerminalReader import TerminalReader

class TWRCalibration:
    def __init__(self, terminal, num_estimates=200):
        """
        Inicializa o processo de calibração de atraso de antena via TWR.
        
        :param terminal: Instância de TerminalReader para comunicação serial.
        :param num_estimates: Número de estimativas de distância (default: 200).
        """
        self.terminal = terminal
        self.num_estimates = num_estimates

    def measure_distances(self):
        """
        Realiza medições de distância utilizando o terminal serial.

        :return: Uma lista contendo as medições de distância.
        """
        distances = []
        print(f"Iniciando medições de distância ({self.num_estimates} estimativas)...")
        for i in range(self.num_estimates):
            distance = self.terminal.read_distance()
            if distance is not None:
                distances.append(distance)
                print(f"Medição {i + 1}/{self.num_estimates}: {distance:.3f} metros")
            else:
                print(f"Medição {i + 1}/{self.num_estimates} falhou.")
        return distances

    def calculate_edm(self, distances, num_devices):
        """
        Calcula a matriz de distâncias Euclidianas (EDM).

        :param distances: Lista de medições de distância.
        :param num_devices: Número total de dispositivos (tags + âncoras).
        :return: Matriz EDM calculada.
        """
        edm = np.zeros((num_devices, num_devices))
        index = 0

        print(f"Calculando EDM para {num_devices} dispositivos.")
        
        for i in range(num_devices):
            for j in range(i + 1, num_devices):
                if index < len(distances):
                    edm[i, j] = distances[index]
                    edm[j, i] = edm[i, j]  # Simetria
                    index += 1

        return edm

    def run(self, num_devices):
        """
        Executa o algoritmo de calibração de atraso de antena via TWR.

        :param num_devices: Número total de dispositivos (tags + âncoras).
        """
        # Etapa 1: Obter medições de distância
        distances = self.measure_distances()

        if not distances:
            print("Nenhuma medição válida foi obtida. Finalizando...")
            return None

        # Etapa 2: Calcular matriz EDM
        edm = self.calculate_edm(distances, num_devices)
        print("Matriz de Distâncias Euclidianas (EDM):")
        print(edm)

        return edm


# Teste local do módulo
if __name__ == "__main__":
    print("Configuração da porta serial para calibração TWR:")
    porta = input("Insira o nome da porta (ex.: COM3): ").strip()
    try:
        baudrate = int(input("Insira o baudrate (ex.: 115200): ").strip())
        timeout = float(input("Insira o timeout em segundos (ex.: 1): ").strip())
    except ValueError:
        print("Valores inválidos! Usando configurações padrão (COM3, 115200, timeout 1s).")
        porta = "COM3"
        baudrate = 115200
        timeout = 1

    num_devices = int(input("Quantos dispositivos estão em uso (tags + âncoras)? ").strip())

    terminal = TerminalReader(port=porta, baudrate=baudrate, timeout=timeout)

    if terminal.connect():
        calibration = TWRCalibration(terminal=terminal, num_estimates=200)
        try:
            edm = calibration.run(num_devices=num_devices)
            if edm is not None:
                print("Calibração concluída com sucesso.")
        except KeyboardInterrupt:
            print("\nFinalizando...")
        finally:
            terminal.close()
