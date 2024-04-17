from uuid import UUID
from fastapi import APIRouter, Depends, Path, HTTPException, Body, Form, File
from pydantic import BaseModel, UUID4, Field
from typing import Optional, Annotated
from pydantic.json_schema import SkipJsonSchema
import db.repo as repo
from utils.ETL_utils.name_parser import parse_carpet_type
from utils.MC_integration.mc_scripts import update_orders
from utils.server_utils.clear_dict import clear_data
from db.models import User
from db.entities import OrderStatus, ComplectType, OrderGroupStatus
from server.pkg.users import current_active_user
import datetime
from utils.cloud.cloud_workflow import generate_download_link, upload_carpet_yandex


router = APIRouter(
    prefix="/auto_layout_dev/v1"
)


# Пагинатор
class Paginator(BaseModel):
    skip: int = 0
    limit: int = 50


# Pydantic-модель для валидации запросов
class OrderFilterParams(BaseModel):
    town_id: Optional[int] = None
    carpet_group_id: Optional[int] = None
    status: Annotated[OrderStatus, Field(description="Статус заказа в системе")] | SkipJsonSchema[None] = None
    order_group_id: Optional[int] = None
    deliver_at: Optional[str] = None
    color_id: Optional[int] = None
    shape_id: Optional[int] = None
    store_id: Optional[int] = None
    name: Optional[str] = None


class PlotterFilterParams(BaseModel):
    town_id: Optional[int] = None


class OrderGroupFilterParams(BaseModel):
    town_id: Optional[int] = None
    color_id: Optional[int] = None
    shape_id: Optional[int] = None
    store_id: Optional[int] = None
    frame_id: Optional[int] = None
    producer_id: Optional[int] = None
    status: Annotated[OrderGroupStatus, Field(description="Статус группы заказов в системе")] | SkipJsonSchema[
        None] = None


class CarpetChangeParams(BaseModel):
    is_defect: bool
    rotation: int


class AlgorithmChangeParams(BaseModel):
    frame_id: int
    color_id: int
    shape_id: int
    town_id: int
    plotter_id: int


class AlgorithmFilterParams(BaseModel):
    frame_id: Optional[int] = None
    color_id: Optional[int] = None
    shape_id: Optional[int] = None
    town_id: Optional[int] = None
    plotter_id: Optional[int] = None


class TownFilterParams(BaseModel):
    name: Optional[str] = None


class ColorFilterParams(BaseModel):
    name: Optional[str] = None


class ShapeFilterParams(BaseModel):
    name: Optional[str] = None


class StoreFilterParams(BaseModel):
    name: Optional[str] = None


class PlottersUpdateParams(BaseModel):
    is_working: Optional[bool] = None
    orders_count: Optional[int] = None
    order_group_id: Optional[int] = None


class OrderGroupStatusParams(BaseModel):
    status: Annotated[OrderGroupStatus, Field(description="Статус группы заказов в системе")] | SkipJsonSchema[
        None] = None


class OrderResponse(BaseModel):
    id: int
    uuid: UUID
    name: str
    description: str
    deliver_at: datetime.datetime
    created_at: datetime.datetime
    color: str
    shape: str
    store: str
    complect_name: str
    order_group_id: int | None
    town_id: int
    status: OrderStatus
    updated_at: datetime.datetime
    complect_type: ComplectType
    complect_id: int | None = None


class PlotterResponse(BaseModel):
    id: int
    description: str | None
    town_id: int
    orders_count: int
    knife_name: str
    marker_name: str
    cutter_name: str
    is_working: bool
    updated_at: datetime.datetime
    created_at: datetime.datetime
    order_group_id: Optional[int] = None


class OrderGroupResponse(BaseModel):
    id: int
    archive_link: str
    status: OrderGroupStatus
    town_id: int
    frame_id: int
    producer_id: int
    color_id: int
    shape_id: int
    store_id: int
    updated_at: datetime.datetime
    created_at: datetime.datetime


class TownResponse(BaseModel):
    id: int
    name: str


class PlotterRequest(BaseModel):
    description: Optional[str] = None
    town_id: Optional[int] = None


class TownRequest(BaseModel):
    name: Optional[str] = None


class DefectFilterParams(BaseModel):
    color_id: Optional[int] = None
    shape_id: Optional[int] = None
    town_id: Optional[int] = None


class OrderCarpetsParams(BaseModel):
    is_defect: Optional[bool] = None


