from fastapi import APIRouter, Body, Request, Path, HTTPException, Depends
from rsouvenir_crm.db.models.schemas import crm
from rsouvenir_crm.db.repo import BuyersOrderRepository
from rsouvenir_crm.services.utils.clear_dict import clear_data
from pydantic import BaseModel, UUID4
import datetime


router = APIRouter(prefix="/products", 
                   tags=["products"])

@router.post("/add")
async def add_products(request: Request, insert_params: crm.AddProduct = Body(...)) -> None:
    """Добавить новые продукты"""
    return insert_params
