from fastapi.routing import APIRouter

from rsouvenir_crm.web.api import crm # , users
from rsouvenir_crm.web.api import users
api_router = APIRouter()
# crm
api_router.include_router(crm.contractor_router)
api_router.include_router(crm.customer_orders_router)
api_router.include_router(crm.branding_types_router)
api_router.include_router(crm.products_views_router)
api_router.include_router(crm.locations_views_router)
api_router.include_router(crm.supplier_order_views_router)
api_router.include_router(crm.buyer_order_statuses_views_router)
api_router.include_router(crm.product_statuses_views_router)

# user
api_router.include_router(users.router)
