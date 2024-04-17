from fastapi import APIRouter, Body, Request, Path, HTTPException, Depends
from rsouvenir_crm.db.repo import BrandingTypesRepository
from rsouvenir_crm.db.models.schemas import crm
from rsouvenir_crm.services.utils.clear_dict import clear_data
from pydantic import BaseModel, UUID4
router = APIRouter(prefix="/branding_types", 
                   tags=["branding_types"])

@router.post("/add")
async def add_branding(request: Request, insert_params: crm.PaintType = Body(...)) -> None:
    """Добавить вид нанесения"""
    insert_params_clear = await clear_data(dict_=insert_params.dict())
    all_data = await BrandingTypesRepository(request).insert_one(data=insert_params_clear)  # Передача request в репозиторий
    return all_data


@router.get("/get/{id}")
async def get_branding(request: Request, id: int = Path(...)):
    """Получить вид нанесения по иду"""
    all_data = await BrandingTypesRepository(request).find_one({"id": id})
    if all_data:
        return all_data
    raise HTTPException(status_code=400, detail=f"Branding with id {id} not found")

@router.get("/get_all")
async def get_all_branding(request: Request):
    """Получить все виды нанесения"""
    all_data = await BrandingTypesRepository(request).find_all()
    if all_data:
        return all_data
    raise HTTPException(status_code=400, detail=f"Branding not found")

@router.put("/update/{id}")
async def update_branding(request: Request, update_params: crm.PaintType = Body(...), id: int = Path(...)):
    """Обновить данные о виде нанесения"""
    update_params_clear = await clear_data(dict_=update_params.dict())
    all_data = await BrandingTypesRepository(request).edit_one(id_=id, data=update_params_clear)
    return all_data