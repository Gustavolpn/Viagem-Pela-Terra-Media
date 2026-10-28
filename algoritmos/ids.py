from algoritmos.dls import dls

# Busca de Aprofundamento Iterativo
# Honestamente nem tem muito o que ver aqui, é testar a DLS com vários limites sucessivamente
def ids(grafo, inicio, objetivo, limite_maximo):
    for limite in range(limite_maximo + 1): 
        destino = dls(grafo, inicio, objetivo, limite)

        if destino == "Corte por limite":
            continue
        else:
            return destino

    return "Corte por limite"