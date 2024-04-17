from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from rsouvenir_crm.db.base import Base


class Address(Base):
    __tablename__ = "addresses"
    __table_args__ = {"comment": "Адреса хранения продукции"}

    id = Column(Integer, primary_key=True, comment="Внутренний номер")
    title = Column(String(20), nullable=False, comment="Отображаемый текст")
    location_id = Column(
        Integer,
        ForeignKey("locations.id"),
        nullable=False,
        comment="Место расположения (номер в соответствующей таблице)",
    )
    location = relationship("Location")


class Box(Base):
    __tablename__ = "boxes"
    __table_args__ = {"comment": "Коробки с товаром"}

    id = Column(Integer, primary_key=True, comment="Внутренний номер")
    packing_id = Column(Integer, ForeignKey("packing.id"), nullable=False)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    packing = relationship("Packing")
    address = relationship("Address")


class BrandingType(Base):
    __tablename__ = "branding_types"
    __table_args__ = {"comment": "Виды нанесения"}

    id = Column(Integer, primary_key=True, comment="Внутренний номер")
    title = Column(String(20), nullable=False, comment="Наименование вида нанесения")


class BuyerOrderStatus(Base):
    __tablename__ = "buyer_order_statuses"
    __table_args__ = {"comment": "Статусы заказов покупателей"}

    id = Column(Integer, primary_key=True, comment="Внутренний номер")
    title = Column(String(20), nullable=False, comment="Отображаемый текст")


class BuyersOrder(Base):
    __tablename__ = "buyers_orders"
    __table_args__ = {"comment": "Заказы покупателей"}

    id = Column(Integer, primary_key=True, comment="Внутренний номер")
    create_date = Column(Date, nullable=False, comment="Дата создания")
    shipment_date_planned = Column(
        Date, nullable=False, comment="Плановая дата отгрузки"
    )
    shipment_date_fact = Column(Date, comment="Фактическая дата отгрузки")
    sell_order_id = Column(
        Integer, nullable=False, comment="Номер сделки продажи в АМО-crm."
    )
    delivery_cost_planned = Column(
        Float, comment="Планируемая стоимость доставки от поставщика до склада"
    )
    shipment_cost_planned = Column(
        Float, comment="Планируемая стоимость доставки до клиента"
    )
    other_expenses_planned = Column(Float, comment="Планируемые прочие расходы")
    instructions = Column(Text, comment="Инструкции по сборке заказа")
    status_id = Column(
        Integer,
        ForeignKey("buyer_order_statuses.id"),
        comment="Статус заказа (номер в соответствующей таблице)",
    )
    owner_id = Column(Integer, nullable=False, comment="Создатель заказа")
    client_id = Column(Integer, nullable=True, comment="Айди клиента")
    status = relationship("BuyerOrderStatus")
    # пока без овнера, т.к база юзеров будет выглядеть по другому


class Carrier(Base):
    __tablename__ = "carriers"
    __table_args__ = {"comment": "Заказы в ТК"}

    id = Column(Integer, primary_key=True, comment="Внутренний номер")
    contractor_id = Column(
        Integer,
        ForeignKey("contractors.id"),
        comment="Контрагент (номер в соответствующей таблице)",
    )
    carrier_number = Column(String(30), comment="Трек-номер в ТК")
    invoice_id = Column(
        Integer,
        ForeignKey("invoices.id"),
        comment="Счёт на оплату (номер в соответствующей таблице)",
    )
    buyer_order_id = Column(
        Integer,
        ForeignKey("buyers_orders.id"),
        comment="Заказ покупателя (номер в соответствующей таблице)",
    )
    owner_id = Column(Integer, nullable=False, comment="Создатель заказа")
    # contractor = relationship("Contractor")
    invoice = relationship("Invoice")
    buyer_order = relationship("BuyersOrder")


class Contact(Base):
    __tablename__ = "contacts"
    __table_args__ = {"comment": "Контактные лица"}

    id = Column(Integer, primary_key=True, comment="Внутренний номер")
    name = Column(String(100), nullable=False, comment="ФИО")
    number = Column(String(12), nullable=False, comment="Номер телефона")
    location_id = Column(Integer, ForeignKey("locations.id"), comment="Локация")
    location = relationship("Location")


class Contractor(Base):
    __tablename__ = "contractors"
    __table_args__ = {"comment": "Контрагенты"}

    id = Column(Integer, primary_key=True, comment="Внутренний номер")
    name = Column(String(100), nullable=False, comment="Наименование контрагента")
    is_supplier = Column(Boolean, comment="Является ли контрагент поставщиком")
    is_contractor = Column(Boolean, comment="Является ли контрагент подрядчиком")
    is_carrier = Column(Boolean, comment="Является ли контрагент перевозчиком")
    is_client = Column(Boolean, comment="Является ли контрагент клиентом")
    locations = relationship("Location", back_populates="contractor")

