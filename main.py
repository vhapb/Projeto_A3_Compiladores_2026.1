# main.py
# Programa principal do transpilador: junta as 4 fases.
#   entrada.latina  ->  lexer  ->  parser  ->  semantico  ->  gerador  ->  saida.py
#
# Uso:
#   python main.py exemplo.latina
#   python main.py exemplo.latina saida.py

import sys
from lexer import Lexer, ErroLexico
from parser import Parser, ErroSintatico
from semantico import AnalisadorSemantico, ErroSemantico
from gerador import Gerador


def transpilar(caminho_entrada, caminho_saida):
    with open(caminho_entrada, encoding="utf-8") as f:
        codigo_fonte = f.read()

    tokens = Lexer(codigo_fonte).tokenizar()       # 1. analise lexica
    arvore = Parser(tokens).parse()                # 2. analise sintatica
    AnalisadorSemantico().analisar(arvore)         # 3. analise semantica
    codigo_python = Gerador().gerar(arvore)        # 4. geracao de codigo

    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(codigo_python)
    return codigo_python


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python main.py <entrada.latina> [saida.py]")
        sys.exit(1)

    entrada = sys.argv[1]
    saida = sys.argv[2] if len(sys.argv) > 2 else "saida.py"

    try:
        codigo = transpilar(entrada, saida)
        print(f"Transpilacao concluida! Codigo Python gravado em '{saida}'.\n")
        print("----- codigo Python gerado -----")
        print(codigo)
    except (ErroLexico, ErroSintatico, ErroSemantico) as e:
        print("ERRO:", e)
        sys.exit(1)
