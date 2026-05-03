# aco.py — Núcleo Local do Algoritmo de Colônia de Formigas

## O que é este módulo

`aco.py` implementa o núcleo local do algoritmo ACO (Ant Colony Optimization / Otimização por Colônia de Formigas).

Esse módulo é responsável por executar o algoritmo de otimização usado para resolver o TSP (Travelling Salesman Problem / Problema do Caixeiro Viajante). Ele recebe uma matriz de distâncias entre cidades, constrói rotas com formigas artificiais, calcula o custo dessas rotas, atualiza a matriz de feromônio e mantém registrada a melhor rota encontrada até o momento.

O módulo foi feito para funcionar de forma isolada. Ele não conhece rede, sockets, eleição de líder, relógio lógico ou mensagens. A parte distribuída é feita posteriormente pelo `no.py`, que apenas chama os métodos públicos da classe `ACO`.

## Responsabilidade do módulo

O `aco.py` faz:

- recebe uma matriz de distâncias;
- cria uma matriz inicial de feromônio;
- executa uma iteração do algoritmo com N formigas;
- constrói uma rota completa para cada formiga;
- calcula a distância total de cada rota;
- identifica a melhor rota da iteração;
- atualiza a melhor rota global;
- evapora feromônio antigo;
- deposita feromônio nas rotas construídas;
- permite obter a matriz de feromônio atual;
- permite aplicar uma matriz de feromônio recebida de outro nó.

O `aco.py` não faz:

- não envia mensagens;
- não recebe mensagens;
- não escolhe líder;
- não usa relógio de Lamport;
- não cria sockets;
- não sabe qual nó está executando;
- não sabe se está rodando localmente ou distribuído.

## Dependências

Apenas biblioteca padrão do Python, sem instalação externa.

| Módulo | Uso |
|---|---|
| `random` | Sorteio da cidade inicial e escolha probabilística da próxima cidade |
| `math.inf` | Valor inicial para representar uma distância infinita antes de encontrar qualquer rota |

## Constante de configuração

| Constante | Valor | Descrição |
|---|---:|---|
| `FEROMONIO_INICIAL` | `0.1` | Valor inicial de feromônio entre cidades diferentes |

A diagonal principal da matriz de feromônio é sempre `0.0`, porque não há deslocamento de uma cidade para ela mesma.

## Classe `ACO`

### O que resolve

A classe `ACO` implementa a busca por boas rotas para o Problema do Caixeiro Viajante.

O problema consiste em encontrar uma rota que:

- comece em uma cidade;
- passe por todas as cidades uma única vez;
- retorne para a cidade inicial;
- tenha a menor distância total possível.

Como testar todas as rotas possíveis é inviável para instâncias maiores, o ACO usa uma abordagem heurística. Em vez de tentar todas as combinações, ele simula formigas artificiais construindo rotas. As rotas melhores reforçam os caminhos usados com mais feromônio. Com o passar das iterações, as próximas formigas tendem a escolher caminhos que historicamente apareceram em rotas melhores.

## Construtor

`ACO(matriz_distancias, alfa=1.0, beta=2.0, rho=0.5, q=100)`

### Parâmetros

| Parâmetro | Tipo | Valor padrão | Descrição |
|---|---|---:|---|
| `matriz_distancias` | `list[list[int ou float]]` | obrigatório | Matriz com as distâncias entre as cidades |
| `alfa` | `float` | `1.0` | Peso do feromônio na escolha da próxima cidade |
| `beta` | `float` | `2.0` | Peso da distância na escolha da próxima cidade |
| `rho` | `float` | `0.5` | Taxa de evaporação do feromônio |
| `q` | `float` | `100` | Fator de escala para depósito de feromônio |

### O que acontece no construtor

Quando um objeto `ACO` é criado, ele executa a seguinte sequência:

