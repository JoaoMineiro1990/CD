# no.py — Programa Principal do Nó Distribuído

## O que é este arquivo

`no.py` é o programa principal de cada nó do sistema distribuído de ACO. Ele é o integrador: importa todos os módulos (`rede.py`, `aco.py`, `coordenacao.py`, `instancia.py`) e os conecta em um único loop de execução contínua.

Cada nó do sistema é um processo Python independente iniciado com:

```bash
python no.py 1   # Nó 1 — porta 5001
python no.py 2   # Nó 2 — porta 5002
python no.py 3   # Nó 3 — porta 5003
```

---

## Dependências

| Módulo | Origem | Uso |
|---|---|---|
| `rede.py` | interno | Comunicação TCP entre nós |
| `aco.py` | interno | Algoritmo de otimização local |
| `coordenacao.py` | interno | Relógio de Lamport e eleição de líder |
| `data/instancia.py` | interno | Matriz de distâncias do TSP |
| `sys` | padrão Python | Leitura do ID do nó via argumento |
| `time` | padrão Python | Controle de timing e sleeps |
| `threading` | padrão Python | Threads de heartbeat e eleição inicial |

---

## Configuração inicial

```python
MEU_ID = int(sys.argv[1])
NOS = {1: ('localhost', 5001), 2: ('localhost', 5002), 3: ('localhost', 5003)}
```

O ID do nó é lido do argumento de linha de comando. O dicionário `NOS` mapeia cada ID ao seu endereço e porta TCP. Para rodar em máquinas diferentes, basta substituir `'localhost'` pelos IPs reais.

---

## Instâncias dos módulos

```python
rede    = Rede(MEU_ID, NOS[MEU_ID][1], NOS)
aco     = ACO(DISTANCIAS)
relogio = RelogioLamport()
eleicao = EleicaoLider(MEU_ID, list(NOS.keys()))
```

Cada nó cria suas próprias instâncias locais de todos os módulos. Eles não compartilham estado entre si — a distribuição acontece apenas pela troca de mensagens pela rede.

---

## Variáveis globais

```python
feromonios_recebidos = {}   # armazena matrizes recebidas dos workers durante sincronização
falhas_lider = 0            # contador de heartbeats sem resposta
```

---

## Funções

### `enviar(destino_id, tipo, conteudo={})`

Monta e envia uma mensagem para um nó específico.

```python
def enviar(destino_id, tipo, conteudo={}):
    msg = {
        "tipo": tipo,
        "remetente_id": MEU_ID,
        "timestamp_lamport": relogio.antes_de_enviar(),
        "conteudo": conteudo,
    }
    return rede.enviar_mensagem(destino_id, msg)
```

**Detalhe importante:** chama `relogio.antes_de_enviar()` antes de enviar, incrementando o contador lógico e carimbando a mensagem com o timestamp atual. Retorna `True` se o envio foi bem-sucedido, `False` se o nó de destino estava offline.

---

### `broadcast(tipo, conteudo={})`

Envia a mesma mensagem para todos os nós conhecidos, exceto si mesmo.

```python
def broadcast(tipo, conteudo={}):
    msg = {
        "tipo": tipo,
        "remetente_id": MEU_ID,
        "timestamp_lamport": relogio.antes_de_enviar(),
        "conteudo": conteudo,
    }
    rede.broadcast(msg)
```

Usado para anunciar liderança (`LIDER`), solicitar feromônio (`SOLICITACAO`) e redistribuir feromônio consolidado (`FEROMONIO`).

---

### `iniciar_eleicao()`

Inicia o processo de eleição pelo algoritmo Bully.

```python
def iniciar_eleicao():
    global falhas_lider
    falhas_lider = 0

    eleicao.resetar_lider()         # limpa estado preso de eleição anterior
    mensagens = eleicao.iniciar_eleicao()

    if not mensagens:
        # sem nós com ID maior — declara-se líder imediatamente
        eleicao.ao_receber_lider(MEU_ID)
        broadcast("LIDER", {"lider_id": MEU_ID})
        print(f"[ELEI] Nó {MEU_ID} venceu a eleição (sem nós maiores).")
        return

    for m in mensagens:
        enviar(m["destino_id"], "ELEICAO", m["conteudo"])
```

**Por que `resetar_lider()` antes de `iniciar_eleicao()`?**  
Se uma eleição anterior ficou com estado inconsistente (por exemplo, `_em_eleicao = True` de uma tentativa anterior), `iniciar_eleicao()` retornaria lista vazia sem fazer nada. O `resetar_lider()` limpa esse estado, permitindo que a nova eleição comece do zero.

**Por que verificar lista vazia?**  
Quando o nó que inicia a eleição já é o de maior ID entre os vivos, não há ninguém para enviar `ELEICAO`. Nesse caso, ele se declara líder imediatamente sem precisar aguardar o timeout de 2 segundos.

---

### `processar_mensagem(msg)`

Roteia cada mensagem recebida para o tratamento correto conforme o tipo.

```python
def processar_mensagem(msg):
    global falhas_lider
    tipo = msg["tipo"]
    rem  = msg["remetente_id"]
```

