import hashlib

from models.entity import Entity


class User(Entity):
    """
    Represents a LinkedOn user and their professional profile. Pillar Used: Inheritance
    """

    def __init__(self, user_id, email, password_hash, name="", age=None, location="", bio="", skills=None):
        # Constructor method used to initialize User objects
        # Pillar Used: Encapsulation (storing data inside the object)

#========================================DIVIDER========================================
        
        self.__user_id = user_id
        self.__email = email
        self.__password_hash = password_hash
        # Pillar Used: Encapsulation (double underscore makes it private)
        # Private attribute for user ID
        # Private email attribute
        # Stores encrypted password instead of plain text

#========================================DIVIDER========================================
        
        # Profile fields (semi-public, editable through the app)
        self._name = name # Protected attribute for user's name
        self._age = age  # Protected age attribute
        self._location = location # Protected location attribute
        self._bio = bio  # Protected bio attribute
        self._skills = skills if skills is not None else []  
        # Stores user skills
        # Uses list initialization to avoid shared mutable lists
        self._experiences = [] # List to store work experiences
        self._educations = []  # List to store educational background

        # Pillar Used: Abstraction
        self._post_ids = []   
        # stores only IDs; Post objects live in the app
        # Helps separate responsibilities between classes
        

    # Password Utilities 
    @staticmethod
    def hash_password(password):
        """One-way SHA-256 hash. Passwords are never stored in plain text."""
        # Pillar Used: Abstraction
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password):
        # Checks if entered password matches stored password hash
        # Pillar Used: Abstraction
        return self.__password_hash == User.hash_password(password)

    def change_password(self, new_password):
        # Updates password hash with a newly encrypted password
        # Pillar Used: Encapsulation
        """Overwrite the stored password hash with a new one."""
        self.__password_hash = User.hash_password(new_password)

    # =========================================================================
    # Getters 
    # =========================================================================


    # Provides controlled access to private/protected attributes
    
    @property
    def user_id(self):
        # Pillar Used: Encapsulation
        return self.__user_id

    @property
    def email(self):
        # Pillar Used: Encapsulation
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
        # Pillar Used: Encapsulation
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

    # Experience Methods 

    def add_experience(self, exp):
        # Adds a work experience object into the experiences list
        # Pillar Used: Abstraction
        self._experiences.append(exp)

    def remove_experience(self, index):
        # Removes an experience using its index position
        del self._experiences[index]

    # Eduction Methods

    def add_education(self, edu):
        # Adds an education object into the educations list
        self._educations.append(edu)

    def remove_education(self, index):
        # Removes education entry using index
        del self._educations[index]

    # Skill Methods 

    def add_skill(self, skill):
        # Adds a skill only if it does not already exist
        # Prevents duplicate entries
        if skill not in self._skills:
            self._skills.append(skill)

    def remove_skill(self, skill):
        # Removes a skill if found in the list
        if skill in self._skills:
            self._skills.remove(skill)

    # Post ID Methods 

    def add_post_id(self, post_id):
        # Adds a post ID into the user's posts list
        self._post_ids.append(post_id)

    def remove_post_id(self, post_id):
        # Removes a post ID if it exists
        if post_id in self._post_ids:
            self._post_ids.remove(post_id)

    # =========================================================================
    # Display & Serialization
    # =========================================================================
    
    def display(self):
        W = 52
        # Width
        
        print("  " + "═" * W)
        # Prints Top Border
        
        name_display = self._name if self._name else "(No name set)"
        # Uses fallback text if no name is provided
        
        print(f"  👤  {name_display}")
        # Displays User's Name
        
        if self._bio:
            print(f"  {self._bio}")
        print()
        if self._age:
            # Displays age only if value exists
            print(f"  Age       : {self._age}")
            
        if self._location:
            # Displays location only if available
            print(f"  📍 Location : {self._location}")
        print(f"  📧 Email    : {self.__email}")
        

        if self._skills:
            # Displays skills section if skills exist
            print()
            print(f"  🛠  Skills  : {', '.join(self._skills)}")

        if self._experiences:
            # Displays work experience records
            print()
            print("  Work Experience:")
            for exp in self._experiences:
                # Iterates through each experience object
                # Pillar Used: Polymorphism
                # exp.display() may behave differently depending on object type
                exp.display()

        if self._educations:
            # Displays education records
            print()
            print("  Education:")
            for edu in self._educations:
                # Iterates through education objects
                # Pillar Used: Polymorphism
                edu.display()

        print("  " + "═" * W)
        # Prints bottom border line

    def to_dict(self):
        # Converts object data into dictionary format. 
        # Useful for saving JSON or database records.
        # Pillar Used: Abstraction
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
            # Converts all experience objects into dictionaries
            # Pillar Used: Polymorphism
            
            "educations": [e.to_dict() for e in self._educations],
            # Converts education objects into dictionaries
            # Pillar Used: Polymorphism

            "post_ids": self._post_ids,
        }

    @classmethod
    def from_dict(cls, data):

        # Creates a User object from dictionary data.
        # Class method because it returns a class instance.
        # Pillar Used: Abstraction
        
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
        # Restores saved post IDs
        return user
        # Returns reconstructed User object
