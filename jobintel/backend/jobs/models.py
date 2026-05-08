from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from backend.storage.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    company = Column(String)
    title = Column(String)
    location = Column(String)

    description = Column(Text)

    source_url = Column(String)

    smi_score = Column(Float)

    status = Column(String, default="discovered")
