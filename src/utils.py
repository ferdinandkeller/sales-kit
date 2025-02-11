"""Utility functions usable across the project."""

from pathlib import Path

from unidecode import unidecode


def clean_name(name: str) -> str:
    """Clean a name by removing unexpected characters and spaces, so that it's compatible with file names."""
    allowed_ascii_chars = "abcdefghijklmnopqrstuvwxyz0123456789_"
    return "".join([c if (c in allowed_ascii_chars) else "_" for c in unidecode(name).lower()])


def generate_output_folder(client_name: str) -> None:
    """Generate the output folder for the client."""
    path = Path("outputs") / clean_name(client_name)
    path.mkdir(parents=True, exist_ok=True)


def get_output_path(client_name: str, filename: str) -> Path:
    """Get the output path for a file."""
    cleaned_name = clean_name(client_name)
    filename_split = filename.split(".")
    filename_split[0] += f"_{cleaned_name}"
    filename = ".".join(filename_split)
    return Path("outputs") / cleaned_name / filename
