import numpy as np

class CandidateEvaluator:
    def __init__(self, edm_actual, tof_measured):
        """
        Inicializa o avaliador de candidatos.
        
        :param edm_actual: Matriz de distâncias reais (média euclidiana conhecida).
        :param tof_measured: Matriz de tempos de voo medidos.
        """
        self.edm_actual = edm_actual
        self.tof_measured = tof_measured

    def evaluate(self, candidates):
        """
        Avalia a qualidade de cada candidato.

        :param candidates: Lista de atrasos candidatos (em segundos).
        :return: Lista de candidatos ordenados pela qualidade (erro crescente).
        """
        errors = []
        tof_actual = self._calculate_tof_actual()

        for idx, candidate_delay in enumerate(candidates):
            tof_candidate = self._calculate_tof_candidate(candidate_delay)
            error = np.linalg.norm(tof_actual - tof_candidate)
            errors.append((candidate_delay, error))
            print(f"Candidato {idx + 1}: Erro = {error:.6f} segundos")

        # Ordenar candidatos pelo erro (menor erro primeiro)
        errors.sort(key=lambda x: x[1])
        return errors

    def _calculate_tof_actual(self):
        """
        Calcula a matriz de tempos de voo reais (ToF_actual) com base no EDM real.
        """
        c = 3e8  # Velocidade da luz (m/s)
        return self.edm_actual / c

    def _calculate_tof_candidate(self, candidate_delay):
        """
        Calcula a matriz de tempos de voo para um candidato (ToF_candidate).
        
        :param candidate_delay: Atraso candidato (em segundos).
        :return: Matriz de tempos de voo ajustada pelo atraso candidato.
        """
        n_devices = self.edm_actual.shape[0]
        tof_candidate = np.zeros_like(self.tof_measured)

        for i in range(n_devices):
            for j in range(n_devices):
                if i != j:
                    tof_candidate[i, j] = (
                        2 * candidate_delay + self.tof_measured[i, j]
                    ) / 4
        return tof_candidate


# Teste local do módulo
if __name__ == "__main__":
    # Exemplo de matriz EDM real (distâncias em metros)
    edm_actual = np.array([
        [0.0, 10.0, 15.0],
        [10.0, 0.0, 12.0],
        [15.0, 12.0, 0.0]
    ])

    # Exemplo de matriz ToF medida (tempo em segundos)
    tof_measured = edm_actual / 3e8  # Simulação: EDM / velocidade da luz

    # Exemplo de candidatos
    candidates = np.random.uniform(513e-9 - 6e-9, 513e-9 + 6e-9, 10)

    evaluator = CandidateEvaluator(edm_actual, tof_measured)
    sorted_candidates = evaluator.evaluate(candidates)

    print("\nCandidatos ordenados:")
    for candidate, error in sorted_candidates:
        print(f"Atraso: {candidate:.9f} s, Erro: {error:.6f} s")
