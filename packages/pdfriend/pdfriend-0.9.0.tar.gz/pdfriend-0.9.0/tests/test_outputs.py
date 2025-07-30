from helpers.file_existence import check_one_output_command
from helpers.managers import FileManager

fm = FileManager.New()


def test_outputs():
    path = "model.pdf"
    fm.new_pdf(path, range(10))

    check_one_output_command(
        commands = ["invert", path],
        input = path,
    )

    fm.delete_all()
