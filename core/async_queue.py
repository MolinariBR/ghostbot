import asyncio
import logging
from typing import Any, Callable, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDENTE = "pendente"
    PROCESSANDO = "processando"
    CONCLUIDA = "concluida"
    FALHOU = "falhou"
    CANCELADA = "cancelada"

@dataclass
class QueueTask:
    id: str
    tipo: str
    dados: Dict[str, Any]
    usuario_id: str
    prioridade: int = 1
    criada_em: datetime = field(default_factory=datetime.now)
    iniciada_em: Optional[datetime] = None
    finalizada_em: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDENTE
    resultado: Optional[Any] = None
    erro: Optional[str] = None
    tentativas: int = 0
    max_tentativas: int = 3

class AsyncQueue:
    """
    Fila assíncrona para processamento de tarefas em background.
    """
    def __init__(self, max_workers: int = 3, max_queue_size: int = 100):
        self.max_workers = max_workers
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.tasks: Dict[str, QueueTask] = {}
        self.workers: list[asyncio.Task] = []
        self.handlers: Dict[str, Callable] = {}
        self.running = False
        self.lock = asyncio.Lock()

    def register_handler(self, tipo: str, handler: Callable):
        """Registra uma função handler para um tipo de tarefa."""
        self.handlers[tipo] = handler
        logger.info(f"Handler registrado para tipo: {tipo}")

    async def start(self):
        if self.running:
            return
        self.running = True
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
        logger.info(f"AsyncQueue iniciada com {self.max_workers} workers")

    async def stop(self):
        self.running = False
        for worker in self.workers:
            worker.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        logger.info("AsyncQueue parada")

    async def add_task(self, tipo: str, dados: Dict[str, Any], usuario_id: str, prioridade: int = 1, task_id: Optional[str] = None) -> str:
        if tipo not in self.handlers:
            raise ValueError(f"Handler não registrado para tipo: {tipo}")
        if not task_id:
            task_id = f"{tipo}_{int(datetime.now().timestamp() * 1000)}_{usuario_id}"
        task = QueueTask(
            id=task_id,
            tipo=tipo,
            dados=dados,
            usuario_id=usuario_id,
            prioridade=prioridade
        )
        async with self.lock:
            self.tasks[task_id] = task
        await self.queue.put(task)
        logger.info(f"Tarefa adicionada: {task_id} (tipo: {tipo}, prioridade: {prioridade})")
        return task_id

    async def get_task_status(self, task_id: str) -> Optional[QueueTask]:
        async with self.lock:
            return self.tasks.get(task_id)

    async def cancel_task(self, task_id: str) -> bool:
        async with self.lock:
            task = self.tasks.get(task_id)
            if not task:
                return False
            if task.status in [TaskStatus.PENDENTE, TaskStatus.PROCESSANDO]:
                task.status = TaskStatus.CANCELADA
                task.finalizada_em = datetime.now()
                logger.info(f"Tarefa cancelada: {task_id}")
                return True
        return False

    async def _worker(self, nome: str):
        logger.info(f"Worker iniciado: {nome}")
        while self.running:
            try:
                task: QueueTask = await self.queue.get()
                if not self.running:
                    break
                await self._process_task(task, nome)
                self.queue.task_done()
            except Exception as e:
                logger.error(f"Erro no worker {nome}: {e}")
        logger.info(f"Worker finalizado: {nome}")

    async def _process_task(self, task: QueueTask, worker_name: str):
        try:
            print(f"[DEBUG] _process_task: {task.id} | tentativas={task.tentativas} | status={task.status}")
            task.status = TaskStatus.PROCESSANDO
            task.iniciada_em = datetime.now()
            handler = self.handlers.get(task.tipo)
            if not handler:
                raise ValueError(f"Handler não encontrado para tipo: {task.tipo}")
            logger.info(f"Processando tarefa: {task.id} (worker: {worker_name})")
            if asyncio.iscoroutinefunction(handler):
                result = await handler(task.dados, task.usuario_id)
            else:
                result = handler(task.dados, task.usuario_id)
            task.status = TaskStatus.CONCLUIDA
            task.resultado = result
            task.finalizada_em = datetime.now()
            logger.info(f"Tarefa concluída: {task.id}")
        except Exception as e:
            task.tentativas += 1
            print(f"[DEBUG] _process_task EXCEPT: {task.id} | tentativas={task.tentativas} | erro={e}")
            task.erro = str(e)
            if task.tentativas < task.max_tentativas:
                delay = min(2 ** task.tentativas, 60)
                logger.warning(f"Tentativa {task.tentativas}/{task.max_tentativas} falhou para {task.id}, tentando em {delay}s")
                await asyncio.sleep(delay)
                await self.queue.put(task)
            else:
                task.status = TaskStatus.FALHOU
                task.finalizada_em = datetime.now()
                logger.error(f"Tarefa falhou definitivamente: {task.id} - {e}")

# Instância global
async_queue = AsyncQueue()

# Funções utilitárias globais
async def add_task_to_queue(tipo: str, dados: Dict[str, Any], usuario_id: str, prioridade: int = 1) -> str:
    return await async_queue.add_task(tipo, dados, usuario_id, prioridade)

async def get_task_status(task_id: str) -> Optional[QueueTask]:
    return await async_queue.get_task_status(task_id)

async def cancel_task(task_id: str) -> bool:
    return await async_queue.cancel_task(task_id) 