from pdfriend.main import run_pdfriend
from helpers.flags import make_args
from helpers.managers import FileManager
from helpers.model_documents import ModelPDF
from pathlib import Path
from random import randrange


def test_invert():
    fm = FileManager.New()

    size = 10
    pages = list(range(size))
    picks = list({
        randrange(1, size)
        for _ in range(3)
    })

    path, path_got = Path("model.pdf"), Path("model_got.pdf")
    fm.new_pdf(path, pages)
    fm.register(path_got)

    run_pdfriend(make_args(
        ["get", path, ",".join([str(pick) for pick in picks])],
        outfile = path_got)
    )

    pdf_got = ModelPDF.Read(path_got)

    assert pdf_got == ModelPDF([pick - 1 for pick in picks])

    fm.delete_all()
