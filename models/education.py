class Education:
    """
    Represents a single education entry on a user's profile.
    """

    def __init__(self, school_name, degree, year_started, year_ended=None):
        self.__school_name = school_name
        self.__degree = degree
        self.__year_started = year_started
        self.__year_ended = year_ended

    # =========================================================================
    # Getters
    # =========================================================================

    @property
    def school_name(self):
        return self.__school_name

    @property
    def degree(self):
        return self.__degree

    @property
    def year_started(self):
        return self.__year_started

    @property
    def year_ended(self):
        return self.__year_ended

    # =========================================================================
    # Setters
    # =========================================================================

    @school_name.setter
    def school_name(self, value):
        self.__school_name = value

    @degree.setter
    def degree(self, value):
        self.__degree = value

    @year_started.setter
    def year_started(self, value):
        self.__year_started = value

    @year_ended.setter
    def year_ended(self, value):
        self.__year_ended = value

    # =========================================================================
    # Display & Serialization
    # =========================================================================

    def display(self):
        end = self.__year_ended if self.__year_ended else "Present"
        print(f"     🎓  {self.__degree}")
        print(f"         {self.__school_name}  ({self.__year_started} – {end})")

    def to_dict(self):
        return {
            "school_name": self.__school_name,
            "degree": self.__degree,
            "year_started": self.__year_started,
            "year_ended": self.__year_ended,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            school_name=data["school_name"],
            degree=data["degree"],
            year_started=data["year_started"],
            year_ended=data.get("year_ended"),
        )
