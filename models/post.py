import uuid
from datetime import datetime

from models.entity import Entity


class Post(Entity):
    """
    Base class for all LinkedOn post types.
    """

    def __init__(self, post_id, author_id, content, post_type, timestamp=None):
        self._post_id = post_id
        self._author_id = author_id
        self._content = content
        self._post_type = post_type
        self._timestamp = timestamp or datetime.now().strftime("%b %d, %Y %I:%M %p")

    # =========================================================================
    # Getters
    # =========================================================================

    @property
    def post_id(self):
        return self._post_id

    @property
    def author_id(self):
        return self._author_id

    @property
    def content(self):
        return self._content

    @property
    def post_type(self):
        return self._post_type

    @property
    def timestamp(self):
        return self._timestamp

    # =========================================================================
    # Display & Serialization
    # =========================================================================

    def display(self):
        print(f"📄  [{self._post_type.upper()} POST]")
        print(f"{self._content}")
        print(f"⏳  {self._timestamp}")

    def to_dict(self):
        return {
            "post_id": self._post_id,
            "author_id": self._author_id,
            "content": self._content,
            "post_type": self._post_type,
            "timestamp": self._timestamp,
        }

    @classmethod
    def from_dict(cls, data):
        """Factory — routes to the correct subclass based on post_type."""
        post_type = data.get("post_type", "text")
        if post_type == "job":
            return JobPost.from_dict(data)
        elif post_type == "achievement":
            return AchievementPost.from_dict(data)
        else:
            return TextPost.from_dict(data)


# =============================================================================
#  Text Post
# =============================================================================

class TextPost(Post):
    """A plain text post — share thoughts, updates, or anything on your mind."""

    def __init__(self, post_id, author_id, content, timestamp=None):
        super().__init__(post_id, author_id, content, "text", timestamp)

    def display(self):
        print(f"TEXT POST")
        print(f"Content: {self._content}")
        print(f"⏳  {self._timestamp}")

    def to_dict(self):
        return super().to_dict()

    @classmethod
    def from_dict(cls, data):
        return cls(
            post_id=data["post_id"],
            author_id=data["author_id"],
            content=data["content"],
            timestamp=data.get("timestamp"),
        )


# =============================================================================
# Job Post
# =============================================================================

class JobPost(Post):
    """A job-related post — advertise an opening or signal you're looking."""

    def __init__(self, post_id, author_id, content, job_title, company, timestamp=None):
        super().__init__(post_id, author_id, content, "job", timestamp)
        self.__job_title = job_title
        self.__company = company

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
        print(f"JOB POST")
        print(f"Job Title: {self.__job_title}")
        print(f"Company: {self.__company}")
        print(f"Content: {self._content}")
        print(f"⏳  {self._timestamp}")

    def to_dict(self):
        d = super().to_dict()
        d["job_title"] = self.__job_title
        d["company"] = self.__company
        return d

    @classmethod
    def from_dict(cls, data):
        return cls(
            post_id=data["post_id"],
            author_id=data["author_id"],
            content=data["content"],
            job_title=data.get("job_title", ""),
            company=data.get("company", ""),
            timestamp=data.get("timestamp"),
        )


# =============================================================================
# Achievement Post
# =============================================================================

class AchievementPost(Post):
    """An achievement post — celebrate a win, certification, or milestone."""

    def __init__(self, post_id, author_id, content, achievement_title, timestamp=None):
        super().__init__(post_id, author_id, content, "achievement", timestamp)
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
        print(f"ACHIEVEMENT")
        print(f"Title: {self.__achievement_title}")
        print(f"Content: {self._content}")
        print(f"⏳  {self._timestamp}")

    def to_dict(self):
        d = super().to_dict()
        d["achievement_title"] = self.__achievement_title
        return d

    @classmethod
    def from_dict(cls, data):
        return cls(
            post_id=data["post_id"],
            author_id=data["author_id"],
            content=data["content"],
            achievement_title=data.get("achievement_title", ""),
            timestamp=data.get("timestamp"),
        )
