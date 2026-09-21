"""
This module contains the base settings for the application.
"""
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Base class for all the models in the application.
    This class is used to define the base settings for the models, such as the metadata and the table name.
    All the models in the application should inherit from this class.
    Base
 ├── Organization
 ├── Patient
 ├── PatientIdentifier
 ├── Device
 ├── HolterSession
 ├── Recording
 ├── AnalysisRun
 └── ...
    """
    pass

from app.models import (
       AcquisitionSession,
       Device,
       User,
       Organization,
       Patient,
       PatientIdentifier,
       Recording,
       HolterSession,)
