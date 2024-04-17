from fastapi import APIRouter, Body, Request, Path, HTTPException, Depends
from rsouvenir_crm.db.repo import ContractorRepository
from rsouvenir_crm.db.models.schemas import crm
from rsouvenir_crm.services.utils.clear_dict import clear_data
from pydantic import BaseModel, UUID4
router = APIRouter(prefix="/contractor", 
                   tags=["contractor"])


@router.post("/add")
async def add_contractor(request: Request, insert_params: crm.ContractorCreate = Body(...)) -> None:
    """Добавить контрагента"""
    insert_params_clear = await clear_data(dict_=insert_params.dict())
    all_data = await ContractorRepository(request).insert_one(data=insert_params_clear)  # Передача request в репозиторий
    return all_data

@router.get("/get/{id}")
async def get_contractor(request: Request, id: int = Path(...)):
    """Получить контрагента по айди"""
    all_data = await ContractorRepository(request).find_one({"id": id})
    if all_data:
        return all_data
    raise HTTPException(status_code=400, detail=f"Contractor with id {id} not found")

@router.get("/get_filter")
async def get_all_contractor(request: Request, filter_by: crm.ContractorFilter = Depends(), 
                             sort_by: str = None, offset: int = 0, limit: int = 50):
    """Получить всех контрагентов"""
    if limit > 1000:
        raise HTTPException(status_code=400, detail=f"Max limit = 1000")
    filter_by = await clear_data(dict_=filter_by.dict())
    all_data = await ContractorRepository(request).find_all(filter_by = filter_by, offset=offset, limit=limit, sort_by=sort_by)
    if all_data:
        return all_data
    raise HTTPException(status_code=400, detail=f"Contractor not found")

@router.put("/update/{id}")
async def update_contractor(request: Request, update_params: crm.ContractorUpdate = Body(), id: int = Path(...)):
    """Обновить данные о контрагенте"""
    update_params_clear = await clear_data(dict_=update_params.dict())
    contractor = await ContractorRepository(request).edit_one(id_=id, data=update_params_clear)
    return contractor
 
 