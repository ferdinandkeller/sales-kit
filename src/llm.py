"""LLM glue logic."""

import json

import ollama
from loguru import logger

from excel import AvailableMachines
from structs import ClientsOrders


def get_schema_machine_options(available_options: list[str]) -> dict:
    """Convert a list of available options into a JSON schema."""
    return {
        "type": "array",
        "items": {
            "type": "string",
            "enum": available_options,
        },
        "uniqueItems": True,
    }


def get_schema_machine(available_options: list[str]) -> dict:
    """Convert a machine's available options into a JSON schema."""
    return {
        "type": "object",
        "properties": {
            "wants_to_buy": {"type": "boolean"},
            "options_to_include": get_schema_machine_options(available_options),
        },
        "required": ["wants_to_buy", "options_to_include"],
    }


def get_schema_orders(machines_details: AvailableMachines) -> dict:
    """Convert a list of machines into a JSON schema."""
    properties = {}
    for machine_details in machines_details.root:
        properties[machine_details.machine] = get_schema_machine(machine_details.available_options)
    return {"type": "object", "properties": properties, "additionalProperties": False}


def get_schema_complete(machines_details: AvailableMachines) -> dict:
    """Convert a list of clients' orders into a JSON schema."""
    return {
        "type": "object",
        "properties": {
            "clients_orders_by_name": {
                "type": "object",
                "additionalProperties": get_schema_orders(machines_details),
            },
        },
        "required": ["clients_orders_by_name"],
    }


def get_context(available_machines: AvailableMachines) -> str:
    """Convert details about available machines into a JSON string."""
    out = []
    for machine in available_machines.root:
        m = f"'{machine.machine}' options:\n"
        for option in machine.available_options:
            m += f"  - {option}\n"
        out.append(m)
    return "\n".join(out)


def get_prompt(available_machines: AvailableMachines, instructions: str) -> str:
    """Convert details about available machines and client instructions into a prompt for LLM."""
    return f"""Use the provided context (machines & options a client can buy) and the instructions (what he wants to buy) to select which machines and which options each client wants (json output). If a machine or an option isn't explicitly mentioned (directly or indirectly), assume the client doesn't want it.

    <context>
    {get_context(available_machines)}
    </context>

    <instructions>
    {instructions}
    </instructions>

    Respond using JSON."""  # noqa: E501


def generate_llm_response(machines_details: AvailableMachines, instructions: str) -> ClientsOrders:
    """Generate a response from LLM."""
    ollama_client = ollama.Client()

    response = json.loads(
        ollama_client.generate(
            model="llama3.1:8b",
            prompt=get_prompt(machines_details, instructions),
            format=get_schema_complete(machines_details),
            options={"temperature": 0.0},
        ).response,
    )
    logger.debug(json.dumps(response, indent=4))

    return ClientsOrders(**response)
