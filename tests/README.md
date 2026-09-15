# Testes de corretude

Cada circuito aritmético deste repositório é uma **permutação dos estados da base
computacional**, então pode ser verificado exaustivamente para operandos pequenos:
prepara-se um estado da base, executa-se no `AerSimulator` e compara-se o resultado com
a aritmética modular clássica em Python.

Os testes usam `unittest` da biblioteca padrão — não é preciso instalar `pytest`.

## Como rodar

A partir da raiz do repositório (`quantum-circuits-implementation-main/`):

```bash
python -m unittest discover -s tests -t . -v
```

Um módulo isolado:

```bash
python -m unittest tests.test_roetteler -v
```

Um teste isolado:

```bash
python -m unittest tests.test_roetteler.TestQQMultMod.test_modular_multiplication -v
```

Dependências: `python -m pip install -r requirements.txt` na raiz do repositório.
A suíte completa leva cerca de 8 minutos — a maior parte em `test_haner` e
`test_roetteler`, que varrem todos os pares de operandos para p ∈ {5, 7, 11, 13}.
`test_imports` roda em menos de um segundo e vale rodar sozinho depois de mexer em
qualquer `import` ou mover arquivo:

```bash
python -m unittest tests.test_imports -v
```

## O que é verificado

Para cada bloco, três coisas — e as três importam:

1. **O valor do resultado** bate com a aritmética clássica equivalente.
2. **Os operandos de entrada são preservados** quando o circuito promete preservá-los.
3. **As ancillas voltam a `|0>`** (ou ao estado sujo original). Uma ancilla que vaza
   deixa o resultado emaranhado e quebra silenciosamente o *uncompute* de
   `elc_sum_1` — é o tipo de bug que não aparece olhando só o valor medido.

O item 3 é capturado por construção: `CircuitRunner.run` exige que a medição produza
**um único** resultado em todas as shots. Se o estado final estiver espalhado por mais
de um estado da base, o teste falha mesmo que o valor "certo" apareça em parte das shots.

## Cobertura atual

| Módulo | Blocos cobertos |
|---|---|
| `tests/test_haner.py` | `incrementer`, `carry_with_const`, `haner_class_adder` (limpo, sujo e inverso), `comparator_class`, `haner_mod_class_adder` (e inverso) |
| `tests/test_cdkm.py` | `adder_CDKM` (com carry, mod 2ⁿ e inverso), `comparator_CDKM` |
| `tests/test_roetteler.py` | `mult_by_2`, `adder_mod` (e inverso), `double_mod`, `mod_negation`, `qq_mult_mod`, `square_mod` |
| `tests/test_imports.py` | todo módulo sob `implementations/` importa; nenhum diretório do caminho sem `__init__.py` |

Ainda **sem cobertura**: inversão modular (`inv_modp_ECDLP2`), soma de pontos
(`elc_sum_1`), casos degenerados da soma de pontos, QROM/aritmética *windowed*,
somadores VBE e Draper.

## Comportamentos conhecidos, fixados em teste

- `mod_negation` **não** tem `0` como ponto fixo: mapeia `|0>` em `|p>`.
  Está fixado em `TestModNegation.test_zero_maps_to_p_not_zero` para que qualquer
  mudança futura nesse comportamento seja deliberada.
- `haner_class_adder(..., dirty=False)` exige a ancilla em `|0>`; a variante
  `dirty=True` aceita qualquer estado e o restaura. Ambas são testadas.
