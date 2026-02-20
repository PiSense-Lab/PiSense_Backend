
class Project():

    def __init__(self, name: str, owner: "User"):
        ...

    def __str__(self):
        ...

    @property
    def users(self) -> list["User"]:
        """list of users that can access this project"""
        ...

    @property
    def name(self) -> str:
        """
        Returns name of object

        :return: name of object
        :rtype: str
        """
        ...

class Group():

    def __init__(self):
        ...

    def __str__(self):
        ...

    @property
    def users(self) -> list["User"]:
        """
        Returns a list of users that are a part of this group

        :return: list of users that are a part of this group
        :rtype: list[User]
        """
        ...

    @property
    def projects(self) -> list["Project"]:
        """
        Returns a list of projects owned by this object

        :return: list of projects owned by this object
        :rtype: list[Project]
        """
        ...

    @property
    def name(self) -> str:
        """
        Returns name of object

        :return: name of object
        :rtype: str
        """
        ...

class User():

    def __init__(self):
        ...

    def __str__(self):
        ...

    @property
    def projects(self) -> list["Project"]:
        """
        Returns a list of projects owned by this object

        :return: list of projects owned by this object
        :rtype: list[Project]
        """
        ...

    @property
    def name(self) -> str:
        """
        Returns name of object

        :return: name of object
        :rtype: str
        """
        ...
