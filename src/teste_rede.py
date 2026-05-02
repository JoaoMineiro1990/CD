import sys
import time

try:
    from rede import Rede
except ModuleNotFoundError:
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
    from rede import Rede


NOS_INTERATIVO = {
    1: ("localhost", 5001),
    2: ("localhost", 5002),
    3: ("localhost", 5003),
}


def montar_mensagem(tipo, remetente_id, timestamp, conteudo):
    return {
        "tipo": tipo,
        "remetente_id": remetente_id,
        "timestamp_lamport": timestamp,
        "conteudo": conteudo,
    }


def cabecalho(texto):
    print()
    print("=" * 60)
    print(f"  {texto}")
    print("=" * 60)



def teste_automatico():
    cabecalho("TESTE 1 — Envio direto entre dois nós")
    _teste_envio_direto()

    cabecalho("TESTE 2 — Broadcast de um nó para todos")
    _teste_broadcast()

    cabecalho("TESTE 3 — Tolerância a falha (nó offline)")
    _teste_no_offline()

    cabecalho("TESTE 4 — Múltiplas mensagens em sequência")
    _teste_multiplas_mensagens()

    print()
    print("Todos os testes passaram.")


def _teste_envio_direto():
    """Nó 2 envia uma mensagem para o Nó 1. Nó 1 deve recebê-la."""
    nos = {1: ("localhost", 5101), 2: ("localhost", 5102)}
    no1 = Rede(meu_id=1, minha_porta=5101, nos_conhecidos=nos)
    no2 = Rede(meu_id=2, minha_porta=5102, nos_conhecidos=nos)

    no1.iniciar_servidor()
    no2.iniciar_servidor()

    mensagem = montar_mensagem("TESTE", 2, 1, {"texto": "olá do nó 2"})
    sucesso = no2.enviar_mensagem(destino_id=1, mensagem=mensagem)
    assert sucesso, "FALHOU: enviar_mensagem retornou False"

    time.sleep(0.3)

    recebida = no1.receber_proxima()
    assert recebida is not None, "FALHOU: nó 1 não recebeu nenhuma mensagem"
    assert recebida["tipo"] == "TESTE", f"FALHOU: tipo errado: {recebida['tipo']}"
    assert recebida["remetente_id"] == 2, "FALHOU: remetente_id errado"
    assert recebida["conteudo"]["texto"] == "olá do nó 2", "FALHOU: conteúdo errado"

    print(f"  Nó 2 enviou:   {mensagem}")
    print(f"  Nó 1 recebeu:  {recebida}")
    print("Envio direto OK")

    no1.parar(); no2.parar()


def _teste_broadcast():
    """Nó 1 faz broadcast. Nós 2 e 3 devem receber. Nó 1 não recebe a si mesmo."""
    nos = {1: ("localhost", 5201), 2: ("localhost", 5202), 3: ("localhost", 5203)}
    no1 = Rede(meu_id=1, minha_porta=5201, nos_conhecidos=nos)
    no2 = Rede(meu_id=2, minha_porta=5202, nos_conhecidos=nos)
    no3 = Rede(meu_id=3, minha_porta=5203, nos_conhecidos=nos)

    no1.iniciar_servidor()
    no2.iniciar_servidor()
    no3.iniciar_servidor()

    mensagem = montar_mensagem("ELEICAO", 1, 2, {"iniciador_id": 1})
    no1.broadcast(mensagem)
    time.sleep(0.4)

    msg2 = no2.receber_proxima()
    msg3 = no3.receber_proxima()
    msg1_proprio = no1.receber_proxima()

    assert msg2 is not None, "FALHOU: nó 2 não recebeu o broadcast"
    assert msg3 is not None, "FALHOU: nó 3 não recebeu o broadcast"
    assert msg1_proprio is None, "FALHOU: nó 1 recebeu a própria mensagem"

    print(f"  Nó 2 recebeu:    {msg2}")
    print(f"  Nó 3 recebeu:    {msg3}")
    print(f"  Nó 1 (próprio):  {msg1_proprio}  ← correto: None")
    print("Broadcast OK")

    no1.parar(); no2.parar(); no3.parar()


