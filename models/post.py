from abc import abstractmethod
from datetime import datetime

from models.entity import Entity


class Post(Entity):
    """
    Abstract base class for all post types.
    """

    def __init__(self, post_id, author_id, author_name, content, timestamp=None):
        self.__post_id = post_id
        self.__author_id = author_id
        self.__author_name = author_name
        self.__content = content
        self.__timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M")

    # =========================================================================
    # Getters
    # =========================================================================

    @property
    def post_id(self):
        return self.__post_id

    @property
    def author_id(self):
        return self.__author_id

    @property
    def author_name(self):
        return self.__author_name

    @property
    def content(self):
        return self.__content

    @property
    def timestamp(self):
        return self.__timestamp

    @content.setter
    def content(self, value):
        self.__content = value

    # =========================================================================
    # Display & Serialization
    # =========================================================================

    @abstractmethod
    def display(self):
        pass

    def to_dict(self):
        return {
            "post_id": self.__post_id,
            "author_id": self.__author_id,
            "author_name": self.__author_name,
            "content": self.__content,
            "timestamp": self.__timestamp,
        }

    @classmethod
    # Polymorph to the correct subclass based on type
    def from_dict(cls, data):
        post_type = data.get("type", "text")
        if post_type == "job":
            return JobPost.from_dict(data)
        elif post_type == "achievement":
            return AchievementPost.from_dict(data)
        else:
            return TextPost.from_dict(data)


class TextPost(Post):
    """
    A plain text status update. Inherits from Post.
    """

    def display(self):
        print(f"  ✏️   {self.author_name}  ·  {self.timestamp}")
        print(f"  {self.content}")

    def to_dict(self):
        d = super().to_dict()
        d["type"] = "text"
        return d

    @classmethod
    def from_dict(cls, data):
        return cls(
            post_id=data["post_id"],
            author_id=data["author_id"],
            author_name=data["author_name"],
            content=data["content"],
            timestamp=data.get("timestamp"),
        )


class JobPost(Post):
    """
    A job listing post. Inherits from Post and adds job-specific fields.
    """

    def __init__(self, post_id, author_id, author_name, content, job_title, company, job_type, timestamp=None):
        super().__init__(post_id, author_id, author_name, content, timestamp)
        self.__job_title = job_title
        self.__company = company
        self.__job_type = job_type

    # =========================================================================
    # Getters
    # =========================================================================

    @property
    def job_title(self):
        return self.__job_title

    @property
    def company(self):
        return self.__company

    # =========================================================================
    # Display & Serialization
    # =========================================================================

    def display(self):
        print(f"  📋  [JOB POSTING]  {self.author_name}  ·  {self.timestamp}")
        print(f"  Position : {self.__job_title}")
        print(f"  Company  : {self.__company}  ({self.__job_type})")
        print(f"  {self.content}")

    def to_dict(self):
        d = super().to_dict()
        d["type"] = "job"
        d["job_title"] = self.__job_title
        d["company"] = self.__company
        d["job_type"] = self.__job_type
        return d

    @classmethod
    def from_dict(cls, data):
        return cls(
            post_id=data["post_id"],
            author_id=data["author_id"],
            author_name=data["author_name"],
            content=data["content"],
            job_title=data["job_title"],
            company=data["company"],
            job_type=data["job_type"],
            timestamp=data.get("timestamp"),
        )


class AchievementPost(Post):
    """
    A milestone or award post. Inherits from Post and adds an achievement title.
    """

    def __init__(self, post_id, author_id, author_name, content, achievement_title, timestamp=None):
        super().__init__(post_id, author_id, author_name, content, timestamp)
        self.__achievement_title = achievement_title

    # =========================================================================
    # Getters
    # =========================================================================

    @property
    def achievement_title(self):
        return self.__achievement_title

    # =========================================================================
    # Display & Serialization
    # =========================================================================

    def display(self):
        print(f"  🏆  [ACHIEVEMENT]  {self.author_name}  ·  {self.timestamp}")
        print(f"  {self.__achievement_title}")
        print(f"  {self.content}")

    def to_dict(self):
        d = super().to_dict()
        d["type"] = "achievement"
        d["achievement_title"] = self.__achievement_title
        return d

    @classmethod
    def from_dict(cls, data):
        return cls(
            post_id=data["post_id"],
            author_id=data["author_id"],
            author_name=data["author_name"],
            content=data["content"],
            achievement_title=data["achievement_title"],
            timestamp=data.get("timestamp"),
        )
