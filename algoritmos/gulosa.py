import heapq

# Busca Gulosa 
# Usa a menor heurística para decidir o próximo no, aqui a heurística é a distância euclidiana do nó atual até o objetivo
def gulosa(grafo, inicio, objetivo):
    heuristica = grafo.calcular_distancia(inicio, objetivo)
    fila_prioridade = [(heuristica, inicio)]
    pai = {inicio: None}

    while fila_prioridade:
        _, atual = heapq.heappop(fila_prioridade) # esse _ é a heuristica do no atual, a gente da pop nela aqui porque tem que tirar tudo enfileirado mas nao usamos mais

        if atual == objetivo:
            return grafo.obter_caminho_e_custo(pai, atual)

        for vizinho in grafo.adjacencia[atual]:
            if vizinho not in pai:
                pai[vizinho] = atual

                # Vai calcular a heurística do vizinho e adicionar na fila de prioridade, com a prioridade sendo os que tem menor heurística
                heuristica = grafo.calcular_distancia(vizinho, objetivo)
                heapq.heappush(fila_prioridade, (heuristica, vizinho))
        
    return None