class ContractorsOrder(Base):
    __tablename__ = "contractors_orders"
    __table_args__ = {"comment": "Заказы у подрядчиков"}

    id = Column(Integer, primary_key=True, comment="Уникальный номер")
    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        comment="Товар, на который производится нанесение (номер в соответствующей таблице)",
    )
    invoice_id = Column(
        Integer,
        ForeignKey("invoices.id"),
        comment="Счёт на плату (номер в соответствующей таблице)",
    )
    type_of_branding_id = Column(Integer)
    contactor_number = Column(String(25), comment="Номер заказа в системе подрядчика")
    contractor_id = Column(
        Integer, ForeignKey("contractors.id"), nullable=False, comment="Подрядчик"
    )
    owner_id = Column(Integer, nullable=False, comment="Создатель заказа")
    product = relationship("Product")
    invoice = relationship("Invoice")
    # добавить связь для owner_id
    # contractor = relationship("Contractor")


class Invoice(Base):
    __tablename__ = "invoices"
    __table_args__ = {"comment": "Счета на оплату"}

    id = Column(Integer, primary_key=True, comment="Внутренний номер")
    create_date = Column(Date, nullable=False, comment="Дата создания")
    payment_date_planned = Column(Date, nullable=False, comment="Плановая дата оплаты")
    payment_date_fact = Column(Date, comment="Фактическая дата оплаты")
    is_adreed = Column(Boolean, comment="Согласованна ли оплата руководителем")
    invoice_link = Column(String(100), nullable=False, comment="Ссылка на счёт")
    payment_full_amount = Column(Float)
    description = Column(Text, comment="Описание счёта")
    is_argeed_2 = Column(Integer)
    payment_order_amout = Column(Float)
    payment_fact_amount = Column(Float, comment="Фактически оплаченная сумма")
    payer = Column(Integer)


class Location(Base):
    __tablename__ = "locations"
    __table_args__ = {
        "comment": "Места расположения продукции\\nСклад НСК, Склад МСК, Подрядчик, Поставщик, Клиент"
    }

    id = Column(Integer, primary_key=True, comment="Внутренний номер")
    name = Column(String(30), nullable=False, comment="Название локации")
    address = Column(String(100), nullable=False, comment="Адрес")
    contractor_id = Column(
        Integer,
        ForeignKey("contractors.id"),
        comment="Контрагент, за которым закреплено место.\\nЕсли поле пустое - значит это один из наших складов.",
    )
    location_type = Column(
        Integer,
        nullable=False,
        comment="0 - склад Россувенир\\n1 - другие внутренние локации (офисы)\\n2 - контрагенты",
    )
    contractor = relationship("Contractor", back_populates="locations")


class Move(Base):
    __tablename__ = "moves"
    __table_args__ = {"comment": "Задачи на перемещения"}

    id = Column(Integer, primary_key=True, comment="Внутренний номер")
    from_id = Column(
        Integer,
        ForeignKey("locations.id"),
        nullable=False,
        comment="Расположение откуда переместить (номер в соответствующей таблице)",
    )
    to_id = Column(
        Integer,
        ForeignKey("locations.id"),
        nullable=False,
        comment="Куда перемещаем (номер в соответствующей таблице)",
    )
    type = Column(
        Integer,
        comment="Тип доставки:\\n0 - запланированная\\n1 - день в день\\n2 - срочная",
    )
    planned_date = Column(Date, nullable=False, comment="Планируемая дата доставки")
    fact_date = Column(Date, comment="Фактическая дата доставки")
    start_time_from = Column(
        Date, comment="Самое раннее вермя посещения точки отправления"
    )
    end_time_from = Column(Date, comment="Крайнее время посещения точки отправления")
    start_time_to = Column(
        Date, comment="Самое раннее время посещения точки назначения"
    )
    end_time_to = Column(Date, comment="Самое позднее время посещения точки назначения")
    owner_id = Column(
        Integer, comment="Создатель задачи (номер в соответствующей таблице)"
    )
    comment = Column(Text, comment="Комментарий")
    vehicle_type = Column(
        Integer,
        comment="Необходимый тип транспортного средства.\\n0 - легковой\\n1 - грузовой S\\n2 - грузовой M\\n3 - грузовой L",
    )
    worker_id = Column(
        Integer, nullable=False, comment="Работник (номер в соответствующей таблице)"
    )
    cost = Column(Integer, comment="Цена перевозки")
    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        comment="Перемещаемый товар (номер в соответствующей таблице)",
    )
    product_count = Column(
        Integer, nullable=False, comment="Количество перемещаемого товара"
    )
    #location = relationship("Location")
    #product = relationship("Product")
    # добавить пользователей


class Packing(Base):
    __tablename__ = "packing"
    __table_args__ = {"comment": "Фасовки товара"}

    id = Column(Integer, primary_key=True)
    product_id = Column(
        Integer, ForeignKey("products.id"), nullable=False, comment="Товар"
    )
    count = Column(Integer, nullable=False, comment="Количество товара в фасовке")
    product = relationship("Product")


