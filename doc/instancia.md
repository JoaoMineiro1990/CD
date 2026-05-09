# Documentação técnica de `instancia.py`

## Objetivo do arquivo

O arquivo `instancia.py` guarda a instância do problema usada pelo projeto.

Ele define uma lista de cidades, suas coordenadas e gera uma matriz de distâncias entre essas cidades. Essa matriz será usada pelo algoritmo ACO (Ant Colony Optimization / Otimização por Colônia de Formigas) para resolver o TSP (Travelling Salesman Problem / Problema do Caixeiro Viajante).

Em termos simples: esse arquivo fornece os dados do mapa que o algoritmo vai usar.

## Dados definidos no arquivo

### NOMES_CIDADES

`NOMES_CIDADES` é uma lista com os nomes das 16 cidades usadas na instância.

Cada cidade é identificada por um índice.

Exemplo:

`NOMES_CIDADES[0]`

retorna:

`"Cidade 1"`

Isso significa que, quando uma rota tiver o índice `0`, ela está passando pela `Cidade 1`.

### COORDENADAS

`COORDENADAS` é uma lista com as coordenadas das 16 cidades.

Cada coordenada está no formato:

`(x, y)`

Exemplo:

`COORDENADAS[0]`

retorna:

`(38.24, 20.42)`

Essa coordenada representa a posição da `Cidade 1`.

As coordenadas usam ponto decimal porque, em Python, valores decimais são escritos com ponto.

Correto:

`38.24`

Errado:

`38,24`

Em Python, `38,24` seria interpretado como uma tupla com dois valores, não como número decimal.

### DISTANCIAS

`DISTANCIAS` é a matriz de distâncias gerada automaticamente a partir das coordenadas.

Ela é criada nesta linha:

`DISTANCIAS = gerar_matriz_distancias()`

Essa matriz tem 16 linhas e 16 colunas.

A posição:

`DISTANCIAS[i][j]`

representa a distância da cidade `i` até a cidade `j`.

Exemplo:

`DISTANCIAS[0][1]`

representa a distância da `Cidade 1` até a `Cidade 2`.

A diagonal principal da matriz é sempre `0`, porque a distância de uma cidade para ela mesma é zero.

Exemplos:

`DISTANCIAS[0][0] == 0`

`DISTANCIAS[1][1] == 0`

`DISTANCIAS[2][2] == 0`

## Funções do arquivo

### calcular_distancia_euclidiana(cidade_a, cidade_b)

Calcula a distância em linha reta entre duas cidades.

Ela recebe duas coordenadas:

`cidade_a = (x1, y1)`

`cidade_b = (x2, y2)`

E retorna a distância entre esses dois pontos.

Exemplo de uso:

`distancia = calcular_distancia_euclidiana((0.0, 0.0), (3.0, 4.0))`

`print(distancia)`

Saída:

`5`

Por quê?

Porque a distância entre `(0, 0)` e `(3, 4)` é `5`.

Essa função usa a fórmula da distância euclidiana:

`raiz((x2 - x1)² + (y2 - y1)²)`

No código, o resultado é arredondado com `round()`, então a distância final vira um número inteiro.

### gerar_matriz_distancias(coordenadas=None)

Gera uma matriz de distâncias entre todas as cidades.

Se nenhuma lista de coordenadas for passada, ela usa automaticamente a lista `COORDENADAS`.

Uso normal:

`matriz = gerar_matriz_distancias()`

Nesse caso, ela usa as 16 coordenadas definidas no próprio arquivo.

Também dá para passar coordenadas customizadas:

`coordenadas_teste = [(0.0, 0.0), (3.0, 4.0)]`

`matriz = gerar_matriz_distancias(coordenadas_teste)`

`print(matriz)`

Saída:

`[[0, 5], [5, 0]]`

Explicação:

- distância da cidade 0 para ela mesma: `0`;
- distância da cidade 0 para cidade 1: `5`;
- distância da cidade 1 para cidade 0: `5`;
- distância da cidade 1 para ela mesma: `0`.

Essa função é usada internamente para criar a matriz `DISTANCIAS`.

### obter_matriz_distancias()

Retorna uma cópia da matriz de distâncias padrão.

Uso recomendado:

`from instancia import obter_matriz_distancias`

`matriz = obter_matriz_distancias()`

Essa é a função que os outros integrantes devem chamar quando precisarem da matriz.

Ela retorna uma cópia para evitar que outro arquivo altere a matriz original sem querer.

Exemplo:

`matriz = obter_matriz_distancias()`

`matriz[0][1] = 999`

Isso altera apenas a cópia que foi retornada, não altera a matriz original `DISTANCIAS`.

Esse cuidado é importante porque vários módulos do projeto podem usar a mesma instância.

### obter_nomes_cidades()

Retorna uma cópia da lista de nomes das cidades.

Exemplo:

`from instancia import obter_nomes_cidades`

`nomes = obter_nomes_cidades()`

`print(nomes)`

Essa função é útil quando outro módulo quiser saber quais cidades existem sem acessar diretamente a variável global `NOMES_CIDADES`.

### obter_coordenadas()

Retorna uma cópia da lista de coordenadas das cidades.

Exemplo:

`from instancia import obter_coordenadas`

`coordenadas = obter_coordenadas()`

`print(coordenadas)`

Essa função é útil para debug, visualização ou validação da instância.

Normalmente, o algoritmo ACO não precisa usar as coordenadas diretamente. Ele usa a matriz de distâncias.

### nomear_rota(rota)

Converte uma rota representada por índices em nomes de cidades.

Exemplo:

`from instancia import nomear_rota`

`rota = [0, 7, 3, 5, 0]`

`nomes = nomear_rota(rota)`

`print(nomes)`

Saída:

`["Cidade 1", "Cidade 8", "Cidade 4", "Cidade 6", "Cidade 1"]`

Essa função ajuda a transformar a saída do algoritmo em algo mais fácil de entender.

O algoritmo normalmente trabalha com índices:

`[0, 7, 3, 5, 0]`

Mas, para apresentação ou relatório, é melhor mostrar:

`["Cidade 1", "Cidade 8", "Cidade 4", "Cidade 6", "Cidade 1"]`

### formatar_rota(rota)

Converte uma rota representada por índices em uma string legível.

Exemplo:

`from instancia import formatar_rota`

`rota = [0, 7, 3, 5, 0]`

`texto = formatar_rota(rota)`

`print(texto)`

Saída:

`Cidade 1 -> Cidade 8 -> Cidade 4 -> Cidade 6 -> Cidade 1`

Essa função é a mais prática para imprimir a melhor rota encontrada pelo algoritmo.

## Como os outros integrantes devem usar

O uso mais importante é obter a matriz de distâncias.

Exemplo:

`from instancia import obter_matriz_distancias`

`matriz = obter_matriz_distancias()`

Depois disso, a matriz pode ser passada para o algoritmo ACO.

Exemplo:

`from instancia import obter_matriz_distancias`

`matriz = obter_matriz_distancias()`

## Como usar para mostrar uma rota

Se o algoritmo retornar uma rota por índices, por exemplo:

`rota = [0, 7, 3, 5, 0]`

Você pode formatar assim:

`from instancia import formatar_rota`

`print(formatar_rota(rota))`

Saída:

`Cidade 1 -> Cidade 8 -> Cidade 4 -> Cidade 6 -> Cidade 1`

## Sobre a distância euclidiana

A distância usada nesse arquivo é a distância euclidiana.

Isso significa que as cidades são tratadas como pontos em um plano, e a distância entre elas é calculada em linha reta.

Essa escolha é suficiente para o trabalho porque o foco principal é testar o algoritmo distribuído, a comunicação entre os nós, a eleição de líder e o relógio lógico.

Para um sistema real de rotas, seria necessário usar outro tipo de distância, como:

- distância por estrada;
- tempo de viagem;
- custo com combustível;
- custo com pedágio;
- dados obtidos por uma API (Application Programming Interface / Interface de Programação de Aplicações) de mapas.

## Sobre a ulysses16

A instância usada é baseada na `ulysses16`, que é uma instância pequena do Problema do Caixeiro Viajante.

Ela possui 16 cidades.

Neste projeto, usamos as coordenadas dessa instância como base e geramos a matriz de distâncias usando distância euclidiana simples.

Isso deixa o código mais simples e mantém o foco na parte distribuída do projeto.

## Por que retornar cópia da matriz?

A função `obter_matriz_distancias()` retorna uma cópia para proteger a matriz original.

Se ela retornasse a própria matriz global, outro módulo poderia alterar `DISTANCIAS` sem querer.

Exemplo perigoso:

`DISTANCIAS[0][1] = 999`

Isso mudaria a instância do problema.

Com a cópia, esse risco diminui.

## Propriedades esperadas da matriz

A matriz gerada deve ter estas propriedades:

- 16 linhas;
- 16 colunas;
- diagonal principal igual a `0`;
- matriz simétrica;
- valores positivos fora da diagonal.

Matriz simétrica significa que:

`DISTANCIAS[0][1] == DISTANCIAS[1][0]`

Ou seja, a distância da `Cidade 1` para a `Cidade 2` é a mesma da `Cidade 2` para a `Cidade 1`.

## Resumo para o grupo

Para usar a instância padrão, basta fazer:

`from instancia import obter_matriz_distancias`

`matriz = obter_matriz_distancias()`

Essa matriz já está pronta para ser usada pelo algoritmo ACO.

Para imprimir uma rota com nomes:

`from instancia import formatar_rota`

`print(formatar_rota(rota))`