#### Tipos tratados:

| Tipo | O que faz |
|---|---|
| `ELEICAO` | Responde OK ao remetente e propaga eleição para nós maiores |
| `OK` | Registra que um nó maior respondeu — para de se considerar candidato |
| `LIDER` | Atualiza o líder conhecido e reseta contador de falhas |
| `SOLICITACAO` | Se não for líder, envia sua matriz de feromônio ao líder |
| `FEROMONIO` | Se for líder, armazena a matriz recebida; se não, aplica externamente |
| `HEARTBEAT` | Responde com `HEARTBEAT_ACK` ao remetente |
| `HEARTBEAT_ACK` | Reseta o contador de falhas do líder |

#### Tratamento de `ELEICAO`:

```python
if tipo == "ELEICAO":
    resultado = eleicao.ao_receber_eleicao(rem)
    ok = resultado["ok"]
    enviar(ok["destino_id"], "OK", ok["conteudo"])
    for m in resultado["eleicao"]:
        enviar(m["destino_id"], "ELEICAO", m["conteudo"])
```

`ao_receber_eleicao()` retorna dois elementos: a mensagem OK para enviar de volta ao remetente, e a lista de mensagens ELEICAO para propagar aos nós com ID ainda maior.

#### Tratamento de `FEROMONIO`:

```python
elif tipo == "FEROMONIO":
    matriz = msg["conteudo"].get("matriz")
    if eleicao.eu_sou_lider():
        feromonios_recebidos[rem] = matriz   # coleta para consolidação
    else:
        aco.aplicar_feromonio_externo(matriz) # aplica feromônio consolidado
```

A mesma mensagem `FEROMONIO` tem dois significados dependendo de quem recebe: o líder a usa para coletar matrizes dos workers; os workers a usam para aplicar o feromônio consolidado que o líder redistribuiu.

---

### `verificar_eleicao()`

Verifica se algum timeout da eleição expirou e declara vencedor se necessário.

```python
def verificar_eleicao():
    mensagens = eleicao.verificar_timeout_ok()
    for m in mensagens:
        enviar(m["destino_id"], "LIDER", m["conteudo"])
    if mensagens:
        print(f"[ELEI] Nó {MEU_ID} venceu a eleição.")
```

Chamada a cada ciclo do loop principal. `verificar_timeout_ok()` retorna lista não vazia apenas quando um dos dois timeouts expirou:
- **TIMEOUT_OK (2s):** nenhum nó maior respondeu com OK
- **TIMEOUT_LIDER (5s):** recebeu OK mas nenhum nó anunciou LIDER

---

### `sincronizar()`

Executada pelo líder a cada 10 iterações para consolidar e redistribuir o feromônio.

```python
def sincronizar():
    feromonios_recebidos.clear()
    broadcast("SOLICITACAO")

    workers = [n for n in NOS if n != MEU_ID]
    prazo = time.time() + 3
    while time.time() < prazo:
        if all(w in feromonios_recebidos for w in workers):
            break
        time.sleep(0.1)

    matrizes = list(feromonios_recebidos.values()) + [aco.obter_feromonio()]
    n = len(matrizes)
    tamanho = len(matrizes[0])
    media = [[sum(m[i][j] for m in matrizes) / n
              for j in range(tamanho)]
              for i in range(tamanho)]

    aco.aplicar_feromonio_externo(media)
    broadcast("FEROMONIO", {"matriz": media})
    print("[SYNC] Feromônio sincronizado.")
```

**Fluxo completo:**
1. Limpa matrizes recebidas anteriormente
2. Envia `SOLICITACAO` em broadcast para os workers
3. Aguarda respostas por até 3 segundos (timeout para não travar)
4. Calcula a média elemento a elemento de todas as matrizes recebidas + a própria
5. Aplica a média localmente
6. Redistribui via `FEROMONIO` em broadcast

**Por que incluir a própria matriz na média?**  
O líder também executa formigas localmente. Ignorar sua própria matriz descartaria o aprendizado acumulado localmente pelo nó líder.

---

### `loop_heartbeat()`

Roda em thread daemon, verificando a disponibilidade do líder a cada 5 segundos.

```python
def loop_heartbeat():
    global falhas_lider
    while True:
        time.sleep(5)
        lider = eleicao.obter_lider()
        if lider and lider != MEU_ID:
            ok = enviar(lider, "HEARTBEAT")
            if not ok:
                falhas_lider += 1
                print(f"[HB] Líder {lider} falhou ({falhas_lider}/3)")
                if falhas_lider >= 3:
                    iniciar_eleicao()
            else:
                falhas_lider = 0
```

**Por que só envia se `lider != MEU_ID`?**  
O líder não envia heartbeat para si mesmo — ele só responde heartbeats recebidos dos workers.

**Por que 3 falhas consecutivas?**  
Uma única falha pode ser ruído de rede. Três falhas consecutivas (≈15 segundos) indicam com mais confiança que o líder está realmente inativo.

---

### `_eleicao_inicial()`

