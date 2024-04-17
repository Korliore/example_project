from fastapi import APIRouter, Body, Request, Path, HTTPException, Depends
from rsouvenir_crm.db.repo import LocationRepository
from rsouvenir_crm.db.models.schemas import crm
from rsouvenir_crm.services.utils.clear_dict import clear_data
from pydantic import BaseModel, UUID4
router = APIRouter(prefix="/locations", 
                   tags=["locations"])


@router.post("/add")
async def add_location(request: Request, insert_params: crm.LocationCreate = Body(...)) -> None:
    """Добавить локацию"""
    insert_params_clear = await clear_data(dict_=insert_params.dict())
    all_data = await LocationRepository(request).insert_one(data=insert_params_clear)  # Передача request в репозиторий
    return all_data

@router.get("/get_filter")
async def get_order(request: Request, filter_by: crm.LocationFilter = Depends(), offset: int = 0, limit: int = 50):
    """Получить все локации"""
    if limit > 1000:
        raise HTTPException(status_code=400, detail=f"Max limit = 1000")
    filter_by = await clear_data(dict_=filter_by.dict())
    if filter_by.get("contractor_id", 0) == -1:
        all_data = await LocationRepository(request).find_all(filter_by = filter_by, offset=offset, limit=limit, filter_only_null=True)
    else:
        all_data = await LocationRepository(request).find_all(filter_by = filter_by, offset=offset, limit=limit)
    if all_data:
        return all_data
    raise HTTPException(status_code=400, detail=f"Locations not found")