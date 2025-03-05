import numpy as np
import pandas as pd

class DataReader:
    def __init__(self, arquivo_txt=None):
        """
        Inicializa a classe para carregar os dados do arquivo .txt.
        :param arquivo_txt: Caminho do arquivo contendo as medidas. (Opcional)
        """
        self.arquivo_txt = arquivo_txt
        self.df = None  # DataFrame Pandas para armazenar os dados

    def carregar_dados(self, arquivo_txt=None):
        """
        Lê o arquivo e armazena os dados no DataFrame Pandas.
        :param arquivo_txt: Caminho opcional do arquivo .txt
        :return: DataFrame Pandas com as medidas e desvios padrão.
        """
        if arquivo_txt:
            self.arquivo_txt = arquivo_txt

        if not self.arquivo_txt:
            print("Nenhum arquivo especificado.")
            return None

        try:
            # Carrega os dados do arquivo
            dados = np.loadtxt(self.arquivo_txt)

            # Verifica se o número de colunas é par (medidas e desvios intercalados)
            num_colunas = dados.shape[1]
            if num_colunas % 2 != 0:
                raise ValueError("O número de colunas deve ser par (medidas e desvios intercalados).")

            # Determina o número de pares de medidas/desvios
            num_pares = num_colunas // 2  

            # Separando medidas (colunas pares) e desvios padrão (colunas ímpares)
            medidas = dados[:, ::2]   # Pegamos apenas as colunas pares (0,2,4,...)
            desvios = dados[:, 1::2]  # Pegamos apenas as colunas ímpares (1,3,5,...)

            # Criar um DataFrame
            colunas_medidas = [f"Medida_{i+1}" for i in range(num_pares)]
            colunas_desvios = [f"Desvio_{i+1}" for i in range(num_pares)]
            colunas = colunas_medidas + colunas_desvios
            dados_formatados = np.hstack((medidas, desvios))
            self.df = pd.DataFrame(dados_formatados, columns=colunas)

            print("Dados carregados com sucesso!")
            return self.df

        except Exception as e:
            print(f"Erro ao carregar arquivo: {e}")
            return None

    def salvar_csv(self, nome_arquivo="dados_coletados.csv"):
        """
        Salva os dados no formato CSV.
        :param nome_arquivo: Nome do arquivo CSV de saída.
        """
        if self.df is not None:
            self.df.to_csv(nome_arquivo, index=False)
            print(f"Dados salvos em {nome_arquivo}")
        else:
            print("Nenhum dado para salvar.")

# Teste Local do Módulo
if __name__ == "__main__":
    leitor = DataReader("ensaio_1_tectrol_descalibrado_06_02_25.txt")
    df = leitor.carregar_dados()

    if df is not None:
        print(df)
        leitor.salvar_csv()
