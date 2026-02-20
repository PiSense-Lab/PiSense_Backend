from typing import Generator

class Project():

    def __init__(self, name: str, owner: "User"):
        ...

    def __str__(self):
        ...

    @property
    def users(self) -> Generator["User"]:
        """Generator of users that can access this project"""
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
    def users(self) -> Generator["User"]:
        """
        Returns a generator of users that are a part of this group
        
        :return: Generator of users that are a part of this group
        :rtype: Generator[User, None, None]
        """
        ...

    @property
    def projects(self) -> Generator["Project"]:
        """
        Returns a generator of projects owned by this object
        
        :return: Generator of projects owned by this object
        :rtype: Generator[Project, None, None]
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
    def projects(self) -> Generator["Project"]:
        """
        Returns a generator of projects owned by this object
        
        :return: Generator of projects owned by this object
        :rtype: Generator[Project, None, None]
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
