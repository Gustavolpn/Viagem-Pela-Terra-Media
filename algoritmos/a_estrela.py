import heapq

# A*
# Basicamente combina a UCS e a gulosa :), ele pega o no que tem o menor heurística, que aqui é o custo do caminho já percorrido + distância euclidiana
def a_estrela(grafo, inicio, objetivo):
    euclidiana = grafo.calcular_distancia(inicio, objetivo)
    fila_prioridade = [(euclidiana, 0, inicio)]
    menores_custos = {inicio: 0}
    pai = {inicio: None}

    while fila_prioridade:
        _, custo_atual, atual = heapq.heappop(fila_prioridade)

        # Se o custo do que entrou na fila de prioridade for maior que o menor custo encontrado ignora.
        if custo_atual > menores_custos[atual]:
            continue

        if atual == objetivo:
            return grafo.obter_caminho_e_custo(pai, atual)

        for vizinho, custo_aresta in grafo.adjacencia[atual].items():
            novo_custo = custo_atual + custo_aresta

            # Se o vizinho não foi visitado ou se o custo do caminho for menor que o menor custo encontrado
            # Ele faz a mesma coisa que a UCS, mas o que define a prioridade é a heuristica
            if vizinho not in menores_custos or novo_custo < menores_custos[vizinho]:
                menores_custos[vizinho] = novo_custo
                pai[vizinho] = atual
                heuristica = novo_custo + grafo.calcular_distancia(vizinho, objetivo)
                heapq.heappush(fila_prioridade, (heuristica, novo_custo, vizinho))

    return None