"""Gherkin Formatter CLI."""

import argparse
import sys
from pathlib import Path
from typing import Any, Optional

# Ensure this relative import works with the project structure and pythonpath
from .parser_writer import GherkinFormatter, parse_gherkin_file

__version__ = "0.1.0"
__all__ = ["main", "__version__"]


def _discover_feature_files(paths: list[str]) -> list[Path]:
    """
    Discovers all .feature files from a list of file or directory paths.

    :param paths: A list of strings, where each string is a path to a
                  .feature file or a directory containing .feature files.
    :type paths: List[str]
    :return: A list of Path objects for all found .feature files.
    :rtype: List[Path]
    """
    feature_files_to_process: list[Path] = []
    for item_str in paths:
        item_path: Path = Path(item_str)
        if not item_path.exists():
            print(
                f"Warning: Path '{item_str}' does not exist. Skipping.", file=sys.stderr
            )
            continue

        if item_path.is_file():
            if item_path.suffix == ".feature":
                feature_files_to_process.append(item_path)
            else:
                print(
                    f"Warning: File '{item_str}' is not a .feature file. Skipping.",
                    file=sys.stderr,
                )
        elif item_path.is_dir():
            # Sort for consistent processing order
            feature_files_to_process.extend(sorted(list(item_path.rglob("*.feature"))))
        else:
            print(
                f"Warning: Path '{item_str}' is neither a file nor a directory."
                "Skipping.",
                file=sys.stderr,
            )
    return feature_files_to_process


def _process_single_file(
    file_path: Path, args: argparse.Namespace
) -> tuple[bool, bool]:
    """
    Processes a single .feature file: parses, formats, and writes or checks.

    :param file_path: The path to the .feature file to process.
    :type file_path: Path
    :param args: The command-line arguments.
    :type args: argparse.Namespace
    :return: A tuple (needs_formatting, error_occurred).
             `needs_formatting` is True if the file needs formatting (for --check mode).
             `error_occurred` is True if any error happened during processing this file.
    :rtype: Tuple[bool, bool]
    """
    print(f"Processing {file_path}...")
    needs_formatting_for_file = False
    error_occurred_for_file = False

    try:
        ast: Optional[Any] = parse_gherkin_file(file_path)
        if ast is None:
            # parse_gherkin_file already prints specific errors
            return True, True  # Needs formatting (due to error), error occurred

        formatter = GherkinFormatter(
            ast,
            tab_width=args.tab_width,
            use_tabs=args.use_tabs,
            alignment=args.alignment,
            multi_line_tags=args.multi_line_tags,
        )
        # formatter.format() always returns content with LF newlines
        formatted_content: str = formatter.format()

        try:
            original_content: str = file_path.read_text(encoding="utf-8")
            # For comparison in --check mode, normalize original to LF
            # This ensures that only content differences, not just newline style,
            # are caught.
            original_content_for_comparison = original_content.replace("\r\n", "\n")
        except (OSError, FileNotFoundError, PermissionError) as e:
            print(f"Error reading file {file_path}: {e}", file=sys.stderr)
            return True, True  # Needs formatting (due to error), error occurred
        # pylint: disable-next=broad-exception-caught
        except Exception as e:  # Catch any other read errors
            print(f"Unexpected error reading file {file_path}: {e}", file=sys.stderr)
            return True, True

        if original_content_for_comparison != formatted_content:
            needs_formatting_for_file = True
            if args.check:
                print(f"File {file_path} needs formatting.")
            elif args.dry_run:
                print(f"Would reformat {file_path}")
                print("--- Formatted content (dry-run) ---")
                sys.stdout.write(formatted_content)  # Assumes formatted_content has LF
                print("--- End formatted content ---")
            else:  # Actual formatting mode
                content_to_write = formatted_content
                try:
                    # Open with newline='' to write newlines as they are in content
                    with file_path.open(mode="w", encoding="utf-8", newline="") as f:
                        f.write(content_to_write)
                    print(f"Reformatted {file_path}")
                except (OSError, PermissionError) as e:
                    print(f"Error writing file {file_path}: {e}", file=sys.stderr)
                    error_occurred_for_file = True  # Mark error for this file
                # pylint: disable-next=broad-exception-caught
                except Exception as e:  # Catch any other write errors
                    print(
                        f"Unexpected error writing file {file_path}: {e}",
                        file=sys.stderr,
                    )
                    error_occurred_for_file = True
        else:
            if args.check or args.dry_run or not args.check:
                print(f"File {file_path} is already well-formatted.")

    # pylint: disable-next=broad-exception-caught
    except Exception as e:
        # Catch-all for unexpected errors during this file's processing
        print(
            f"An unexpected internal error occurred while processing {file_path}: {e}",
            file=sys.stderr,
        )
        error_occurred_for_file = True  # Mark error for this file
        # In --check mode, this implies it needs formatting or couldn't be verified
        needs_formatting_for_file = True

    return needs_formatting_for_file, error_occurred_for_file


def main() -> None:
    """
    Main command-line interface function for the Gherkin Formatter.
    """
    parser = argparse.ArgumentParser(
        description="A command-line tool to format Gherkin .feature files.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "files_or_dirs",
        nargs="+",
        metavar="FILES_OR_DIRECTORIES",
        help="One or more .feature files or directories to format.",
    )
    parser.add_argument(
        "--tab-width",
        type=int,
        default=2,
        help="Number of spaces for indentation (default: 2).",
    )
    parser.add_argument(
        "--use-tabs",
        action="store_true",
        help="Use tabs for indentation. Overrides --tab-width.",
    )
    parser.add_argument(
        "-a",
        "--alignment",
        choices=["left", "right"],
        default="left",
        help="Alignment for table cells (default: left).",
    )
    parser.add_argument(
        "--multi-line-tags",
        action="store_true",
        help="Format tags over multiple lines (default: single-line).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show program's version number and exit.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Preview changes without modifying files. Formatted output (if\n"
            "different) will be printed to the console."
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Check if files are formatted. Exits 0 if formatted, 1 if needs\n"
            "formatting, 123 on error."
        ),
    )

    args: argparse.Namespace = parser.parse_args()
    overall_internal_error_occurred = False
    total_needs_formatting_count = 0

    try:
        feature_files_to_process: list[Path] = _discover_feature_files(
            args.files_or_dirs
        )

        if not feature_files_to_process:
            print("No .feature files found to process.")
            sys.exit(0)

        for file_path in feature_files_to_process:
            needs_formatting, file_error = _process_single_file(file_path, args)
            if needs_formatting:  # This is mainly for --check mode logic
                total_needs_formatting_count += 1
            if file_error:  # If any file processing had an error, mark overall error
                overall_internal_error_occurred = True

        if args.check:
            if overall_internal_error_occurred:
                # If any file had an error (parsing, reading, writing, unexpected)
                print(
                    "\nProcessing completed with file-specific or internal errors.",
                    file=sys.stderr,
                )
                sys.exit(123)  # Prioritize internal error code
            elif total_needs_formatting_count > 0:
                print(
                    f"\nFound {total_needs_formatting_count} file(s) that need"
                    " formatting.",
                    file=sys.stderr,
                )
                sys.exit(1)
            else:
                print("\nAll checked files are well-formatted.")
                sys.exit(0)
        else:  # For format or dry-run modes
            if overall_internal_error_occurred:
                print(
                    "\nProcessing completed with file-specific or internal errors.",
                    file=sys.stderr,
                )
                sys.exit(123)
            sys.exit(0)

    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"A critical unhandled error occurred: {e}", file=sys.stderr)
        sys.exit(123)


if __name__ == "__main__":
    main()
