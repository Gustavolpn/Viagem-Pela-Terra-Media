import json
import math # Carrega math.hypot() para calcular a distância euclidiana a partir das diferenças de coordenadas

class Grafo:
    def __init__(self, arquivo):

        # Carrega os nós, arestas e as outras infos do JSON
        # Tive que colocar o utf-8 pra ele ler acento
        with open(arquivo, "r", encoding="utf-8") as f:
            self.dados = json.load(f)

        self.nos = self.dados["nos"]
        self.arestas = self.dados["arestas"]
        self.adjacencia = {     # Cada nó vai ter um dicionário de vizinhos e seus custos (as distâncias no caso)
            no : {} 
            for no in self.nos
        }

        for aresta in self.arestas:
            origem = aresta["origem"]
            destino = aresta["destino"]
            distancia = self.calcular_distancia(origem, destino) 

            # Adiciona a conexão nos dois sentidos.
            self.adjacencia[origem][destino] = distancia
            self.adjacencia[destino][origem] = distancia
        
    # Vai retornar a distância entre dois nós em quilômetros, de acordo com as infos do JSON que eu tirei aproximando daquela escala do mapa
    def calcular_distancia(self, origem, destino):
        a = self.nos[origem]
        b = self.nos[destino]
        
        distancia = math.hypot(a["x"] - b["x"], a["y"] - b["y"])
        return self.pixels_para_km(distancia)

        
    def pixels_para_km(self, distancia_em_pixels):
        return distancia_em_pixels * self.dados['km_por_pixel']

    
    def obter_caminho(self, pai, no):
        caminho = []

        while no is not None:
            caminho.append(no)
            no = pai[no]

        caminho.reverse()
        return caminho

    
    def obter_custo_total(self, caminho):
        custo_total = 0

        for i in range(len(caminho) - 1):
            origem = caminho[i]
            destino = caminho[i + 1]
            custo_total += self.adjacencia[origem][destino]

        return custo_total

    # Deixei em função porque tava fazendo a mesma coisa pra todos os algoritmos de busca
    # Resumindo a gente refaz o caminho até o início usando os pais, depois pega o custo total, no caso a distância total percorrida
    def obter_caminho_e_custo(self, pai, no):
        caminho = self.obter_caminho(pai, no)
        custo_total = self.obter_custo_total(caminho)
        
        return caminho, custo_total