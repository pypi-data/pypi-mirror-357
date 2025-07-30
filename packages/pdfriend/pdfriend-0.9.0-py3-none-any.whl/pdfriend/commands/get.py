import pdfriend.classes.wrappers as wrappers
import pdfriend.classes.exceptions as exceptions
import pathlib

from .tinker import DocObjectKind, iter_pdf_page_objects


def get(
    subcommand: str,
    pdf: wrappers.PDFWrapper,
    slice: list[int],
    output: str | pathlib.Path,
):
    output_dir = pathlib.Path(output)
    if not output_dir.exists():
        output_dir.mkdir()

    pdf_stem = pdf.source.stem

    if subcommand == "images":
        for page_num, page in enumerate(pdf.get_pages()):
            if page_num not in slice:
                continue

            for obj in iter_pdf_page_objects(page):
                if obj.kind() != DocObjectKind.IMAGE:
                    continue

                output_dir.joinpath(
                    f"{pdf_stem}-{page_num + 1}-{obj.name()}"
                ).write_bytes(obj.data())
    else:
        raise exceptions.ExpectedError(f"Invalid subcommand \"{subcommand}\" to get")
