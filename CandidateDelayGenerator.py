import numpy as np

class CandidateDelayGenerator:
    def __init__(self, initial_delay=513e-9, perturbation_limit=0.2e-9, iterations=100, num_candidates=1000):
        """
        Inicializa o gerador de candidatos de atraso.
        
        :param initial_delay: Atraso inicial em segundos (~513 ns).
        :param perturbation_limit: Limite inicial de perturbação (~0.2 ns).
        :param iterations: Número total de iterações.
        :param num_candidates: Número total de candidatos gerados em cada iteração.
        """
        self.initial_delay = initial_delay
        self.perturbation_limit = perturbation_limit
        self.iterations = iterations
        self.num_candidates = num_candidates

    def generate_candidates(self):
        """
        Gera o conjunto de candidatos iterativamente.

        :return: O melhor conjunto de candidatos após todas as iterações.
        """
        # Inicializar conjunto de candidatos
        candidate_set = np.random.uniform(
            self.initial_delay - 6e-9, 
            self.initial_delay + 6e-9, 
            self.num_candidates
        )
        print(f"Conjunto inicial de {self.num_candidates} candidatos gerado.")

        for iteration in range(1, self.iterations + 1):
            # Avaliar a qualidade dos candidatos (simulação: quanto mais próximo do inicial, melhor)
            errors = np.abs(candidate_set - self.initial_delay)
            sorted_indices = np.argsort(errors)
            
            # Selecionar os melhores 25%
            top_25_percent = sorted_indices[:self.num_candidates // 4]
            best_candidates = candidate_set[top_25_percent]
            print(f"Iteração {iteration}: Selecionados {len(best_candidates)} melhores candidatos.")

            # Perturbar os melhores candidatos
            perturbations = np.random.uniform(
                -self.perturbation_limit, 
                self.perturbation_limit, 
                len(best_candidates)
            )
            new_candidates = best_candidates + perturbations

            # Combinar candidatos antigos e novos
            candidate_set = np.concatenate([best_candidates, new_candidates])

            # Reduzir limite de perturbação a cada 20 iterações
            if iteration % 20 == 0:
                self.perturbation_limit /= 2
                print(f"Iteração {iteration}: Limite de perturbação reduzido para {self.perturbation_limit:.2e}.")

        return candidate_set

# Teste local do módulo
if __name__ == "__main__":
    generator = CandidateDelayGenerator(
        initial_delay=513e-9, 
        perturbation_limit=0.2e-9, 
        iterations=100, 
        num_candidates=1000
    )
    final_candidates = generator.generate_candidates()
    print("Conjunto final de candidatos:")
    print(final_candidates)
