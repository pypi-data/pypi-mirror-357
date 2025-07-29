def combine_dedupe_values(values: list[str], separator: str) -> str: ...

"""Take a list of values, split them by a separator, and combine them into a single string with no duplicates."""

def fix_lt_gt(value: str) -> str: ...

"""Adds a space character after each "<" or ">" symbol in a string, as long as the symbol is not an HTML tag.

Returns the modified string.

Args:
    value (str): The input string to be modified.

Returns:
    str: The modified string, with a space character added after each "<" or ">" symbol that is not part of an HTML
    tag.
"""

def unescape_html_chars(value: str) -> str: ...

"""Unescapes HTML characters from `value` (e.g. "100 &mu;g" returns "100 µg")."""

def clean_temperature(value: str) -> str: ...

"""Cleans common issues with 'Degrees Celsius' values.

Changes any non ° characters to a °
Fixes the combined degree C character

"""

def remove_chinese_chars(value: str) -> str: ...

"""Removes all Chinese characters from `value`."""

def strip_html_tags(value: str) -> str: ...

"""Removes all HTML tags from `value`."""

def add_chemical_formula_subscript(value: str) -> str: ...

"""Adds subscript formatting to chemical formulas in `value`."""

def convert_to_xlsx(csv_path: str) -> None: ...

"""Converts a CSV file located at `csv_path` to an XLSX file.

Args:
    csv_path (str): The path to the CSV file to be converted.

Returns:
    None

Raises:
    FileNotFoundError: If the file at `csv_path` does not exist.
    ValueError: If the file at `csv_path` is not a CSV file or if the contents of the file cannot be written to an XLSX.
"""
