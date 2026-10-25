from collections import deque

# Busca em Largura
def bfs(grafo, inicio, objetivo):
    fila = deque([inicio]) 
    visitados = set([inicio]) # ja deixei o primeiro no como visitado
    pai = {inicio: None}

    while fila:
        atual = fila.popleft()

        # Se achar o objetivo, reconstruimos o caminho até o início usando o dicionário de pais
        if atual == objetivo:
            return grafo.obter_caminho_e_custo(pai, objetivo)

        for vizinho in grafo.adjacencia[atual]: 
            # Se o vizinho não foi visitado, visita ele, bota o no atual como pai e bota na fila
            if vizinho not in visitados:
                visitados.add(vizinho)
                pai[vizinho] = atual
                fila.append(vizinho)
    

    return None

# OBS: A implementação do BFS e DFS são quase iguais, só que aqui é fila