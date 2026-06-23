from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime,timezone
from typing import Annotated


class BabyImage_Base(BaseModel): 
    i_save : str
    i_origin : str
    i_label : str | None=None
    i_image : str | None=None
    b_id : int

    model_config = ConfigDict(from_attributes=True)


class BabyImage_Create(BabyImage_Base):
    pass


class BabyImage_Update(BaseModel):
    i_label: str | None = None   


class BabyImage_Multi_del(BaseModel):
    i_ids:list[int]

    
class BabyImage_Read(BabyImage_Base):
    i_id: int
    i_date : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


