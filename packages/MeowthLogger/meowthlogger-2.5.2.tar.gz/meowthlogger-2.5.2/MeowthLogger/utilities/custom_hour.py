class Hour:
    """Using for validating hour and preparing previous or next hour of hour"""

    hour: int

    def __init__(self, hour: int) -> None:
        self.validate_hour(hour)
        self.hour = hour

    def __repr__(self) -> str:
        return f"<UtilHour: {self.hour}>"

    def __str__(self) -> str:
        if self.hour <= 9:
            return f"0{self.hour}"
        return f"{self.hour}"

    @property
    def next_hour(self) -> "Hour":
        hour = self.hour + 1
        if hour >= 24:
            return self.__class__(0)
        return self.__class__(hour)

    @property
    def previous_hour(self) -> "Hour":
        hour = self.hour - 1
        if hour <= -1:
            return self.__class__(23)
        return self.__class__(hour)

    @staticmethod
    def validate_hour(hour: int) -> None:
        if hour >= 24 or hour < 0:
            raise ValueError("Hour can be more then 0 and less then 24.")
