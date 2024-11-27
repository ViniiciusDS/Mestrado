from TerminalReader import TerminalReader
from TWRCalibration import TWRCalibration
from CandidateDelayGenerator import CandidateDelayGenerator

def main():
    print("Configuração da porta serial para calibração de atraso de antena:")
    porta = input("Insira o nome da porta (ex.: COM3): ").strip()
    try:
        baudrate = int(input("Insira o baudrate (ex.: 115200): ").strip())
        timeout = float(input("Insira o timeout em segundos (ex.: 1): ").strip())
    except ValueError:
        print("Valores inválidos! Usando configurações padrão (COM3, 115200, timeout 1s).")
        porta = "COM3"
        baudrate = 115200
        timeout = 1

    num_tags = int(input("Quantas tags estão em uso? ").strip())
    num_anchors = int(input("Quantas âncoras estão em uso? ").strip())
    num_devices = num_tags + num_anchors
    print(f"Configuração: {num_tags} tags e {num_anchors} âncoras ({num_devices} dispositivos no total).")

    print("Insira a matriz euclidiana conhecida (valores separados por espaço, linha por linha):")
    edm_manual = []
    for i in range(num_devices):
        linha = list(map(float, input(f"Linha {i + 1}: ").strip().split()))
        edm_manual.append(linha)
    edm_manual = np.array(edm_manual)
    print("Matriz euclidiana conhecida carregada:")
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
                print("Candidatos gerados com sucesso:")
                print(candidates)

                print("\nExecutando a avaliação dos candidatos...")
            
                evaluator = CandidateEvaluator(edm_actual=edm_manual, tof_measured=edm_measured / 3e8)
                sorted_candidates = evaluator.evaluate(candidates)

                print("\nCandidatos ordenados por qualidade:")
                for candidate, error in sorted_candidates:
                    print(f"Atraso: {candidate:.9f} s, Erro: {error:.6f} s")
                    
        except KeyboardInterrupt:
            print("\nProcesso interrompido pelo usuário.")
        finally:
            terminal.close()

if __name__ == "__main__":
    main()
