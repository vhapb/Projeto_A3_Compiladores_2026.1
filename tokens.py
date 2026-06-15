# tokens.py
# Define os TIPOS de token e a classe Token usada por todo o transpilador.
# (O lexer produz Tokens; o parser os consome.)

class TokenType:
    # Marcadores de programa
    INITIUM = "INITIUM"
    FINIS   = "FINIS"

    # Tipos de dados
    INTEGER = "INTEGER"
    REALIS  = "REALIS"
    TEXTUS  = "TEXTUS"
    LOGICUS = "LOGICUS"

    # Controle e repeticao
    SI      = "SI"
    ALITER  = "ALITER"
    DUM     = "DUM"
    FAC     = "FAC"
    PRO     = "PRO"

    # Entrada e saida
    LEGE    = "LEGE"
    SCRIBE  = "SCRIBE"

    # Operadores logicos (palavras)
    ET      = "ET"
    VEL     = "VEL"
    NON     = "NON"

    # Literais
    ID       = "ID"
    NUM      = "NUM"        # inteiro:  42
    REAL     = "REAL"       # decimal:  3.14
    TEXTO    = "TEXTO"      # string:   "ola"
    BOOLEANO = "BOOLEANO"   # verum / falsum

    # Operadores
    ASSIGN = "ASSIGN"   # =
    EQ     = "EQ"       # ==
    NEQ    = "NEQ"      # !=
    LT     = "LT"       # <
    GT     = "GT"       # >
    LE     = "LE"       # <=
    GE     = "GE"       # >=
    PLUS   = "PLUS"     # +
    MINUS  = "MINUS"    # -
    TIMES  = "TIMES"    # *
    DIVIDE = "DIVIDE"   # /

    # Delimitadores
    LPAREN = "LPAREN"   # (
    RPAREN = "RPAREN"   # )
    LBRACE = "LBRACE"   # {
    RBRACE = "RBRACE"   # }
    SEMI   = "SEMI"     # ;
    COMMA  = "COMMA"    # ,

    EOF    = "EOF"      # fim do arquivo


# Palavras reservadas (latim) -> tipo de token.
# verum/falsum viram BOOLEANO; o valor original ("verum"/"falsum") fica guardado no Token.
KEYWORDS = {
    "initium": TokenType.INITIUM,
    "finis":   TokenType.FINIS,
    "integer": TokenType.INTEGER,
    "realis":  TokenType.REALIS,
    "textus":  TokenType.TEXTUS,
    "logicus": TokenType.LOGICUS,
    "si":      TokenType.SI,
    "aliter":  TokenType.ALITER,
    "dum":     TokenType.DUM,
    "fac":     TokenType.FAC,
    "pro":     TokenType.PRO,
    "lege":    TokenType.LEGE,
    "scribe":  TokenType.SCRIBE,
    "et":      TokenType.ET,
    "vel":     TokenType.VEL,
    "non":     TokenType.NON,
    "verum":   TokenType.BOOLEANO,
    "falsum":  TokenType.BOOLEANO,
}


class Token:
    def __init__(self, tipo, valor, linha, coluna):
        self.tipo = tipo        # ex.: TokenType.NUM
        self.valor = valor      # texto original: "42", "media", "verum"...
        self.linha = linha      # para mensagens de erro
        self.coluna = coluna

    def __repr__(self):
        return f"Token({self.tipo:<8} {self.valor!r:<12} lin={self.linha} col={self.coluna})"
