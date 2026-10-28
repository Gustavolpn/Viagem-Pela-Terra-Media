# Busca em Profundidade Limitada
# Tem umas diferenças em relação ao DFS, como ele tem limite de profundidade, a gente tem que ver qual a menor profundidade com que a gente consegue chegar em um no
# Por exemplo, se nosso limite é 4, a gente chega no no X com profundidade 3 e depois 2, a gente marca a menor profundidade como 2, e consegue se aprofundar mais 2 vezes
# Se bater no limite e não achar porque bateu no limite, retorna "Corte por limite"
def dls(grafo, inicio, objetivo, limite):
    pilha = [(inicio, 0)]
    pai = {inicio: None}
    menor_profundidade = {inicio: 0}
    nos_alem_do_limite = set() # Para verificar se existem nos que não foram explorados porque deu o limite

    while pilha:
        atual, profundidade = pilha.pop()

        # Por exemplo, se a gente chegou no no X com 2 de profundidade e depois com 3, so ignora o 3 porque ja chegamos com menos profundidade
        if profundidade > menor_profundidade[atual]:
            continue

        if atual == objetivo:
            return grafo.obter_caminho_e_custo(pai, atual)
            
        if profundidade < limite: 
                for vizinho in grafo.adjacencia[atual]:
                    # So adiciona na fila se ainda não foi visitado ou se chegou com menos profundidade que a ultima vez que chegou nele      
                    if vizinho not in menor_profundidade or profundidade + 1 < menor_profundidade[vizinho]:
                        menor_profundidade[vizinho] = profundidade + 1
                        pai[vizinho] = atual
                        pilha.append((vizinho, profundidade + 1))

                        # As vezes foi marcado como alem do limite porque chegamos nele por um caminho maior, aqui eu checo isso
                        if vizinho in nos_alem_do_limite:
                            nos_alem_do_limite.remove(vizinho)      
        
        if profundidade == limite:
            for vizinho in grafo.adjacencia[atual]:
                if vizinho not in menor_profundidade:
                    nos_alem_do_limite.add(vizinho)

    if nos_alem_do_limite:
        return "Corte por limite"
    else:                   
        return None