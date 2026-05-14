class Connection:
    """
    Represents a connection relationship between two users.
    """

    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"

    def __init__(self, sender_id, receiver_id, status=None):
        self.__sender_id = sender_id
        self.__receiver_id = receiver_id
        self.__status = status or self.PENDING

    # =========================================================================
    # Getters
    # =========================================================================

    @property
    def sender_id(self):
        return self.__sender_id

    @property
    def receiver_id(self):
        return self.__receiver_id

    @property
    def status(self):
        return self.__status

    # =========================================================================
    # Actions
    # =========================================================================

    def accept(self):
        self.__status = self.ACCEPTED

    def decline(self):
        self.__status = self.DECLINED

    # Check if a given user is part of this connection
    def involves(self, user_id):
        return self.__sender_id == user_id or self.__receiver_id == user_id

    # Given one user's ID, return the other participant's ID.
    def get_other(self, user_id):
        if self.__sender_id == user_id:
            return self.__receiver_id
        return self.__sender_id

    # =========================================================================
    # Serialization
    # =========================================================================

    def to_dict(self):
        return {
            "sender_id": self.__sender_id,
            "receiver_id": self.__receiver_id,
            "status": self.__status,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            sender_id=data["sender_id"],
            receiver_id=data["receiver_id"],
            status=data.get("status", cls.PENDING),
        )
