import logging


logging.basicConfig()


class Config:
    """Global configuration class"""

    Debug = False
    OpenPDFs = True
    Logger = logging.getLogger("pdfriend")

    @classmethod
    def Init(cls, debug: bool):
        cls.Debug = debug

        if cls.Debug:
            cls.Logger.setLevel(logging.DEBUG)
        else:
            cls.Logger.setLevel(logging.WARNING)
