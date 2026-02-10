"""Database models for HoneyBadger Pro"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    """User model - workers and admins"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    initials = Column(String(10), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="basic")  # "admin" or "basic"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    job_assignments = relationship("JobAssignment", back_populates="user")
    time_entries = relationship("TimeEntry", back_populates="user")
    created_jobs = relationship("Job", back_populates="created_by_user")


class Job(Base):
    """Job model - work orders created by admins"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)  # Optional list stored as text
    max_workers = Column(Integer, default=1)
    auto_review = Column(Boolean, default=False)
    is_complete = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    marked_for_review = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    created_by_user = relationship("User", back_populates="created_jobs")
    assignments = relationship("JobAssignment", back_populates="job", cascade="all, delete-orphan")
    time_entries = relationship("TimeEntry", back_populates="job", cascade="all, delete-orphan")


class JobAssignment(Base):
    """Job assignment - links users to jobs"""
    __tablename__ = "job_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="assignments")
    user = relationship("User", back_populates="job_assignments", foreign_keys=[user_id])


class TimeEntry(Base):
    """Time entry - clock in/out records for jobs"""
    __tablename__ = "time_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    clock_in = Column(DateTime(timezone=True), server_default=func.now())
    clock_out = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="time_entries")
    job = relationship("Job", back_populates="time_entries")
