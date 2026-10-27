from pathlib import Path
import ast
import sys
from collections import deque
from time import perf_counter
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from algoritmos.a_estrela import a_estrela
from algoritmos.bfs import bfs
from algoritmos.dfs import dfs
from algoritmos.dls import dls
from algoritmos.gulosa import gulosa
from algoritmos.ids import ids
from algoritmos.ucs import ucs


class Interface:
    ALGORITMOS = {
        "Custo uniforme (UCS)": ucs,
        "A estrela (A*)": a_estrela,
        "Largura (BFS)": bfs,
        "Profundidade (DFS)": dfs,
        "Profundidade limitada (DLS)": dls,
        "Aprofundamento iterativo (IDS)": ids,
        "Gulosa": gulosa,
    }

    def __init__(self, janela, grafo, pasta):
        self.janela = janela
        self.grafo = grafo
        self.caminho = []
        self.zoom = 1.0
        self.calculo_agendado = None
        self.imagem_tk = None
        self.imagem = None
        self.posicoes_nos = {}
        self.inicio_clique = None
        self.arrastando = False
        self.animacao_agendada = None
        self.passos_busca = []
        self.indice_passo = 0
        self.nos_explorados = set()
        self.arestas_exploradas = set()
        self.no_atual = None
        self.rota_movimento = []
        self.trecho_movimento = 0
        self.fracao_movimento = 0.0
        self.ultimo_quadro = 0.0
        self.pontos_mapa = {}
        self.resultado_busca = None
        self.mensagem_final = ""
        arquivo_mapa = Path(pasta) / grafo.dados.get("imagem", "mapa.png")
        if arquivo_mapa.is_file():
            with Image.open(arquivo_mapa) as imagem:
                self.imagem = imagem.convert("RGB")

        self.rotulos = {
            no["nome"]: chave
            for chave, no in grafo.nos.items()
            if no.get("nome", "Via").strip().casefold() != "via"
        }
        self.nomes = {chave: rotulo for rotulo, chave in self.rotulos.items()}
        opcoes = sorted(self.rotulos)
        self.origem = tk.StringVar(value=self.nomes.get("hobbiton", opcoes[0]))
        self.destino = tk.StringVar(value=self.nomes.get("orodruin", opcoes[-1]))
        self.algoritmo = tk.StringVar(value=next(iter(self.ALGORITMOS)))
        self.limite = tk.StringVar(value=str(max(0, len(grafo.nos) - 1)))
        self.custo = tk.StringVar(value="— km")
        self.status = tk.StringVar(value="Escolha a origem e o destino.")
        self.texto_zoom = tk.StringVar(value="100%")
        self.selecao_mapa = tk.StringVar(value="origem")
        self.intervalo = tk.DoubleVar(value=0.0)
        self.texto_intervalo = tk.StringVar(value="0,0 s")

        janela.title("Viagem Pela Terra-média")
        janela.protocol("WM_DELETE_WINDOW", self.fechar)
        janela.geometry("1200x820")
        janela.minsize(1000, 650)
        janela.columnconfigure(0, weight=1)
        janela.rowconfigure(0, weight=1)
        painel = ttk.Frame(janela, padding=16)
        painel.grid(sticky="nsew")
        painel.columnconfigure(0, weight=1)
        painel.rowconfigure(2, weight=1)

        ttk.Label(painel, text="Viagem pela Terra-média", font=("Segoe UI", 19, "bold")).grid(sticky="w")

        controles = ttk.Frame(painel)
        controles.grid(row=1, sticky="ew", pady=(12, 12))
        for coluna in range(3):
            controles.columnconfigure(coluna, weight=1)
        for coluna, (titulo, variavel) in enumerate((("Origem", self.origem), ("Destino", self.destino))):
            ttk.Label(controles, text=titulo).grid(row=0, column=coluna, sticky="w")
            ttk.Combobox(controles, textvariable=variavel, values=opcoes, state="readonly", width=32).grid(row=1, column=coluna, sticky="ew", padx=(0, 10))
        ttk.Label(controles, text="Algoritmo").grid(row=0, column=2, sticky="w")
        seletor = ttk.Combobox(controles, textvariable=self.algoritmo, values=list(self.ALGORITMOS), state="readonly", width=28)
        seletor.grid(row=1, column=2, sticky="ew", padx=(0, 10))
        seletor.bind("<<ComboboxSelected>>", self.atualizar_limite)
        ttk.Label(controles, text="Limite de arestas").grid(row=0, column=3, sticky="w")
        self.campo_limite = ttk.Spinbox(controles, from_=0, to=max(0, len(grafo.nos) - 1), textvariable=self.limite, width=8, state="disabled")
        self.campo_limite.grid(row=1, column=3, padx=(0, 10))

        conteudo = ttk.Frame(painel)
        conteudo.grid(row=2, sticky="nsew")
        conteudo.columnconfigure(0, weight=1)
        conteudo.rowconfigure(0, weight=1)

        quadro_mapa = ttk.Frame(conteudo)
        quadro_mapa.grid(row=0, column=0, sticky="nsew")
        quadro_mapa.columnconfigure(0, weight=1)
        quadro_mapa.rowconfigure(1, weight=1)
        ferramentas = ttk.Frame(quadro_mapa)
        ferramentas.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        ttk.Label(ferramentas, text="Mapa", font=("Segoe UI", 12, "bold")).pack(side="left")
        ttk.Button(ferramentas, text="−", width=3, command=lambda: self.alterar_zoom(1 / 1.25)).pack(side="left", padx=(16, 4))
        ttk.Label(ferramentas, textvariable=self.texto_zoom, width=6, anchor="center").pack(side="left")
        ttk.Button(ferramentas, text="+", width=3, command=lambda: self.alterar_zoom(1.25)).pack(side="left", padx=4)
        ttk.Button(ferramentas, text="Enquadrar mapa", command=self.enquadrar_mapa).pack(side="left", padx=8)
        ttk.Label(ferramentas, text="Selecionar:").pack(side="left", padx=(12, 4))
        ttk.Radiobutton(ferramentas, text="Origem", variable=self.selecao_mapa, value="origem").pack(side="left")
        ttk.Radiobutton(ferramentas, text="Destino", variable=self.selecao_mapa, value="destino").pack(side="left", padx=4)

        self.canvas = tk.Canvas(quadro_mapa, background="#e9e4d4", borderwidth=0, highlightthickness=0, height=400)
        self.canvas.grid(row=1, column=0, sticky="nsew")
        horizontal = ttk.Scrollbar(quadro_mapa, orient="horizontal", command=self.canvas.xview)
        horizontal.grid(row=2, column=0, sticky="ew")
        vertical = ttk.Scrollbar(quadro_mapa, orient="vertical", command=self.canvas.yview)
        vertical.grid(row=1, column=1, sticky="ns")
        self.canvas.configure(xscrollcommand=horizontal.set, yscrollcommand=vertical.set)
        self.canvas.bind("<Configure>", self.desenhar_mapa)
        self.canvas.bind("<MouseWheel>", self.zoom_roda)
        self.canvas.bind("<ButtonPress-1>", self.iniciar_arrasto)
        self.canvas.bind("<B1-Motion>", self.arrastar_mapa)
        self.canvas.bind("<ButtonRelease-1>", self.finalizar_clique)
        self.canvas.bind("<Motion>", self.atualizar_cursor)

        resultado = ttk.Frame(conteudo, padding=(20, 8, 0, 0), width=250)
        resultado.grid(row=0, column=1, sticky="ns")
        resultado.columnconfigure(0, weight=1)
        ttk.Label(resultado, text="Distância percorrida", font=("Segoe UI", 12, "bold")).grid(sticky="w")
        ttk.Label(resultado, textvariable=self.custo, font=("Segoe UI", 24, "bold")).grid(sticky="w", pady=(8, 16))
        ttk.Label(resultado, textvariable=self.status, wraplength=240).grid(sticky="w")
        ttk.Separator(resultado).grid(sticky="ew", pady=20)
        ttk.Label(resultado, text="Verde: origem\nVermelho: destino", justify="left").grid(sticky="w")
        ttk.Separator(resultado).grid(sticky="ew", pady=20)
        ttk.Label(resultado, text="Intervalo da animação entre nós").grid(sticky="w")
        ttk.Scale(resultado, from_=0, to=3, variable=self.intervalo,
                  command=self.atualizar_intervalo).grid(sticky="ew", pady=(8, 0))
        ttk.Label(resultado, textvariable=self.texto_intervalo).grid(sticky="w")
        ttk.Button(resultado, text="Repetir busca", command=self.calcular).grid(sticky="ew", pady=(12, 0))

        for variavel in (self.origem, self.destino, self.algoritmo, self.limite):
            variavel.trace_add("write", self.agendar_calculo)
        self.agendar_calculo()

    def atualizar_limite(self, evento=None):
        usa_limite = self.ALGORITMOS[self.algoritmo.get()] in (dls, ids)
        self.campo_limite.configure(state="normal" if usa_limite else "disabled")

    def agendar_calculo(self, *args):
        self.cancelar_animacao()
        self.atualizar_limite()
        if self.calculo_agendado is not None:
            self.janela.after_cancel(self.calculo_agendado)
        self.calculo_agendado = self.janela.after(150, self.calcular)

    def limpar_resultado(self, mensagem):
        self.cancelar_animacao()
        self.nos_explorados.clear()
        self.arestas_exploradas.clear()
        self.no_atual = None
        self.caminho = []
        self.custo.set("— km")
        self.status.set(mensagem)
        self.desenhar_mapa()

    def calcular(self):
        self.cancelar_animacao()
        if self.calculo_agendado is not None:
            self.janela.after_cancel(self.calculo_agendado)
            self.calculo_agendado = None
        if self.origem.get() not in self.rotulos or self.destino.get() not in self.rotulos:
            self.limpar_resultado("Escolha uma origem e um destino.")
            return
        busca = self.ALGORITMOS[self.algoritmo.get()]
        argumentos = []
        if busca in (dls, ids):
            try:
                limite = int(self.limite.get())
                if limite < 0:
                    raise ValueError
            except ValueError:
                self.limpar_resultado("Informe um limite inteiro maior ou igual a zero.")
                return
            argumentos.append(limite)
        origem = self.rotulos[self.origem.get()]
        destino = self.rotulos[self.destino.get()]
        self.passos_busca = []
        resultado = self.executar_busca(busca, origem, destino, argumentos)
        self.resultado_busca = resultado
        self.indice_passo = 0
        self.nos_explorados.clear()
        self.arestas_exploradas.clear()
        self.no_atual = None
        self.caminho = []
        self.custo.set("— km")
        self.mensagem_final = "Nenhum caminho encontrado" + (" dentro do limite informado." if argumentos else ".")
        self.desenhar_mapa()
        self.avancar_animacao()

    def executar_busca(self, busca, origem, destino, argumentos):
        linhas_visita = {}
        for algoritmo in self.ALGORITMOS.values():
            codigo = algoritmo.__code__
            fonte = Path(codigo.co_filename).read_text(encoding="utf-8-sig")
            arvore = ast.parse(fonte)
            for instrucao in ast.walk(arvore):
                if (isinstance(instrucao, ast.If)
                        and isinstance(instrucao.test, ast.Compare)
                        and ast.dump(instrucao.test) == ast.dump(ast.parse("atual == objetivo", mode="eval").body)):
                    linhas_visita[codigo] = instrucao.lineno
                    break

        def acompanhar(quadro, evento, argumento):
            if quadro.f_code not in linhas_visita:
                return None
            if evento == "line" and quadro.f_lineno == linhas_visita[quadro.f_code]:
                atual = quadro.f_locals["atual"]
                pai = quadro.f_locals["pai"].get(atual)
                self.passos_busca.append((atual, pai))
            return acompanhar

        observador_anterior = sys.gettrace()
        try:
            sys.settrace(acompanhar)
            return busca(self.grafo, origem, destino, *argumentos)
        finally:
            sys.settrace(observador_anterior)

    def cancelar_animacao(self):
        if self.animacao_agendada is not None:
            self.janela.after_cancel(self.animacao_agendada)
            self.animacao_agendada = None
        self.rota_movimento = []

    def fechar(self):
        self.cancelar_animacao()
        if self.calculo_agendado is not None:
            self.janela.after_cancel(self.calculo_agendado)
        self.janela.destroy()

    def atualizar_intervalo(self, valor=None):
        segundos = min(3.0, max(0.0, round(self.intervalo.get(), 1)))
        self.intervalo.set(segundos)
        self.texto_intervalo.set(f"{segundos:.1f} s".replace(".", ","))
        if self.animacao_agendada is not None:
            self.janela.after_cancel(self.animacao_agendada)
            proximo = self.animar_movimento if self.rota_movimento else self.avancar_animacao
            self.ultimo_quadro = perf_counter()
            self.animacao_agendada = self.janela.after(0, proximo)

    def avancar_animacao(self):
        self.animacao_agendada = None
        if self.intervalo.get() == 0:
            self.indice_passo = len(self.passos_busca)
            self.concluir_animacao()
            return
        if self.indice_passo >= len(self.passos_busca):
            self.concluir_animacao()
            return
        no, pai = self.passos_busca[self.indice_passo]
        if pai is None:
            self.nos_explorados.clear()
            self.arestas_exploradas.clear()
            self.no_atual = None
        nome = self.nomes.get(no, "Via")
        self.status.set(f"{self.algoritmo.get()}\nExplorando: {nome}\nPasso {self.indice_passo + 1} de {len(self.passos_busca)}")
        if self.no_atual is not None and self.no_atual != no:
            self.rota_movimento = self.caminho_ate_proximo(no, pai)
            self.trecho_movimento = 0
            self.fracao_movimento = 0.0
            self.ultimo_quadro = perf_counter()
            self.animar_movimento()
        else:
            self.chegar_ao_no()

    def caminho_ate_proximo(self, no, pai):
        vizinhos = {}
        for a, b in sorted(self.arestas_exploradas | ({(pai, no)} if pai is not None else set())):
            vizinhos.setdefault(a, []).append(b)
            vizinhos.setdefault(b, []).append(a)
        fila = deque([self.no_atual])
        anteriores = {self.no_atual: None}
        while fila:
            atual = fila.popleft()
            if atual == no:
                rota = []
                while atual is not None:
                    rota.append(atual)
                    atual = anteriores[atual]
                return list(reversed(rota))
            for vizinho in vizinhos.get(atual, []):
                if vizinho not in anteriores:
                    anteriores[vizinho] = atual
                    fila.append(vizinho)
        return [pai, no] if pai is not None else [no]

    def animar_movimento(self):
        self.animacao_agendada = None
        if self.intervalo.get() == 0:
            self.rota_movimento = []
            self.concluir_animacao()
            return
        agora = perf_counter()
        self.fracao_movimento += (agora - self.ultimo_quadro) / self.intervalo.get()
        self.ultimo_quadro = agora
        while self.fracao_movimento >= 1:
            self.fracao_movimento -= 1
            self.trecho_movimento += 1
        if self.trecho_movimento >= len(self.rota_movimento) - 1:
            self.rota_movimento = []
            self.chegar_ao_no()
            return
        self.desenhar_movimento()
        self.animacao_agendada = self.janela.after(16, self.animar_movimento)

    def chegar_ao_no(self):
        no, pai = self.passos_busca[self.indice_passo]
        self.nos_explorados.add(no)
        if pai is not None:
            self.arestas_exploradas.add((pai, no))
        self.no_atual = no
        self.indice_passo += 1
        self.desenhar_exploracao()
        self.animacao_agendada = self.janela.after(16, self.avancar_animacao)

    def concluir_animacao(self):
        self.rota_movimento = []
        self.no_atual = None
        self.nos_explorados.clear()
        self.arestas_exploradas.clear()
        resultado = self.resultado_busca
        if resultado is None:
            self.custo.set("— km")
            self.status.set(self.mensagem_final)
        else:
            self.caminho, custo = resultado
            distancia = f"{custo:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
            self.custo.set(f"{distancia} km")
            self.status.set(f"{self.algoritmo.get()}\n{len(self.caminho) - 1} trechos percorridos")
        self.desenhar_mapa()

    def zoom_roda(self, evento):
        if evento.delta:
            self.alterar_zoom(1.25 if evento.delta > 0 else 1 / 1.25)
        return "break"

    def alterar_zoom(self, fator):
        novo_zoom = min(4.0, max(1.0, self.zoom * fator))
        if novo_zoom == self.zoom:
            return
        regiao = self.canvas.cget("scrollregion")
        limites = list(map(float, self.canvas.tk.splitlist(regiao))) if regiao else []
        largura = max(self.canvas.winfo_width(), 1)
        altura = max(self.canvas.winfo_height(), 1)
        cx = self.canvas.canvasx(largura / 2) / limites[2] if limites else 0.5
        cy = self.canvas.canvasy(altura / 2) / limites[3] if limites else 0.5
        self.zoom = novo_zoom
        self.texto_zoom.set(f"{self.zoom:.0%}")
        self.desenhar_mapa()
        limites = list(map(float, self.canvas.tk.splitlist(self.canvas.cget("scrollregion"))))
        self.canvas.xview_moveto(cx - largura / (2 * limites[2]))
        self.canvas.yview_moveto(cy - altura / (2 * limites[3]))

    def enquadrar_mapa(self):
        self.zoom = 1.0
        self.texto_zoom.set("100%")
        self.desenhar_mapa()
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

    def iniciar_arrasto(self, evento):
        self.inicio_clique = (evento.x, evento.y)
        self.arrastando = False
        self.canvas.scan_mark(evento.x, evento.y)

    def arrastar_mapa(self, evento):
        if self.inicio_clique is None:
            return
        x, y = self.inicio_clique
        if (evento.x - x) ** 2 + (evento.y - y) ** 2 > 25:
            self.arrastando = True
        if self.arrastando:
            self.canvas.configure(cursor="fleur")
            self.canvas.scan_dragto(evento.x, evento.y, gain=1)

    def no_sob_cursor(self, evento):
        x, y = self.canvas.canvasx(evento.x), self.canvas.canvasy(evento.y)
        if not self.posicoes_nos:
            return None
        no = min(self.posicoes_nos, key=lambda chave: (self.posicoes_nos[chave][0] - x) ** 2 + (self.posicoes_nos[chave][1] - y) ** 2)
        nx, ny = self.posicoes_nos[no]
        return no if (nx - x) ** 2 + (ny - y) ** 2 <= 100 else None

    def atualizar_cursor(self, evento):
        self.canvas.configure(cursor="hand2" if self.no_sob_cursor(evento) is not None else "")

    def finalizar_clique(self, evento):
        if self.inicio_clique is not None and not self.arrastando:
            x, y = self.inicio_clique
            if (evento.x - x) ** 2 + (evento.y - y) ** 2 <= 25:
                no = self.no_sob_cursor(evento)
                if no is not None:
                    escolhendo_origem = self.selecao_mapa.get() == "origem"
                    variavel = self.origem if escolhendo_origem else self.destino
                    variavel.set(self.nomes[no])
                    self.selecao_mapa.set("destino" if escolhendo_origem else "origem")
                    self.calcular()
        self.inicio_clique = None
        self.arrastando = False
        self.atualizar_cursor(evento)

    def desenhar_mapa(self, evento=None):
        self.canvas.delete("all")
        largura = max(self.canvas.winfo_width(), 1)
        altura = max(self.canvas.winfo_height(), 1)
        largura_original = self.imagem.width if self.imagem else self.grafo.dados.get("largura", 1600)
        altura_original = self.imagem.height if self.imagem else self.grafo.dados.get("altura", 1131)
        escala = max(largura / largura_original, altura / altura_original) * self.zoom
        w, h = max(largura, round(largura_original * escala)), max(altura, round(altura_original * escala))
        largura_area, altura_area = max(largura, w), max(altura, h)
        dx, dy = (largura_area - w) / 2, (altura_area - h) / 2
        self.canvas.configure(scrollregion=(0, 0, largura_area, altura_area))
        if self.imagem:
            self.imagem_tk = ImageTk.PhotoImage(self.imagem.resize((w, h), Image.Resampling.LANCZOS))
            self.canvas.create_image(dx, dy, image=self.imagem_tk, anchor="nw")

        def ponto(no):
            dados = self.grafo.nos[no]
            return dx + dados["x"] * escala, dy + dados["y"] * escala

        self.pontos_mapa = {no: ponto(no) for no in self.grafo.nos}
        for aresta in self.grafo.arestas:
            self.canvas.create_line(*ponto(aresta["origem"]), *ponto(aresta["destino"]), fill="#716753", width=1)
        for i in range(len(self.caminho) - 1):
            self.canvas.create_line(*ponto(self.caminho[i]), *ponto(self.caminho[i+1]), fill="#ffb000", width=4)
        self.posicoes_nos = {no: ponto(no) for no in self.nomes}
        for x, y in self.posicoes_nos.values():
            self.canvas.create_oval(x-4, y-4, x+4, y+4, fill="#554b3b", outline="white", width=1.5, tags="marcador")
        for no, cor in ((self.rotulos.get(self.origem.get()), "#198754"), (self.rotulos.get(self.destino.get()), "#dc3545")):
            if no in self.posicoes_nos:
                x, y = self.posicoes_nos[no]
                self.canvas.create_oval(x-6, y-6, x+6, y+6, fill=cor, outline="white", width=2, tags="marcador")
        self.desenhar_exploracao()

    def desenhar_exploracao(self):
        self.canvas.delete("busca")
        for pai, no in self.arestas_exploradas:
            self.canvas.create_line(*self.pontos_mapa[pai], *self.pontos_mapa[no],
                                    fill="#287dcc", width=3, tags="busca")
        for no in self.nos_explorados:
            if no in self.posicoes_nos:
                x, y = self.posicoes_nos[no]
                self.canvas.create_oval(x-7, y-7, x+7, y+7,
                                        outline="#287dcc", width=2, tags="busca")
        self.canvas.tag_raise("marcador")
        if self.rota_movimento:
            self.desenhar_movimento()
        elif self.no_atual in self.pontos_mapa:
            x, y = self.pontos_mapa[self.no_atual]
            self.canvas.create_oval(x-10, y-10, x+10, y+10,
                                    outline="#0057b8", width=3, tags=("busca", "ponteiro"))

    def desenhar_movimento(self):
        self.canvas.delete("movimento")
        self.canvas.delete("ponteiro")
        a = self.rota_movimento[self.trecho_movimento]
        b = self.rota_movimento[self.trecho_movimento + 1]
        ax, ay = self.pontos_mapa[a]
        bx, by = self.pontos_mapa[b]
        t = self.fracao_movimento
        t = t * t * (3 - 2 * t)
        x, y = ax + (bx - ax) * t, ay + (by - ay) * t
        self.canvas.create_line(ax, ay, x, y, fill="#287dcc", width=3,
                                tags=("busca", "movimento"))
        self.canvas.create_oval(x-6, y-6, x+6, y+6, fill="#0057b8",
                                outline="white", width=2, tags=("busca", "movimento"))
