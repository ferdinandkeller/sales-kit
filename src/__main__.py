"""Main entry point of the application."""

import streamlit as st
from loguru import logger

from excel import excel_process_order, get_available_machines
from llm import generate_llm_response
from ppt import ppt_process_order
from utils import generate_output_folder

book_filename = "data/products.xlsx"
pptx_template_filename = "templates/template.pptx"


def process_query(instructions: str) -> list[str]:
    """Convert user's instructions into a excel+ppt set of orders."""
    machines_details = get_available_machines(book_filename)
    logger.debug(machines_details.model_dump_json(indent=4))
    clients_orders = generate_llm_response(machines_details, instructions)
    chat_return = []
    for client_name, client_machines in clients_orders.clients_orders_by_name.items():
        generate_output_folder(client_name)

        chat_return_x = f"*Client '{client_name}' order estimate*\n\nOrder:\n"
        for machine_name, options in client_machines.root.items():
            chat_return_x += f"  - {machine_name}:\n"
            for option in options.options_to_include:
                chat_return_x += f"    - {option}\n"

        order_estimate = excel_process_order(book_filename, machines_details, client_name, client_machines)

        chat_return_x += "\nMachines Total:\n"
        for estimate in order_estimate.orders:
            chat_return_x += f"  - {estimate.machine}: ${estimate.total:,.2f}\n"

        chat_return_x += f"\n**Order Total: ${order_estimate.total:,.2f}**"

        chat_return.append(chat_return_x)

        logger.debug(order_estimate.model_dump_json(indent=4))
        ppt_process_order(pptx_template_filename, order_estimate)
    logger.success("All orders processed.")
    return chat_return


title = "📄 Prospect Builder"
st.set_page_config(page_title=title)
st.title(title)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Please describe what the client wants to buy."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    chat_return = process_query(prompt)
    for msg in chat_return:
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)
        # add a button to download the pptx file