# Эндпоинты для заказов
@router.get("/orders/")
async def get_orders(filter_params: OrderFilterParams = Depends(),
                     paginator: Paginator = Depends(),
                     user: User = Depends(current_active_user),):
    filter_params = await clear_data(dict_=filter_params.dict())
    count = await repo.OrderRepository().get_count_pages(filter_params)
    all_data = await repo.OrderRepository().find_all_orders(
        filter_by=filter_params, 
        offset=paginator.skip, 
        limit=paginator.limit
        )
    data = {
        "rows": all_data,
        "meta": {
            "count": count,
            "limit": paginator.limit,
            "skip": paginator.skip
        }
    }
    return data


@router.get("/order/{uuid}/")
async def get_order(uuid: UUID4 = Path(...),
                    user: User = Depends(current_active_user),) -> OrderResponse:
    all_data = await repo.OrderRepository().find_order({"uuid": uuid})
    if all_data:
        return all_data
    raise HTTPException(status_code=400, detail=f"Order with uuid {uuid} not found")


# Эндпоинты для плоттеров
@router.get("/plotters/")
async def get_plotters(filter_params: PlotterFilterParams = Depends(),
                       paginator: Paginator = Depends(),
                       user: User = Depends(current_active_user),):
    filter_params = await clear_data(dict_=filter_params.dict())
    count = await repo.PlotterRepository().get_count_pages(filter_params)
    all_data = await repo.PlotterRepository().find_all_plotters(filter_by=filter_params,
                                                                offset=paginator.skip,
                                                                limit=paginator.limit)
    data = {
        "rows": all_data,
        "meta": {
            "count": count,
            "limit": paginator.limit,
            "skip": paginator.skip
        }
    }
    return data


@router.get("/plotters/{id}/")
async def get_plotter(id: int = Path(...),
                      user: User = Depends(current_active_user),) -> PlotterResponse:
    all_data = await repo.PlotterRepository().find_plotter({"id": id})
    if all_data:
        return all_data
    raise HTTPException(status_code=400, detail=f"Plotter with id {id} not found")


@router.post("/plotters/")
async def create_plotter(insert_params: PlotterRequest = Body(),
                         user: User = Depends(current_active_user),) -> PlotterResponse:
    insert_params_clear = await clear_data(dict_=insert_params.dict())
    all_data = await repo.PlotterRepository().insert_one(data=insert_params_clear)
    all_data = await repo.PlotterRepository().find_plotter(filter_by={"id": all_data.id})
    if all_data:
        return all_data


@router.patch("/plotters/{id}/")
async def update_plotter(update_params: PlottersUpdateParams = Body(),
                         id: int = Path(...),
                         user: User = Depends(current_active_user),) -> PlotterResponse:
    update_params_clear = await clear_data(dict_=update_params.dict())
    await repo.PlotterRepository().edit_one(id_=id, data=update_params_clear)
    all_data = await repo.PlotterRepository().find_plotter({"id": id})
    if all_data:
        return all_data


# Эндпоинты для групп заказов
@router.get("/order_groups/")
async def get_order_groups(filter_params: OrderGroupFilterParams = Depends(),
                           paginator: Paginator = Depends(),
                           user: User = Depends(current_active_user),):
    filter_params = await clear_data(dict_=filter_params.dict())
    count = await repo.OrderGroupRepository().get_count_pages(filter_params)
    all_data = await repo.OrderGroupRepository().find_all(filter_by=filter_params,
                                                          offset=paginator.skip,
                                                          limit=paginator.limit,
                                                          order_by="id")
    data = {
        "rows": all_data,
        "meta": {
            "count": count,
            "limit": paginator.limit,
            "skip": paginator.skip
        }
    }
    return data


@router.get("/order_groups/{id}/")
async def get_order_group(id: int = Path(...),
                          user: User = Depends(current_active_user),) -> OrderGroupResponse:
    all_data = await repo.OrderGroupRepository().find_one(filter_by={"id": id})
    if all_data:
        return all_data
    raise HTTPException(status_code=400, detail=f"Order group with id {id} not found")


@router.patch("/order_groups/{id}/")
async def update_status(update_params: OrderGroupStatusParams = Body(),
                        id: int = Path(...),
                        user: User = Depends(current_active_user),) -> OrderGroupResponse:
    update_params_clear = await clear_data(dict_=update_params.dict())
    orders_uuids = []
    if update_params_clear.get("status") == "cut":
        order_group = await repo.OrderGroupRepository().find_one(filter_by={"id": id})
        producer = await repo.ProducerRepository().find_one(filter_by={"id": order_group.producer_id})
        orders = await repo.OrderRepository().find_all(filter_by={"order_group_id": id})
        for order in orders:
            orders_uuids.append(order.uuid)
        update_orders(orders_uuids=orders_uuids, producer=producer.name)
        await repo.OrderGroupRepository().edit_one(id_=id, data={"status": "cut"})
        order_group = await repo.OrderGroupRepository().find_one(filter_by={"id": id})
        return order_group
    else:
        order_group = await repo.OrderGroupRepository().find_one(filter_by={"id": id})
        return order_group