1. Recebe a matriz de distâncias.
2. Valida se a matriz é quadrada.
3. Valida se a matriz não está vazia.
4. Valida se os valores são numéricos.
5. Valida se não existem distâncias negativas.
6. Valida se a diagonal principal é zero.
7. Copia a matriz recebida para proteger o estado interno.
8. Calcula a quantidade de cidades.
9. Armazena os parâmetros `alfa`, `beta`, `rho` e `q`.
10. Cria a matriz inicial de feromônio.
11. Inicializa a melhor rota global como vazia.
12. Inicializa a melhor distância global como infinito.

O módulo não busca a matriz diretamente em `instancia.py`. Quem cria o objeto `ACO` é responsável por passar a matriz.

Exemplo de uso esperado:

`matriz = obter_matriz_distancias()`

`aco = ACO(matriz)`

## Parâmetros matemáticos

### `alfa`

Controla o peso do feromônio.

Quanto maior o `alfa`, mais a formiga confia nos caminhos que já foram reforçados anteriormente.

Se `alfa` for muito alto, o algoritmo tende a seguir cedo demais os caminhos que parecem bons. Isso pode acelerar a convergência, mas também pode prender o algoritmo em uma solução ruim.

No projeto, usamos `alfa = 1.0`, que dá peso normal ao feromônio.

### `beta`

Controla o peso da distância.

A distância entra no algoritmo por meio da visibilidade:

`visibilidade = 1 / distancia`

Quanto menor a distância, maior a visibilidade.

Se `beta` for alto, a formiga dá mais preferência para cidades próximas.

No projeto, usamos `beta = 2.0`, dando mais importância à distância do que ao feromônio no início da execução.

### `rho`

Controla a evaporação do feromônio.

A evaporação reduz o feromônio antigo usando a regra:

`novo_feromonio = feromonio_atual * (1 - rho)`

Com `rho = 0.5`, metade do feromônio evapora a cada atualização.

A evaporação evita que o algoritmo fique preso cedo demais em caminhos que foram reforçados por acaso nas primeiras iterações.

### `q`

Controla a quantidade de feromônio depositado por uma rota.

O depósito é calculado assim:

`deposito = q / distancia_da_rota`

Rotas menores depositam mais feromônio. Rotas maiores depositam menos.

Com `q = 100`, uma rota de distância `50` deposita `2.0`, enquanto uma rota de distância `200` deposita `0.5`.

## Estrutura interna

### `self.matriz_distancias`

Cópia da matriz de distâncias recebida no construtor.

Essa matriz representa o custo fixo entre as cidades.

Ela não muda durante a execução.

### `self.feromonio`

Matriz de feromônio usada pelo algoritmo.

Ela representa o quanto cada caminho entre duas cidades parece promissor.

Essa matriz muda ao final de cada iteração.

A posição:

`feromonio[i][j]`

representa o feromônio no caminho da cidade `i` para a cidade `j`.

### `self.melhor_rota_global`

Guarda a melhor rota encontrada desde a criação do objeto `ACO`.

### `self.melhor_distancia_global`

Guarda a distância da melhor rota global.

Antes de qualquer iteração, ela começa como infinito.

## Métodos públicos

## `executar_iteracao(num_formigas: int) -> tuple[list, float]`

Executa uma iteração completa do algoritmo.

Uma iteração é composta por várias formigas construindo rotas. Depois que todas as formigas terminam, o algoritmo atualiza o feromônio.

### Entrada

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `num_formigas` | `int` | Quantidade de formigas artificiais que serão executadas naquela iteração |

### Saída

Retorna uma tupla:

`(melhor_rota_iteracao, melhor_distancia_iteracao)`

Onde:

- `melhor_rota_iteracao` é a melhor rota encontrada somente naquela iteração;
- `melhor_distancia_iteracao` é a distância dessa rota.

### Fluxo interno

A função executa a seguinte sequência:

1. Valida se `num_formigas` é maior que zero.
2. Cria uma lista para guardar as rotas encontradas.
3. Inicializa a melhor distância da iteração como infinito.
4. Para cada formiga:
   - chama `_construir_rota()`;
   - recebe uma rota completa;
   - chama `_calcular_distancia_rota(rota)`;
   - recebe a distância total da rota;
   - salva a rota e a distância em `rotas_encontradas`;
   - verifica se essa é a melhor rota da iteração;
   - verifica se essa é a melhor rota global.
