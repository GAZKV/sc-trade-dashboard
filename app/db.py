import os
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./names.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class ResourceName(Base):
    __tablename__ = "resource_names"
    guid = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)


class ShopName(Base):
    __tablename__ = "shop_names"
    shop_id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_all_names() -> dict:
    with SessionLocal() as session:
        resources = {r.guid: r.name for r in session.query(ResourceName).all()}
        shops = {s.shop_id: s.name for s in session.query(ShopName).all()}
        return {"resourceNames": resources, "shopNames": shops}


def save_resource_name(guid: str, name: str) -> None:
    with SessionLocal() as session:
        rec = session.get(ResourceName, guid)
        if rec:
            rec.name = name
        else:
            session.add(ResourceName(guid=guid, name=name))
        session.commit()


def save_shop_name(shop_id: str, name: str) -> None:
    with SessionLocal() as session:
        rec = session.get(ShopName, shop_id)
        if rec:
            rec.name = name
        else:
            session.add(ShopName(shop_id=shop_id, name=name))
        session.commit()
