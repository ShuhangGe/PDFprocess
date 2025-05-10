from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base

class Document(Base):
    """
    Document model to store information about processed PDF documents
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    upload_date = Column(DateTime, server_default=func.now())
    items = relationship("LineItem", back_populates="document", cascade="all, delete-orphan")


class LineItem(Base):
    """
    LineItem model to store line items extracted from documents
    """
    __tablename__ = "line_items"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    description = Column(Text, nullable=False)
    quantity = Column(Integer)
    document = relationship("Document", back_populates="items")
    matches = relationship("ProductMatch", back_populates="line_item", cascade="all, delete-orphan")


class ProductCatalog(Base):
    """
    ProductCatalog model to store product catalog information
    """
    __tablename__ = "product_catalog"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    material = Column(String)
    size = Column(String)
    length = Column(String)
    coating = Column(String)
    thread_type = Column(String)
    description = Column(Text, nullable=False, unique=True)


class ProductMatch(Base):
    """
    ProductMatch model to store matches between line items and product catalog
    """
    __tablename__ = "product_matches"

    id = Column(Integer, primary_key=True, index=True)
    line_item_id = Column(Integer, ForeignKey("line_items.id"))
    product_id = Column(Integer, ForeignKey("product_catalog.id"))
    score = Column(Float)
    is_selected = Column(Boolean, default=False)
    
    line_item = relationship("LineItem", back_populates="matches")
    product = relationship("ProductCatalog") 