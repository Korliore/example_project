import abc


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    async def find_one(self, filter_by: dict, order_by=None):
        raise NotImplementedError

    @abc.abstractmethod
    async def find_all(self, filter_by: dict, order_by=None):
        raise NotImplementedError

    @abc.abstractmethod
    async def edit_many(self, ids: list, data):
        raise NotImplementedError

    @abc.abstractmethod
    async def edit_one(self, id_: int, data):
        raise NotImplementedError

    @abc.abstractmethod
    async def insert_one(self, data):
        raise NotImplementedError

    @abc.abstractmethod
    async def insert_many(self, data):
        raise NotImplementedError