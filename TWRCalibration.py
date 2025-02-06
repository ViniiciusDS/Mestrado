import sys
import numpy as np
from TerminalReader import TerminalReader

class TWRCalibration:
    def __init__(self, terminal, num_estimates=200):
        self.terminal = terminal
        self.num_estimates = num_estimates

    def measure_distances(self):
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
        edm = np.zeros((num_devices, num_devices))
        index = 0
        print(f"Calculando EDM para {num_devices} dispositivos.")
        for i in range(num_devices):
            for j in range(i + 1, num_devices):
                if index < len(distances):
                    edm[i, j] = distances[index]
                    edm[j, i] = edm[i, j]
                    index += 1
        return edm

    def run(self, num_devices):
        distances = self.measure_distances()
        if not distances:
            print("Nenhuma medição válida foi obtida. Finalizando...")
            return None
        edm = self.calculate_edm(distances, num_devices)
        print("Matriz EDM medida:")
        print(edm)
        return edm

#   Teste local do modulo
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: TWRCalibration.py <porta> <baudrate> <timeout>")
        sys.exit(1)

    porta = sys.argv[1]
    baudrate = int(sys.argv[2])
    timeout = float(sys.argv[3])

    terminal = TerminalReader(port=porta, baudrate=baudrate, timeout=timeout)

    if not terminal.connect():
        sys.exit(1)  # Falha na conexão, retorna erro para a interface

    calibration = TWRCalibration(terminal=terminal, num_estimates=200)
    try:
        edm = calibration.run(num_devices=4)
        if edm is not None:
            print("Calibração concluída com sucesso.")
    except KeyboardInterrupt:
        print("\nFinalizando...")
    finally:
        terminal.close()
