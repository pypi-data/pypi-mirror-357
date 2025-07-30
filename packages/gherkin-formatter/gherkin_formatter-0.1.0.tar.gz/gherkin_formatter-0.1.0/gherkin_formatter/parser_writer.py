"""Gherkin parsing and formatting."""

import json
import sys
from pathlib import Path
from typing import (
    Any,
    Optional,
    Union,
)

from gherkin.errors import CompositeParserException
from gherkin.parser import Parser
from gherkin.parser_types import GherkinDocument

__all__ = ["parse_gherkin_file", "GherkinFormatter"]


def parse_gherkin_file(file_path: Path) -> Optional[GherkinDocument]:
    """
    Parses a Gherkin .feature file and returns its Abstract Syntax Tree (AST).

    The AST structure is typically a dictionary-like object (gherkin.GherkinDocument)
    representing the Gherkin document, with a top-level 'feature' key.
    Using `Any` for now as `GherkinDocument` type is not easily importable for hinting.

    :param file_path: The path to the .feature file.
    :type file_path: Path
    :return: The GherkinDocument, or None if parsing fails.
    :rtype: Optional[GherkinDocument]
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            file_content: str = f.read()

        return Parser().parse(file_content)
    except CompositeParserException as e:
        # Consider logging this error instead of just printing if this were a library
        print(f"Error parsing file: {file_path}\n{e}", file=sys.stderr)
        return None
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}", file=sys.stderr)
        return None
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            f"An unexpected error occurred while parsing {file_path}: {e}",
            file=sys.stderr,
        )
        return None


# pylint: disable-next=too-many-instance-attributes, too-few-public-methods
class GherkinFormatter:
    """
    Formats a Gherkin Abstract Syntax Tree (AST) into a consistently styled string.

    This class takes a Gherkin AST (as produced by `gherkin.parser.Parser`)
    and applies formatting rules for indentation, spacing, and alignment
    to generate a standardized string representation of the feature file.
    """

    # pylint: disable-next=too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        ast: Union[GherkinDocument, dict[str, Any]],
        tab_width: int = 2,
        use_tabs: bool = False,
        alignment: str = "left",
        multi_line_tags: bool = False,
    ) -> None:
        """
        Initializes the GherkinFormatter.

        :param ast: The Gherkin Abstract Syntax Tree (GherkinDocument).
        :type ast: Union[GherkinDocument, dict[str, Any]]
        :param tab_width: Spaces for indentation if not using tabs (default: 2).
        :type tab_width: int
        :param use_tabs: Whether to use tabs for indentation (default: False).
        :type use_tabs: bool
        :param alignment: Table cell content alignment ('left'/'right').
        :type alignment: str
        :param multi_line_tags: Format tags over multiple lines (default: False).
        :type multi_line_tags: bool
        """
        self.ast: Any = ast
        self.tab_width: int = tab_width
        self.use_tabs: bool = use_tabs
        self.alignment: str = alignment
        self.multi_line_tags: bool = multi_line_tags
        self.indent_str = "\t" if self.use_tabs else " " * self.tab_width

    def _indent_line(self, text: str, level: int) -> str:
        """
        Applies indentation to a single line of text.

        :param text: The text to indent.
        :type text: str
        :param level: The indentation level (number of indent units).
        :type level: int
        :return: The indented string.
        :rtype: str
        """
        return f"{self.indent_str * level}{text}"

    def _format_description(
        self, description: Optional[str], current_indent_level: int
    ) -> list[str]:
        """
        Formats a multi-line description string with appropriate indentation.

        :param description: The description text, possibly None or empty.
        :type description: Optional[str]
        :param current_indent_level: The current indentation level for these lines.
        :type current_indent_level: int
        :return: A list of formatted description lines.
        :rtype: List[str]
        """
        lines: list[str] = []
        if description:
            for line in description.strip().split("\n"):
                lines.append(self._indent_line(line.strip(), current_indent_level))
        return lines

    def _format_tags(
        self, tags_list: list[dict[str, str]], current_indent_level: int
    ) -> list[str]:
        """
        Formats a list of tags.

        Example AST for tags: `[{'name': '@tag1', ...}, {'name': '@tag2', ...}]`
        Can format as single line or multi-line based on `self.multi_line_tags`.

        :param tags_list: A list of tag dictionaries from the AST.
        :type tags_list: List[Dict[str, str]]
        :param current_indent_level: The indentation level for the tag line(s).
        :type current_indent_level: int
        :return: A list containing formatted tag lines, or an empty list if no tags.
        :rtype: List[str]
        """
        if not tags_list:
            return []

        if self.multi_line_tags:
            return [
                self._indent_line(tag["name"], current_indent_level)
                for tag in tags_list
            ]
        tag_names: list[str] = [tag["name"] for tag in tags_list]
        return [self._indent_line(" ".join(tag_names), current_indent_level)]

    def _format_table(
        self, table_node_rows: list[dict[str, Any]], current_indent_level: int
    ) -> list[str]:
        """
        Formats a Gherkin data table with aligned columns.

        Assumes `table_node_rows` is a list of row dicts, each with a 'cells' key
        containing a list of cell dicts (each with a 'value').

        :param table_node_rows: List of row data from AST (tableHeader + tableBody).
        :type table_node_rows: List[Dict[str, Any]]
        :param current_indent_level: Indentation level for each table line.
        :type current_indent_level: int
        :return: A list of formatted table lines.
        :rtype: List[str]
        """
        if not table_node_rows:
            return []

        num_columns: int = len(table_node_rows[0]["cells"]) if table_node_rows else 0
        if num_columns == 0:
            # Minimal representation for empty row
            return [
                self._indent_line("| |", current_indent_level) for _ in table_node_rows
            ]

        col_widths: list[int] = [0] * num_columns
        for row_data in table_node_rows:
            for i, cell in enumerate(row_data["cells"]):
                col_widths[i] = max(col_widths[i], len(cell["value"]))

        formatted_lines: list[str] = []
        for row_data in table_node_rows:
            formatted_cells: list[str] = [
                cell["value"].ljust(col_widths[i])
                for i, cell in enumerate(row_data["cells"])
            ]
            formatted_lines.append(
                self._indent_line(
                    f"| {' | '.join(formatted_cells)} |", current_indent_level
                )
            )
        return formatted_lines

    def _format_docstring(
        self, docstring_node: dict[str, Any], current_indent_level: int
    ) -> list[str]:
        """Formats a Gherkin DocString.

        Attempts to parse content as JSON and formats it; otherwise,
        treats as plain text.

        :param docstring_node: The DocString node from the AST.
        :type docstring_node: Dict[str, Any]
        :param current_indent_level: Indentation level for the DocString.
        :type current_indent_level: int
        :return: A list of formatted DocString lines.
        :rtype: List[str]
        """
        lines: list[str] = []
        delimiter: str = docstring_node.get("delimiter", '"""')
        lines.append(self._indent_line(delimiter, current_indent_level))

        content: str = docstring_node.get("content", "")

        try:
            json_obj: Any = json.loads(content)
            # If successful, format with indentation.
            # json.dumps indent parameter expects int for spaces.
            # If using tabs for Gherkin, JSON will use spaces for simplicity.
            json_indent_size = self.tab_width
            json_formatted_str: str = json.dumps(json_obj, indent=json_indent_size)

            for line in json_formatted_str.split("\n"):
                lines.append(self._indent_line(line, current_indent_level))
        except json.JSONDecodeError:
            # If not JSON, treat as plain text.
            for line in content.split("\n"):
                if line.strip() == "":
                    # Append empty lines directly without indentation
                    lines.append(line)
                else:
                    lines.append(self._indent_line(line, current_indent_level))

        lines.append(self._indent_line(delimiter, current_indent_level))
        return lines

    def _format_step(
        self, step_node: dict[str, Any], current_indent_level: int, max_keyword_len: int
    ) -> list[str]:
        """
        Formats a single Gherkin step, including DataTable or DocString.
        Keywords are aligned based on `max_keyword_len` and `self.alignment`.

        :param step_node: The step node from the AST.
        :type step_node: Dict[str, Any]
        :param current_indent_level: Indentation level for the step.
        :type current_indent_level: int
        :param max_keyword_len: Max keyword length in the current block for alignment.
        :type max_keyword_len: int
        :return: A list of formatted step lines.
        :rtype: List[str]
        """
        lines: list[str] = []
        keyword: str = step_node["keyword"].strip()
        text: str = step_node["text"].strip()

        if max_keyword_len > 0:
            aligned_keyword: str
            if self.alignment == "right":
                aligned_keyword = keyword.rjust(max_keyword_len)
            else:  # Default to left alignment
                aligned_keyword = keyword.ljust(max_keyword_len)
            lines.append(
                self._indent_line(
                    f"{aligned_keyword.rstrip()} {text}", current_indent_level
                )
            )
        else:
            lines.append(self._indent_line(f"{keyword} {text}", current_indent_level))

        if "dataTable" in step_node and step_node["dataTable"]:
            lines.extend(
                self._format_table(
                    step_node["dataTable"]["rows"], current_indent_level + 1
                )
            )
        if "docString" in step_node and step_node["docString"]:
            lines.extend(
                self._format_docstring(step_node["docString"], current_indent_level + 1)
            )
        return lines

    def _format_steps_block(
        self, steps_nodes: list[dict[str, Any]], current_indent_level: int
    ) -> list[str]:
        """
        Formats a block of steps, aligning keywords.

        :param steps_nodes: A list of step nodes.
        :param current_indent_level: The indentation level for this block.
        :return: A list of formatted step lines.
        """
        if not steps_nodes:
            return []

        max_keyword_len: int = 0
        for step_node in steps_nodes:
            keyword = step_node["keyword"].strip()
            max_keyword_len = max(max_keyword_len, len(keyword))

        formatted_steps_lines: list[str] = []
        for step_node in steps_nodes:
            formatted_steps_lines.extend(
                self._format_step(step_node, current_indent_level, max_keyword_len)
            )
        return formatted_steps_lines

    def _format_examples(
        self, examples_node: dict[str, Any], current_indent_level: int
    ) -> list[str]:
        """
        Formats an Examples block, including tags, description, and table.

        :param examples_node: The Examples node from the AST.
        :type examples_node: Dict[str, Any]
        :param current_indent_level: Indentation level for the Examples block.
        :type current_indent_level: int
        :return: A list of formatted Examples lines.
        :rtype: List[str]
        """
        lines: list[str] = []
        lines.extend(
            self._format_tags(examples_node.get("tags", []), current_indent_level)
        )

        keyword: str = examples_node["keyword"].strip()
        name_part: str = (
            f" {examples_node['name']}" if examples_node.get("name") else ""
        )
        # Ensure colon after "Examples" keyword
        lines.append(self._indent_line(f"{keyword}:{name_part}", current_indent_level))

        lines.extend(
            self._format_description(
                examples_node.get("description"), current_indent_level + 1
            )
        )

        if "tableHeader" in examples_node and examples_node["tableHeader"]:
            all_rows_data: list[dict[str, Any]] = [
                examples_node["tableHeader"]
            ] + examples_node.get("tableBody", [])
            lines.extend(self._format_table(all_rows_data, current_indent_level + 1))
        return lines

    def _format_scenario_definition(
        self, scenario_node: dict[str, Any], current_indent_level: int
    ) -> list[str]:
        """
        Formats a Scenario or Scenario Outline definition.

        Includes tags, keyword, name, description, steps, and examples (for outlines).

        :param scenario_node: The Scenario/Scenario Outline node from the AST.
        :type scenario_node: Dict[str, Any]
        :param current_indent_level: Indentation level for the definition.
        :type current_indent_level: int
        :return: A list of formatted lines for the scenario definition.
        :rtype: List[str]
        """
        lines: list[str] = []
        lines.extend(
            self._format_tags(scenario_node.get("tags", []), current_indent_level)
        )

        keyword: str = scenario_node["keyword"].strip()
        name_part: str = (
            f": {scenario_node['name']}" if scenario_node.get("name") else ""
        )
        lines.append(self._indent_line(f"{keyword}{name_part}", current_indent_level))

        lines.extend(
            self._format_description(
                scenario_node.get("description"), current_indent_level + 1
            )
        )

        lines.extend(
            self._format_steps_block(
                scenario_node.get("steps", []), current_indent_level + 1
            )
        )

        for examples_node in scenario_node.get("examples", []):
            lines.append("")  # Blank line before Examples section for readability
            lines.extend(self._format_examples(examples_node, current_indent_level + 1))
        return lines

    def _format_background(
        self, background_node: dict[str, Any], current_indent_level: int
    ) -> list[str]:
        """
        Formats a Background section.

        :param background_node: The Background node from the AST.
        :type background_node: Dict[str, Any]
        :param current_indent_level: Indentation level for the Background.
        :type current_indent_level: int
        :return: A list of formatted lines for the Background.
        :rtype: List[str]
        """
        lines: list[str] = []
        keyword: str = background_node["keyword"].strip()
        name_part: str = (
            f" {background_node['name']}" if background_node.get("name") else ""
        )
        # Ensure colon after "Background" keyword
        lines.append(self._indent_line(f"{keyword}:{name_part}", current_indent_level))

        lines.extend(
            self._format_description(
                background_node.get("description"), current_indent_level + 1
            )
        )

        lines.extend(
            self._format_steps_block(
                background_node.get("steps", []), current_indent_level + 1
            )
        )
        return lines

    def _format_rule(
        self, rule_node: dict[str, Any], current_indent_level: int
    ) -> list[str]:
        """
        Formats a Rule section.

        :param rule_node: The Rule node from the AST.
        :type rule_node: Dict[str, Any]
        :param current_indent_level: Indentation level for the Rule.
        :type current_indent_level: int
        :return: A list of formatted lines for the Rule.
        :rtype: List[str]
        """
        lines: list[str] = []
        lines.append(
            self._indent_line(
                f"{rule_node['keyword']}: {rule_node['name']}", current_indent_level
            )
        )

        lines.extend(
            self._format_description(
                rule_node.get("description"), current_indent_level + 1
            )
        )

        children_nodes: list[dict[str, Any]] = rule_node.get("children", [])
        if children_nodes:
            lines.append("")  # Ensure blank line before children block

        for i, child in enumerate(children_nodes):
            if i > 0:  # Add a blank line between children
                lines.append("")
            if "scenario" in child:
                lines.extend(
                    self._format_scenario_definition(
                        child["scenario"], current_indent_level + 1
                    )
                )
            elif "background" in child:
                lines.extend(
                    self._format_background(
                        child["background"], current_indent_level + 1
                    )
                )
        return lines

    def _format_feature(
        self, feature_node: dict[str, Any], current_indent_level: int
    ) -> list[str]:
        """
        Formats the main Feature section of the Gherkin document.

        :param feature_node: The Feature node from the AST.
        :type feature_node: Dict[str, Any]
        :param current_indent_level: The starting indentation level (usually 0).
        :type current_indent_level: int
        :return: A list of formatted lines for the Feature.
        :rtype: List[str]
        """
        lines: list[str] = []
        lines.extend(
            self._format_tags(feature_node.get("tags", []), current_indent_level)
        )

        keyword: str = feature_node["keyword"].strip()
        name_part: str = f": {feature_node['name']}" if feature_node.get("name") else ""
        lines.append(self._indent_line(f"{keyword}{name_part}", current_indent_level))

        if feature_node.get("description"):
            desc_lines: list[str] = feature_node["description"].strip().split("\n")
            for line in desc_lines:
                if line.strip():  # Only indent non-empty description lines
                    lines.append(
                        self._indent_line(line.strip(), current_indent_level + 1)
                    )
                else:  # Keep empty lines in description as they are, but without indent
                    lines.append("")

        children_nodes: list[dict[str, Any]] = feature_node.get("children", [])
        if children_nodes:
            lines.append("")  # Ensure blank line before children block

        for i, child in enumerate(children_nodes):
            if i > 0:  # Add a blank line between children (Scenarios, Rules, etc.)
                lines.append("")

            if "background" in child:
                lines.extend(
                    self._format_background(
                        child["background"], current_indent_level + 1
                    )
                )
            elif "rule" in child:
                lines.extend(self._format_rule(child["rule"], current_indent_level + 1))
            elif "scenario" in child:
                lines.extend(
                    self._format_scenario_definition(
                        child["scenario"], current_indent_level + 1
                    )
                )
        return lines

    def format(self) -> str:
        """
        Orchestrates the formatting of the entire Gherkin AST.

        :return: A single string representing the fully formatted Gherkin document.
        :rtype: str
        """
        output_lines: list[str] = []

        if not self.ast:
            return "\n"  # Empty line for an empty AST

        # Format top-level comments first (if any)
        # Assuming comments are at the root of the AST, not inside 'feature'
        if "comments" in self.ast:  # Check if self.ast is a dictionary
            for comment_node in self.ast.get("comments", []):  # type: ignore
                if "text" in comment_node:
                    # Comments are usually not indented, prepended as is
                    output_lines.append(comment_node["text"])

        feature_node: Optional[dict[str, Any]] = self.ast.get("feature")

        if not feature_node:
            if output_lines:  # Only comments were present
                return "\n".join(output_lines) + "\n"
            return "\n"  # Empty line for an empty or unparsable document (no feature)

        output_lines.extend(self._format_feature(feature_node, 0))

        if not output_lines:
            return "\n"  # Empty line if feature processing resulted in no lines

        # Join all collected lines, strip any existing newlines/whitespace,
        # then add a empty line.
        full_content: str = "\n".join(output_lines)
        return full_content.strip() + "\n"