5. Depois que todas as formigas terminam:
   - chama `_atualizar_feromonio(rotas_encontradas)`.
6. Retorna a melhor rota e a melhor distância da iteração.

### Observação importante

A melhor rota da iteração pode piorar de uma iteração para outra.

Exemplo:

- iteração 1: melhor distância `86`;
- iteração 2: melhor distância `74`;
- iteração 3: melhor distância `76`.

Isso é normal. A melhor rota global continua sendo `74`, porque o algoritmo guarda o melhor resultado encontrado até agora.

## `obter_feromonio() -> list[list[float]]`

Retorna uma cópia da matriz de feromônio atual.

Essa função será usada na parte distribuída quando o líder solicitar o feromônio de cada nó.

### Por que retorna uma cópia?

Para evitar que outro módulo altere diretamente a matriz interna do ACO.

Uso esperado:

`feromonio = aco.obter_feromonio()`

Na integração distribuída, essa matriz será enviada ao líder.

## `aplicar_feromonio_externo(matriz_externa: list[list[float]]) -> None`

Aplica uma matriz de feromônio recebida de fora.

Essa função é o principal ponto de integração com a parte distribuída.

Quando o líder consolidar o feromônio dos nós, ele enviará uma matriz consolidada para cada nó. Cada nó chamará esta função para misturar o feromônio recebido com o feromônio local.

### Regra usada

Para cada posição da matriz:

`feromonio_local[i][j] = (feromonio_local[i][j] + matriz_externa[i][j]) / 2`

A diagonal principal continua `0.0`.

### Por que fazer média?

A média permite misturar o aprendizado local do nó com o aprendizado recebido da rede.

Essa abordagem é simples e estável. Ela evita que um único nó domine imediatamente todo o sistema, mas também pode diluir descobertas locais muito boas.

Como melhoria futura, o líder poderia reforçar a melhor rota global recebida entre os nós antes de redistribuir a matriz consolidada.

## `obter_melhor_global() -> tuple[list, float]`

Retorna a melhor rota encontrada pelo objeto `ACO` desde o início da execução.

### Saída

Retorna:

`(melhor_rota_global, melhor_distancia_global)`

Se nenhuma iteração foi executada ainda, retorna:

`([], infinito)`

Essa função pode ser usada para logs, testes, apresentação e relatório.

## Métodos internos

Os métodos internos começam com `_` e não devem ser chamados diretamente por outros módulos.

Eles existem para dividir a lógica do algoritmo em partes menores.

## `_criar_matriz_feromonio()`

Cria a matriz inicial de feromônio.

A matriz tem o mesmo tamanho da matriz de distâncias.

Para cidades diferentes, usa `FEROMONIO_INICIAL`.

Para a diagonal principal, usa `0.0`.

Exemplo conceitual com 4 cidades:

`[0.0, 0.1, 0.1, 0.1]`

`[0.1, 0.0, 0.1, 0.1]`

`[0.1, 0.1, 0.0, 0.1]`

`[0.1, 0.1, 0.1, 0.0]`

## `_construir_rota()`

Constrói uma rota completa para uma formiga.

### Fluxo

1. Sorteia uma cidade inicial.
2. Coloca essa cidade na rota.
3. Cria o conjunto de cidades ainda não visitadas.
4. Enquanto ainda houver cidade não visitada:
   - chama `_escolher_proxima_cidade(cidade_atual, cidades_nao_visitadas)`;
   - adiciona a cidade escolhida na rota;
   - remove a cidade escolhida das não visitadas;
   - atualiza a cidade atual.
5. Quando todas as cidades forem visitadas, adiciona a cidade inicial no final da rota.
6. Retorna a rota completa.

### Exemplo de rota retornada

`[0, 7, 3, 5, 2, 1, 0]`

Isso significa:

`Cidade 1 -> Cidade 8 -> Cidade 4 -> Cidade 6 -> Cidade 3 -> Cidade 2 -> Cidade 1`

## `_escolher_proxima_cidade(cidade_atual, cidades_candidatas)`

Escolhe a próxima cidade da formiga.

A escolha não é puramente gulosa. A formiga não escolhe sempre a cidade mais próxima. Ela escolhe com base em probabilidade.

A probabilidade usa dois fatores:

- feromônio do caminho;
- distância até a cidade candidata.

### Fórmula do peso

Para cada cidade candidata `j`, saindo da cidade atual `i`, o peso é:

`peso = feromonio[i][j]^alfa * (1 / distancia[i][j])^beta`

Depois o algoritmo faz um sorteio proporcional aos pesos.

### Exemplo conceitual

Se a formiga está na `Cidade 1`, e pode ir para:

- `Cidade 2`;
- `Cidade 3`;
- `Cidade 4`;

o algoritmo calcula um peso para cada opção.

Se `Cidade 4` tem maior peso, ela tem maior chance de ser escolhida, mas as outras ainda podem ser escolhidas.

Isso mantém diversidade na busca.

## `_calcular_distancia_rota(rota)`

Calcula a distância total de uma rota.

A rota já precisa estar completa.

Exemplo:

`[0, 2, 3, 1, 0]`

A função soma:

- distância de `0` para `2`;
- distância de `2` para `3`;
- distância de `3` para `1`;
- distância de `1` para `0`.

O retorno é a distância total da rota.

## `_atualizar_feromonio(rotas_encontradas)`

Atualiza a matriz de feromônio depois que todas as formigas terminaram suas rotas.

Ela chama duas funções:

1. `_evaporar_feromonio()`;
2. `_depositar_feromonio(rotas_encontradas)`.

A ordem é importante.

Primeiro o feromônio antigo evapora. Depois as rotas encontradas depositam novo feromônio.

## `_evaporar_feromonio()`

Reduz o feromônio de todos os caminhos.

A regra é:

`novo_feromonio = feromonio_atual * (1 - rho)`

Com `rho = 0.5`, todo caminho perde metade do feromônio.

A diagonal principal não é alterada.

## `_depositar_feromonio(rotas_encontradas)`

Deposita feromônio nos caminhos usados pelas formigas.

Para cada rota encontrada, calcula:

`deposito = q / distancia_da_rota`

Rotas menores geram depósitos maiores.

Depois, para cada trecho da rota, soma esse depósito na matriz de feromônio.

Exemplo:

Rota:

`Cidade 1 -> Cidade 4 -> Cidade 2 -> Cidade 1`

Recebe depósito nos caminhos:

- `Cidade 1 -> Cidade 4`;
- `Cidade 4 -> Cidade 2`;
- `Cidade 2 -> Cidade 1`.

Como a instância é simétrica, o código também reforça o caminho inverso:

- `Cidade 4 -> Cidade 1`;
- `Cidade 2 -> Cidade 4`;
- `Cidade 1 -> Cidade 2`.

## `_validar_matriz_distancias(matriz)`

Valida a matriz de distâncias recebida no construtor.

Verifica:

- se a matriz não está vazia;
- se é uma lista de listas;
- se é quadrada;
- se tem pelo menos duas cidades;
- se todos os valores são numéricos;
- se não existem valores negativos;
- se a diagonal principal é zero.

Se alguma regra for violada, lança erro.

## `_validar_matriz_generica(matriz, nome)`

Valida uma matriz genérica.

É usada tanto para a matriz de distâncias quanto para a matriz externa de feromônio.

Verifica:

- se a matriz existe;
- se é uma lista;
- se cada linha é uma lista;
- se é quadrada;
- se possui pelo menos duas cidades.

## Fluxo completo de uma iteração

Uma iteração do ACO acontece assim:

1. `executar_iteracao(num_formigas)` é chamada.
2. Para cada formiga, o algoritmo chama `_construir_rota()`.
3. `_construir_rota()` sorteia uma cidade inicial.
4. Enquanto ainda faltarem cidades, `_construir_rota()` chama `_escolher_proxima_cidade()`.
5. `_escolher_proxima_cidade()` calcula o peso de cada caminho possível e sorteia a próxima cidade.
6. Quando a rota está completa, `_construir_rota()` retorna a rota.
7. `executar_iteracao()` chama `_calcular_distancia_rota(rota)`.
8. `_calcular_distancia_rota()` soma todos os trechos da rota e retorna a distância total.
9. `executar_iteracao()` guarda a rota e compara com a melhor rota da iteração.
10. `executar_iteracao()` também compara com a melhor rota global.
11. Depois que todas as formigas terminam, `executar_iteracao()` chama `_atualizar_feromonio()`.
12. `_atualizar_feromonio()` chama `_evaporar_feromonio()`.
13. `_atualizar_feromonio()` chama `_depositar_feromonio(rotas_encontradas)`.
14. `executar_iteracao()` retorna a melhor rota e a melhor distância daquela iteração.

Resumo:

`executar_iteracao() -> _construir_rota() -> _escolher_proxima_cidade() -> _calcular_distancia_rota() -> _atualizar_feromonio() -> _evaporar_feromonio() -> _depositar_feromonio()`

## Exemplo de uma iteração

Imagine uma instância pequena com 4 cidades.

A formiga começa na `Cidade 1`.

Ela escolhe a próxima cidade com base em feromônio e distância.

Suponha que escolha:

`Cidade 1 -> Cidade 4`

Depois escolhe:

`Cidade 4 -> Cidade 2`

Depois só falta:

`Cidade 2 -> Cidade 3`

Ao final, volta para a origem:

`Cidade 1 -> Cidade 4 -> Cidade 2 -> Cidade 3 -> Cidade 1`

Agora o algoritmo calcula a distância total dessa rota.

Se a distância for `42`, essa rota deposita:

`q / 42`

Se `q = 100`, o depósito é aproximadamente `2.38`.

Esse depósito é aplicado nos caminhos usados pela rota.

Se outra formiga encontrou uma rota de distância `39`, ela deposita:

`100 / 39`, aproximadamente `2.56`.

A rota de distância `39` deposita mais feromônio porque é melhor.

## Como isso vira distribuído

O `aco.py` sozinho é local. Ele roda dentro de um único processo.

A distribuição acontece quando vários nós executam o mesmo algoritmo localmente e compartilham seus feromônios.

Exemplo com 3 nós:

- Nó 1 cria seu próprio `ACO`;
- Nó 2 cria seu próprio `ACO`;
- Nó 3 cria seu próprio `ACO`.

Todos usam a mesma matriz de distâncias, porque estão resolvendo o mesmo problema.

Mas cada nó faz sorteios próprios. Por isso, mesmo com a mesma matriz de distâncias e o mesmo feromônio inicial, as rotas podem ser diferentes.

Depois de algumas iterações, cada nó terá uma matriz de feromônio diferente.

A integração distribuída funciona assim:

1. Cada nó executa o ACO localmente.
2. Cada nó atualiza seu próprio feromônio.
3. A cada período de sincronização, o líder solicita as matrizes de feromônio.
4. Cada nó envia sua matriz de feromônio atual.
5. O líder recebe as matrizes.
6. O líder consolida essas matrizes, por exemplo calculando uma média.
7. O líder envia uma matriz consolidada para todos.
8. Cada nó chama `aplicar_feromonio_externo(matriz_consolidada)`.
9. Cada nó continua executando o ACO localmente com o feromônio atualizado.

## Papel do líder na integração

O líder não executa as formigas dos outros nós.

Cada nó executa suas próprias formigas.

O papel do líder é apenas coordenar a sincronização.

Ele faz:

- solicita feromônio dos nós;
- recebe as matrizes;
- consolida as informações;
- redistribui uma matriz consolidada.

O líder transforma várias matrizes locais em uma matriz comum de aprendizado compartilhado.

## O que trafega pela rede

