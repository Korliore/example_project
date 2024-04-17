from fastapi import APIRouter, Body, Request, Path, HTTPException, Depends
from rsouvenir_crm.db.models.schemas import crm
from rsouvenir_crm.db.repo import SupplierOrderRepository
from rsouvenir_crm.services.utils.clear_dict import clear_data
from pydantic import BaseModel, UUID4
import datetime


router = APIRouter(prefix="/supplier_order", 
                   tags=["supplier_order"])

@router.get("/get/{id}")
async def get_order(request: Request, id: int = Path(...)):
   """Получить заказ поставищка по иду"""
   all_data = await SupplierOrderRepository(request).find_one({"id": id})
   if all_data:
       return all_data
   raise HTTPException(status_code=400, detail=f"Supplier order with id {id} not found")

@router.get("/get_filter")
async def get_order(request: Request, filter_by: crm.SupplierOrderFilter = Depends(), offset: int = 0, limit: int = 50):
    """Получить все заказы поставищка по фильтрам"""
    if limit > 1000:
        raise HTTPException(status_code=400, detail=f"Max limit = 1000")
    filter_by = await clear_data(dict_=filter_by.dict())
    all_data = await SupplierOrderRepository(request).find_all(filter_by = filter_by, offset=offset, limit=limit)
    if all_data:
        return all_data
    raise HTTPException(status_code=400, detail=f"Orders not found")

@router.post("/add")
async def add_order(request: Request, insert_params: crm.SupplierOrderCreate = Body(...)) -> None:
    """Добавить заказ поставищка"""
    insert_params_clear = await clear_data(dict_=insert_params.dict())
    insert_params_clear["create_date"] = datetime.date.today()
    insert_params_clear["shipment_date_planned"] = datetime.datetime.strptime(insert_params_clear["shipment_date_planned"], '%Y-%m-%d')
    # todo add normal owner_id
    insert_params_clear["owner_id"] = 1
    all_data = await SupplierOrderRepository(request).insert_one(data=insert_params_clear)  # Передача request в репозиторий
    return all_data