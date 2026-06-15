# Transpilador *Latina*

Trabalho da disciplina **Teoria da Computação e Compiladores** — Prof. Eduardo Xavier.
Transpilador de uma linguagem própria, com vocabulário em **Latim** (*Latina*), para **Python**.

---

## Componentes do grupo

- Vitor Hugo Almeida Passos Braga — RA: 12724145826
- Marcelo Silva do Carmo Filho - RA: 1272323017

---

## Visão geral

- **Idioma da linguagem fonte:** Latim
- **Linguagem destino:** Python
- **Nome da linguagem:** *Latina*

O transpilador lê um arquivo `.latina`, valida-o (léxico, sintático e semântico) e gera um
arquivo `.py` equivalente, que pode ser executado diretamente pelo interpretador Python.

---

## Arquivos do projeto

| Arquivo | Responsabilidade |
|---|---|
| `tokens.py` | Tipos de token e a classe `Token` |
| **`lexer.py`** | **Análise léxica (Lexer)** — transforma o texto-fonte em tokens |
| **`parser.py`** | **Análise sintática (Parser)** — valida a gramática e constrói a AST |
| `ast_nodes.py` | Nós da Árvore Sintática Abstrata (AST) |
| `semantico.py` | Análise semântica — declaração, tipos e escopo |
| `gerador.py` | Geração do código Python a partir da AST |
| `main.py` | Programa principal (aplicação executável) que une as 4 fases |
| `exemplo.latina` e demais `*.latina` | Programas de teste |

> **Análise léxica:** `lexer.py` · **Análise sintática:** `parser.py`

---

## A linguagem *Latina*

### Palavras reservadas

| Latim | Função |
|---|---|
| `initium` … `finis` | início / fim do programa |
| `integer` | tipo inteiro |
| `realis` | tipo decimal |
| `textus` | tipo string |
| `logicus` | tipo booleano |
| `verum` / `falsum` | valores booleanos (true / false) |
| `si` / `aliter` | if / else |
| `dum` | while |
| `fac` … `dum` | do … while |
| `pro` | for |
| `lege` | leitura do teclado (input) |
| `scribe` | impressão na tela (print) |
| `et` / `vel` / `non` | and / or / not |

### Símbolos

`=` atribuição · `== != < > <= >=` relacionais · `+ - * /` aritméticos ·
`( )` agrupamento · `{ }` blocos · `;` fim de comando · `,` separador ·
`"…"` texto · `.` separador decimal.

### Tipos de dados (requisito: ≥ 4)

`integer` (inteiro), `realis` (decimal), `textus` (string), `logicus` (booleano).

### Exemplo de programa

```
initium
  integer a, b;
  realis media;

  scribe("Digite dois numeros");
  lege(a);
  lege(b);

  media = (a + b) / 2;

  si (media >= 7) {
    scribe("Aprovado");
  } aliter {
    scribe("Reprovado");
  }
finis
```

---

## Gramática (EBNF)

```
Programa     → 'initium' Comando+ 'finis'

Comando      → Declaracao | Atribuicao | Leitura | Escrita
             | Condicional | Enquanto | FacaEnquanto | Para

Declaracao   → Tipo Id ( ',' Id )* ';'
Tipo         → 'integer' | 'realis' | 'textus' | 'logicus'

Atribuicao   → AtrSimples ';'
AtrSimples   → Id '=' Expr

Leitura      → 'lege' '(' Id ')' ';'
Escrita      → 'scribe' '(' Expr ')' ';'

Condicional  → 'si' '(' Expr ')' Bloco ( 'aliter' Bloco )?
Enquanto     → 'dum' '(' Expr ')' Bloco
FacaEnquanto → 'fac' Bloco 'dum' '(' Expr ')' ';'
Para         → 'pro' '(' AtrSimples ';' Expr ';' AtrSimples ')' Bloco
Bloco        → '{' Comando+ '}'

Expr     → ExprE   ( 'vel' ExprE )*
ExprE    → ExprRel ( 'et'  ExprRel )*
ExprRel  → ExprAd  ( OpRel ExprAd )*
OpRel    → '==' | '!=' | '<' | '>' | '<=' | '>='
ExprAd   → Termo   ( ('+' | '-') Termo )*
Termo    → Fator   ( ('*' | '/') Fator )*
Fator    → ( 'non' | '-' ) Fator | '(' Expr ')'
         | Num | Real | Texto | Booleano | Id

Num      → Digito+
Real     → Digito+ '.' Digito+
Texto    → '"' (qualquer caractere exceto '"')* '"'
Booleano → 'verum' | 'falsum'
Id       → Letra ( Letra | Digito )*
Letra    → 'a'..'z' | 'A'..'Z' | '_'
Digito   → '0'..'9'
```

