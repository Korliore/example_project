from fastapi import APIRouter, Body, Request, Path, HTTPException, Depends
from rsouvenir_crm.db.repo import BuyerOrderStatusesRepository
from rsouvenir_crm.db.models.schemas import crm
from rsouvenir_crm.services.utils.clear_dict import clear_data
from pydantic import BaseModel, UUID4
router = APIRouter(prefix="/buyer_order_statuses", 
                   tags=["buyer_order_statuses"])


@router.post("/add")
async def add_statuses(request: Request, insert_params: crm.BuyerOrderStatuses = Body(...)) -> None:
    """Добавить статус"""
    insert_params_clear = await clear_data(dict_=insert_params.dict())
    all_data = await BuyerOrderStatusesRepository(request).insert_one(data=insert_params_clear)  # Передача request в репозиторий
    return all_data

@router.get("/get/{id}")
async def get_statuses(request: Request, id: int = Path(...)):
    """Получить статус по айди"""
    all_data = await BuyerOrderStatusesRepository(request).find_one({"id": id})
    if all_data:
        return all_data
    raise HTTPException(status_code=400, detail=f"Statuses with id {id} not found")

@router.get("/get_filter")
async def get_all_statuses(request: Request, sort_by: str = None, offset: int = 0, limit: int = 50):
    """Получение статусов"""
    if limit > 1000:
        raise HTTPException(status_code=400, detail=f"Max limit = 1000")
    all_data = await BuyerOrderStatusesRepository(request).find_all(offset=offset, limit=limit)
    if all_data:
        return all_data
    raise HTTPException(status_code=400, detail=f"Statuses not found")

@router.put("/update/{id}")
async def update_contractor(request: Request, update_params: crm.BuyerOrderStatuses = Body(), id: int = Path(...)):
    """Обновить статус"""
    update_params_clear = await clear_data(dict_=update_params.dict())
    contractor = await BuyerOrderStatusesRepository(request).edit_one(id_=id, data=update_params_clear)
    return contractor
 
 