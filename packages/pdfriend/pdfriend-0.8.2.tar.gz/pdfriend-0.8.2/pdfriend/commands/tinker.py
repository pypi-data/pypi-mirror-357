import pathlib
from enum import Enum
from typing import Iterator
from abc import ABC, abstractmethod

import pdfriend.classes.wrappers as wrappers
import pdfriend.classes.exceptions as exceptions
import pdfriend.classes.cmdparsers as cmdparsers
import pdfriend.classes.shells as shells
import pdfriend.classes.info as info
import pdfriend.utils as utils
from ..classes.platforms import Platform
from ..classes.config import Config


program_info = info.ProgramInfo(
    info.CommandInfo("help", "h", descr = """[command?]
    display help message. If given a command, it will only display the help message for that command.

    examples:
        help list
            displays the help blurb for the list command
        help exit
            displays the help blurb for the exit command
    """),
    info.CommandInfo("exit", "e", descr = """
    exits the edit mode
    """),
    info.CommandInfo("undo", "u", descr = """[number?]
    undo the previous [number] commands.

    examples:
        u
            undoes the previous command
        u 3
            undoes the previous 3 commands
        u all
            undoes all commands issued this session (reverts document fully)
    """),
    info.CommandInfo("export", "x", descr = """[filename?=pdfriend_tinker.txt]
    exports all the commands you ran into a text file

        examples:
            x
                exports your commands to pdfriend_edit.txt
            x out.txt
                exports your commands to out.txt
    """),
    info.CommandInfo("page", "p", descr = """[page]
    focuses on the given page

        examples:
            p 2
                focuses on page 2
    """),
    info.CommandInfo("list", "ls", descr = """[-l]
    lists objects on the current focused page. Use the -l flag to display additional information.

        examples:
            ls
                lists objects on the current page
    """),
    info.CommandInfo("show", "s", descr = """[name]
    opens the selected object as a separate file (currently only works with images)

        examples:
            s image.jpg
                opens the image as if it was a separate file
            s Im4.png
                same as above
    """),
    info.CommandInfo("write", "w", descr = """[name] [filename?=name]
    writes the selected object to the given file (currently only works with images)

        examples:
            w image.jpg
                writes image.jpg to ./image.jpg
            w Im7.png image.png
                writes Im7.png to ./image.png
    """),
    foreword = "pdfriend tinker shell for quick in-page changes. Currently, only image manipulation is supported. Commands:",
    postword = "use h [command] to learn more about a specific command"
)


class DocObjectKind(Enum):
    IMAGE = "image"


