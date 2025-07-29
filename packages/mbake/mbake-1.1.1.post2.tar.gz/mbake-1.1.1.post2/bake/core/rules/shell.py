"""Shell script formatting rule for Makefile recipes."""

import re

from ...plugins.base import FormatResult, FormatterPlugin


class ShellFormattingRule(FormatterPlugin):
    """Handles proper indentation of shell scripts within recipe lines."""

    def __init__(self) -> None:
        super().__init__("shell_formatting", priority=50)

    def format(self, lines: list[str], config: dict) -> FormatResult:
        """Format shell script indentation within recipes."""
        formatted_lines = []
        changed = False
        errors: list[str] = []
        warnings: list[str] = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if this is a recipe line
            if line.startswith("\t") and line.strip():
                # Look for shell control structures
                stripped = line.lstrip("\t ")

                # Check if this starts a shell control structure
                if self._is_shell_control_start(stripped):
                    # Process the shell block
                    shell_block, block_end = self._extract_shell_block(lines, i)
                    formatted_block = self._format_shell_block(shell_block)

                    if formatted_block != shell_block:
                        changed = True

                    formatted_lines.extend(formatted_block)
                    i = block_end
                else:
                    formatted_lines.append(line)
                    i += 1
            else:
                formatted_lines.append(line)
                i += 1

        return FormatResult(
            lines=formatted_lines, changed=changed, errors=errors, warnings=warnings
        )

    def _is_shell_control_start(self, line: str) -> bool:
        """Check if line starts a shell control structure."""
        control_patterns = [
            r"^if\s+\[",
            r"^for\s+\w+\s+in\s+",
            r"^while\s+",
            r"^case\s+",
            r"^{\s*$",
        ]

        return any(re.match(pattern, line) for pattern in control_patterns)

    def _extract_shell_block(
        self, lines: list[str], start_idx: int
    ) -> tuple[list[str], int]:
        """Extract a shell control block from lines."""
        block = []
        i = start_idx

        while i < len(lines):
            line = lines[i]
            block.append(line)

            # If line doesn't end with continuation, this might be the end
            if not line.rstrip().endswith("\\"):
                i += 1
                break

            # Check for control structure end markers
            stripped = line.lstrip("\t ")
            if any(
                stripped.strip().startswith(end) for end in ["fi", "done", "esac", "}"]
            ):
                i += 1
                break

            i += 1

        return block, i

    def _format_shell_block(self, block: list[str]) -> list[str]:
        """Format a shell control block with proper indentation."""
        if not block:
            return block

        formatted = []
        indent_level = 0

        for line in block:
            if not line.strip():
                formatted.append(line)
                continue

            # Preserve the original line ending (including any trailing spaces)
            line_content = line.rstrip("\n\r")
            stripped = line_content.lstrip("\t ")

            # Check for trailing spaces/content after the main command
            trailing = ""
            if line_content.endswith(" "):
                # Count trailing spaces
                trailing_spaces = len(line_content) - len(line_content.rstrip(" "))
                trailing = " " * trailing_spaces
                stripped = stripped.rstrip(" ")

            # Adjust indent level for closing keywords
            if any(
                stripped.strip().startswith(end)
                for end in ["else", "elif", "fi", "done", "esac", "}"]
            ):
                indent_level = max(0, indent_level - 1)

            # Calculate proper indentation
            if indent_level == 0:
                # Primary recipe level
                new_line = "\t" + stripped + trailing
            else:
                # Nested shell level
                new_line = "\t" + "  " * indent_level + stripped + trailing

            formatted.append(new_line)

            # Adjust indent level for opening keywords
            if any(
                stripped.strip().startswith(start)
                for start in ["if", "for", "while", "case", "else", "elif"]
            ) and stripped.rstrip().endswith("\\"):
                indent_level += 1

        return formatted
