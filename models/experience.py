class Experience:
    """
    Represents a single work experience entry on a user's profile.
    """

    def __init__(self, company, role, start_date, end_date=None, is_current=False):
        self.__company = company
        self.__role = role
        self.__start_date = start_date
        self.__end_date = end_date
        self.__is_current = is_current

    # =========================================================================
    # Getters
    # =========================================================================

    @property
    def company(self):
        return self.__company

    @property
    def role(self):
        return self.__role

    @property
    def start_date(self):
        return self.__start_date

    @property
    def end_date(self):
        return self.__end_date

    @property
    def is_current(self):
        return self.__is_current

    # =========================================================================
    # Setters
    # =========================================================================

    @company.setter
    def company(self, value):
        self.__company = value

    @role.setter
    def role(self, value):
        self.__role = value

    @start_date.setter
    def start_date(self, value):
        self.__start_date = value

    @end_date.setter
    def end_date(self, value):
        self.__end_date = value

    @is_current.setter
    def is_current(self, value):
        self.__is_current = value

    # =========================================================================
    # Display & Serialization
    # =========================================================================

    def display(self):
        end = "Present" if self.__is_current else (self.__end_date or "N/A")
        print(f"     💼  {self.__role} at {self.__company}")
        print(f"         {self.__start_date} – {end}")

    def to_dict(self):
        return {
            "company": self.__company,
            "role": self.__role,
            "start_date": self.__start_date,
            "end_date": self.__end_date,
            "is_current": self.__is_current,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            company=data["company"],
            role=data["role"],
            start_date=data["start_date"],
            end_date=data.get("end_date"),
            is_current=data.get("is_current", False),
        )
