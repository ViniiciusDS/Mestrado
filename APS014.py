import sys
import numpy as np
from TerminalReader import TerminalReader
from TWRCalibration import TWRCalibration
from CandidateDelayGenerator import CandidateDelayGenerator
from CandidateEvaluator import CandidateEvaluator

def main():
    if len(sys.argv) < 6:
        print("Uso: APS014.py <porta> <baudrate> <timeout> <num_tags> <num_anchors> <matriz_edm>")
        sys.exit(1)

    porta = sys.argv[1]
    baudrate = int(sys.argv[2])
    timeout = float(sys.argv[3])
    num_tags = int(sys.argv[4])
    num_anchors = int(sys.argv[5])
    edm_manual = np.array(eval(sys.argv[6]))

    num_devices = num_tags + num_anchors
    print(f"Configuração: {num_tags} tags e {num_anchors} âncoras ({num_devices} dispositivos no total).")

    terminal = TerminalReader(port=porta, baudrate=baudrate, timeout=timeout)

    if not terminal.connect():
        sys.exit(1)  # Retorna erro para a interface

    try:
        print("\nExecutando o algoritmo TWR Calibration...")
        twr_calibration = TWRCalibration(terminal=terminal, num_estimates=200)
        edm_measured = twr_calibration.run(num_devices=num_devices)

        if edm_measured is not None:
            print("Matriz EDM medida com sucesso:")
            print(edm_measured)

            erro = np.linalg.norm(edm_measured - edm_manual)
            print(f"Erro total entre EDM medida e manual: {erro:.4f}")

            print("\nGerando candidatos de atraso...")
            generator = CandidateDelayGenerator(
                initial_delay=513e-9, 
                perturbation_limit=0.2e-9, 
                iterations=100, 
                num_candidates=1000
            )
            candidates = generator.generate_candidates()

            print("\nExecutando a avaliação dos candidatos...")
            evaluator = CandidateEvaluator(edm_actual=edm_manual, tof_measured=edm_measured / 3e8)
            sorted_candidates = evaluator.evaluate(candidates)

            print("\nCandidatos ordenados por qualidade:")
            for candidate, error in sorted_candidates[:5]:  
                print(f"Atraso: {candidate:.9f} s, Erro: {error:.6f} s")

    except KeyboardInterrupt:
        print("\nProcesso interrompido pelo usuário.")
    finally:
        terminal.close()


#   Teste local do modulo
if __name__ == "__main__":
    main()