Roda em thread daemon, garantindo que o nó tenha um líder após a inicialização.

```python
def _eleicao_inicial():
    time.sleep(3)
    if eleicao.obter_lider() is None:
        print(f"[INIT] Nó {MEU_ID} sem líder, iniciando eleição...")
        iniciar_eleicao()
```

**Por que essa função existe?**  
Se os nós forem iniciados em ordem diferente de 3 → 2 → 1, o broadcast inicial do Nó 3 pode ocorrer antes dos outros estarem prontos para receber. Essa thread garante que, independentemente da ordem de inicialização, qualquer nó sem líder após 3 segundos inicia uma eleição automaticamente.

---

## Bloco de inicialização

```python
rede.iniciar_servidor()
if MEU_ID == max(NOS.keys()):
    eleicao.ao_receber_lider(MEU_ID)
    print(f"[INIT] Nó {MEU_ID} inicia como líder.")
    time.sleep(1)
    broadcast("LIDER", {"lider_id": MEU_ID})

threading.Thread(target=_eleicao_inicial, daemon=True).start()
threading.Thread(target=loop_heartbeat, daemon=True).start()
```

**Sequência:**
1. Sobe o servidor TCP em background
2. Se for o nó de maior ID (Nó 3), declara-se líder e aguarda 1 segundo para que os outros nós estejam prontos antes de fazer o broadcast
3. Dispara a thread de eleição inicial (verifica após 3s se há líder)
4. Dispara a thread de heartbeat (roda indefinidamente)

---

## Loop principal

```python
iteracao = 0
while True:
    msg = rede.receber_proxima()
    if msg:
        relogio.ao_receber(msg["timestamp_lamport"])
        processar_mensagem(msg)

    verificar_eleicao()

    aco.executar_iteracao(num_formigas=5)
    iteracao += 1

    if iteracao % 10 == 0:
        _, dist = aco.obter_melhor_global()
        print(f"[ACO] iter {iteracao} | dist {dist:.2f} | líder: {eleicao.obter_lider()}")

    if iteracao % 10 == 0 and eleicao.eu_sou_lider():
        sincronizar()

    time.sleep(0.01)
```

**A cada ciclo (≈10ms), o loop faz:**

| Passo | O que faz |
|---|---|
| 1 | Verifica se há mensagem na fila — se sim, atualiza o relógio de Lamport e processa |
| 2 | Verifica se algum timeout de eleição expirou |
| 3 | Executa uma iteração do ACO com 5 formigas |
| 4 | A cada 10 iterações, imprime o estado atual |
| 5 | A cada 10 iterações, se for líder, executa sincronização de feromônio |

**Por que `time.sleep(0.01)`?**  
Evita que o loop consuma 100% da CPU. 10ms é tempo suficiente para não perder mensagens importantes, pois elas ficam enfileiradas no `queue.Queue` interno do `rede.py`.

**Por que o Lamport é atualizado antes de `processar_mensagem()`?**  
A regra do Lamport exige que o relógio seja atualizado com `max(local, recebido) + 1` antes de qualquer processamento do conteúdo da mensagem. Isso garante que eventos causalmente posteriores sempre tenham timestamps maiores.

---

## Threads em execução simultânea

| Thread | Função | Intervalo |
|---|---|---|
| Loop principal | Processa mensagens, executa ACO, sincroniza | Contínuo (10ms) |
| `loop_heartbeat` | Verifica disponibilidade do líder | A cada 5s |
| `_eleicao_inicial` | Garante líder após inicialização | Uma vez, após 3s |
| Servidor TCP (rede.py) | Aceita conexões e enfileira mensagens | Contínuo |

---

## Fluxo completo de uma execução típica

```
Nó 3 sobe → declara-se líder → broadcast LIDER
Nós 1 e 2 sobem → recebem LIDER → atualizam lider_atual = 3

Loop rodando:
  → ACO executa localmente em cada nó
  → A cada 10 iterações, Nó 3 sincroniza feromônio
  → Workers enviam heartbeat a cada 5s para o Nó 3

Nó 3 cai:
  → Heartbeats falham 3 vezes (≈15s)
  → Nós 1 e 2 chamam iniciar_eleicao()
  → Nó 2 (maior ID vivo) vence após TIMEOUT_OK (2s)
  → Nó 2 faz broadcast LIDER
  → Nó 1 atualiza lider_atual = 2
  → Sistema continua normalmente com Nó 2 como líder
```

---

## Saída esperada no terminal

```
[Rede] Nó 3 escutando na porta 5003
[INIT] Nó 3 inicia como líder.
[ACO] iter 10 | dist 82.00 | líder: 3
[SYNC] Feromônio sincronizado.
[ACO] iter 20 | dist 79.00 | líder: 3
...
[HB] Líder 3 falhou (1/3)
[HB] Líder 3 falhou (2/3)
[HB] Líder 3 falhou (3/3)
[ELEI] Nó 2 venceu a eleição.
[ELEI] Novo líder: Nó 2
[ACO] iter 6400 | dist 73.00 | líder: 2
[SYNC] Feromônio sincronizado.
```