class DocObject(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def kind(self) -> DocObjectKind:
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def data(self) -> bytes:
        pass


class ImageDocObject(DocObject):
    def __init__(self, obj):
        self._obj = obj

    def name(self) -> str:
        return self._obj.name

    def kind(self) -> DocObjectKind:
        return DocObjectKind.IMAGE

    def show(self):
        temp_path = Platform.NewTemp(self._obj.name)
        temp_path.write_bytes(self.data())
        Platform.OpenFile(temp_path)

    def data(self) -> bytes:
        return self._obj.data


class TinkerRunner(shells.ShellRunner):
    def __init__(self, pdf: wrappers.PDFWrapper, open_pdf: bool = True, open_page: bool = True):
        backup_path = pdf.backup()
        print(f"editing {pdf.source}\nbackup created in {backup_path}")

        self.pdf = pdf
        self.backup_path = backup_path
        self.open_pdf = open_pdf
        self.open_page = open_page

        self.current_page_num = None
        self.current_page_pdf = None
        self.current_page_path = Platform.NewTemp("current_page.pdf")

        if open_pdf:
            Platform.OpenFile(pdf.source)

    def current_page(self):
        return self.current_page_pdf.pages_get(0)

    def raise_if_no_page(self):
        if self.current_page_pdf is None:
            raise exceptions.ExpectedError(
                "no page selected! Use page [page_number] to select a page."
            )

    def iter_objects(self) -> Iterator[DocObject]:
        iter = self.current_page().images.__iter__()
        while True:
            try:
                yield ImageDocObject(next(iter))
            except Exception as e:
                if Config.Debug:
                    print(f"Failed to list objects: {e}")
                break

    def get_object(self, obj_name: str) -> DocObject:
        for obj in self.iter_objects():
            if obj.name() == obj_name:
                return obj

        raise exceptions.ExpectedError(
            f"No object named {obj_name} in page {self.current_page_num}"
        )

    def write_object(self, obj: DocObject, output_path: pathlib.Path | None = None):
        if output_path is None:
            output_path = Platform.NewTemp(obj.name())

        output_path.write_bytes(obj.data())
        return output_path

    def parse(self, arg_str) -> list[str]:
        return utils.parse_command_string(arg_str)

    def run(self, args: list[str]):
        cmd_parser = cmdparsers.CmdParser.FromArgs(
            program_info,
            args,
            no_command_message = "No command specified! Type h or help for a list of the available commands"
        )
        short = cmd_parser.short()

        if short == "h":
            subcommand = cmd_parser.next_str_or(None)
            print(program_info.help(subcommand))

            # this is to prevent rewriting the file and appending
            # the command to the command stack
            raise exceptions.ShellContinue()
        elif short == "e":
            raise exceptions.ShellExit()
        elif short == "u":
            # arg will be converted to int, unless it's "all". Defaults to 1
            num_of_commands = cmd_parser.next_typed_or(
                "int or \"all\"", lambda s: s if s == "all" else int(s),
                1  # default value
            )

            raise exceptions.ShellUndo(num_of_commands)
        elif short == "x":
            filename = cmd_parser.next_str_or("pdfriend_tinker.txt")

            raise exceptions.ShellExport(filename)
        elif short == "p":
            page_num = cmd_parser.next_int() - 1
            self.pdf.raise_if_out_of_range(page_num)

            if self.current_page_pdf is None:
                current_page_pdf = wrappers.PDFWrapper(pages = [self.pdf.pages_get(page_num)])
                current_page_pdf.write(self.current_page_path)
                self.current_page_pdf = wrappers.PDFWrapper.Read(self.current_page_path)

                if self.open_page:
                    Platform.OpenFile(self.current_page_path)
            else:
                self.current_page_pdf.pages_set(0, self.pdf.pages_get(page_num))

            self.current_page_num = page_num
        elif short == "ls":
            self.raise_if_no_page()
            subcommand = cmd_parser.next_str_or(None, name = "subcommand")
            long = subcommand == "-l"

            for obj in self.iter_objects():
                extra = ""
                if long:
                    extra = f"    {len(obj.data()) / 1000} KB"

                print(f"{obj.name()}{extra}")

            raise exceptions.ShellContinue()
        elif short == "s":
            self.raise_if_no_page()
            obj_name = cmd_parser.next_str("name")

            self.get_object(obj_name).show()

            raise exceptions.ShellContinue()
        elif short == "w":
            self.raise_if_no_page()
            obj_name = cmd_parser.next_str(name = "name")
            filename = cmd_parser.next_str_or(obj_name, name = "filename")

            obj = self.get_object(obj_name)
            self.write_object(obj, pathlib.Path(filename))

            raise exceptions.ShellContinue()

    def reset(self):
        self.pdf.reread(self.backup_path)

    def save(self):
        if self.current_page_pdf is None:
            return
        self.pdf.pages_set(self.current_page_num, self.current_page())
        self.current_page_pdf.write()

    def exit(self):
        self.pdf.write()


def tinker(
    pdf: wrappers.PDFWrapper,
    commands: list[str] | None = None,
    open_pdf: bool = True,
    open_page: bool = True
):
    tinker_shell = shells.Shell(
        runner = TinkerRunner(pdf, open_pdf = open_pdf, open_page = open_page)
    )

    tinker_shell.run(commands)