@router.get("/order_groups/{id}/files/")
async def download_order_group_files(id: int = Path(...),
                                     user: User = Depends(current_active_user),):
    order_group = await repo.OrderGroupRepository().find_one({"id": id})
    if order_group:
        link = generate_download_link(order_group.archive_link)
        return link
    else:
        raise HTTPException(status_code=400, detail="Order group not found")


@router.get("/order_groups/{id}/applications")
async def get_applications(user: User = Depends(current_active_user),
                           id: int = Path(...),):
    order_group = await repo.OrderGroupRepository().find_one(filter_by={"id": id})
    download_link = generate_download_link(order_group.application_link)
    return download_link


# Эндпоинты для городов
@router.get("/towns/")
async def get_towns(filter_params: TownFilterParams = Depends(),
                    paginator: Paginator = Depends(),
                    user: User = Depends(current_active_user),):
    filter_params = await clear_data(dict_=filter_params.dict())
    count = await repo.TownRepository().get_count_pages(filter_params)
    all_data = await repo.TownRepository().find_all(filter_by=filter_params, offset=paginator.skip, limit=paginator.limit)
    data = {
        "rows": all_data,
        "meta": {
            "count": count,
            "limit": paginator.limit,
            "skip": paginator.skip
        }
    }
    return data


@router.get("/towns/{id}/")
async def get_town(id: int = Path(...),
                   user: User = Depends(current_active_user),) -> TownResponse:
    all_data = await repo.TownRepository().find_one({"id": id})
    if all_data:
        return all_data
    raise HTTPException(status_code=400, detail=f"Town with id {id} not found")


@router.post("/towns/")
async def create_town(insert_params: TownRequest = Body(),
                      user: User = Depends(current_active_user),) -> TownResponse:
    insert_params_clear = await clear_data(dict_=insert_params.dict())
    all_data = await repo.TownRepository().insert_one(data=insert_params_clear)
    if all_data:
        return all_data


@router.patch("/order_carpets/{id}")
async def patch_order_carpets(carpet: CarpetChangeParams,
                              id:  int = Path(...),
                              user: User = Depends(current_active_user),):

    if carpet.is_defect == True:
        changed_carpet = await repo.OrderCarpetsRepository().edit_one(id_=id, data={"is_defect": carpet.is_defect})
        order = await repo.OrderRepository().find_one(filter_by={"id": changed_carpet.order_id})
        defect = await repo.DefectRepository().find_one(filter_by={"order_id": order.id})
        if defect is None:
            await repo.DefectRepository().insert_one(data={"color_id": order.color_id,
                                                           "shape_id": order.shape_id,
                                                           "town_id": order.town_id,
                                                           "order_id": order.id})
    else:
        await repo.OrderCarpetsRepository().edit_one(id_=id, data={"is_defect": carpet.is_defect})


@router.get("/defects/")
async def get_defects(filter_params: DefectFilterParams = Depends(),
                      paginator: Paginator = Depends(),
                      user: User = Depends(current_active_user),):
    filter_params = await clear_data(dict_=filter_params.dict())
    count = await repo.DefectRepository().get_count_pages(filter_params)
    all_data = await repo.DefectRepository().find_all_defects(offset=paginator.skip,
                                                              limit=paginator.limit,
                                                              filter_by={})
    data = {
        "rows": all_data,
        "meta": {
            "count": count,
            "limit": paginator.limit,
            "skip": paginator.skip
        }
    }
    return data


@router.get("/defects/{id}")
async def get_defects(filter_params: DefectFilterParams = Depends(),
                      paginator: Paginator = Depends(),
                      user: User = Depends(current_active_user)):
    all_data = await repo.DefectRepository()

    return all_data


@router.get("/order_carpets/{order_id}")
async def get_carpets(order_id: int = Path(...),
                      filter_params: OrderCarpetsParams = Depends(),
                      user: User = Depends(current_active_user),):
    filter_params = await clear_data(dict_=filter_params.dict())
    filter_params.update({"order_id": order_id})
    all_data = await repo.OrderCarpetsRepository().find_all_order_carpets(filter_by=filter_params)
    if all_data:
        return all_data
    raise HTTPException(status_code=400, detail=f"Carpets weren't found!")


