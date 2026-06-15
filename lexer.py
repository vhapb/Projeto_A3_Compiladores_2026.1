# lexer.py
# Analisador lexico: percorre o texto-fonte caractere a caractere
# e produz a lista de tokens que o parser vai consumir.

from tokens import Token, TokenType, KEYWORDS


class ErroLexico(Exception):
    pass


class Lexer:
    def __init__(self, fonte):
        self.fonte = fonte    # todo o codigo-fonte como uma string
        self.pos = 0          # indice do caractere atual
        self.linha = 1
        self.coluna = 1

    # ------- navegacao -------

    def _atual(self):
        # caractere atual, ou None se acabou
        return self.fonte[self.pos] if self.pos < len(self.fonte) else None

    def _proximo(self):
        # espia 1 caractere a frente (lookahead), sem consumir
        i = self.pos + 1
        return self.fonte[i] if i < len(self.fonte) else None

    def _avancar(self):
        # consome o caractere atual, controlando linha/coluna
        c = self.fonte[self.pos]
        self.pos += 1
        if c == "\n":
            self.linha += 1
            self.coluna = 1
        else:
            self.coluna += 1
        return c

    # ------- analise principal -------

    def tokenizar(self):
        tokens = []
        while self._atual() is not None:
            c = self._atual()

            # 1) espacos, tabs, \r e \n sao descartados
            if c in " \t\r\n":
                self._avancar()
                continue

            # 2) identificador ou palavra reservada: comeca por letra ou _
            if c.isalpha() or c == "_":
                tokens.append(self._ler_identificador())
                continue

            # 3) numero (inteiro ou decimal): comeca por digito
            if c.isdigit():
                tokens.append(self._ler_numero())
                continue

            # 4) texto entre aspas
            if c == '"':
                tokens.append(self._ler_texto())
                continue

            # 5) operadores e delimitadores
            tokens.append(self._ler_simbolo())

        tokens.append(Token(TokenType.EOF, None, self.linha, self.coluna))
        return tokens

    def _ler_identificador(self):
        linha, coluna = self.linha, self.coluna
        inicio = self.pos
        while self._atual() is not None and (self._atual().isalnum() or self._atual() == "_"):
            self._avancar()
        texto = self.fonte[inicio:self.pos]
        # se estiver na tabela de palavras reservadas, usa o tipo dela; senao e um ID
        tipo = KEYWORDS.get(texto, TokenType.ID)
        return Token(tipo, texto, linha, coluna)

    def _ler_numero(self):
        linha, coluna = self.linha, self.coluna
        inicio = self.pos
        while self._atual() is not None and self._atual().isdigit():
            self._avancar()
        # so e decimal se houver '.' SEGUIDO de digito (assim "5;" nao confunde)
        if self._atual() == "." and self._proximo() is not None and self._proximo().isdigit():
            self._avancar()  # consome o '.'
            while self._atual() is not None and self._atual().isdigit():
                self._avancar()
            return Token(TokenType.REAL, self.fonte[inicio:self.pos], linha, coluna)
        return Token(TokenType.NUM, self.fonte[inicio:self.pos], linha, coluna)

    def _ler_texto(self):
        linha, coluna = self.linha, self.coluna
        self._avancar()           # consome a aspa de abertura
        inicio = self.pos
        while self._atual() is not None and self._atual() != '"':
            if self._atual() == "\n":
                raise ErroLexico(f"Texto sem aspa de fechamento na linha {linha}")
            self._avancar()
        if self._atual() is None:
            raise ErroLexico(f"Texto sem aspa de fechamento na linha {linha}")
        texto = self.fonte[inicio:self.pos]
        self._avancar()           # consome a aspa de fechamento
        return Token(TokenType.TEXTO, texto, linha, coluna)

    def _ler_simbolo(self):
        linha, coluna = self.linha, self.coluna
        c = self._avancar()

        # operadores de DOIS caracteres (checa o proximo)
        if c == "=" and self._atual() == "=":
            self._avancar(); return Token(TokenType.EQ, "==", linha, coluna)
        if c == "!" and self._atual() == "=":
            self._avancar(); return Token(TokenType.NEQ, "!=", linha, coluna)
        if c == "<" and self._atual() == "=":
            self._avancar(); return Token(TokenType.LE, "<=", linha, coluna)
        if c == ">" and self._atual() == "=":
            self._avancar(); return Token(TokenType.GE, ">=", linha, coluna)

        # operadores e delimitadores de UM caractere
        simples = {
            "=": TokenType.ASSIGN, "<": TokenType.LT, ">": TokenType.GT,
            "+": TokenType.PLUS,   "-": TokenType.MINUS,
            "*": TokenType.TIMES,  "/": TokenType.DIVIDE,
            "(": TokenType.LPAREN, ")": TokenType.RPAREN,
            "{": TokenType.LBRACE, "}": TokenType.RBRACE,
            ";": TokenType.SEMI,   ",": TokenType.COMMA,
        }
        if c in simples:
            return Token(simples[c], c, linha, coluna)

        raise ErroLexico(f"Caractere inesperado {c!r} na linha {linha}, coluna {coluna}")


# Permite testar direto:  python lexer.py exemplo.latina
if __name__ == "__main__":
    import sys
    caminho = sys.argv[1] if len(sys.argv) > 1 else "exemplo.latina"
    with open(caminho, encoding="utf-8") as f:
        codigo = f.read()
    for t in Lexer(codigo).tokenizar():
        print(t)
