from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel


class ProductCatalogBase(BaseModel):
    type: Optional[str] = None
    material: Optional[str] = None
    size: Optional[str] = None
    length: Optional[str] = None
    coating: Optional[str] = None
    thread_type: Optional[str] = None
    description: str


class ProductCatalogCreate(ProductCatalogBase):
    pass


class ProductCatalog(ProductCatalogBase):
    id: int

    class Config:
        orm_mode = True


class ProductMatchBase(BaseModel):
    product_id: int
    score: float
    is_selected: bool = False


class ProductMatchCreate(ProductMatchBase):
    pass


class ProductMatch(ProductMatchBase):
    id: int
    line_item_id: int
    product: ProductCatalog

    class Config:
        orm_mode = True


class LineItemBase(BaseModel):
    description: str
    quantity: Optional[int] = None


class LineItemCreate(LineItemBase):
    pass


class LineItem(LineItemBase):
    id: int
    document_id: int
    matches: List[ProductMatch] = []

    class Config:
        orm_mode = True


class DocumentBase(BaseModel):
    filename: str


class DocumentCreate(DocumentBase):
    pass


class Document(DocumentBase):
    id: int
    upload_date: datetime
    items: List[LineItem] = []

    class Config:
        orm_mode = True


class DocumentUploadResponse(BaseModel):
    document_id: int
    filename: str
    items: List[Dict[str, Any]]


class UpdateMatchRequest(BaseModel):
    line_item_id: int
    selected_product_id: int


class SearchProductRequest(BaseModel):
    query: str
    limit: int = 3  # Default to 3 matches 