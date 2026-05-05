import time
import threading

TIMEOUT_OK = 2.0
TIMEOUT_LIDER = 5.0  

class RelogioLamport:

    def __init__(self):
        self.tempo = 0
        self._lock = threading.Lock()

    def antes_de_enviar(self) -> int:
        with self._lock:
            self.tempo += 1
            return self.tempo

    def ao_receber(self, timestamp_recebido: int) -> None:
        with self._lock:
            self.tempo = max(self.tempo, timestamp_recebido) + 1

    def evento_interno(self) -> int:
        with self._lock:
            self.tempo += 1
            return self.tempo

    def obter(self) -> int:
        with self._lock:
            return self.tempo


class EleicaoLider:

    def __init__(self, meu_id: int, todos_ids: list):
        self.meu_id = meu_id
        self.todos_ids = sorted(todos_ids)
        self.lider_atual = None
        self._em_eleicao = False
        self._recebeu_ok = False
        self._momento_eleicao = None
        self._lock = threading.Lock()

    def em_eleicao(self) -> bool:
        with self._lock:
            return self._em_eleicao

    def iniciar_eleicao(self) -> list:
        with self._lock:
            if self._em_eleicao:
                return []

            self._em_eleicao = True
            self._recebeu_ok = False
            self._momento_eleicao = time.time()

        nos_maiores = [nid for nid in self.todos_ids if nid > self.meu_id]

        return [
            {
                "tipo": "ELEICAO",
                "remetente_id": self.meu_id,
                "conteudo": {"iniciador_id": self.meu_id},
                "destino_id": nid,
            }
            for nid in nos_maiores
        ]

    def ao_receber_eleicao(self, remetente_id: int) -> dict:
        mensagem_ok = {
            "tipo": "OK",
            "remetente_id": self.meu_id,
            "conteudo": {},
            "destino_id": remetente_id,
        }

        with self._lock:
            if not self._em_eleicao:
                self._em_eleicao = True
                self._recebeu_ok = False
                self._momento_eleicao = time.time()

        nos_maiores = [nid for nid in self.todos_ids if nid > self.meu_id]

        return {
            "ok": mensagem_ok,
            "eleicao": [
                {
                    "tipo": "ELEICAO",
                    "remetente_id": self.meu_id,
                    "conteudo": {"iniciador_id": self.meu_id},
                    "destino_id": nid,
                }
                for nid in nos_maiores
            ],
        }

    def ao_receber_ok(self, remetente_id: int) -> None:
        with self._lock:
            self._recebeu_ok = True
            self._momento_eleicao = time.time()

    def ao_receber_lider(self, lider_id: int) -> None:
        with self._lock:
            self.lider_atual = lider_id
            self._em_eleicao = False
            self._recebeu_ok = False
            self._momento_eleicao = None

    def verificar_timeout_ok(self) -> list:
        with self._lock:
            if not self._em_eleicao:
                return []

            if self._momento_eleicao is None:
                return []

            agora = time.time()
            tempo_decorrido = agora - self._momento_eleicao

            if self._recebeu_ok:
                if tempo_decorrido < TIMEOUT_LIDER:
                    return []
            else:
                if tempo_decorrido < TIMEOUT_OK:
                    return []

            # Ninguém assumiu → eu sou líder
            self.lider_atual = self.meu_id
            self._em_eleicao = False
            self._recebeu_ok = False
            self._momento_eleicao = None

        return [
            {
                "tipo": "LIDER",
                "remetente_id": self.meu_id,
                "conteudo": {"lider_id": self.meu_id},
                "destino_id": nid,
            }
            for nid in self.todos_ids
            if nid != self.meu_id
        ]
    
    def obter_lider(self):
        with self._lock:
            return self.lider_atual

    def eu_sou_lider(self) -> bool:
        with self._lock:
            return self.lider_atual == self.meu_id

    def resetar_lider(self) -> None:
        with self._lock:
            if self._em_eleicao:
                return
            self.lider_atual = None
            self._recebeu_ok = False
            self._momento_eleicao = None

class MembrosGrupo:

    def __init__(self, meu_id: int):
        self.meu_id = meu_id
        self._participantes = {meu_id}
        self._lock = threading.Lock()

    def adicionar(self, no_id: int) -> None:
        with self._lock:
            self._participantes.add(no_id)

    def adicionar_varios(self, ids: list[int]) -> None:
        with self._lock:
            self._participantes.update(ids)
            self._participantes.add(self.meu_id)

    def remover(self, no_id: int) -> None:
        with self._lock:
            if no_id != self.meu_id:
                self._participantes.discard(no_id)

    def listar(self) -> list[int]:
        with self._lock:
            return sorted(self._participantes)

    def workers(self) -> list[int]:
        with self._lock:
            return sorted(
                no_id
                for no_id in self._participantes
                if no_id != self.meu_id
            )