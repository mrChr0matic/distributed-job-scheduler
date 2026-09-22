from pydantic import BaseModel

class TaskRequest(BaseModel):
    inputs : dict
    function : str | None = None
    src_file : str | None = None
    