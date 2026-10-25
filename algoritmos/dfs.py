# Busca em Profundidade
def dfs(grafo, inicio, objetivo):
    pilha = [inicio]
    visitados = set([inicio]) # ja deixei o primeiro no como visitado
    pai = {inicio: None}

    while pilha:
        atual = pilha.pop()

        if atual == objetivo:
            return grafo.obter_caminho_e_custo(pai, objetivo)

        for vizinho in grafo.adjacencia[atual]:
            # Se o vizinho não foi visitado, visita ele, bota o no atual como pai e bota na pilha
            if vizinho not in visitados: 
                visitados.add(vizinho)
                pai[vizinho] = atual
                pilha.append(vizinho)

    return None

# OBS: A implementação do BFS e DFS são quase iguais, só que aqui é pilha