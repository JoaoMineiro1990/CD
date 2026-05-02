import math


NOMES_CIDADES = [
    "Cidade 1",
    "Cidade 2",
    "Cidade 3",
    "Cidade 4",
    "Cidade 5",
    "Cidade 6",
    "Cidade 7",
    "Cidade 8",
    "Cidade 9",
    "Cidade 10",
    "Cidade 11",
    "Cidade 12",
    "Cidade 13",
    "Cidade 14",
    "Cidade 15",
    "Cidade 16",
]


COORDENADAS = [
    (38.24, 20.42),
    (39.57, 26.15),
    (40.56, 25.32),
    (36.26, 23.12),
    (33.48, 10.54),
    (37.56, 12.19),
    (38.42, 13.11),
    (37.52, 20.44),
    (41.23, 9.10),
    (41.17, 13.05),
    (36.08, -5.21),
    (38.47, 15.13),
    (38.15, 15.35),
    (37.51, 15.17),
    (35.49, 14.32),
    (39.36, 19.56),
]


def calcular_distancia_euclidiana(cidade_a, cidade_b):
    x1, y1 = cidade_a
    x2, y2 = cidade_b

    return round(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))


def gerar_matriz_distancias(coordenadas=None):
    """
    Gera e retorna uma matriz quadrada de distâncias.

    Se nenhuma lista de coordenadas for passada, usa COORDENADAS.
    """

    if coordenadas is None:
        coordenadas = COORDENADAS

    quantidade_cidades = len(coordenadas)
    matriz = []

    for i in range(quantidade_cidades):
        linha = []

        for j in range(quantidade_cidades):
            if i == j:
                linha.append(0)
            else:
                linha.append(
                    calcular_distancia_euclidiana(coordenadas[i], coordenadas[j])
                )

        matriz.append(linha)

    return matriz


DISTANCIAS = gerar_matriz_distancias()


def obter_matriz_distancias():
    """
    Retorna uma cópia da matriz de distâncias da instância padrão.
    """

    return [linha[:] for linha in DISTANCIAS]


def obter_nomes_cidades():
    return NOMES_CIDADES[:]


def obter_coordenadas():
    return COORDENADAS[:]


def nomear_rota(rota):
    return [NOMES_CIDADES[indice] for indice in rota]


def formatar_rota(rota):
    return " -> ".join(nomear_rota(rota))
