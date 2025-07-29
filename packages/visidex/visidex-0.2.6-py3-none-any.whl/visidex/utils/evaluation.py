import numpy as np
from prettytable import PrettyTable

def evaluate_matches(matches_matrix, threshold=0.5):
    """
    Avalia correspondências entre imagens de inspeção e uma base de referência.

    Parâmetros:
    - matches_matrix (np.ndarray): matriz (n, m) de similaridade.
      Primeiras m linhas: imagens conhecidas (espera-se identificação correta).
      Últimas m linhas: imagens desconhecidas (espera-se não-identificação).
    - threshold (float): limiar mínimo para considerar uma correspondência válida.

    Retorna:
    - TP (int): Verdadeiros Positivos – identificados corretamente.
    - FP (int): Falsos Positivos – identificados incorretamente como existentes.
    - FN (int): Falsos Negativos – não identificados ou mal identificados.
    - TN (int): Verdadeiros Negativos – corretamente não identificados.
    """
    n, m = matches_matrix.shape
    TP, FP, FN, TN = 0, 0, 0, 0

    # Casos positivos: imagens que devem ser reconhecidas
    for i in range(m):
        max_sim = np.max(matches_matrix[i])
        pred_index = np.argmax(matches_matrix[i])
        if max_sim >= threshold and pred_index == i:
            TP += 1
        else:
            FN += 1

    # Casos negativos: imagens que não estão na base
    for i in range(m, n):
        max_sim = np.max(matches_matrix[i])
        pred_index = np.argmax(matches_matrix[i])
        if max_sim >= threshold and pred_index < m:
            FP += 1
        else:
            TN += 1

    return TP, FP, FN, TN


def generate_metrics_output(TP, FP, FN, TN):
    """
    Gera uma string formatada com os valores de TP, FP, FN, TN, Precisão (P), Recall (R), F1-score (F1) e Acurácia (Acc).

    Args:
    TP (int): Verdadeiros Positivos.
    FP (int): Falsos Positivos.
    FN (int): Falsos Negativos.
    TN (int): Verdadeiros Negativos.

    Returns:
    str: String formatada contendo as métricas.
    """
    # Calcular métricas
    P = TP / (TP + FP) if TP + FP > 0 else 0      # Precisão
    R = TP / (TP + FN) if TP + FN > 0 else 0      # Recall
    F1 = 2 * (P * R) / (P + R) if P + R > 0 else 0 # F1-score
    Acc = (TP + TN) / (TP + FP + FN + TN) if TP + FP + FN + TN > 0 else 0  # Acurácia

    return "[TP:{},FN:{},TN:{},FP:{}]\n[P:{:.2f},R:{:.2f},F1:{:.2f},Acc:{:.2f}]".format(
        TP, FN, TN, FP, P, R, F1, Acc
    )


def print_results_table(all_results):
    """
    Imprime uma tabela com os resultados de avaliação usando PrettyTable.

    Args:
    - all_results (list of dict): Lista de dicionários contendo parâmetros e métricas.
    """
    table = PrettyTable()
    table.field_names = ["Num Features", "Feature Local Class", "Distance", "Threshold", "Matches", "Scores"]

    for result in all_results:
        params = result['params']
        matches = result['matches']
        scores = result.get('scores')  # Retorna None se 'scores' não estiver presente

        matches_str = generate_metrics_output(
            TP=matches["TP"], FP=matches["FP"], FN=matches["FN"], TN=matches["TN"]
        )

        if scores:
            scores_str = generate_metrics_output(
                TP=scores["TP"], FP=scores["FP"], FN=scores["FN"], TN=scores["TN"]
            )
        else:
            scores_str = "N/A"

        table.add_row([
            params['num_features'],
            params['feature_local_class'],
            params['distance'],
            params['threshold'],
            matches_str,
            scores_str
        ])

    print(table)