class ProductStatus(Base):
    __tablename__ = "product_statuses"
    __table_args__ = {"comment": "Статусы товара"}

    id = Column(Integer, primary_key=True, comment="Внутренний номер")
    title = Column(String(20), nullable=False, comment="Отображаемый текст")


class Product(Base):
    __tablename__ = "products"
    __table_args__ = {"comment": "Товары в заказах покупателей"}

    id = Column(Integer, primary_key=True, comment="Внутренний номер")
    buyer_order_id = Column(
        Integer,
        ForeignKey("buyers_orders.id"),
        comment="Номер заказа покупателя.\\nМожет быть пустым, так как на складе присутствуют товары на реализацию, которые уже не относятся ник одной актуальной сделке.",
    )
    name = Column(String(100), nullable=False, comment="Наименование товара")
    description = Column(
        Text, comment="Описание товара (или ссылка на товар в каталоге)"
    )
    count = Column(
        Integer, nullable=False, comment="Количество товара необходимое клиенту"
    )
    planned_supplier_id = Column(
        Integer,
        ForeignKey("contractors.id"),
        nullable=False,
        comment="Планируемый поставщик",
    )
    supplier_order_id = Column(
        Integer,
        ForeignKey("suppliers_orders.id"),
        comment="Внутренний номер заказа поставщику",
    )
    planned_type_of_branding_id = Column(
        Integer,
        ForeignKey("branding_types.id"),
        comment="Планируемый метод нанесения",
    )
    planned_contractor_id = Column(
        Integer, ForeignKey("contractors.id"), comment="Планируемый подрядчик"
    )
    product_cost_price_planned = Column(
        Float, comment="Планируемая себестоимость товара."
    )
    branding_cost_price_planned = Column(
        Float, comment="Планируемая стоимость нанесения."
    )
    price = Column(Float, comment="Цена для клиента за единицу товара.")
    product_cost_price_fact = Column(Float, comment="Фактическая себестоимость товара.")
    brading_cost_price_fact = Column(
        Float, comment="Фактическая себестоимость нанесения."
    )
    status_id = Column(
        Integer,
        ForeignKey("product_statuses.id"),
        comment="Номер статуса товара(из соответствующей таблицы)",
    )
    shipment_location_id = Column(
        Integer,
        ForeignKey("locations.id"),
        nullable=False,
        comment="Склад отгрузки продукции (номер в соответствующей таблице)",
    )
    design_link = Column(
        String(100), comment="Ссылка на макеты (исходник в цвете и подписанный скан)"
    )
    buyers_orders = relationship("BuyersOrder")
    # contractor = relationship("Contractor")
    suppliers_order = relationship("SuppliersOrder")
    brandingtype = relationship("BrandingType")
    product_status = relationship("ProductStatus")
    locations = relationship("Location")


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {"comment": "Флаги ролей"}

    key = Column(String(1), primary_key=True, comment="Флаг")
    name = Column(String(100), nullable=False, comment="Обозначение флага")


class SuppliersOrder(Base):
    __tablename__ = "suppliers_orders"
    __table_args__ = {"comment": "Заказы поставщикам."}

    id = Column(Integer, primary_key=True, comment="Внутренний номер")
    contractor_id = Column(Integer, ForeignKey("contractors.id"), nullable=False)
    supplier_order_number = Column(
        String(25), comment="Номер заказа в системе поставщика"
    )
    create_date = Column(Date, nullable=False, comment="Дата создания")
    shipment_date_planned = Column(
        Date, nullable=False, comment="Плановая дата прибытия"
    )
    shipment_date_fact = Column(Date, comment="Фактическая дата прибытия")
    delivery_type = Column(
        Integer,
        comment="Тип доставки от поставщика.\\n0 - доставка до склада\\n1 - доставка до ПВЗ\\n2 - доставка до ТК",
    )
    invoice_id = Column(
        Integer,
        ForeignKey("invoices.id"),
        comment="Счёт (номер в соответствующей таблице)",
    )
    carrier_order_id = Column(
        Integer,
        ForeignKey("carriers.id"),
        comment="Заказ в ТК (номер в соответствующей таблице)",
    )
    owner_id = Column(Integer, nullable=False, comment="Создатель заказа")
    # contractor = relationship("Contractor")
    invoice = relationship("Invoice")
    carrier = relationship("Carrier")


class Worker(Base):
    __tablename__ = "workers"
    __table_args__ = {"comment": "Список сотрудников в системе"}

    id = Column(Integer, primary_key=True, comment="Уникальный номер")
    name = Column(String(100), nullable=False, comment="ФИО")
    roles_flags = Column(
        Integer, comment="Роли, определяющие функционал и полномочия в системе"
    )