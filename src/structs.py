"""Pydantic models used in the application."""

from pydantic import BaseModel, RootModel


class AvailableMachine(BaseModel):
    """Machine that can be ordered and its options."""

    machine: str
    available_options: list[str]


AvailableMachines = RootModel[list[AvailableMachine]]
"""List of machines that can be ordered and their options."""


class ClientOrderMachine(BaseModel):
    """Machine ordered by a client, along with its options."""

    wants_to_buy: bool
    options_to_include: list[str]


ClientOrderMachines = RootModel[dict[str, ClientOrderMachine]]
"""List of machines ordered by a client, along with their options."""


class ClientsOrders(BaseModel):
    """List of clients and the machines they ordered."""

    clients_orders_by_name: dict[str, ClientOrderMachines]


class ClientOrderMachineEstimate(BaseModel):
    """Estimate of the cost of a machine ordered by a client, options included."""

    machine: str
    total: float


class ClientOrderEstimate(BaseModel):
    """Total estimate of the cost of all the machines ordered by a client."""

    client_name: str
    orders: list[ClientOrderMachineEstimate]
    total: float
