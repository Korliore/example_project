import pprint
import typing
from sqlalchemy import null, update, select, func, text
from rsouvenir_crm.db.abstract_repository import AbstractRepository
from rsouvenir_crm.db.dependencies import get_db_session
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import load_only
from rsouvenir_crm.db.models import crm
from starlette.requests import Request
from sqlalchemy.orm import joinedload

class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, request: Request):
        self.request = request

    async def edit_many(self, 
                        ids: list, 
                        data,):
        async with self.session as s:
            stmt = update(self.model).where(
                self.model.id.in_(ids)).values(**data)
            await s.execute(stmt)

    async def find_one(self, filter_by: dict, order_by=None, fields=None):
        async for session in get_db_session(self.request):
            query = select(self.model).filter_by(**filter_by)

            if order_by:
                query = query.order_by(order_by)

            if fields:
                # Преобразуем имена полей в соответствующие атрибуты модели
                field_attributes = [getattr(self.model, field) for field in fields]
                # Если указан список полей, используем метод load_only для выбора только этих полей
                query = query.options(load_only(*field_attributes))
            res = await session.execute(query)
            result = res.scalars().first()

        return result

    async def find_all(self, filter_by: dict, order_by=None, offset=0, limit=50, fields=None):
        async for session in get_db_session(self.request):
            query = select(self.model).filter_by(**filter_by)

            if order_by == "id":
                query = query.order_by(self.model.id)

            if offset or limit:
                query = query.offset(offset).limit(limit)

            if fields:
                # Преобразуем имена полей в соответствующие атрибуты модели
                field_attributes = [getattr(self.model, field) for field in fields]
                # Используем атрибуты модели в методе load_only
                query = query.options(load_only(*field_attributes))

            res = await session.execute(query)
            results = res.scalars().all()

            return results

    async def edit_one(self, id_: int, data):
        async for session in get_db_session(self.request):
            stmt = update(self.model).where(
                self.model.id == id_).values(**data).returning(self.model)
            res = await session.execute(stmt)
            results = res.scalars().first()

            return results

    async def insert_one(self, data):
        async for session in get_db_session(self.request):
            stmt = insert(self.model).returning(self.model).on_conflict_do_nothing()
            result = await session.execute(stmt, data)
            return result.scalars().first()

    async def insert_many(self, data):
        async with self.session as s:
            ids = await s.execute(insert(self.model).on_conflict_do_nothing().returning(self.model),
                                  data)
            return ids.scalars().all()

    async def execute_query(self, query: str):
        async with self.session as s:
            sql = text(query)
            await s.execute(sql)

class ContractorRepository(SQLAlchemyRepository):
    model = crm.Contractor

    async def find_one(self, filter_by: dict, order_by=None, fields=None):
        async for session in get_db_session(self.request):
            query = select(self.model).filter_by(**filter_by).outerjoin(crm.Location).options(joinedload(self.model.locations))

            if order_by:
                query = query.order_by(order_by)

            if fields:
                # Преобразуем имена полей в соответствующие атрибуты модели
                field_attributes = [getattr(self.model, field) for field in fields]
                # Если указан список полей, используем метод load_only для выбора только этих полей
                query = query.options(load_only(*field_attributes))
            res = await session.execute(query)
            result = res.scalars().first()

        return result

    async def find_all(self, filter_by: dict, sort_by: str, order_by=None, offset=0, limit=50, fields=None):
        async for session in get_db_session(self.request):
            # Создаем запрос к таблице контрагентов
            query = select(self.model).outerjoin(crm.Location).options(joinedload(self.model.locations))
            
            # Если нужна сортировка по имени или дате создания
            if sort_by in ["name", "created_date"]:
                # Создаем базовый запрос
                query = select(self.model)
                
                # Сортируем по имени
                if sort_by == "name":
                    query = query.order_by(self.model.name)
                # Сортируем по дате создания
                elif sort_by == "created_date":
                    query = query.order_by(self.model.created_date)
                
                # Если нужно дополнительно сортировать по id
                if order_by == "id":
                    query = query.order_by(self.model.id)
                    
            # Если заданы offset и/или limit
            if offset or limit:
                query = query.offset(offset).limit(limit)
            
            # Если заданы поля, которые нужно вернуть
            if fields:
                # Преобразуем имена полей в соответствующие атрибуты модели
                field_attributes = [getattr(self.model, field) for field in fields]
                # Используем атрибуты модели в методе load_only
                query = query.options(load_only(*field_attributes))
            
            # Выполняем запрос
            res = await session.execute(query)
            results = res.unique().scalars().all()

        return results


class LocationRepository(SQLAlchemyRepository):
    model = crm.Location

