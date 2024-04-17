from rsouvenir_crm.web.api.crm.contractor_views import router as contractor_router
from rsouvenir_crm.web.api.crm.customerorders_views import router as customer_orders_router
from rsouvenir_crm.web.api.crm.branding_types_views import router as branding_types_router
from rsouvenir_crm.web.api.crm.products_views import router as products_views_router
from rsouvenir_crm.web.api.crm.locations_views import router as locations_views_router
from rsouvenir_crm.web.api.crm.supplier_order import router as supplier_order_views_router
from rsouvenir_crm.web.api.crm.buyer_order_statuses_views import router as buyer_order_statuses_views_router
from rsouvenir_crm.web.api.crm.product_statuses_views import router as product_statuses_views_router

__all__ = ["contractor_router", 
           "customer_orders_router", 
           "branding_types_router", 
           "products_views_router",
           "locations_views_router",
           "supplier_order_views_router",
           "buyer_order_statuses_views_router",
           "product_statuses_views_router",
           ]