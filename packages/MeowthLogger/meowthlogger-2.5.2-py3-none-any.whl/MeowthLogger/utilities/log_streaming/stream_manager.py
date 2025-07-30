class Stream:
    def setup_logger(self, logger) -> None:  # noqa: ANN001
        self.logger = logger

    def write(self, message: str) -> None:
        raise NotImplementedError
