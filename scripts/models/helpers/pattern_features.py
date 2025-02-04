from pydantic import BaseModel

class PatternAttribute(BaseModel):
    """
    Pattern attributes are unique features of a craft item
    
    Examples:
    - Crew neck 
    - Raglan sleeves
    - I-cord border
    - lace 
    - cable work

    Args:
        BaseModel (pydantic.BaseModel): The base model for all pattern attributes.
    """

    id: int
    permalink: str

class PatternCategories(BaseModel):
    """
    Pattern categories describe the type of craft item
    
    Examples:
    - Sweater
    - Hat
    - Sock
    """
    id: int
    permalink: str