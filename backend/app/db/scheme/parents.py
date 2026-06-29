from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class Parent_Base(BaseModel): 
    p_role: str
    p_category : str
    p_state: str

    model_config = ConfigDict(from_attributes=True)


class Parent_Create(BaseModel):
    p_role: str
    p_category: str
    p_state: str
    g_id: Optional[int] = None
    u_id: int
    current_b_id: Optional[int] = None
    

class Parent_Update(Parent_Base):
    current_b_id : int | None=None
    p_role: str | None=None
    p_category : str | None=None
    p_state: str | None=None

    
class Parent_Read(Parent_Create):
    p_id:int
    current_b_id : int

class Parent_CurrentBaby_Update(BaseModel):
    b_id: int