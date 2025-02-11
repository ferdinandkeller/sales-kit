"""Excel manipulation logic."""

from xlwings import App, Book

from structs import (
    AvailableMachine,
    AvailableMachines,
    ClientOrderEstimate,
    ClientOrderMachineEstimate,
    ClientOrderMachines,
)
from utils import get_output_path


class ExcelApp:
    """A wrapper around the xlwings App and Book objects."""

    app: App
    book: Book

    def __init__(self, book_filename: str) -> None:
        """Open the Excel file and hide the Excel application."""
        self.app = App()
        self.app.visible = False
        self.book = self.app.books.open(book_filename)

    def __enter__(self) -> "ExcelApp":
        """Access the app and book objects."""
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback) -> None:  # noqa: ANN001
        """Make sure everything is closed gracefully."""
        self.book.close()
        self.app.quit()


def get_available_machines(
    book_filename: str,
    options_column: str = "A",
) -> AvailableMachines:
    """Get the available machines and options from an Excel file."""
    with ExcelApp(book_filename) as app:
        machines_details = []
        for sheet in app.book.sheets:
            options = [cell for cell in sheet.range(f"{options_column}1:{options_column}999").value if cell is not None]
            machines_details.append(AvailableMachine(machine=sheet.name, available_options=options[1:]))
    return AvailableMachines(machines_details)


def excel_process_order(
    book_filename: str,
    machines_details: AvailableMachines,
    client_name: str,
    client_order_machines: ClientOrderMachines,
) -> ClientOrderEstimate:
    """Convert a client order into an estimate and save it to a new Excel file."""
    with ExcelApp(book_filename) as app:
        orders = []
        total = 0
        sheets = app.book.sheets
        for machine, machine_order in client_order_machines.root.items():
            if not machine_order.wants_to_buy:
                continue
            sheet = sheets[machine]
            # enable base
            sheet.range("C2").value = "TRUE"
            # enable options
            for option in machine_order.options_to_include:
                option_index = next(m for m in machines_details.root if m.machine == machine).available_options.index(
                    option,
                )
                sheet.range(f"C{option_index + 3}").value = "TRUE"
            # get total
            machine_total = sheet.range("G1").value
            orders.append(ClientOrderMachineEstimate(machine=machine, total=machine_total))
            total += machine_total

            app.book.save(get_output_path(client_name, "pricing_details.xlsx"))
    return ClientOrderEstimate(client_name=client_name, orders=orders, total=total)
