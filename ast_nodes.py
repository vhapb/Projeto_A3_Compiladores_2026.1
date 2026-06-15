# ast_nodes.py
# "Tijolos" da Arvore Sintatica Abstrata (AST).
# O parser cria esses nos; a analise semantica e o gerador os percorrem.
# Cada no guarda 'linha' para permitir mensagens de erro precisas.

# ----- Estrutura do programa -----

class Programa:
    def __init__(self, comandos):
        self.comandos = comandos          # lista de comandos

class Declaracao:
    def __init__(self, tipo, nomes, linha):
        self.tipo = tipo                  # 'integer' | 'realis' | 'textus' | 'logicus'
        self.nomes = nomes                # lista de nomes declarados
        self.linha = linha

class Atribuicao:
    def __init__(self, nome, expr, linha):
        self.nome = nome
        self.expr = expr
        self.linha = linha

class Leitura:
    def __init__(self, nome, linha):
        self.nome = nome
        self.linha = linha

class Escrita:
    def __init__(self, expr, linha):
        self.expr = expr
        self.linha = linha

class Condicional:
    def __init__(self, cond, entao, senao, linha):
        self.cond = cond
        self.entao = entao                # lista de comandos
        self.senao = senao                # lista de comandos ou None
        self.linha = linha

class Enquanto:
    def __init__(self, cond, corpo, linha):
        self.cond = cond
        self.corpo = corpo
        self.linha = linha

class FacaEnquanto:
    def __init__(self, corpo, cond, linha):
        self.corpo = corpo
        self.cond = cond
        self.linha = linha

class Para:
    def __init__(self, init, cond, incr, corpo, linha):
        self.init = init                  # Atribuicao
        self.cond = cond
        self.incr = incr                  # Atribuicao
        self.corpo = corpo
        self.linha = linha

# ----- Expressoes -----

class OpBin:                              # operacao binaria: a + b, a == b, a et b...
    def __init__(self, op, esq, dir, linha):
        self.op = op                      # '+', '-', '*', '/', '==', 'et', 'vel'...
        self.esq = esq
        self.dir = dir
        self.linha = linha

class OpUn:                              # operacao unaria: -a, non a
    def __init__(self, op, operando, linha):
        self.op = op                      # '-' | 'non'
        self.operando = operando
        self.linha = linha

class LiteralNum:                        # inteiro: 42
    def __init__(self, valor, linha):
        self.valor = valor
        self.linha = linha

class LiteralReal:                       # decimal: 3.14
    def __init__(self, valor, linha):
        self.valor = valor
        self.linha = linha

class LiteralTexto:                      # string: "ola"
    def __init__(self, valor, linha):
        self.valor = valor
        self.linha = linha

class LiteralBool:                       # verum | falsum
    def __init__(self, valor, linha):
        self.valor = valor
        self.linha = linha

class Variavel:                          # uso de uma variavel: media
    def __init__(self, nome, linha):
        self.nome = nome
        self.linha = linha