Na integração, o principal dado que sai do `aco.py` para a rede é a matriz de feromônio.

Quando o líder solicita, o nó chama:

`aco.obter_feromonio()`

Depois envia essa matriz no conteúdo da mensagem.

Quando o nó recebe uma matriz consolidada do líder, ele chama:

`aco.aplicar_feromonio_externo(matriz_recebida)`

A matriz de distâncias não precisa trafegar pela rede, porque todos os nós já possuem o mesmo `instancia.py`.

## Diferença entre matriz de distâncias e matriz de feromônio

### Matriz de distâncias

É fixa.

Ela representa o custo entre as cidades.

Exemplo:

`DISTANCIAS[0][1]`

significa:

`distância da Cidade 1 até a Cidade 2`

Essa matriz vem de `instancia.py`.

### Matriz de feromônio

É dinâmica.

Ela representa o quanto cada caminho parece promissor para o algoritmo.

Exemplo:

`feromonio[0][1]`

significa:

`quantidade de feromônio no caminho Cidade 1 -> Cidade 2`

Essa matriz começa quase uniforme e muda a cada iteração.

## O feromônio é por rota ou por cidade?

O feromônio não é por cidade isolada.

Também não é guardado como uma rota inteira.

O feromônio é por caminho entre duas cidades.

Ou seja, ele fica nas arestas do grafo.

Se uma formiga percorre:

`Cidade 1 -> Cidade 4 -> Cidade 2 -> Cidade 3 -> Cidade 1`

ela deposita feromônio nos caminhos:

- `Cidade 1 -> Cidade 4`;
- `Cidade 4 -> Cidade 2`;
- `Cidade 2 -> Cidade 3`;
- `Cidade 3 -> Cidade 1`.

## Sobre aleatoriedade e seed

O algoritmo usa sorteios para:

- escolher a cidade inicial da formiga;
- escolher a próxima cidade com base em probabilidades.

Sem definir uma seed manualmente, o Python usa o comportamento padrão do módulo `random`.

Em geral, processos diferentes terão sequências aleatórias diferentes.

Se uma seed igual for usada em todos os nós, eles podem gerar sequências de escolhas iguais, o que reduz a diversidade.

Para uma versão distribuída mais controlada, cada nó poderia usar uma seed diferente, por exemplo baseada no ID do nó.

Exemplo conceitual:

- Nó 1 usa seed `1`;
- Nó 2 usa seed `2`;
- Nó 3 usa seed `3`.

A seed não muda o feromônio inicial.

Ela só controla a sequência de sorteios feita pelo algoritmo.

## Visualização usada no teste

O teste imprime, por iteração:

- melhor distância da iteração;
- melhor distância global até agora;
- melhor rota da iteração;
- resumo do feromônio antes da iteração;
- resumo do feromônio depois da iteração;
- caminhos que mais ganharam feromônio.

Essa visualização foi escolhida porque imprimir uma matriz 16x16 em toda iteração geraria muito ruído.

Em vez disso, o teste mostra:

- valor mínimo de feromônio;
- valor máximo de feromônio;
- média do feromônio;
- soma total do feromônio;
- top caminhos reforçados.

Isso permite enxergar que a matriz está sendo atualizada sem precisar imprimir todos os 256 valores.

## Como testar

Arquivo sugerido:

`src/testes/teste_aco.py`

Execução pela raiz do projeto:

`python src/testes/teste_aco.py`

ou:

`py src/testes/teste_aco.py`

O teste deve:

1. Carregar a matriz de distâncias de `instancia.py`.
2. Criar o objeto `ACO`.
3. Rodar 50 iterações.
4. Usar 10 formigas por iteração.
5. Imprimir a melhor distância da iteração.
6. Imprimir a melhor distância global.
7. Mostrar o resumo do feromônio antes e depois.
8. Testar `obter_feromonio()`.
9. Testar `aplicar_feromonio_externo()`.

## O que observar no teste

O teste está funcionando se:

- a melhor rota da iteração aparece em todas as iterações;
- a melhor distância global não volta a piorar;
- o feromônio máximo aumenta em alguns caminhos;
- os top caminhos reforçados mudam ou se repetem conforme o algoritmo aprende;
- `obter_feromonio()` retorna uma matriz quadrada;
- `aplicar_feromonio_externo()` faz a média corretamente.

A melhor distância da iteração pode piorar de uma iteração para outra.

Isso é normal porque cada iteração faz novos sorteios.

A melhor distância global deve manter o melhor valor encontrado até então.

## Decisões de design

### Por que o `aco.py` não importa `instancia.py`?

Para manter o módulo independente.

O `ACO` recebe uma matriz de distâncias no construtor. Isso permite usar o mesmo algoritmo com qualquer instância do TSP.

Quem usa o `ACO` decide de onde vem a matriz.

No projeto, ela vem de `instancia.py`.

### Por que copiar a matriz de distâncias?

Para evitar que alterações externas afetem o estado interno do algoritmo.

Se outro módulo modificar a matriz original, o objeto `ACO` continua usando sua cópia interna.

### Por que `obter_feromonio()` retorna cópia?

Para proteger a matriz interna de feromônio.

Se retornasse a própria matriz, outro módulo poderia alterá-la diretamente sem passar pelas regras do algoritmo.

### Por que primeiro construir a rota e só depois calcular a distância?

Porque a qualidade da solução só pode ser avaliada depois que a rota completa existe.

Uma decisão local pode parecer boa, mas a rota final pode ser ruim.

Separar construção e cálculo também deixa o código mais claro.

### Por que atualizar o feromônio só depois de todas as formigas terminarem?

Porque a iteração representa um ciclo coletivo.

Todas as formigas constroem rotas com base no mesmo estado de feromônio. Depois, o algoritmo usa o conjunto de rotas para atualizar a matriz.

Isso evita que a primeira formiga da iteração influencie imediatamente a segunda dentro da mesma rodada.

### Por que depositar feromônio nos caminhos inversos?

A matriz de distâncias usada é simétrica.

Nesse caso, ir de `Cidade 1` para `Cidade 4` tem o mesmo custo que ir de `Cidade 4` para `Cidade 1`.

Por isso, quando um caminho é reforçado, o caminho inverso também é reforçado.

### Por que usar média no feromônio externo?

A média é uma forma simples de combinar o aprendizado local com o aprendizado recebido de outro nó.

Ela é adequada para a primeira versão porque é fácil de implementar e explicar.

Uma limitação é que ela pode diluir uma descoberta muito boa feita por um único nó.

## Limitações conhecidas

- O algoritmo é heurístico, então não garante encontrar a rota ótima.
- Os parâmetros `alfa`, `beta`, `rho` e `q` não foram calibrados exaustivamente.
- A média de feromônio externo pode diluir bons caminhos encontrados localmente.
- A matriz de feromônio pode crescer bastante se o depósito superar a evaporação por muitas iterações.
- A distância usada pela instância é euclidiana, não distância real por estrada.
- A melhor rota da iteração pode piorar entre iterações, embora a melhor global seja preservada.
- A execução local é rápida porque o algoritmo testa apenas uma amostra de rotas, não todas as combinações possíveis.

## Texto curto para o relatório

O módulo `aco.py` implementa o núcleo local do algoritmo ACO (Ant Colony Optimization / Otimização por Colônia de Formigas) aplicado ao TSP (Travelling Salesman Problem / Problema do Caixeiro Viajante). Cada iteração executa um conjunto de formigas artificiais, que constroem rotas completas com base na matriz de distâncias e na matriz de feromônio. Após todas as formigas concluírem suas rotas, o algoritmo calcula as distâncias, identifica as melhores soluções, evapora o feromônio antigo e deposita novo feromônio nos caminhos utilizados. Para a integração distribuída, o módulo expõe métodos para obter a matriz de feromônio local e aplicar uma matriz externa consolidada, permitindo que diferentes nós compartilhem aprendizado sem acoplar o algoritmo à camada de rede.