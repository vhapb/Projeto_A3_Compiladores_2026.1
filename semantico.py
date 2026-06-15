# semantico.py
# Analise semantica: percorre a AST verificando as regras que a sintaxe
# sozinha nao garante:
#   1) toda variavel usada foi declarada antes (e no escopo certo);
#   2) os tipos das operacoes e atribuicoes sao compativeis;
#   3) condicoes de si/dum/fac/pro sao logicas.
#
# Usa uma PILHA DE ESCOPOS: cada bloco { } empilha um dicionario
# nome -> tipo; ao sair do bloco, ele e desempilhado.

from ast_nodes import (
    Programa, Declaracao, Atribuicao, Leitura, Escrita,
    Condicional, Enquanto, FacaEnquanto, Para,
    OpBin, OpUn, LiteralNum, LiteralReal, LiteralTexto, LiteralBool, Variavel,
)

NUMERICOS = ("integer", "realis")


class ErroSemantico(Exception):
    pass


class AnalisadorSemantico:
    def __init__(self):
        self.escopos = [{}]          # pilha de escopos; comeca com o escopo global

    # ------- tabela de simbolos -------

    def _declarar(self, nome, tipo, linha):
        atual = self.escopos[-1]
        if nome in atual:
            raise ErroSemantico(
                f"Variavel '{nome}' ja foi declarada neste escopo (linha {linha})."
            )
        atual[nome] = tipo

    def _tipo_de(self, nome, linha):
        # procura do escopo mais interno para o mais externo
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return escopo[nome]
        raise ErroSemantico(
            f"Variavel '{nome}' usada sem ter sido declarada (linha {linha})."
        )

    # ------- percurso dos comandos -------

    def analisar(self, programa):
        for cmd in programa.comandos:
            self._comando(cmd)

    def _bloco(self, comandos):
        self.escopos.append({})      # entra em um novo escopo
        for cmd in comandos:
            self._comando(cmd)
        self.escopos.pop()           # sai do escopo (variaveis locais somem)

    def _comando(self, no):
        if isinstance(no, Declaracao):
            for nome in no.nomes:
                self._declarar(nome, no.tipo, no.linha)

        elif isinstance(no, Atribuicao):
            tipo_var = self._tipo_de(no.nome, no.linha)
            tipo_expr = self._tipo_expr(no.expr)
            if not self._compativel(tipo_var, tipo_expr):
                raise ErroSemantico(
                    f"Nao e possivel atribuir um valor '{tipo_expr}' a variavel "
                    f"'{no.nome}', que e '{tipo_var}' (linha {no.linha})."
                )

        elif isinstance(no, Leitura):
            self._tipo_de(no.nome, no.linha)        # so confere se foi declarada

        elif isinstance(no, Escrita):
            self._tipo_expr(no.expr)                # valida a expressao impressa

        elif isinstance(no, Condicional):
            self._exigir_logica(no.cond, no.linha)
            self._bloco(no.entao)
            if no.senao is not None:
                self._bloco(no.senao)

        elif isinstance(no, Enquanto):
            self._exigir_logica(no.cond, no.linha)
            self._bloco(no.corpo)

        elif isinstance(no, FacaEnquanto):
            self._bloco(no.corpo)
            self._exigir_logica(no.cond, no.linha)

        elif isinstance(no, Para):
            self._comando(no.init)                  # init: atribuicao no escopo atual
            self._exigir_logica(no.cond, no.linha)
            self._comando(no.incr)                  # incremento: atribuicao
            self._bloco(no.corpo)

        else:
            raise ErroSemantico(f"Comando desconhecido: {type(no).__name__}")

    def _exigir_logica(self, no_cond, linha):
        t = self._tipo_expr(no_cond)
        if t != "logicus":
            raise ErroSemantico(
                f"A condicao precisa ser logica (logicus), mas foi '{t}' (linha {linha})."
            )

    # ------- tipo de uma expressao -------

    def _tipo_expr(self, no):
        if isinstance(no, LiteralNum):   return "integer"
        if isinstance(no, LiteralReal):  return "realis"
        if isinstance(no, LiteralTexto): return "textus"
        if isinstance(no, LiteralBool):  return "logicus"
        if isinstance(no, Variavel):     return self._tipo_de(no.nome, no.linha)
        if isinstance(no, OpUn):         return self._tipo_unario(no)
        if isinstance(no, OpBin):        return self._tipo_binario(no)
        raise ErroSemantico("Expressao invalida na arvore.")

    def _tipo_unario(self, no):
        t = self._tipo_expr(no.operando)
        if no.op == "non":
            if t != "logicus":
                raise ErroSemantico(
                    f"'non' so se aplica a logicus, mas recebeu '{t}' (linha {no.linha})."
                )
            return "logicus"
        # '-' unario
        if t not in NUMERICOS:
            raise ErroSemantico(
                f"O '-' so se aplica a numeros, mas recebeu '{t}' (linha {no.linha})."
            )
        return t

    def _tipo_binario(self, no):
        e = self._tipo_expr(no.esq)
        d = self._tipo_expr(no.dir)
        op = no.op

        # aritmeticos
        if op in ("+", "-", "*", "/"):
            if e not in NUMERICOS or d not in NUMERICOS:
                raise ErroSemantico(
                    f"O operador '{op}' exige numeros, mas recebeu '{e}' e '{d}' "
                    f"(linha {no.linha})."
                )
            if op == "/":
                return "realis"                      # divisao sempre gera decimal
            return "realis" if "realis" in (e, d) else "integer"

        # relacionais de ordem
        if op in ("<", ">", "<=", ">="):
            if e not in NUMERICOS or d not in NUMERICOS:
                raise ErroSemantico(
                    f"O operador '{op}' compara numeros, mas recebeu '{e}' e '{d}' "
                    f"(linha {no.linha})."
                )
            return "logicus"

        # igualdade / diferenca
        if op in ("==", "!="):
            compat = (e in NUMERICOS and d in NUMERICOS) or (e == d)
            if not compat:
                raise ErroSemantico(
                    f"O operador '{op}' nao compara '{e}' com '{d}' (linha {no.linha})."
                )
            return "logicus"

        # logicos
        if op in ("et", "vel"):
            if e != "logicus" or d != "logicus":
                raise ErroSemantico(
                    f"O operador '{op}' exige logicus, mas recebeu '{e}' e '{d}' "
                    f"(linha {no.linha})."
                )
            return "logicus"

        raise ErroSemantico(f"Operador desconhecido: '{op}'")

    # ------- compatibilidade de atribuicao -------

    def _compativel(self, destino, origem):
        if destino == origem:
            return True
        if destino == "realis" and origem == "integer":   # promocao inteiro -> decimal
            return True
        return False


# Teste: python semantico.py [arquivo.latina]
if __name__ == "__main__":
    import sys
    from lexer import Lexer, ErroLexico
    from parser import Parser, ErroSintatico

    caminho = sys.argv[1] if len(sys.argv) > 1 else "exemplo.latina"
    with open(caminho, encoding="utf-8") as f:
        codigo = f.read()

    try:
        tokens = Lexer(codigo).tokenizar()
        arvore = Parser(tokens).parse()
        AnalisadorSemantico().analisar(arvore)
        print("Analise semantica OK: declaracoes, tipos e escopos validos.")
    except (ErroLexico, ErroSintatico, ErroSemantico) as e:
        print("ERRO:", e)