@router.get("/colors/")
async def get_colors(filter_params: ColorFilterParams = Depends(),
                     paginator: Paginator = Depends(),
                     user: User = Depends(current_active_user),):
    filter_params = await clear_data(dict_=filter_params.dict())
    count = await repo.ColorRepository().get_count_pages(filter_params)
    all_data = await repo.ColorRepository().find_all(filter_by=filter_params, offset=paginator.skip, limit=paginator.limit)
    data = {
        "rows": all_data,
        "meta": {
            "count": count,
            "limit": paginator.limit,
            "skip": paginator.skip
        }
    }
    return data


@router.get("/shapes/")
async def get_shapes(filter_params: ShapeFilterParams = Depends(),
                     paginator: Paginator = Depends(),
                     user: User = Depends(current_active_user),):
    filter_params = await clear_data(dict_=filter_params.dict())
    count = await repo.ShapeRepository().get_count_pages(filter_params)
    all_data = await repo.ShapeRepository().find_all(filter_by=filter_params, offset=paginator.skip, limit=paginator.limit)
    data = {
        "rows": all_data,
        "meta": {
            "count": count,
            "limit": paginator.limit,
            "skip": paginator.skip
        }
    }
    return data


@router.get("/stores/")
async def get_stores(filter_params: StoreFilterParams = Depends(),
                     paginator: Paginator = Depends(),
                     user: User = Depends(current_active_user),):
    filter_params = await clear_data(dict_=filter_params.dict())
    count = await repo.StoreRepository().get_count_pages(filter_params)
    all_data = await repo.StoreRepository().find_all(filter_by=filter_params, offset=paginator.skip, limit=paginator.limit)
    data = {
        "rows": all_data,
        "meta": {
            "count": count,
            "limit": paginator.limit,
            "skip": paginator.skip
        }
    }
    return data


@router.get("/producers/")
async def get_producers(user: User = Depends(current_active_user),
                        paginator: Paginator = Depends(),):
    count = await repo.ProducerRepository().get_count_pages()
    all_data = await repo.ProducerRepository().find_all(filter_by={},
                                                        offset=paginator.skip,
                                                        limit=paginator.limit)
    data = {
        "rows": all_data,
        "meta": {
            "count": count,
            "limit": paginator.limit,
            "skip": paginator.skip
        }
    }
    return data

@router.post("/uploadcarpet/")
async def create_upload_file(file: Annotated[bytes, File()],
    complect_name: Annotated[str, Form()],
    complect_type: Annotated[str, Form()],):
    path_to_carpet = upload_carpet_yandex(complect_type=complect_type, file=file)
    carpet_type = parse_carpet_type(file_name=file.filename)
    await repo.CarpetRepository().insert_one(data={
        'complect_name': complect_name,
        'file_path': path_to_carpet,
        'complect_type': complect_type,
        'carpet_type': carpet_type,
        'file_name': file.filename,
    })
    return {"filename": file.filename}


@router.get("/algorithms_params/")
async def get_algorithms_params(filter_params: AlgorithmFilterParams = Depends(),
                                user: User = Depends(current_active_user),
                                paginator: Paginator = Depends(),):
    filter_params = await clear_data(dict_=filter_params.dict())
    count = await repo.AlgorithmParamsRepository().get_count_pages()
    algorithms_settings = await repo.AlgorithmParamsRepository().find_all(filter_by=filter_params,
                                                                          offset=paginator.skip,
                                                                          limit=paginator.limit)
    data = {
        "rows": algorithms_settings,
        "meta": {
            "count": count,
            "limit": paginator.limit,
            "skip": paginator.skip
        }
    }
    return data


@router.patch("/algorithms_params/{id}")
async def patch_algorithms_params(algorithm_param: AlgorithmChangeParams,
                                  user: User = Depends(current_active_user),
                                  id: int = Path(...),):
    update_params_clear = await clear_data(dict_=algorithm_param.dict())
    algorithm = await repo.AlgorithmParamsRepository().edit_one(id_=id,
                                                                data=update_params_clear)
    return algorithm


@router.get("/frames/")
async def get_frames(user: User = Depends(current_active_user),
                     paginator: Paginator = Depends(),):
    count = await repo.FrameRepository().get_count_pages()
    all_data = await repo.FrameRepository().find_all(filter_by={},
                                                     offset=paginator.skip,
                                                     limit=paginator.limit)
    data = {
        "rows": all_data,
        "meta": {
            "count": count,
            "limit": paginator.limit,
            "skip": paginator.skip
        }
    }
    return data
