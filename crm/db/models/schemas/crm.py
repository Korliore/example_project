from pydantic import BaseModel
from typing import Optional, List

# контрагенты

class ContractorCreate(BaseModel):
    name: str
    is_supplier: bool = False
    is_contractor: bool = False
    is_carrier: bool = False
    is_client: bool = False

class ContractorFilter(BaseModel):
    name: Optional[str] = None
    is_supplier: Optional[bool] = None
    is_contractor: Optional[bool] = None
    is_carrier: Optional[bool] = None
    is_client: Optional[bool] = None

class ContractorUpdate(BaseModel):
    name: Optional[str] = None
    is_supplier: Optional[bool] = False
    is_contractor: Optional[bool] = False
    is_carrier: Optional[bool] = False
    is_client: Optional[bool] = False

# заказы покупателей
    
class CustomerOrderFilter(BaseModel):
    create_date: Optional[str] = None
    shipment_date_planned: Optional[str] = None
    shipment_date_fact: Optional[str] = None
    sell_order_id: Optional[int] = None
    delivery_cost_planned: Optional[float] = None
    shipment_cost_planned: Optional[float] = None
    other_expenses_planned: Optional[float] = None
    status_id: Optional[int] = None
    owner_id: Optional[int] = None

class CustomerOrderCreate(BaseModel):
    shipment_date_planned: Optional[str] = None
    sell_order_id: Optional[int] = None
    delivery_cost_planned: Optional[float] = None
    shipment_cost_planned: Optional[float] = None
    other_expenses_planned: Optional[float] = None
    status_id: Optional[int] = None
    client_id: Optional[int] = None
    instructions: Optional[str] = None

# виды нанесения

class PaintType(BaseModel):
    title: str

# продукты

class Product(BaseModel):
    name: str
    discription: Optional[str] = None
    count: int
    planned_supplier_id: int
    supplier_order_id: Optional[int] = None
    planned_type_of_branding_id: Optional[int] = None
    planned_contractor_id: Optional[int] = None
    product_cost_price_planned: Optional[float] = None
    branding_cost_price_planned: Optional[float] = None
    price: Optional[float] = None
    product_cost_price_fact: Optional[float] = None
    brading_cost_price_fact: Optional[float] = None
    status_id: Optional[int] = None
    shipment_location_id: int
    design_link: Optional[str] = None

class AddProduct(BaseModel):
    buyer_order_id: Optional[int] = None
    products: List[Product]

# локации
    
class LocationCreate(BaseModel):
    name: str
    address: str
    contractor_id: Optional[int] = None
    location_type: int

class LocationFilter(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    contractor_id: Optional[int] = None
    location_type: Optional[int] = None

# заказы поставщику
    
class SupplierOrderCreate(BaseModel):
    contractor_id: int
    supplier_order_number: str
    shipment_date_planned: str
    delivery_type: int
    invoice_id: Optional[int] = None
    carrier_order_id: Optional[int] = None

class SupplierOrderFilter(BaseModel):
    contractor_id: Optional[int] = None
    supplier_order_number: Optional[str] = None
    create_date: Optional[str] = None
    shipment_date_planned: Optional[str] = None
    shipment_date_fact: Optional[str] = None
    delivery_type: Optional[int] = None
    invoice_id: Optional[int] = None
    carrier_order_id: Optional[int] = None
    owner_id: Optional[int] = None

# статус заказа покупателя

class BuyerOrderStatuses(BaseModel):
    title: str

# статусы продуктов
    
class ProductStatuses(BaseModel):
    title: str