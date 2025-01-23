import sys
import numpy as np
from TerminalReader import TerminalReader
from TWRCalibration import TWRCalibration
from CandidateDelayGenerator import CandidateDelayGenerator
from CandidateEvaluator import CandidateEvaluator

def main():
    # Validar argumentos da linha de comando
    if len(sys.argv) < 6:
        print("Uso: APS014.py <porta> <baudrate> <timeout> <num_tags> <num_anchors> <matriz_edm>")
        sys.exit(1)

    # Receber parâmetros da interface
    porta = sys.argv[1]
    baudrate = int(sys.argv[2])
    timeout = float(sys.argv[3])
    num_tags = int(sys.argv[4])
    num_anchors = int(sys.argv[5])
    edm_manual = np.array(eval(sys.argv[6]))  # Converter string para matriz numpy

    num_devices = num_tags + num_anchors
    print(f"Configuração: {num_tags} tags e {num_anchors} âncoras ({num_devices} dispositivos no total).")
    print("Matriz euclidiana conhecida:")
    print(edm_manual)

    terminal = TerminalReader(port=porta, baudrate=baudrate, timeout=timeout)

    if terminal.connect():
        try:
            # Etapa 1: Executar TWR Calibration
            print("\nExecutando o algoritmo TWR Calibration...")
            twr_calibration = TWRCalibration(terminal=terminal, num_estimates=200)
            edm_measured = twr_calibration.run(num_devices=num_devices)

            if edm_measured is not None:
                print("Matriz EDM medida com sucesso:")
                print(edm_measured)

                # Comparação com a matriz conhecida
                erro = np.linalg.norm(edm_measured - edm_manual)
                print(f"Erro total entre EDM medida e manual: {erro:.4f}")

                # Etapa 2: Gerar candidatos de atraso
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
                for candidate, error in sorted_candidates[:5]:  # Mostrar os 5 melhores
                    print(f"Atraso: {candidate:.9f} s, Erro: {error:.6f} s")
                    
        except KeyboardInterrupt:
            print("\nProcesso interrompido pelo usuário.")
        finally:
            terminal.close()
    else:
        print("Não foi possível conectar à porta. Retornando ao controle da interface.")
        sys.exit(1)

if __name__ == "__main__":
    main()
