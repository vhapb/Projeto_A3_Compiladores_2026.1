# gerador.py
# Gerador de codigo: percorre a AST ja validada e escreve o codigo Python
# equivalente. Cada no vira uma ou mais linhas de Python, com a indentacao
# correta (Python usa indentacao no lugar das chaves { }).

from ast_nodes import (
    Programa, Declaracao, Atribuicao, Leitura, Escrita,
    Condicional, Enquanto, FacaEnquanto, Para,
    OpBin, OpUn, LiteralNum, LiteralReal, LiteralTexto, LiteralBool, Variavel,
)

# valor inicial de cada tipo (garante que a variavel exista no Python)
VALOR_INICIAL = {"integer": "0", "realis": "0.0", "textus": '""', "logicus": "False"}


class Gerador:
    def __init__(self):
        self.tipos = {}        # nome -> tipo, para saber como ler com input()
        self.linhas = []

    def gerar(self, programa):
        self.linhas = ["# Codigo Python gerado pelo transpilador Latina", ""]
        for cmd in programa.comandos:
            self._comando(cmd, 0)
        return "\n".join(self.linhas) + "\n"

    def _emitir(self, nivel, texto):
        self.linhas.append("    " * nivel + texto)   # 4 espacos por nivel

    # ------- comandos -------

    def _comando(self, no, nivel):
        if isinstance(no, Declaracao):
            inicial = VALOR_INICIAL[no.tipo]
            for nome in no.nomes:
                self.tipos[nome] = no.tipo
                self._emitir(nivel, f"{nome} = {inicial}")

        elif isinstance(no, Atribuicao):
            self._emitir(nivel, f"{no.nome} = {self._expr(no.expr)}")

        elif isinstance(no, Leitura):
            tipo = self.tipos.get(no.nome, "textus")
            if tipo == "integer":
                self._emitir(nivel, f"{no.nome} = int(input())")
            elif tipo == "realis":
                self._emitir(nivel, f"{no.nome} = float(input())")
            elif tipo == "logicus":
                self._emitir(nivel, f'{no.nome} = (input() == "verum")')
            else:  # textus
                self._emitir(nivel, f"{no.nome} = input()")

        elif isinstance(no, Escrita):
            self._emitir(nivel, f"print({self._expr(no.expr)})")

        elif isinstance(no, Condicional):
            self._emitir(nivel, f"if {self._expr(no.cond)}:")
            self._corpo(no.entao, nivel + 1)
            if no.senao is not None:
                self._emitir(nivel, "else:")
                self._corpo(no.senao, nivel + 1)

        elif isinstance(no, Enquanto):
            self._emitir(nivel, f"while {self._expr(no.cond)}:")
            self._corpo(no.corpo, nivel + 1)

        elif isinstance(no, FacaEnquanto):
            # Python nao tem do-while: usamos while True + break no fim
            self._emitir(nivel, "while True:")
            self._corpo(no.corpo, nivel + 1)
            self._emitir(nivel + 1, f"if not ({self._expr(no.cond)}):")
            self._emitir(nivel + 2, "break")

        elif isinstance(no, Para):
            # pro(init; cond; incr){corpo}  ->  init; while cond: corpo; incr
            self._comando(no.init, nivel)
            self._emitir(nivel, f"while {self._expr(no.cond)}:")
            self._corpo(no.corpo, nivel + 1)
            self._comando(no.incr, nivel + 1)

        else:
            raise Exception(f"No de comando desconhecido: {type(no).__name__}")

    def _corpo(self, comandos, nivel):
        # um bloco nunca e vazio na nossa gramatica, entao nao precisa de 'pass'
        for c in comandos:
            self._comando(c, nivel)

    # ------- expressoes (viram Python infixo, com parenteses por seguranca) -------

    def _expr(self, no):
        if isinstance(no, LiteralNum):   return no.valor
        if isinstance(no, LiteralReal):  return no.valor
        if isinstance(no, LiteralTexto): return repr(no.valor)          # vira "texto" valido
        if isinstance(no, LiteralBool):  return "True" if no.valor == "verum" else "False"
        if isinstance(no, Variavel):     return no.nome
        if isinstance(no, OpUn):
            if no.op == "non":
                return f"(not {self._expr(no.operando)})"
            return f"(-{self._expr(no.operando)})"
        if isinstance(no, OpBin):
            op = {"et": "and", "vel": "or"}.get(no.op, no.op)
            return f"({self._expr(no.esq)} {op} {self._expr(no.dir)})"
        raise Exception("Expressao desconhecida na geracao de codigo")
