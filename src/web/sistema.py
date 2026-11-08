"""O estado do sistema (CPU, memoria, disco) para o painel de administracao. Usa `psutil`; no contentor le tambem o limite de memoria (cgroup)."""
from __future__ import annotations

import os
import platform
import shutil
import sys
import time
from pathlib import Path

import psutil

MB = 1024 * 1024


def _cgroup() -> tuple[float | None, float | None]:
    """(usado, limite) em MB da memoria do contentor (cgroup v2 ou v1); (None, None) fora de um contentor com limite."""
    pares = (("/sys/fs/cgroup/memory.current", "/sys/fs/cgroup/memory.max"),
             ("/sys/fs/cgroup/memory/memory.usage_in_bytes", "/sys/fs/cgroup/memory/memory.limit_in_bytes"))
    for usado_p, limite_p in pares:
        try:
            usado = int(Path(usado_p).read_text().strip())
            bruto = Path(limite_p).read_text().strip()
        except (OSError, ValueError):
            continue
        limite = None if bruto == "max" or int(bruto) >= 1 << 60 else int(bruto)
        return round(usado / MB, 1), (round(limite / MB, 1) if limite else None)
    return None, None


class Observador:
    """Le CPU e memoria do servidor e do processo do motor (filho), e o disco da pasta de armazenamento."""

    def __init__(self, raiz: Path):
        self.raiz = Path(raiz)
        self._eu = psutil.Process()
        self._eu.cpu_percent(None)                           # a primeira leitura e sempre 0: serve de ponto de partida
        self._filhos: dict[int, psutil.Process] = {}
        self._disco: tuple[float, float] = (0.0, 0.0)
        self._disco_em = float("-inf")                       # 0.0 falhava: o relogio monotonico de uma maquina acabada de ligar ainda vai abaixo de 55 s

    def _processos_filhos(self) -> list[psutil.Process]:
        atuais = {}
        for p in self._eu.children(recursive=True):
            atuais[p.pid] = self._filhos.get(p.pid) or p
            if p.pid not in self._filhos:
                p.cpu_percent(None)
        self._filhos = atuais
        return list(atuais.values())

    def _tamanho_pasta(self) -> float:
        total = 0
        for dentro, _, ficheiros in os.walk(self.raiz):
            for f in ficheiros:
                try:
                    total += os.path.getsize(os.path.join(dentro, f))
                except OSError:
                    pass
        return total / MB

    def ler(self, sessoes: int, geracao_em_curso: bool, reinicios_motor: int) -> dict:
        """Um instante do sistema. `cpu` e a percentagem de UM nucleo (pode passar de 100 com varios)."""
        filhos = self._processos_filhos()
        mem_motor = cpu_motor = 0.0
        for p in filhos:
            try:
                mem_motor += p.memory_info().rss / MB
                cpu_motor += p.cpu_percent(None)
            except psutil.Error:
                pass
        usado_cont, limite_cont = _cgroup()
        agora = time.monotonic()
        if agora - self._disco_em > 55:                      # percorrer a pasta custa: uma vez por minuto
            livre = shutil.disk_usage(self.raiz).free / MB if self.raiz.exists() else 0.0
            self._disco, self._disco_em = (self._tamanho_pasta(), livre), agora
        return {
            "cpu": round(self._eu.cpu_percent(None) + cpu_motor, 1),
            "cpu_nucleos": psutil.cpu_count() or 1,
            "mem_servidor_mb": round(self._eu.memory_info().rss / MB, 1),
            "mem_motor_mb": round(mem_motor, 1),
            "mem_contentor_mb": usado_cont if usado_cont is not None else round(self._eu.memory_info().rss / MB + mem_motor, 1),
            "mem_limite_mb": limite_cont,
            "mem_no_contentor": usado_cont is not None,
            "disco_usado_mb": round(self._disco[0], 1),
            "disco_livre_mb": round(self._disco[1], 1),
            "sessoes_ativas": sessoes,
            "geracao_em_curso": geracao_em_curso,
            "motor_vivo": bool(filhos),
            "motor_reinicios": reinicios_motor,
            "python": sys.version.split()[0],
            "plataforma": f"{platform.system()} {platform.release()}",
        }
