"""Task Tracker Logic - handles time tracking data"""
import json
import os
from datetime import datetime
from typing import Optional


def get_data_file_path():
    """Get the path for the task data file - Android compatible"""
    try:
        from kivy.utils import platform
        if platform == 'android':
            # On Android, use app's private storage
            from android import mActivity
            context = mActivity.getApplicationContext()
            data_dir = context.getFilesDir().getAbsolutePath()
        else:
            # Desktop: use home directory
            home = os.path.expanduser('~')
            data_dir = os.path.join(home, '.honeybadger')
    except ImportError:
        # Fallback for non-Kivy environments
        home = os.path.expanduser('~')
        data_dir = os.path.join(home, '.honeybadger')
    
    if not os.path.exists(data_dir):
        try:
            os.makedirs(data_dir)
        except Exception:
            pass  # Directory might already exist or be inaccessible
    
    return os.path.join(data_dir, 'tasks.json')


def load_tasks():
    """Load tasks from the JSON file"""
    file_path = get_data_file_path()
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {'active': [], 'archived': []}
    return {'active': [], 'archived': []}


def save_tasks(data):
    """Save tasks to the JSON file"""
    file_path = get_data_file_path()
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


# Priority levels
PRIORITY_LEVELS = ['Low', 'Normal', 'High', 'Urgent']
PRIORITY_COLORS = {
    'Low': 'gray',
    'Normal': 'green',
    'High': 'orange', 
    'Urgent': 'red'
}


def create_task(name: str, notes: str = "", priority: str = "Normal") -> dict:
    """Create a new task"""
    data = load_tasks()
    
    if priority not in PRIORITY_LEVELS:
        priority = "Normal"
    
    task = {
        'id': datetime.now().strftime('%Y%m%d%H%M%S%f'),
        'name': name,
        'notes': notes,
        'priority': priority,
        'time_entries': [],  # List of {punch_in, punch_out} dicts
        'created': datetime.now().isoformat(),
        'is_active': False  # Currently punched in?
    }
    
    data['active'].append(task)
    save_tasks(data)
    return task


def punch_in(task_id: str) -> dict:
    """Punch in to a task - starts a new time entry"""
    data = load_tasks()
    
    for task in data['active']:
        if task['id'] == task_id:
            if task['is_active']:
                return {'success': False, 'error': 'Already punched in to this task'}
            
            # Start a new time entry
            task['time_entries'].append({
                'punch_in': datetime.now().isoformat(),
                'punch_out': None
            })
            task['is_active'] = True
            save_tasks(data)
            return {'success': True, 'task': task}
    
    return {'success': False, 'error': 'Task not found'}


def punch_out(task_id: str) -> dict:
    """Punch out of a task - ends the current time entry"""
    data = load_tasks()
    
    for task in data['active']:
        if task['id'] == task_id:
            if not task['is_active']:
                return {'success': False, 'error': 'Not currently punched in'}
            
            # Find the open time entry and close it
            for entry in task['time_entries']:
                if entry['punch_out'] is None:
                    entry['punch_out'] = datetime.now().isoformat()
                    break
            
            task['is_active'] = False
            save_tasks(data)
            return {'success': True, 'task': task}
    
    return {'success': False, 'error': 'Task not found'}


def get_active_tasks() -> list:
    """Get all active (non-archived) tasks, sorted by priority"""
    data = load_tasks()
    tasks = data['active']
    
    # Sort by priority (Urgent first, then High, Normal, Low)
    priority_order = {'Urgent': 0, 'High': 1, 'Normal': 2, 'Low': 3}
    tasks.sort(key=lambda t: priority_order.get(t.get('priority', 'Normal'), 2))
    
    return tasks


def get_archived_tasks() -> list:
    """Get all archived tasks"""
    data = load_tasks()
    return data['archived']


def archive_task(task_id: str) -> dict:
    """Move a task to the archive"""
    data = load_tasks()
    
    for i, task in enumerate(data['active']):
        if task['id'] == task_id:
            if task['is_active']:
                return {'success': False, 'error': 'Punch out before archiving'}
            
            archived_task = data['active'].pop(i)
            archived_task['archived_date'] = datetime.now().isoformat()
            data['archived'].append(archived_task)
            save_tasks(data)
            return {'success': True, 'task': archived_task}
    
    return {'success': False, 'error': 'Task not found'}


def unarchive_task(task_id: str) -> dict:
    """Move a task from archive back to active"""
    data = load_tasks()
    
    for i, task in enumerate(data['archived']):
        if task['id'] == task_id:
            restored_task = data['archived'].pop(i)
            if 'archived_date' in restored_task:
                del restored_task['archived_date']
            data['active'].append(restored_task)
            save_tasks(data)
            return {'success': True, 'task': restored_task}
    
    return {'success': False, 'error': 'Task not found'}


def update_task(task_id: str, name: Optional[str] = None, notes: Optional[str] = None, priority: Optional[str] = None) -> dict:
    """Update task name, notes, and/or priority"""
    data = load_tasks()
    
    for task in data['active']:
        if task['id'] == task_id:
            if name is not None:
                task['name'] = name
            if notes is not None:
                task['notes'] = notes
            if priority is not None and priority in PRIORITY_LEVELS:
                task['priority'] = priority
            save_tasks(data)
            return {'success': True, 'task': task}
    
    return {'success': False, 'error': 'Task not found'}


def delete_task(task_id: str, from_archive: bool = False) -> dict:
    """Permanently delete a task"""
    data = load_tasks()
    task_list = data['archived'] if from_archive else data['active']
    
    for i, task in enumerate(task_list):
        if task['id'] == task_id:
            if not from_archive and task['is_active']:
                return {'success': False, 'error': 'Punch out before deleting'}
            deleted = task_list.pop(i)
            save_tasks(data)
            return {'success': True, 'task': deleted}
    
    return {'success': False, 'error': 'Task not found'}


def delete_time_entry(task_id: str, entry_index: int) -> dict:
    """Delete a specific time entry from a task"""
    data = load_tasks()
    
    for task in data['active']:
        if task['id'] == task_id:
            if entry_index < 0 or entry_index >= len(task['time_entries']):
                return {'success': False, 'error': 'Invalid entry index'}
            
            entry = task['time_entries'][entry_index]
            if entry['punch_out'] is None:
                return {'success': False, 'error': 'Cannot delete active time entry'}
            
            task['time_entries'].pop(entry_index)
            save_tasks(data)
            return {'success': True, 'task': task}
    
    return {'success': False, 'error': 'Task not found'}


def calculate_total_time(task: dict) -> float:
    """Calculate total hours worked on a task"""
    total_seconds = 0
    
    for entry in task.get('time_entries', []):
        if entry['punch_in']:
            punch_in = datetime.fromisoformat(entry['punch_in'])
            
            if entry['punch_out']:
                punch_out = datetime.fromisoformat(entry['punch_out'])
            else:
                # Currently punched in - calculate up to now
                punch_out = datetime.now()
            
            delta = punch_out - punch_in
            total_seconds += delta.total_seconds()
    
    return total_seconds / 3600  # Return hours


def format_time(hours: float) -> str:
    """Format hours into a readable string"""
    total_minutes = int(hours * 60)
    h = total_minutes // 60
    m = total_minutes % 60
    
    if h > 0:
        return f"{h}h {m}m"
    else:
        return f"{m}m"


def get_currently_active_task() -> Optional[dict]:
    """Get the task that is currently punched in, if any"""
    data = load_tasks()
    for task in data['active']:
        if task['is_active']:
            return task
    return None
