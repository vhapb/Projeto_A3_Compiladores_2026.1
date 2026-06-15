# parser.py
# Analisador sintatico recursivo-descendente.
# Consome a lista de tokens do lexer, confere a sintaxe (gramatica) e
# constroi a AST. Cada metodo _xxx corresponde a uma regra da gramatica.

from tokens import TokenType
from ast_nodes import (
    Programa, Declaracao, Atribuicao, Leitura, Escrita,
    Condicional, Enquanto, FacaEnquanto, Para,
    OpBin, OpUn, LiteralNum, LiteralReal, LiteralTexto, LiteralBool, Variavel,
)


class ErroSintatico(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ------- utilitarios -------

    def _atual(self):
        return self.tokens[self.pos]

    def _verificar(self, tipo):
        return self._atual().tipo == tipo

    def _avancar(self):
        tok = self.tokens[self.pos]
        if tok.tipo != TokenType.EOF:
            self.pos += 1
        return tok

    def _consumir(self, tipo, descricao):
        # exige um token do tipo esperado; senao, gera erro de sintaxe
        if self._verificar(tipo):
            return self._avancar()
        tok = self._atual()
        raise ErroSintatico(
            f"Esperava {descricao} na linha {tok.linha}, "
            f"mas encontrei '{tok.valor}' ({tok.tipo})."
        )

    # ------- regra inicial: Programa -> 'initium' Comando+ 'finis' -------

    def parse(self):
        self._consumir(TokenType.INITIUM, "'initium'")
        comandos = []
        while not self._verificar(TokenType.FINIS):
            if self._verificar(TokenType.EOF):
                raise ErroSintatico("O programa terminou sem 'finis'.")
            comandos.append(self._comando())
        self._consumir(TokenType.FINIS, "'finis'")
        return Programa(comandos)

    # ------- Comando (escolhe pela palavra-chave: LL(1)) -------

    def _comando(self):
        t = self._atual().tipo
        if t in (TokenType.INTEGER, TokenType.REALIS, TokenType.TEXTUS, TokenType.LOGICUS):
            return self._declaracao()
        if t == TokenType.ID:
            return self._atribuicao()
        if t == TokenType.LEGE:
            return self._leitura()
        if t == TokenType.SCRIBE:
            return self._escrita()
        if t == TokenType.SI:
            return self._condicional()
        if t == TokenType.DUM:
            return self._enquanto()
        if t == TokenType.FAC:
            return self._faca_enquanto()
        if t == TokenType.PRO:
            return self._para()
        tok = self._atual()
        raise ErroSintatico(
            f"Comando invalido comecando por '{tok.valor}' na linha {tok.linha}."
        )

    def _declaracao(self):
        tipo_tok = self._avancar()
        nomes = [self._consumir(TokenType.ID, "um nome de variavel").valor]
        while self._verificar(TokenType.COMMA):
            self._avancar()
            nomes.append(self._consumir(TokenType.ID, "um nome de variavel").valor)
        self._consumir(TokenType.SEMI, "';'")
        return Declaracao(tipo_tok.valor, nomes, tipo_tok.linha)

    def _atr_simples(self):
        # AtrSimples -> Id '=' Expr   (sem ';' final; usado no 'pro')
        nome_tok = self._consumir(TokenType.ID, "um nome de variavel")
        self._consumir(TokenType.ASSIGN, "'='")
        expr = self._expr()
        return Atribuicao(nome_tok.valor, expr, nome_tok.linha)

    def _atribuicao(self):
        atr = self._atr_simples()
        self._consumir(TokenType.SEMI, "';'")
        return atr

    def _leitura(self):
        linha = self._avancar().linha
        self._consumir(TokenType.LPAREN, "'('")
        nome = self._consumir(TokenType.ID, "um nome de variavel").valor
        self._consumir(TokenType.RPAREN, "')'")
        self._consumir(TokenType.SEMI, "';'")
        return Leitura(nome, linha)

    def _escrita(self):
        linha = self._avancar().linha
        self._consumir(TokenType.LPAREN, "'('")
        expr = self._expr()
        self._consumir(TokenType.RPAREN, "')'")
        self._consumir(TokenType.SEMI, "';'")
        return Escrita(expr, linha)

    def _bloco(self):
        # Bloco -> '{' Comando+ '}'
        self._consumir(TokenType.LBRACE, "'{'")
        comandos = []
        while not self._verificar(TokenType.RBRACE):
            if self._verificar(TokenType.EOF):
                raise ErroSintatico("Bloco sem '}' de fechamento.")
            comandos.append(self._comando())
        self._consumir(TokenType.RBRACE, "'}'")
        return comandos

    def _condicional(self):
        linha = self._avancar().linha
        self._consumir(TokenType.LPAREN, "'('")
        cond = self._expr()
        self._consumir(TokenType.RPAREN, "')'")
        entao = self._bloco()
        senao = None
        if self._verificar(TokenType.ALITER):   # 'aliter' opcional (lookahead)
            self._avancar()
            senao = self._bloco()
        return Condicional(cond, entao, senao, linha)

    def _enquanto(self):
        linha = self._avancar().linha
        self._consumir(TokenType.LPAREN, "'('")
        cond = self._expr()
        self._consumir(TokenType.RPAREN, "')'")
        corpo = self._bloco()
        return Enquanto(cond, corpo, linha)

    def _faca_enquanto(self):
        linha = self._avancar().linha
        corpo = self._bloco()
        self._consumir(TokenType.DUM, "'dum'")
        self._consumir(TokenType.LPAREN, "'('")
        cond = self._expr()
        self._consumir(TokenType.RPAREN, "')'")
        self._consumir(TokenType.SEMI, "';'")
        return FacaEnquanto(corpo, cond, linha)

    def _para(self):
        linha = self._avancar().linha
        self._consumir(TokenType.LPAREN, "'('")
        init = self._atr_simples()
        self._consumir(TokenType.SEMI, "';'")
        cond = self._expr()
        self._consumir(TokenType.SEMI, "';'")
        incr = self._atr_simples()
        self._consumir(TokenType.RPAREN, "')'")
        corpo = self._bloco()
        return Para(init, cond, incr, corpo, linha)

    # ------- Expressoes: um metodo por nivel de precedencia -------
    # Cada laco 'while' implementa o ( ... )* da gramatica, sem recursao a esquerda.

    def _expr(self):                       # vel  (menor precedencia)
        no = self._expr_e()
        while self._verificar(TokenType.VEL):
            op = self._avancar()
            no = OpBin(op.valor, no, self._expr_e(), op.linha)
        return no

    def _expr_e(self):                     # et
        no = self._expr_rel()
        while self._verificar(TokenType.ET):
            op = self._avancar()
            no = OpBin(op.valor, no, self._expr_rel(), op.linha)
        return no

    def _expr_rel(self):                   # == != < > <= >=
        no = self._expr_ad()
        while self._atual().tipo in (TokenType.EQ, TokenType.NEQ, TokenType.LT,
                                     TokenType.GT, TokenType.LE, TokenType.GE):
            op = self._avancar()
            no = OpBin(op.valor, no, self._expr_ad(), op.linha)
        return no

    def _expr_ad(self):                    # + -
        no = self._termo()
        while self._atual().tipo in (TokenType.PLUS, TokenType.MINUS):
            op = self._avancar()
            no = OpBin(op.valor, no, self._termo(), op.linha)
        return no

    def _termo(self):                      # * /
        no = self._fator()
        while self._atual().tipo in (TokenType.TIMES, TokenType.DIVIDE):
            op = self._avancar()
            no = OpBin(op.valor, no, self._fator(), op.linha)
        return no

    def _fator(self):                      # unario, parenteses, literais, variavel
        tok = self._atual()
        if tok.tipo in (TokenType.NON, TokenType.MINUS):
            self._avancar()
            return OpUn(tok.valor, self._fator(), tok.linha)
        if tok.tipo == TokenType.LPAREN:
            self._avancar()
            no = self._expr()
            self._consumir(TokenType.RPAREN, "')'")
            return no
        if tok.tipo == TokenType.NUM:
            self._avancar(); return LiteralNum(tok.valor, tok.linha)
        if tok.tipo == TokenType.REAL:
            self._avancar(); return LiteralReal(tok.valor, tok.linha)
        if tok.tipo == TokenType.TEXTO:
            self._avancar(); return LiteralTexto(tok.valor, tok.linha)
        if tok.tipo == TokenType.BOOLEANO:
            self._avancar(); return LiteralBool(tok.valor, tok.linha)
        if tok.tipo == TokenType.ID:
            self._avancar(); return Variavel(tok.valor, tok.linha)
        raise ErroSintatico(
            f"Esperava um valor ou expressao na linha {tok.linha}, "
            f"mas encontrei '{tok.valor}'."
        )


# Teste:  python parser.py exemplo.latina  -> imprime a AST indentada
if __name__ == "__main__":
    import sys
    from lexer import Lexer

    caminho = sys.argv[1] if len(sys.argv) > 1 else "exemplo.latina"
    with open(caminho, encoding="utf-8") as f:
        codigo = f.read()

    tokens = Lexer(codigo).tokenizar()
    arvore = Parser(tokens).parse()

    def mostrar(no, nivel=0):
        id = "  " * nivel
        if isinstance(no, Programa):
            print(id + "Programa")
            for c in no.comandos: mostrar(c, nivel + 1)
        elif isinstance(no, Declaracao):
            print(f"{id}Declaracao {no.tipo}: {', '.join(no.nomes)}")
        elif isinstance(no, Atribuicao):
            print(f"{id}Atribuicao {no.nome} =")
            mostrar(no.expr, nivel + 1)
        elif isinstance(no, Leitura):
            print(f"{id}Leitura -> {no.nome}")
        elif isinstance(no, Escrita):
            print(f"{id}Escrita"); mostrar(no.expr, nivel + 1)
        elif isinstance(no, Condicional):
            print(f"{id}Si"); mostrar(no.cond, nivel + 1)
            print(f"{id}  entao:")
            for c in no.entao: mostrar(c, nivel + 2)
            if no.senao is not None:
                print(f"{id}  aliter:")
                for c in no.senao: mostrar(c, nivel + 2)
        elif isinstance(no, Enquanto):
            print(f"{id}Dum"); mostrar(no.cond, nivel + 1)
            for c in no.corpo: mostrar(c, nivel + 1)
        elif isinstance(no, FacaEnquanto):
            print(f"{id}Fac...Dum")
            for c in no.corpo: mostrar(c, nivel + 1)
            mostrar(no.cond, nivel + 1)
        elif isinstance(no, Para):
            print(f"{id}Pro")
            mostrar(no.init, nivel + 1)
            mostrar(no.cond, nivel + 1)
            mostrar(no.incr, nivel + 1)
            for c in no.corpo: mostrar(c, nivel + 1)
        elif isinstance(no, OpBin):
            print(f"{id}OpBin '{no.op}'")
            mostrar(no.esq, nivel + 1); mostrar(no.dir, nivel + 1)
        elif isinstance(no, OpUn):
            print(f"{id}OpUn '{no.op}'"); mostrar(no.operando, nivel + 1)
        elif isinstance(no, LiteralNum):
            print(f"{id}Num {no.valor}")
        elif isinstance(no, LiteralReal):
            print(f"{id}Real {no.valor}")
        elif isinstance(no, LiteralTexto):
            print(f'{id}Texto "{no.valor}"')
        elif isinstance(no, LiteralBool):
            print(f"{id}Bool {no.valor}")
        elif isinstance(no, Variavel):
            print(f"{id}Var {no.nome}")

    mostrar(arvore)
    print("\nParse concluido com sucesso! Sintaxe valida.")
