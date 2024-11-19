import numpy as np

# Distâncias reais entre os dispositivos (em metros)
dist_real = np.array([[0, 7.914, 7.914],
                      [7.914, 0, 7.914],
                      [7.914, 7.914, 0]])

# Função para simular medição de TWR e calcular o EDM
def calcular_edm_medido(delays, num_medicoes=200):
    edm_medido = np.zeros((3, 3))
    for i in range(3):
        for j in range(i + 1, 3):
            # Medição simulada de tempo de voo com base no atraso
            tof_medido = (2 * delays[i] + 2 * delays[j]) / 4
            edm_medido[i, j] = tof_medido
            edm_medido[j, i] = tof_medido
    return edm_medido

# Função de calibração para encontrar os melhores atrasos
def calibrar_atrasos(dist_real, iteracoes=1000):
    melhor_erro = float('inf')
    melhores_delays = None
    delays_iniciais = np.random.uniform(500e-9, 520e-9, 3)  # Inicialização em ns
    for _ in range(iteracoes):
        edm_medido = calcular_edm_medido(delays_iniciais)
        erro = np.linalg.norm(dist_real - edm_medido)
        if erro < melhor_erro:
            melhor_erro = erro
            melhores_delays = delays_iniciais
        # Perturbação dos atrasos para nova tentativa
        delays_iniciais += np.random.normal(0, 1e-9, 3)
    return melhores_delays

# Execução da calibração
delays_calibrados = calibrar_atrasos(dist_real)
print("Delays de antena calibrados:", delays_calibrados)