def _teste_no_offline():
    """Tenta enviar para um nó offline. Deve retornar False rapidamente."""
    nos = {1: ("localhost", 5301), 2: ("localhost", 5302)}
    no1 = Rede(meu_id=1, minha_porta=5301, nos_conhecidos=nos)
    no1.iniciar_servidor()
    # Nó 2 não é iniciado — está "offline"

    mensagem = montar_mensagem("TESTE", 1, 0, {})
    inicio = time.time()
    resultado = no1.enviar_mensagem(destino_id=2, mensagem=mensagem)
    duracao = time.time() - inicio

    assert resultado is False, "FALHOU: deveria retornar False para nó offline"
    assert duracao < 5, f"FALHOU: demorou demais ({duracao:.1f}s)"

    print(f"  Retornou:              {resultado}  ← correto: False")
    print(f"  Tempo até detectar:    {duracao:.2f}s  ← deve ser < 5s")
    print("Tolerância a falha OK")

    no1.parar()


def _teste_multiplas_mensagens():
    """Nó 2 envia 5 mensagens em sequência. Todas devem chegar."""
    nos = {1: ("localhost", 5401), 2: ("localhost", 5402)}
    no1 = Rede(meu_id=1, minha_porta=5401, nos_conhecidos=nos)
    no2 = Rede(meu_id=2, minha_porta=5402, nos_conhecidos=nos)

    no1.iniciar_servidor()
    no2.iniciar_servidor()

    quantidade = 5
    for i in range(quantidade):
        msg = montar_mensagem("FEROMONIO", 2, i + 1, {"sequencia": i})
        no2.enviar_mensagem(1, msg)

    time.sleep(0.5)

    recebidas = []
    while True:
        msg = no1.receber_proxima()
        if msg is None:
            break
        recebidas.append(msg)

    assert len(recebidas) == quantidade, (
        f"FALHOU: esperava {quantidade} mensagens, recebeu {len(recebidas)}"
    )

    for i, msg in enumerate(recebidas):
        print(f"  Mensagem {i+1}: tipo={msg['tipo']}, "
              f"timestamp={msg['timestamp_lamport']}, "
              f"seq={msg['conteudo']['sequencia']}")

    print(f"{quantidade} mensagens recebidas corretamente")
    no1.parar(); no2.parar()


# ── MODO 2: Servidor interativo ───────────────────────────────────────────────

def modo_servidor(meu_id: int):
    """
    Sobe o nó e fica imprimindo mensagens recebidas.
    Use num terminal enquanto o modo cliente roda em outro.
    """
    rede = Rede(meu_id=meu_id, minha_porta=NOS_INTERATIVO[meu_id][1],
                nos_conhecidos=NOS_INTERATIVO)
    rede.iniciar_servidor()

    print(f"\n[Servidor] Nó {meu_id} rodando na porta {NOS_INTERATIVO[meu_id][1]}.")
    print("[Servidor] Aguardando mensagens... (Ctrl+C para parar)\n")

    try:
        while True:
            msg = rede.receber_proxima()
            if msg:
                print(f"[Servidor] ← Recebido: {msg}")
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\n[Servidor] Encerrando...")
        rede.parar()


# ── MODO 3: Cliente interativo ────────────────────────────────────────────────

def modo_cliente(meu_id: int, destino_id: int):
    """
    Envia uma bateria de mensagens para o nó destino.
    """
    rede = Rede(meu_id=meu_id, minha_porta=NOS_INTERATIVO[meu_id][1],
                nos_conhecidos=NOS_INTERATIVO)
    rede.iniciar_servidor()

    print(f"\n[Cliente] Nó {meu_id} pronto. Enviando para nó {destino_id}...\n")

    msg = montar_mensagem("TESTE", meu_id, 1, {"texto": f"oi do nó {meu_id}"})
    ok = rede.enviar_mensagem(destino_id, msg)
    print(f"[Cliente] TESTE    → {'OK' if ok else 'FALHOU'}: {msg}")
    time.sleep(0.3)

    msg = montar_mensagem("ELEICAO", meu_id, 2, {"iniciador_id": meu_id})
    ok = rede.enviar_mensagem(destino_id, msg)
    print(f"[Cliente] ELEICAO  → {'OK' if ok else 'FALHOU'}: {msg}")
    time.sleep(0.3)

    msg = montar_mensagem("LIDER", meu_id, 3, {"lider_id": meu_id})
    print(f"[Cliente] Broadcast LIDER → enviando para todos exceto nó {meu_id}")
    rede.broadcast(msg)

    print("\n[Cliente] Concluído.")
    rede.parar()


# ── Ponto de entrada ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] == "auto":
        teste_automatico()
    elif args[0] == "servidor" and len(args) == 2:
        modo_servidor(int(args[1]))
    elif args[0] == "cliente" and len(args) == 3:
        modo_cliente(int(args[1]), int(args[2]))
    else:
        print(__doc__)
        sys.exit(1)