#entidades, logica de negocio
from __future__ import annotations
from datetime import date
from dataclasses import dataclass, field       # decorador para clases que van a manejar datos
from uuid import uuid4

from app.domain.enums import TaskStatus
from app.domain.exceptions import InvalidStatusTransition, ValidationError, NotFoundError
from app.domain.priority import PriorityStrategy, PriorityContext


@dataclass          # el data class ya crea el constructor, por eso no lo declaramos
class Project:
    id: str = field(default_factory=lambda: str(uuid4))
    """ lamba es una funcion anonima que regresa el uuid4 como string
            - id ya esta inicializada (antes del constructor)
            - usamos el field para que darle un valor cuando se crea
    """

    name: str
    
    def __post_init__(self) -> None:
        if not self.name or len(self.name.strip()) < 5:
            raise ValidationError("Project.name debe tener minimo 5 caracteres")
        
        
@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid4))
    title: str
    project_id: str
    strategy: PriorityStrategy
    due_date: date | None = None        # None es el valor default del due_date ( = None)
    _status: TaskStatus = field(default_factory=TaskStatus.TODO)    # el underscore es para hacer la variable oculta (private)
    
    
    def __post_init__(self) -> None:
        if not self.title or len(self.name.strip()) < 5:
             raise ValidationError("Task.title debe tener minimo 5 caracteres")
    
    @property           # permite hacer una funcion para regresar los atributos 
    def status(self) -> TaskStatus:         # GETTER 
        return self._status
    
    @property
    def priority_score(self) -> int:
        return self.strategy.compute(
            PriorityContext(due_date=self.due_date)
            )
        
    def update_due_date(self, new_due_date: date | None) -> None:
        self.due_date = new_due_date

    def update_title(self, new_title: str) -> None:
        if not new_title or len(new_title) < 5:
            raise ValidationError('El nuevo titulo debe tener como minimo 5 caracteres')
        self.title= new_title
    
    def transition_to(self, new_status: TaskStatus) -> None:
        allowed = {         # aqui las llaves son un dict
            TaskStatus.TODO: {TaskStatus.DOING},       # aqui las llaves son un set
            TaskStatus.DOING: {TaskStatus.DONE},
            TaskStatus.DONE: set()
        }
        
        if new_status == self._status:
            return
        
        if new_status not in allowed[self._status]:
            raise InvalidStatusTransition(f'Transición invalida de {self._status} -> {new_status}')
        
        self._status = new_status