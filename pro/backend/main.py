"""HoneyBadger Pro - Main FastAPI Application"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List
import os

from database import engine, get_db, Base
from models import User, Job, JobAssignment, TimeEntry
from schemas import (
    UserCreate, UserLogin, UserResponse, Token,
    JobCreate, JobUpdate, JobResponse, JobAssignmentResponse, TimeEntryResponse,
    ClockIn, ClockOut, ActiveClockResponse
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_active_user, require_admin
)
from config import ROLE_ADMIN, ROLE_BASIC

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HoneyBadger Pro", version="1.0.0")

# CORS - allow all origins for local network use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (frontend)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@app.get("/")
async def root():
    """Serve the frontend"""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "HoneyBadger Pro API", "docs": "/docs"}


# ==================== AUTH ROUTES ====================

@app.post("/api/auth/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (admin only in production, open for first user)"""
    # Check if first user (auto-make admin)
    user_count = db.query(User).count()
    
    # Check if username exists
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # First user becomes admin
    role = ROLE_ADMIN if user_count == 0 else user.role
    
    db_user = User(
        username=user.username,
        initials=user.initials.upper(),
        password_hash=get_password_hash(user.password),
        role=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/api/auth/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token"""
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current user info"""
    return current_user


# ==================== USER MANAGEMENT (Admin) ====================

@app.get("/api/users", response_model=List[UserResponse])
def get_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    return db.query(User).all()


@app.post("/api/users", response_model=UserResponse)
def create_user(
    user: UserCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new user (admin only)"""
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    db_user = User(
        username=user.username,
        initials=user.initials.upper(),
        password_hash=get_password_hash(user.password),
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete("/api/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a user (admin only)"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}


# ==================== JOB ROUTES ====================

def build_job_response(job: Job, db: Session) -> dict:
    """Build a job response with computed fields"""
    # Get assignments with user info
    assignments = []
    for assignment in job.assignments:
        # Check if user is currently clocked in
        active_entry = db.query(TimeEntry).filter(
            TimeEntry.job_id == job.id,
            TimeEntry.user_id == assignment.user_id,
            TimeEntry.clock_out.is_(None)
        ).first()
        
        assignments.append({
            "id": assignment.id,
            "user_id": assignment.user_id,
            "username": assignment.user.username,
            "initials": assignment.user.initials,
            "assigned_at": assignment.assigned_at,
            "is_clocked_in": active_entry is not None
        })
    
    # Calculate total time
    total_seconds = 0
    for entry in job.time_entries:
        if entry.clock_out:
            delta = entry.clock_out - entry.clock_in
            total_seconds += delta.total_seconds()
        elif entry.clock_in:
            # Still clocked in
            delta = datetime.utcnow() - entry.clock_in.replace(tzinfo=None)
            total_seconds += delta.total_seconds()
    
    return {
        "id": job.id,
        "job_name": job.job_name,
        "description": job.description,
        "requirements": job.requirements,
        "max_workers": job.max_workers,
        "auto_review": job.auto_review,
        "is_complete": job.is_complete,
        "is_archived": job.is_archived,
        "marked_for_review": job.marked_for_review,
        "created_by": job.created_by,
        "created_at": job.created_at,
        "completed_at": job.completed_at,
        "current_workers": len(assignments),
        "assignments": assignments,
        "total_time_seconds": total_seconds
    }


@app.get("/api/jobs", response_model=List[JobResponse])
def get_jobs(
    include_archived: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all active jobs (job board)"""
    query = db.query(Job)
    if not include_archived:
        query = query.filter(Job.is_archived == False)
    jobs = query.order_by(Job.created_at.desc()).all()
    return [build_job_response(job, db) for job in jobs]


@app.get("/api/jobs/archived", response_model=List[JobResponse])
def get_archived_jobs(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get archived/completed jobs"""
    jobs = db.query(Job).filter(Job.is_archived == True).order_by(Job.completed_at.desc()).all()
    return [build_job_response(job, db) for job in jobs]


@app.get("/api/jobs/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific job"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return build_job_response(job, db)


@app.post("/api/jobs", response_model=JobResponse)
def create_job(
    job: JobCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new job (admin only)"""
    db_job = Job(
        job_name=job.job_name,
        description=job.description,
        requirements=job.requirements,
        max_workers=job.max_workers,
        auto_review=job.auto_review,
        created_by=current_user.id
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return build_job_response(db_job, db)


@app.put("/api/jobs/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_update: JobUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a job (admin only)"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    for field, value in job_update.model_dump(exclude_unset=True).items():
        setattr(job, field, value)
    
    db.commit()
    db.refresh(job)
    return build_job_response(job, db)


@app.delete("/api/jobs/{job_id}")
def delete_job(
    job_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a job (admin only)"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db.delete(job)
    db.commit()
    return {"message": "Job deleted"}


# ==================== JOB ASSIGNMENT ROUTES ====================

@app.post("/api/jobs/{job_id}/join")
def join_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Join a job (add yourself to assignment list)"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.is_complete or job.is_archived:
        raise HTTPException(status_code=400, detail="Job is already complete")
    
    # Check if already assigned
    existing = db.query(JobAssignment).filter(
        JobAssignment.job_id == job_id,
        JobAssignment.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already assigned to this job")
    
    # Check max workers
    current_count = db.query(JobAssignment).filter(JobAssignment.job_id == job_id).count()
    if current_count >= job.max_workers:
        raise HTTPException(status_code=400, detail="Job is full")
    
    assignment = JobAssignment(
        job_id=job_id,
        user_id=current_user.id,
        assigned_by=current_user.id
    )
    db.add(assignment)
    db.commit()
    return {"message": "Joined job successfully"}


@app.post("/api/jobs/{job_id}/assign/{user_id}")
def assign_user_to_job(
    job_id: int,
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Assign a user to a job (admin only)"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already assigned
    existing = db.query(JobAssignment).filter(
        JobAssignment.job_id == job_id,
        JobAssignment.user_id == user_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already assigned")
    
    assignment = JobAssignment(
        job_id=job_id,
        user_id=user_id,
        assigned_by=current_user.id
    )
    db.add(assignment)
    db.commit()
    return {"message": f"Assigned {user.username} to job"}


@app.delete("/api/jobs/{job_id}/leave")
def leave_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Leave a job (remove yourself from assignment)"""
    assignment = db.query(JobAssignment).filter(
        JobAssignment.job_id == job_id,
        JobAssignment.user_id == current_user.id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=404, detail="Not assigned to this job")
    
    # Make sure not clocked in
    active_entry = db.query(TimeEntry).filter(
        TimeEntry.job_id == job_id,
        TimeEntry.user_id == current_user.id,
        TimeEntry.clock_out.is_(None)
    ).first()
    if active_entry:
        raise HTTPException(status_code=400, detail="Clock out first before leaving")
    
    db.delete(assignment)
    db.commit()
    return {"message": "Left job"}


# ==================== TIME TRACKING ROUTES ====================

@app.post("/api/time/clockin")
def clock_in(
    data: ClockIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Clock in to a job"""
    job = db.query(Job).filter(Job.id == data.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.is_complete or job.is_archived:
        raise HTTPException(status_code=400, detail="Job is already complete")
    
    # Check if assigned
    assignment = db.query(JobAssignment).filter(
        JobAssignment.job_id == data.job_id,
        JobAssignment.user_id == current_user.id
    ).first()
    if not assignment:
        raise HTTPException(status_code=400, detail="Not assigned to this job")
    
    # Check if already clocked in to this job
    existing = db.query(TimeEntry).filter(
        TimeEntry.job_id == data.job_id,
        TimeEntry.user_id == current_user.id,
        TimeEntry.clock_out.is_(None)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already clocked in to this job")
    
    entry = TimeEntry(
        user_id=current_user.id,
        job_id=data.job_id
    )
    db.add(entry)
    db.commit()
    return {"message": "Clocked in", "clock_in": entry.clock_in}


@app.post("/api/time/clockout")
def clock_out(
    data: ClockOut,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Clock out of a job"""
    entry = db.query(TimeEntry).filter(
        TimeEntry.job_id == data.job_id,
        TimeEntry.user_id == current_user.id,
        TimeEntry.clock_out.is_(None)
    ).first()
    
    if not entry:
        raise HTTPException(status_code=400, detail="Not clocked in to this job")
    
    entry.clock_out = datetime.utcnow()
    db.commit()
    return {"message": "Clocked out", "clock_out": entry.clock_out}


@app.get("/api/time/active", response_model=List[ActiveClockResponse])
def get_active_clocks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all jobs the current user is clocked in to"""
    entries = db.query(TimeEntry).filter(
        TimeEntry.user_id == current_user.id,
        TimeEntry.clock_out.is_(None)
    ).all()
    
    result = []
    for entry in entries:
        result.append({
            "job_id": entry.job_id,
            "job_name": entry.job.job_name,
            "clock_in": entry.clock_in
        })
    return result


# ==================== JOB COMPLETION ROUTES ====================

@app.post("/api/jobs/{job_id}/mark-complete")
def mark_job_complete(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a job as complete (triggers review or auto-completes)"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if user is assigned
    assignment = db.query(JobAssignment).filter(
        JobAssignment.job_id == job_id,
        JobAssignment.user_id == current_user.id
    ).first()
    if not assignment and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not assigned to this job")
    
    # Clock out all users
    active_entries = db.query(TimeEntry).filter(
        TimeEntry.job_id == job_id,
        TimeEntry.clock_out.is_(None)
    ).all()
    for entry in active_entries:
        entry.clock_out = datetime.utcnow()
    
    if job.auto_review:
        # Auto-complete
        job.is_complete = True
        job.is_archived = True
        job.completed_at = datetime.utcnow()
    else:
        # Mark for admin review
        job.marked_for_review = True
    
    db.commit()
    return {"message": "Job marked for completion", "auto_completed": job.auto_review}


@app.post("/api/jobs/{job_id}/approve")
def approve_job(
    job_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Approve and archive a completed job (admin only)"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job.is_complete = True
    job.is_archived = True
    job.marked_for_review = False
    job.completed_at = datetime.utcnow()
    db.commit()
    return {"message": "Job approved and archived"}


@app.post("/api/jobs/{job_id}/reopen")
def reopen_job(
    job_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Reopen a job that was marked for review (admin only)"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job.marked_for_review = False
    db.commit()
    return {"message": "Job reopened"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
