# I do not use sets or dictionaries here because they're not necessary
# the number of commands is not expected to be large
import re


class CommandInfo:
    def __init__(self, primary_name: str, short_name: str, alt_names: set[str] = None, descr: str = ""):
        self.primary_name = primary_name
        self.short_name = short_name
        self.alt_names = [short_name] + (alt_names or [])
        self.all_names = [primary_name] + self.alt_names
        self.descr = descr

    def help(self) -> str:
        return f"{' | '.join(self.all_names)} {self.descr}"


_whitespace_re = re.compile(r"\s+")


def _indent_line(
    line: str,
    baseline_spaces: int = 4,
    spaces_per_tab: int = 4,
    output_spacing: str = "  "
) -> tuple[str,str]:
    space_match = _whitespace_re.match(line)
    if space_match is None:
        return "", line

    lower, upper = space_match.span(0)
    if lower != 0:
        return "", line
    if upper == len(line):
        return None, line

    indentation = 0
    space_char_num = 0
    for space_char in line[lower:upper]:
        if space_char == "\t":
            indentation += 1
        elif space_char == " ":
            space_char_num += 1

    indentation += int((space_char_num - baseline_spaces) / 4)
    if indentation < 0:
        indentation = 0

    return (indentation * output_spacing, line[upper:])


def _split_line(line: str, wrap_len: int) -> list[str]:
    prefix, line = _indent_line(line)
    if prefix is None:  # The line is only spaces
        return []

    result = []
    start, current_max_len = 0, wrap_len
    spaces = list(_whitespace_re.finditer(line))
    if len(spaces) == 0:
        return [prefix + line]

    for lower_space, upper_space in zip(spaces[:-1], spaces[1:]):
        lower_lower, lower_upper = lower_space.span(0)
        upper_lower, upper_upper = upper_space.span(0)

        if upper_upper < current_max_len:
            continue

        if upper_lower < current_max_len:  # The break is inside the space
            result.append(prefix + line[start:upper_lower])
            start = upper_upper
        elif lower_upper < current_max_len:  # The break is inside the word
            result.append(prefix + line[start:lower_lower])
            start = lower_upper
        else:
            continue
        current_max_len = start + wrap_len

    result.append(prefix + line[start:])
    return result


class ProgramInfo:
    def __init__(self, *commands: CommandInfo, foreword: str = "", postword: str = "", wrap_len: int = 80):
        self.foreword = foreword
        self.commands = commands
        self.postword = postword
        self.wrap_len = wrap_len

    def word_wrap(self, text: str) -> str:
        if len(text) <= self.wrap_len:
            return text

        lines = []
        for line in text.split("\n"):
            lines.extend(_split_line(line, self.wrap_len))

        return "\n".join(lines)

    def get_command_info(self, command_name: str) -> CommandInfo | None:
        return next(
            (
                command for command in self.commands
                if command_name in command.all_names
            ),
            None
        )

    def help(self, command_name: str | None) -> str | None:
        if command_name is not None:
            command_info = self.get_command_info(command_name)
            if command_info is None:
                return None

            return self.word_wrap(command_info.help())

        column_names = ["command", "alternatively"]
        spaces = 2
        spacing = " " * spaces

        width = max(
            [len(column_names[0])] + [
                len(command.primary_name) for command in self.commands
            ]
        ) + spaces

        column_heads = f"{column_names[0].rjust(width)}{spacing}{column_names[1]}"
        command_list = "\n".join([
            f"{command.primary_name.rjust(width)}{spacing}{','.join(command.alt_names)}"
            for command in self.commands
        ])

        return "\n".join([
            self.word_wrap(self.foreword),
            column_heads,
            command_list,
            self.word_wrap(self.postword),
        ])