### Recursão à esquerda e fatoração

- **Sem recursão à esquerda:** as expressões usam a forma `Termo ( op Termo )*`, que é a
  versão sem recursão à esquerda do clássico `Expr → Expr op Termo`. O `( … )*` é
  implementado no parser como um laço `while`, sem necessidade de produções vazias (ε).
- **Sem necessidade de fatoração:** cada `Comando` inicia por um token distinto
  (palavra-chave de tipo, `Id`, `lege`, `scribe`, `si`, `dum`, `fac` ou `pro`), tornando a
  gramática **LL(1)** — o parser decide com **um único token** de lookahead. O `aliter`
  opcional também é resolvido por lookahead.

---

## Metodologia / estratégia de implementação

O transpilador foi implementado em Python, dividido em quatro fases encadeadas:

```
arquivo.latina → [Lexer] → tokens → [Parser] → AST → [Semântico] → [Gerador] → arquivo.py
```

1. **Análise léxica** (`lexer.py`): percorre o texto caractere a caractere e produz a lista
   de tokens, descartando espaços, tabs e quebras de linha, e registrando linha/coluna.
2. **Análise sintática** (`parser.py`): parser **recursivo-descendente** escrito à mão — cada
   regra da gramática corresponde a um método. Valida a sintaxe e constrói a AST.
3. **Análise semântica** (`semantico.py`): percorre a AST com uma **pilha de escopos**
   (tabela de símbolos por bloco), verificando: (a) variável declarada antes do uso;
   (b) compatibilidade de tipos em atribuições e operações; (c) condições lógicas em
   `si`/`dum`/`fac`/`pro`.
4. **Geração de código** (`gerador.py`): percorre a AST já validada e emite o código Python
   equivalente, com a indentação correta.

A escolha pelo parser recursivo-descendente justifica a  eliminarexclusão da recursão à
esquerda: esse tipo de parser (LL) só opera com a gramática nesse formato.

---

## Como executar

Pré-requisito: **Python 3.10+**. Todos os arquivos `.py` devem estar na mesma pasta.

Transpilar um programa e gerar o `.py`:

```
python main.py exemplo.latina saida.py
```

Executar o código gerado:

```
python saida.py
```

> Cada comando `lege` é uma leitura independente: forneça **um valor por linha**.

Inspecionar fases isoladas:

```
python lexer.py exemplo.latina       # lista de tokens
python parser.py exemplo.latina      # árvore sintática (AST)
python semantico.py exemplo.latina   # validação semântica
```

---

## Equivalência *Latina*

### Estruturas

| *Latina* | Python gerado |
|---|---|
| `initium … finis` | corpo do script |
| `integer a, b;` | `a = 0` / `b = 0` |
| `realis x;` | `x = 0.0` |
| `textus s;` | `s = ""` |
| `logicus f;` | `f = False` |
| `x = expr;` | `x = expr` |
| `lege(a);` *(integer)* | `a = int(input())` |
| `lege(a);` *(realis)* | `a = float(input())` |
| `lege(a);` *(textus)* | `a = input()` |
| `lege(a);` *(logicus)* | `a = (input() == "verum")` |
| `scribe(e);` | `print(e)` |
| `si (c) { … } aliter { … }` | `if c:` … `else:` … |
| `dum (c) { … }` | `while c:` … |
| `fac { … } dum (c);` | `while True:` … `if not (c): break` |
| `pro (i = 0; c; i = i + 1) { … }` | `i = 0` / `while c:` … `i = (i + 1)` |

### Operadores e literais

| *Latina* | Python | | *Latina* | Python |
|---|---|---|---|---|
| `et` | `and` | | `==` `!=` | `==` `!=` |
| `vel` | `or` | | `<` `>` `<=` `>=` | `<` `>` `<=` `>=` |
| `non` | `not` | | `+` `-` `*` `/` | `+` `-` `*` `/` |
| `verum` | `True` | | `42` | `42` |
| `falsum` | `False` | | `3.14` | `3.14` |
| | | | `"texto"` | `'texto'` |

---

## Cenários de teste

| Arquivo | Demonstra | Resultado esperado |
|---|---|---|
| `exemplo.latina` | os 4 tipos, `si/aliter`, as 3 repetições, precedência | transpila e executa |
| `teste_logica.latina` | `et` / `vel` / `non`, booleanos | transpila e executa |
| `teste_decimais.latina` | `realis`, decimais, precedência `*` antes de `-` | transpila e executa |
| `erro_naodeclarada.latina` | uso de variável não declarada | **rejeitado** (erro semântico) |
| `erro_tipo.latina` | atribuição de tipo incompatível | **rejeitado** (erro semântico) |

Os dois últimos comprovam que o transpilador valida o programa, recusando código inválido
com mensagem de erro indicando a linha.
