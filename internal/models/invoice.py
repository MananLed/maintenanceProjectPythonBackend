from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Invoice:
    amount: float = field(metadata={"json": "amount"})
    month: int = field(metadata={"json": "month"})
    year: int = field(metadata={"json": "year"})
    id: UUID = field(metadata={"json": "id"}, default_factory=uuid4)


