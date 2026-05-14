import hashlib

from models.entity import Entity


class User(Entity):
    """
    Represents a LinkedOn user and their professional profile.
    """

    def __init__(self, user_id, email, password_hash, name="", age=None, location="", bio="", skills=None):
        self.__user_id = user_id
        self.__email = email
        self.__password_hash = password_hash

        # Profile fields (semi-public, editable through the app)
        self._name = name
        self._age = age
        self._location = location
        self._bio = bio
        self._skills = skills if skills is not None else []
        self._experiences = []
        self._educations = []
        self._post_ids = []   # stores only IDs; Post objects live in the app

    # Password Utilities ------------------------------------------------------
    @staticmethod
    def hash_password(password):
        """One-way SHA-256 hash. Passwords are never stored in plain text."""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password):
        return self.__password_hash == User.hash_password(password)

    def change_password(self, new_password):
        """Overwrite the stored password hash with a new one."""
        self.__password_hash = User.hash_password(new_password)

    # =========================================================================
    # Getters
    # =========================================================================

    @property
    def user_id(self):
        return self.__user_id

    @property
    def email(self):
        return self.__email

    @property
    def name(self):
        return self._name

    @property
    def age(self):
        return self._age

    @property
    def location(self):
        return self._location

    @property
    def bio(self):
        return self._bio

    @property
    def skills(self):
        return self._skills

    @property
    def experiences(self):
        return self._experiences

    @property
    def educations(self):
        return self._educations

    @property
    def post_ids(self):
        return self._post_ids

    # =========================================================================
    # Setters
    # =========================================================================

    @email.setter
    def email(self, value):
        self.__email = value

    @name.setter
    def name(self, value):
        self._name = value

    @age.setter
    def age(self, value):
        self._age = value

    @location.setter
    def location(self, value):
        self._location = value

    @bio.setter
    def bio(self, value):
        self._bio = value

    # Experience Methods ------------------------------------------------------
    def add_experience(self, exp):
        self._experiences.append(exp)

    def remove_experience(self, index):
        del self._experiences[index]

    # Eduction Methods --------------------------------------------------------
    def add_education(self, edu):
        self._educations.append(edu)

    def remove_education(self, index):
        del self._educations[index]

    # Skill Methods -----------------------------------------------------------
    def add_skill(self, skill):
        if skill not in self._skills:
            self._skills.append(skill)

    def remove_skill(self, skill):
        if skill in self._skills:
            self._skills.remove(skill)

    # Post ID Methods ---------------------------------------------------------
    def add_post_id(self, post_id):
        self._post_ids.append(post_id)

    def remove_post_id(self, post_id):
        if post_id in self._post_ids:
            self._post_ids.remove(post_id)

    # =========================================================================
    # Display & Serialization
    # =========================================================================
    
    def display(self):
        W = 52
        print("  " + "═" * W)
        name_display = self._name if self._name else "(No name set)"
        print(f"  👤  {name_display}")
        if self._bio:
            print(f"  {self._bio}")
        print()
        if self._age:
            print(f"  Age       : {self._age}")
        if self._location:
            print(f"  📍 Location : {self._location}")
        print(f"  📧 Email    : {self.__email}")

        if self._skills:
            print()
            print(f"  🛠  Skills  : {', '.join(self._skills)}")

        if self._experiences:
            print()
            print("  Work Experience:")
            for exp in self._experiences:
                exp.display()

        if self._educations:
            print()
            print("  Education:")
            for edu in self._educations:
                edu.display()

        print("  " + "═" * W)

    def to_dict(self):
        return {
            "user_id": self.__user_id,
            "email": self.__email,
            "password_hash": self.__password_hash,
            "name": self._name,
            "age": self._age,
            "location": self._location,
            "bio": self._bio,
            "skills": self._skills,
            "experiences": [e.to_dict() for e in self._experiences],
            "educations": [e.to_dict() for e in self._educations],
            "post_ids": self._post_ids,
        }

    @classmethod
    def from_dict(cls, data):
        user = cls(
            user_id=data["user_id"],
            email=data["email"],
            password_hash=data["password_hash"],
            name=data.get("name", ""),
            age=data.get("age"),
            location=data.get("location", ""),
            bio=data.get("bio", ""),
            skills=data.get("skills", []),
        )
        user._post_ids = data.get("post_ids", [])
        return user
