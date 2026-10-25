import heapq

# Busca em Custo Uniforme
# O custo usado aqui é o custo do caminho que já foi percorrido
def ucs(grafo, inicio, objetivo):
    fila_prioridade = [(0, inicio)]
    menores_custos = {inicio: 0}
    pai = {inicio: None}

    while fila_prioridade:
        custo_atual, atual = heapq.heappop(fila_prioridade)

        if atual == objetivo:
                    return grafo.obter_caminho_e_custo(pai, atual)
        
        # Se o custo do que entrou na fila de prioridade for maior que o menor custo encontrado ignora.
        if custo_atual > menores_custos[atual]:
            continue

        # Vai ver o custo do caminho para cada vizinho
        for vizinho, custo_aresta in grafo.adjacencia[atual].items():
            novo_custo = custo_atual + custo_aresta

            # Se o vizinho não foi visitado ou se o custo do caminho for menor que o menor custo encontrado, atualiza o menor custo e adiciona na fila de prioridade
            if vizinho not in menores_custos or novo_custo < menores_custos[vizinho]:
                menores_custos[vizinho] = novo_custo
                pai[vizinho] = atual
                heapq.heappush(fila_prioridade, (novo_custo, vizinho))

    return None