class BuyersOrderRepository(SQLAlchemyRepository):
    model = crm.BuyersOrder

    async def find_one(self, filter_by: dict, order_by=None, fields=None):
        async for session in get_db_session(self.request):
            query = select(self.model).filter_by(**filter_by)

            if order_by:
                query = query.order_by(order_by)

            if fields:
                field_attributes = [getattr(self.model, field) for field in fields]
                query = query.options(load_only(*field_attributes))
                
            query = query.join(crm.BuyerOrderStatus, self.model.status_id == crm.BuyerOrderStatus.id)
            
            res = await session.execute(query)
            result = res.scalars().first()

        return result

    async def find_all(self, filter_by: dict, order_by="id", offset=0, limit=50, fields=None):
        async for session in get_db_session(self.request):
            query = select(self.model).filter_by(**filter_by)

            if order_by == "id":
                query = query.order_by(self.model.id)

            if offset or limit:
                query = query.offset(offset).limit(limit)

            if fields:
                # Преобразуем имена полей в соответствующие атрибуты модели
                field_attributes = [getattr(self.model, field) for field in fields]
                # Используем атрибуты модели в методе load_only
                query = query.options(load_only(*field_attributes))

            # Загружаем данные из связанной таблицы
            query = query.options(joinedload(self.model.status))

            res = await session.execute(query)
            results = res.scalars().all()

            return results


            

class LocationRepository(SQLAlchemyRepository):
    model = crm.Location

    async def find_all(self, filter_by: dict, order_by=None, offset=0, limit=50, fields=None, filter_only_null = False):
        async for session in get_db_session(self.request):
            if filter_only_null:
                query = select(self.model)
                query = query.filter(self.model.contractor_id == None)
                res = await session.execute(query)
                results = res.scalars().all()
                return results
            query = select(self.model).filter_by(**filter_by)

            if filter_only_null:
                query = query.filter(self.model.contractor_id == None)
                print(query)
                res = await session.execute(query)
                results = res.scalars().all()
                return results

            if order_by == "id":
                query = query.order_by(self.model.id)

            if offset or limit:
                query = query.offset(offset).limit(limit)

            if fields:
                # Преобразуем имена полей в соответствующие атрибуты модели
                field_attributes = [getattr(self.model, field) for field in fields]
                # Используем атрибуты модели в методе load_only
                query = query.options(load_only(*field_attributes))

            res = await session.execute(query)
            results = res.scalars().all()

            return results

class BrandingTypesRepository(SQLAlchemyRepository):
    model = crm.BrandingType

    async def find_all(self, order_by=None, offset=0, limit=1000, fields=None):
        async for session in get_db_session(self.request):
            query = select(self.model)

            if order_by == "id":
                query = query.order_by(self.model.id)

            if offset or limit:
                query = query.offset(offset).limit(limit)

            if fields:
                # Преобразуем имена полей в соответствующие атрибуты модели
                field_attributes = [getattr(self.model, field) for field in fields]
                # Используем атрибуты модели в методе load_only
                query = query.options(load_only(*field_attributes))

            res = await session.execute(query)
            results = res.scalars().all()

            return results
        

class SupplierOrderRepository(SQLAlchemyRepository):
    model = crm.SuppliersOrder

    async def find_one(self, filter_by: dict, order_by=None, fields=None):
        async for session in get_db_session(self.request):
            query = select(self.model).filter_by(**filter_by)

            if order_by:
                query = query.order_by(order_by)

            if fields:
                field_attributes = [getattr(self.model, field) for field in fields]
                query = query.options(load_only(*field_attributes))
            res = await session.execute(query)
            result = res.scalars().first()

        return result

    async def find_all(self, filter_by: dict, order_by="id", offset=0, limit=50, fields=None):
        async for session in get_db_session(self.request):
            query = select(self.model).filter_by(**filter_by)

            if order_by == "id":
                query = query.order_by(self.model.id)

            if offset or limit:
                query = query.offset(offset).limit(limit)

            if fields:
                # Преобразуем имена полей в соответствующие атрибуты модели
                field_attributes = [getattr(self.model, field) for field in fields]
                # Используем атрибуты модели в методе load_only
                query = query.options(load_only(*field_attributes))
            res = await session.execute(query)
            results = res.scalars().all()

            return results


class BuyerOrderStatusesRepository(SQLAlchemyRepository):
    model = crm.BuyerOrderStatus

    async def find_all(self, order_by=None, offset=0, limit=50, fields=None):
        async for session in get_db_session(self.request):
            query = select(self.model)

            if order_by == "id":
                query = query.order_by(self.model.id)

            if offset or limit:
                query = query.offset(offset).limit(limit)

            if fields:
                # Преобразуем имена полей в соответствующие атрибуты модели
                field_attributes = [getattr(self.model, field) for field in fields]
                # Используем атрибуты модели в методе load_only
                query = query.options(load_only(*field_attributes))

            res = await session.execute(query)
            results = res.scalars().all()

            return results
        

class ProductStatusesRepository(SQLAlchemyRepository):
    model = crm.ProductStatus

    async def find_all(self, order_by=None, offset=0, limit=50, fields=None):
        async for session in get_db_session(self.request):
            query = select(self.model)

            if order_by == "id":
                query = query.order_by(self.model.id)

            if offset or limit:
                query = query.offset(offset).limit(limit)

            if fields:
                # Преобразуем имена полей в соответствующие атрибуты модели
                field_attributes = [getattr(self.model, field) for field in fields]
                # Используем атрибуты модели в методе load_only
                query = query.options(load_only(*field_attributes))

            res = await session.execute(query)
            results = res.scalars().all()

            return results