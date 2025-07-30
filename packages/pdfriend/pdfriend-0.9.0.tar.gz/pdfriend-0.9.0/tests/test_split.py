from pdfriend.main import run_pdfriend
from helpers.flags import make_args
from helpers.managers import FileManager
from helpers.model_documents import ModelPDF
from pathlib import Path


def test_split():
    fm = FileManager.New()

    pages_0 = list(range(40))
    splits = [0, 10, 20, 30, 40]
    path_0, out_dir = Path("model_0.pdf"), Path("model_out")
    fm.new_pdf(path_0, pages_0)
    out_dir.mkdir(parents = True, exist_ok = True)
    fm.register(out_dir)

    out_paths, out_models = [], []
    for i, (lower, upper) in enumerate(zip(
        splits[:-2], splits[1:-1]
    )):
        if lower < 1:
            lower = 1

        path = out_dir.joinpath(f"model_0-{i}.pdf")
        out_paths.append(path)
        out_models.append(ModelPDF(list(range(lower - 1, upper - 1))))
        fm.register(path)

    run_pdfriend(make_args(
        ["split", path_0, ",".join([str(split) for split in splits[:-1]])],
        output = out_dir
    ))

    for out_path, out_model in zip(out_paths, out_models):
        assert ModelPDF.Read(out_path) == out_model

    fm.delete_all()


if __name__ == "__main__":
    test_split()
