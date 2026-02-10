"""Pydantic schemas for API request/response validation"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ============ User Schemas ============

class UserCreate(BaseModel):
    username: str
    initials: str
    password: str
    role: str = "basic"


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    initials: str
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# ============ Job Schemas ============

class JobCreate(BaseModel):
    job_name: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    max_workers: int = 1
    auto_review: bool = False


class JobUpdate(BaseModel):
    job_name: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    max_workers: Optional[int] = None
    auto_review: Optional[bool] = None


class TimeEntryResponse(BaseModel):
    id: int
    user_id: int
    username: str
    initials: str
    clock_in: datetime
    clock_out: Optional[datetime]
    
    class Config:
        from_attributes = True


class JobAssignmentResponse(BaseModel):
    id: int
    user_id: int
    username: str
    initials: str
    assigned_at: datetime
    is_clocked_in: bool = False
    
    class Config:
        from_attributes = True


class JobResponse(BaseModel):
    id: int
    job_name: str
    description: Optional[str]
    requirements: Optional[str]
    max_workers: int
    auto_review: bool
    is_complete: bool
    is_archived: bool
    marked_for_review: bool
    created_by: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]
    current_workers: int = 0
    assignments: List[JobAssignmentResponse] = []
    total_time_seconds: float = 0
    
    class Config:
        from_attributes = True


# ============ Time Entry Schemas ============

class ClockIn(BaseModel):
    job_id: int


class ClockOut(BaseModel):
    job_id: int


class ActiveClockResponse(BaseModel):
    job_id: int
    job_name: str
    clock_in: datetime
    
    class Config:
        from_attributes = True
