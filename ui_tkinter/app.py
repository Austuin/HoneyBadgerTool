"""Tkinter Desktop Application - Single Window with Frame Navigation"""
import os
import tkinter as tk
from tkinter import messagebox, Text, Scrollbar, filedialog
from datetime import datetime

from calculators import (
    calculate_key_crest, calculate_point_to_point,
    create_task, punch_in, punch_out, get_active_tasks, get_archived_tasks,
    archive_task, unarchive_task, update_task, delete_task, delete_time_entry,
    calculate_total_time, format_time, get_currently_active_task,
    PRIORITY_LEVELS, PRIORITY_COLORS
)

# Get the icon path
ICON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Apptools', 'Icon.ico')

# Common styling
COLORS = {
    'bg': 'black',
    'fg': 'green',
    'input_fg': 'blue',
    'error': 'red',
    'disabled': 'gray',
    'active': '#00ff00',  # Bright green for active status
}

FONTS = {
    'title': ('Arial', 24, 'bold'),
    'heading': ('Arial', 18, 'bold'),
    'normal': ('Arial', 14),
    'button': ('Arial', 14),
    'small': ('Arial', 12),
}


class HoneyBadgerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HoneyBadger")
        self.root.configure(bg=COLORS['bg'])
        self.root.geometry("1100x800")
        self.root.minsize(900, 700)
        
        # Set the window icon
        if os.path.exists(ICON_PATH):
            self.root.iconbitmap(ICON_PATH)
        
        # Container for all frames
        self.container = tk.Frame(self.root, bg=COLORS['bg'])
        self.container.pack(fill='both', expand=True)
        
        # Store all frames
        self.frames = {}
        
        # Create all frames
        self.create_frames()
        
        # Show main menu
        self.show_frame('menu')
        
        self.root.mainloop()

    def create_frames(self):
        """Create all application frames"""
        # Main Menu
        self.frames['menu'] = MenuFrame(self.container, self)
        # Key Crest Calculator
        self.frames['key_crest'] = KeyCrestFrame(self.container, self)
        # Point to Point Calculator
        self.frames['point_to_point'] = PointToPointFrame(self.container, self)
        # Task Tracker Main
        self.frames['task_tracker'] = TaskTrackerFrame(self.container, self)
        # Task Tracker Archive
        self.frames['task_archive'] = TaskArchiveFrame(self.container, self)
        
        # Configure all frames to fill the container
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky='nsew')
        
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

    def show_frame(self, frame_name):
        """Raise the specified frame to the front"""
        frame = self.frames.get(frame_name)
        if frame:
            # Call refresh if the frame has it (for task tracker)
            if hasattr(frame, 'refresh'):
                frame.refresh()
            frame.tkraise()


class MenuFrame(tk.Frame):
    """Main menu frame"""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg'])
        self.controller = controller
        
        # Title
        title = tk.Label(self, text="Honey Badger.", fg=COLORS['fg'], bg=COLORS['bg'], font=FONTS['title'])
        title.pack(pady=40)
        
        # Buttons container
        btn_frame = tk.Frame(self, bg=COLORS['bg'])
        btn_frame.pack(pady=20)
        
        buttons = [
            ("1. Key Crest Calculator", 'key_crest'),
            ("2. Point to Point Calculator", 'point_to_point'),
            ("3. Task Tracker", 'task_tracker'),
        ]
        
        for text, frame_name in buttons:
            btn = tk.Button(btn_frame, text=text, fg=COLORS['fg'], bg=COLORS['bg'],
                          activeforeground=COLORS['fg'], activebackground=COLORS['bg'],
                          font=FONTS['button'], width=35,
                          command=lambda f=frame_name: controller.show_frame(f))
            btn.pack(pady=10)
        
        # Exit button
        exit_btn = tk.Button(btn_frame, text="0. Exit", fg=COLORS['fg'], bg=COLORS['bg'],
                            activeforeground=COLORS['fg'], activebackground=COLORS['bg'],
                            font=FONTS['button'], width=35,
                            command=self.exit_app)
        exit_btn.pack(pady=30)

    def exit_app(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?", parent=self.controller.root):
            self.controller.root.quit()


class KeyCrestFrame(tk.Frame):
    """Key Crest Calculator frame"""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg'])
        self.controller = controller
        self.valid_inputs = {'shaft': False, 'key': False}
        
        # Title
        title = tk.Label(self, text="Key Crest Calculator", fg=COLORS['fg'], bg=COLORS['bg'], font=FONTS['heading'])
        title.pack(pady=20)
        
        # Instructions
        instr = tk.Label(self, text="Enter the shaft diameter and key width.", fg=COLORS['fg'], bg=COLORS['bg'], font=FONTS['normal'])
        instr.pack(pady=10)
        
        # Input frame
        input_frame = tk.Frame(self, bg=COLORS['bg'])
        input_frame.pack(pady=20)
        
        # Shaft Diameter
        tk.Label(input_frame, text="Shaft Diameter:", fg=COLORS['fg'], bg=COLORS['bg'], font=FONTS['normal']).grid(row=0, column=0, pady=10, padx=10, sticky='e')
        self.shaft_entry = tk.Entry(input_frame, fg=COLORS['input_fg'], bg=COLORS['bg'], insertbackground=COLORS['fg'], font=FONTS['normal'], width=20)
        self.shaft_entry.grid(row=0, column=1, pady=10, padx=10)
        
        # Key Width
        tk.Label(input_frame, text="Key Width:", fg=COLORS['fg'], bg=COLORS['bg'], font=FONTS['normal']).grid(row=1, column=0, pady=10, padx=10, sticky='e')
        self.key_entry = tk.Entry(input_frame, fg=COLORS['input_fg'], bg=COLORS['bg'], insertbackground=COLORS['fg'], font=FONTS['normal'], width=20)
        self.key_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # Calculate button
        self.calc_button = tk.Button(self, text="Calculate", fg=COLORS['disabled'], bg=COLORS['disabled'],
                                     font=FONTS['button'], state='disabled', command=self.calculate)
        self.calc_button.pack(pady=20)
        
        # Result
        self.result_text = Text(self, fg=COLORS['fg'], bg=COLORS['bg'], height=3, width=40, font=FONTS['normal'], state='disabled')
        self.result_text.pack(pady=10)
        self.result_text.tag_config('blue', foreground=COLORS['input_fg'])
        self.result_text.tag_config('green', foreground=COLORS['fg'])
        
        # Back button
        back_btn = tk.Button(self, text="Back to Menu", fg=COLORS['fg'], bg=COLORS['bg'],
                            activeforeground=COLORS['fg'], activebackground=COLORS['bg'],
                            font=FONTS['button'], command=self.go_back)
        back_btn.pack(pady=30)
        
        # Bind validation
        self.shaft_entry.bind("<KeyRelease>", lambda e: self.validate_input('shaft'))
        self.key_entry.bind("<KeyRelease>", lambda e: self.validate_input('key'))

    def validate_input(self, field):
        entry = self.shaft_entry if field == 'shaft' else self.key_entry
        value = entry.get()
        
        try:
            val = float(value)
            if val > 0:
                entry.config(fg=COLORS['input_fg'])
                self.valid_inputs[field] = True
            else:
                entry.config(fg=COLORS['error'])
                self.valid_inputs[field] = False
        except ValueError:
            entry.config(fg=COLORS['error'])
            self.valid_inputs[field] = False
        
        # Check key < shaft
        try:
            shaft = float(self.shaft_entry.get()) if self.shaft_entry.get() else float('inf')
            key = float(self.key_entry.get()) if self.key_entry.get() else 0
            if key >= shaft and shaft != float('inf'):
                self.key_entry.config(fg=COLORS['error'])
                self.valid_inputs['key'] = False
        except ValueError:
            pass
        
        # Update button
        if all(self.valid_inputs.values()):
            self.calc_button.config(state='normal', fg=COLORS['fg'], bg=COLORS['bg'])
        else:
            self.calc_button.config(state='disabled', fg=COLORS['disabled'], bg=COLORS['disabled'])

    def calculate(self):
        shaft = float(self.shaft_entry.get())
        key = float(self.key_entry.get())
        
        result = calculate_key_crest(shaft, key)
        
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        
        if result['success']:
            self.result_text.insert(tk.END, "Crest: ", 'green')
            self.result_text.insert(tk.END, f"{result['crest']:.4f}", 'blue')
        else:
            self.result_text.insert(tk.END, result['error'], 'green')
        
        self.result_text.config(state='disabled')

    def go_back(self):
        self.shaft_entry.delete(0, tk.END)
        self.key_entry.delete(0, tk.END)
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state='disabled')
        self.valid_inputs = {'shaft': False, 'key': False}
        self.calc_button.config(state='disabled', fg=COLORS['disabled'], bg=COLORS['disabled'])
        self.controller.show_frame('menu')


class PointToPointFrame(tk.Frame):
    """Point to Point Calculator frame"""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg'])
        self.controller = controller
        self.valid_inputs = {'p1y': False, 'p1z': False, 'p2y': False, 'p2z': False, 'steps': False}
        self.last_result = None
        
        # Title
        title = tk.Label(self, text="Point to Point Calculator", fg=COLORS['fg'], bg=COLORS['bg'], font=FONTS['heading'])
        title.pack(pady=15)
        
        # Instructions
        instr = tk.Label(self, text="Enter the points and number of steps.", fg=COLORS['fg'], bg=COLORS['bg'], font=FONTS['normal'])
        instr.pack(pady=5)
        
        # Input frame
        input_frame = tk.Frame(self, bg=COLORS['bg'])
        input_frame.pack(pady=10)
        
        labels = ["Point 1 Y:", "Point 1 Z:", "Point 2 Y:", "Point 2 Z:", "Number of Steps:"]
        fields = ['p1y', 'p1z', 'p2y', 'p2z', 'steps']
        self.entries = {}
        
        for i, (label, field) in enumerate(zip(labels, fields)):
            tk.Label(input_frame, text=label, fg=COLORS['fg'], bg=COLORS['bg'], font=FONTS['normal']).grid(row=i, column=0, pady=5, padx=10, sticky='e')
            entry = tk.Entry(input_frame, fg=COLORS['input_fg'], bg=COLORS['bg'], insertbackground=COLORS['fg'], font=FONTS['normal'], width=20)
            entry.grid(row=i, column=1, pady=5, padx=10)
            self.entries[field] = entry
            entry.bind("<KeyRelease>", lambda e, f=field: self.validate_input(f))
        
        # Calculate button
        self.calc_button = tk.Button(self, text="Calculate", fg=COLORS['disabled'], bg=COLORS['disabled'],
                                     font=FONTS['button'], state='disabled', command=self.calculate)
        self.calc_button.pack(pady=10)
        
        # Result area with scrollbar
        result_frame = tk.Frame(self, bg=COLORS['bg'])
        result_frame.pack(pady=10, fill='both', expand=True, padx=20)
        
        scrollbar = Scrollbar(result_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.output_text = Text(result_frame, fg=COLORS['fg'], bg=COLORS['bg'], height=12, width=50, font=FONTS['normal'], state='disabled', yscrollcommand=scrollbar.set)
        self.output_text.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=self.output_text.yview)
        
        self.output_text.tag_config('blue', foreground=COLORS['input_fg'])
        self.output_text.tag_config('green', foreground=COLORS['fg'])
        
        # Button frame
        btn_frame = tk.Frame(self, bg=COLORS['bg'])
        btn_frame.pack(pady=10)
        
        # Save button
        self.save_button = tk.Button(btn_frame, text="Save Results", fg=COLORS['disabled'], bg=COLORS['disabled'],
                                     font=FONTS['button'], state='disabled', command=self.save_results)
        self.save_button.pack(side=tk.LEFT, padx=10)
        
        # Back button
        back_btn = tk.Button(btn_frame, text="Back to Menu", fg=COLORS['fg'], bg=COLORS['bg'],
                            activeforeground=COLORS['fg'], activebackground=COLORS['bg'],
                            font=FONTS['button'], command=self.go_back)
        back_btn.pack(side=tk.LEFT, padx=10)

    def validate_input(self, field):
        entry = self.entries[field]
        value = entry.get()
        
        try:
            if field == 'steps':
                if value.isdigit() and int(value) > 0:
                    entry.config(fg=COLORS['input_fg'])
                    self.valid_inputs[field] = True
                else:
                    entry.config(fg=COLORS['error'])
                    self.valid_inputs[field] = False
            else:
                val = float(value)
                if val > 0:
                    entry.config(fg=COLORS['input_fg'])
                    self.valid_inputs[field] = True
                else:
                    entry.config(fg=COLORS['error'])
                    self.valid_inputs[field] = False
        except ValueError:
            entry.config(fg=COLORS['error'])
            self.valid_inputs[field] = False
        
        if all(self.valid_inputs.values()):
            self.calc_button.config(state='normal', fg=COLORS['fg'], bg=COLORS['bg'])
        else:
            self.calc_button.config(state='disabled', fg=COLORS['disabled'], bg=COLORS['disabled'])

    def calculate(self):
        p1y = float(self.entries['p1y'].get())
        p1z = float(self.entries['p1z'].get())
        p2y = float(self.entries['p2y'].get())
        p2z = float(self.entries['p2z'].get())
        steps = int(self.entries['steps'].get())
        
        result = calculate_point_to_point(p1y, p1z, p2y, p2z, steps)
        
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        
        if result['success']:
            self.output_text.insert(tk.END, "Rate of change Y: ", 'green')
            self.output_text.insert(tk.END, f"{result['rate_of_change_y']:.4f}\n", 'blue')
            self.output_text.insert(tk.END, "Rate of change Z: ", 'green')
            self.output_text.insert(tk.END, f"{result['rate_of_change_z']:.4f}\n\n", 'blue')
            
            for point in result['points']:
                self.output_text.insert(tk.END, f"Step ", 'green')
                self.output_text.insert(tk.END, f"{point['step']}", 'blue')
                self.output_text.insert(tk.END, f": (", 'green')
                self.output_text.insert(tk.END, f"{point['y']:.4f}", 'blue')
                self.output_text.insert(tk.END, f", ", 'green')
                self.output_text.insert(tk.END, f"{point['z']:.4f}", 'blue')
                self.output_text.insert(tk.END, f")\n", 'green')
            
            self.last_result = result
            self.save_button.config(state='normal', fg=COLORS['fg'], bg=COLORS['bg'])
        else:
            self.output_text.insert(tk.END, result['error'], 'green')
        
        self.output_text.config(state='disabled')

    def save_results(self):
        if not self.last_result:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"PtoP_{timestamp}.txt"
        
        file_path = filedialog.asksaveasfilename(
            parent=self.controller.root,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=default_filename,
            title="Save Results"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write("===============Slope Plotting==============\n")
                    f.write(f"Rate of change Y: {self.last_result['rate_of_change_y']:.4f}\n")
                    f.write(f"Rate of change Z: {self.last_result['rate_of_change_z']:.4f}\n\n")
                    for point in self.last_result['points']:
                        f.write(f"Step {point['step']}: ({point['y']:.4f}, {point['z']:.4f})\n")
                messagebox.showinfo("Saved", f"Results saved to:\n{file_path}", parent=self.controller.root)
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{str(e)}", parent=self.controller.root)

    def go_back(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state='disabled')
        self.valid_inputs = {'p1y': False, 'p1z': False, 'p2y': False, 'p2z': False, 'steps': False}
        self.calc_button.config(state='disabled', fg=COLORS['disabled'], bg=COLORS['disabled'])
        self.save_button.config(state='disabled', fg=COLORS['disabled'], bg=COLORS['disabled'])
        self.last_result = None
        self.controller.show_frame('menu')


class TaskTrackerFrame(tk.Frame):
    """Task Tracker main frame - shows active tasks"""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg'])
        self.controller = controller
        
        # Header
        header_frame = tk.Frame(self, bg=COLORS['bg'])
        header_frame.pack(fill='x', pady=10, padx=20)
        
        title = tk.Label(header_frame, text="Task Tracker", fg=COLORS['fg'], bg=COLORS['bg'], font=FONTS['heading'])
        title.pack(side=tk.LEFT)
        
        # Currently clocked in indicator
        self.status_label = tk.Label(header_frame, text="", fg=COLORS['active'], bg=COLORS['bg'], font=FONTS['small'])
        self.status_label.pack(side=tk.RIGHT)
        
        # Button bar
        btn_bar = tk.Frame(self, bg=COLORS['bg'])
        btn_bar.pack(fill='x', padx=20, pady=10)
        
        new_btn = tk.Button(btn_bar, text="+ New Task", fg=COLORS['fg'], bg=COLORS['bg'],
                           font=FONTS['button'], command=self.new_task)
        new_btn.pack(side=tk.LEFT, padx=5)
        
        archive_btn = tk.Button(btn_bar, text="View Archive", fg=COLORS['fg'], bg=COLORS['bg'],
                               font=FONTS['button'], command=lambda: controller.show_frame('task_archive'))
        archive_btn.pack(side=tk.LEFT, padx=5)
        
        back_btn = tk.Button(btn_bar, text="Back to Menu", fg=COLORS['fg'], bg=COLORS['bg'],
                            font=FONTS['button'], command=lambda: controller.show_frame('menu'))
        back_btn.pack(side=tk.RIGHT, padx=5)
        
        # Task list container with scrollbar
        list_container = tk.Frame(self, bg=COLORS['bg'])
        list_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(list_container, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = Scrollbar(list_container, orient="vertical", command=canvas.yview)
        
        self.task_frame = tk.Frame(canvas, bg=COLORS['bg'])
        
        self.task_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.task_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.canvas = canvas

    def refresh(self):
        """Refresh the task list"""
        # Clear existing widgets
        for widget in self.task_frame.winfo_children():
            widget.destroy()
        
        tasks = get_active_tasks()
        
        # Update status indicator
        active = get_currently_active_task()
        if active:
            self.status_label.config(text=f"⏱ Clocked in: {active['name']}")
        else:
            self.status_label.config(text="")
        
        if not tasks:
            no_tasks = tk.Label(self.task_frame, text="No active tasks. Click '+ New Task' to create one.",
                               fg=COLORS['fg'], bg=COLORS['bg'], font=FONTS['normal'])
            no_tasks.pack(pady=50)
            return
        
        for task in tasks:
            self.create_task_card(task)

    def create_task_card(self, task):
        """Create a task card widget"""
        # Get priority color
        priority = task.get('priority', 'Normal')
        priority_color = PRIORITY_COLORS.get(priority, 'green')
        
        card = tk.Frame(self.task_frame, bg='#1a1a1a', relief='ridge', bd=1)
        card.pack(fill='x', pady=5, padx=5)
        
        # Top row: Priority indicator, Name and time
        top_row = tk.Frame(card, bg='#1a1a1a')
        top_row.pack(fill='x', padx=10, pady=5)
        
        # Priority badge
        if priority != 'Normal':
            priority_label = tk.Label(top_row, text=f"[{priority}]", fg=priority_color,
                                     bg='#1a1a1a', font=FONTS['small'])
            priority_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Name with active indicator
        name_text = task['name']
        if task['is_active']:
            name_text = "⏱ " + name_text
        
        name_label = tk.Label(top_row, text=name_text, fg=COLORS['active'] if task['is_active'] else COLORS['fg'],
                             bg='#1a1a1a', font=FONTS['normal'])
        name_label.pack(side=tk.LEFT)
        
        # Total time
        total_hours = calculate_total_time(task)
        time_label = tk.Label(top_row, text=format_time(total_hours), fg=COLORS['input_fg'],
                             bg='#1a1a1a', font=FONTS['normal'])
        time_label.pack(side=tk.RIGHT)
        
        # Notes (if any)
        if task.get('notes'):
            notes_label = tk.Label(card, text=task['notes'], fg='gray', bg='#1a1a1a', font=FONTS['small'],
                                  wraplength=800, justify='left')
            notes_label.pack(fill='x', padx=10, pady=2, anchor='w')
        
        # Time entries count
        entry_count = len(task.get('time_entries', []))
        if entry_count > 0:
            entries_label = tk.Label(card, text=f"{entry_count} time entr{'y' if entry_count == 1 else 'ies'}",
                                    fg='gray', bg='#1a1a1a', font=FONTS['small'])
            entries_label.pack(padx=10, anchor='w')
        
        # Button row
        btn_row = tk.Frame(card, bg='#1a1a1a')
        btn_row.pack(fill='x', padx=10, pady=5)
        
        if task['is_active']:
            punch_btn = tk.Button(btn_row, text="Punch Out", fg='orange', bg='#1a1a1a',
                                 font=FONTS['small'], command=lambda t=task: self.do_punch_out(t['id']))
        else:
            punch_btn = tk.Button(btn_row, text="Punch In", fg=COLORS['fg'], bg='#1a1a1a',
                                 font=FONTS['small'], command=lambda t=task: self.do_punch_in(t['id']))
        punch_btn.pack(side=tk.LEFT, padx=2)
        
        details_btn = tk.Button(btn_row, text="Details", fg=COLORS['fg'], bg='#1a1a1a',
                               font=FONTS['small'], command=lambda t=task: self.show_task_details(t))
        details_btn.pack(side=tk.LEFT, padx=2)
        
        edit_btn = tk.Button(btn_row, text="Edit", fg=COLORS['fg'], bg='#1a1a1a',
                            font=FONTS['small'], command=lambda t=task: self.edit_task(t))
        edit_btn.pack(side=tk.LEFT, padx=2)
        
        if not task['is_active']:
            archive_btn = tk.Button(btn_row, text="Archive", fg='gray', bg='#1a1a1a',
                                   font=FONTS['small'], command=lambda t=task: self.do_archive(t['id']))
            archive_btn.pack(side=tk.LEFT, padx=2)
            
            delete_btn = tk.Button(btn_row, text="Delete", fg=COLORS['error'], bg='#1a1a1a',
                                  font=FONTS['small'], command=lambda t=task: self.do_delete(t['id']))
            delete_btn.pack(side=tk.LEFT, padx=2)

    def new_task(self):
        """Create a new task"""
        dialog = TaskEditDialog(self.controller.root, "New Task")
        if dialog.result:
            name, notes, priority = dialog.result
            if name:
                create_task(name, notes, priority)
                self.refresh()

    def edit_task(self, task):
        """Edit an existing task"""
        dialog = TaskEditDialog(self.controller.root, "Edit Task", task['name'], 
                               task.get('notes', ''), task.get('priority', 'Normal'))
        if dialog.result:
            name, notes, priority = dialog.result
            if name:
                update_task(task['id'], name, notes, priority)
                self.refresh()

    def do_punch_in(self, task_id):
        # Check if already punched in to another task
        active = get_currently_active_task()
        if active and active['id'] != task_id:
            if messagebox.askyesno("Switch Task", 
                                   f"You're currently punched into '{active['name']}'.\n\nPunch out and switch to this task?",
                                   parent=self.controller.root):
                punch_out(active['id'])
            else:
                return
        
        result = punch_in(task_id)
        if result['success']:
            self.refresh()
        else:
            messagebox.showerror("Error", result['error'], parent=self.controller.root)

    def do_punch_out(self, task_id):
        result = punch_out(task_id)
        if result['success']:
            self.refresh()
        else:
            messagebox.showerror("Error", result['error'], parent=self.controller.root)

    def do_archive(self, task_id):
        if messagebox.askyesno("Archive Task", "Move this task to the archive?", parent=self.controller.root):
            result = archive_task(task_id)
            if result['success']:
                self.refresh()
            else:
                messagebox.showerror("Error", result['error'], parent=self.controller.root)

    def do_delete(self, task_id):
        if messagebox.askyesno("Delete Task", "Permanently delete this task?\nThis cannot be undone.",
                              parent=self.controller.root):
            result = delete_task(task_id)
            if result['success']:
                self.refresh()
            else:
                messagebox.showerror("Error", result['error'], parent=self.controller.root)

    def show_task_details(self, task):
        """Show detailed time entries for a task"""
        TaskDetailsDialog(self.controller.root, task, self.refresh)


class TaskArchiveFrame(tk.Frame):
    """Task Tracker archive frame - shows archived tasks"""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLORS['bg'])
        self.controller = controller
        
        # Header
        header_frame = tk.Frame(self, bg=COLORS['bg'])
        header_frame.pack(fill='x', pady=10, padx=20)
        
        title = tk.Label(header_frame, text="Archived Tasks", fg=COLORS['fg'], bg=COLORS['bg'], font=FONTS['heading'])
        title.pack(side=tk.LEFT)
        
        back_btn = tk.Button(header_frame, text="Back to Tasks", fg=COLORS['fg'], bg=COLORS['bg'],
                            font=FONTS['button'], command=lambda: controller.show_frame('task_tracker'))
        back_btn.pack(side=tk.RIGHT)
        
        # Task list container with scrollbar
        list_container = tk.Frame(self, bg=COLORS['bg'])
        list_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(list_container, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = Scrollbar(list_container, orient="vertical", command=canvas.yview)
        
        self.task_frame = tk.Frame(canvas, bg=COLORS['bg'])
        
        self.task_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=self.task_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def refresh(self):
        """Refresh the archive list"""
        for widget in self.task_frame.winfo_children():
            widget.destroy()
        
        tasks = get_archived_tasks()
        
        if not tasks:
            no_tasks = tk.Label(self.task_frame, text="No archived tasks.",
                               fg=COLORS['fg'], bg=COLORS['bg'], font=FONTS['normal'])
            no_tasks.pack(pady=50)
            return
        
        for task in tasks:
            self.create_archive_card(task)

    def create_archive_card(self, task):
        """Create an archived task card widget"""
        card = tk.Frame(self.task_frame, bg='#1a1a1a', relief='ridge', bd=1)
        card.pack(fill='x', pady=5, padx=5)
        
        # Top row: Name and time
        top_row = tk.Frame(card, bg='#1a1a1a')
        top_row.pack(fill='x', padx=10, pady=5)
        
        name_label = tk.Label(top_row, text=task['name'], fg='gray', bg='#1a1a1a', font=FONTS['normal'])
        name_label.pack(side=tk.LEFT)
        
        total_hours = calculate_total_time(task)
        time_label = tk.Label(top_row, text=format_time(total_hours), fg=COLORS['input_fg'],
                             bg='#1a1a1a', font=FONTS['normal'])
        time_label.pack(side=tk.RIGHT)
        
        # Archived date
        if task.get('archived_date'):
            archived = datetime.fromisoformat(task['archived_date']).strftime('%Y-%m-%d')
            date_label = tk.Label(card, text=f"Archived: {archived}", fg='gray', bg='#1a1a1a', font=FONTS['small'])
            date_label.pack(padx=10, anchor='w')
        
        # Button row
        btn_row = tk.Frame(card, bg='#1a1a1a')
        btn_row.pack(fill='x', padx=10, pady=5)
        
        restore_btn = tk.Button(btn_row, text="Restore", fg=COLORS['fg'], bg='#1a1a1a',
                               font=FONTS['small'], command=lambda t=task: self.do_restore(t['id']))
        restore_btn.pack(side=tk.LEFT, padx=2)
        
        delete_btn = tk.Button(btn_row, text="Delete", fg=COLORS['error'], bg='#1a1a1a',
                              font=FONTS['small'], command=lambda t=task: self.do_delete(t['id']))
        delete_btn.pack(side=tk.LEFT, padx=2)

    def do_restore(self, task_id):
        result = unarchive_task(task_id)
        if result['success']:
            self.refresh()
        else:
            messagebox.showerror("Error", result['error'], parent=self.controller.root)

    def do_delete(self, task_id):
        if messagebox.askyesno("Delete Task", "Permanently delete this archived task?\nThis cannot be undone.",
                              parent=self.controller.root):
            result = delete_task(task_id, from_archive=True)
            if result['success']:
                self.refresh()
            else:
                messagebox.showerror("Error", result['error'], parent=self.controller.root)


class TaskEditDialog(tk.Toplevel):
    """Dialog for creating/editing a task"""
    def __init__(self, parent, title, name="", notes="", priority="Normal"):
        super().__init__(parent)
        self.result = None
        
        self.title(title)
        self.configure(bg=COLORS['bg'])
        self.geometry("500x400")
        self.transient(parent)
        self.grab_set()
        
        if os.path.exists(ICON_PATH):
            self.iconbitmap(ICON_PATH)
        
        # Name
        tk.Label(self, text="Task Name:", fg=COLORS['fg'], bg=COLORS['bg'], font=FONTS['normal']).pack(pady=(20, 5))
        self.name_entry = tk.Entry(self, fg=COLORS['input_fg'], bg=COLORS['bg'], insertbackground=COLORS['fg'],
                                  font=FONTS['normal'], width=40)
        self.name_entry.pack(pady=5)
        self.name_entry.insert(0, name)
        
        # Priority
        tk.Label(self, text="Priority:", fg=COLORS['fg'], bg=COLORS['bg'], font=FONTS['normal']).pack(pady=(15, 5))
        
        priority_frame = tk.Frame(self, bg=COLORS['bg'])
        priority_frame.pack(pady=5)
        
        self.priority_var = tk.StringVar(value=priority)
        
        for p in PRIORITY_LEVELS:
            color = PRIORITY_COLORS.get(p, 'green')
            rb = tk.Radiobutton(priority_frame, text=p, variable=self.priority_var, value=p,
                               fg=color, bg=COLORS['bg'], selectcolor=COLORS['bg'],
                               activeforeground=color, activebackground=COLORS['bg'],
                               font=FONTS['normal'])
            rb.pack(side=tk.LEFT, padx=10)
        
        # Notes
        tk.Label(self, text="Notes (optional):", fg=COLORS['fg'], bg=COLORS['bg'], font=FONTS['normal']).pack(pady=(15, 5))
        self.notes_entry = tk.Entry(self, fg=COLORS['input_fg'], bg=COLORS['bg'], insertbackground=COLORS['fg'],
                                   font=FONTS['normal'], width=40)
        self.notes_entry.pack(pady=5)
        self.notes_entry.insert(0, notes)
        
        # Buttons
        btn_frame = tk.Frame(self, bg=COLORS['bg'])
        btn_frame.pack(pady=30)
        
        save_btn = tk.Button(btn_frame, text="Save", fg=COLORS['fg'], bg=COLORS['bg'],
                            font=FONTS['button'], command=self.save)
        save_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", fg=COLORS['fg'], bg=COLORS['bg'],
                              font=FONTS['button'], command=self.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        self.name_entry.focus_set()
        self.wait_window()

    def save(self):
        name = self.name_entry.get().strip()
        notes = self.notes_entry.get().strip()
        priority = self.priority_var.get()
        if name:
            self.result = (name, notes, priority)
        self.destroy()


class TaskDetailsDialog(tk.Toplevel):
    """Dialog showing detailed time entries for a task"""
    def __init__(self, parent, task, refresh_callback):
        super().__init__(parent)
        self.task = task
        self.refresh_callback = refresh_callback
        
        self.title(f"Time Entries - {task['name']}")
        self.configure(bg=COLORS['bg'])
        self.geometry("600x500")
        self.transient(parent)
        
        if os.path.exists(ICON_PATH):
            self.iconbitmap(ICON_PATH)
        
        # Header
        header = tk.Label(self, text=task['name'], fg=COLORS['fg'], bg=COLORS['bg'], font=FONTS['heading'])
        header.pack(pady=10)
        
        total_hours = calculate_total_time(task)
        total_label = tk.Label(self, text=f"Total: {format_time(total_hours)}", fg=COLORS['input_fg'],
                              bg=COLORS['bg'], font=FONTS['normal'])
        total_label.pack(pady=5)
        
        # Entries list with scrollbar
        list_frame = tk.Frame(self, bg=COLORS['bg'])
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.entries_list = tk.Listbox(list_frame, fg=COLORS['fg'], bg='#1a1a1a', font=FONTS['normal'],
                                       selectbackground=COLORS['fg'], selectforeground=COLORS['bg'],
                                       yscrollcommand=scrollbar.set, height=15)
        self.entries_list.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=self.entries_list.yview)
        
        self.populate_entries()
        
        # Buttons
        btn_frame = tk.Frame(self, bg=COLORS['bg'])
        btn_frame.pack(pady=10)
        
        delete_btn = tk.Button(btn_frame, text="Delete Selected Entry", fg=COLORS['error'], bg=COLORS['bg'],
                              font=FONTS['button'], command=self.delete_entry)
        delete_btn.pack(side=tk.LEFT, padx=10)
        
        close_btn = tk.Button(btn_frame, text="Close", fg=COLORS['fg'], bg=COLORS['bg'],
                             font=FONTS['button'], command=self.destroy)
        close_btn.pack(side=tk.LEFT, padx=10)

    def populate_entries(self):
        self.entries_list.delete(0, tk.END)
        
        entries = self.task.get('time_entries', [])
        if not entries:
            self.entries_list.insert(tk.END, "No time entries yet")
            return
        
        for i, entry in enumerate(entries):
            punch_in_dt = datetime.fromisoformat(entry['punch_in'])
            in_str = punch_in_dt.strftime('%Y-%m-%d %I:%M %p')
            
            if entry['punch_out']:
                punch_out_dt = datetime.fromisoformat(entry['punch_out'])
                out_str = punch_out_dt.strftime('%I:%M %p')
                delta = punch_out_dt - punch_in_dt
                hours = delta.total_seconds() / 3600
                self.entries_list.insert(tk.END, f"{i+1}. {in_str} -> {out_str}  ({format_time(hours)})")
            else:
                self.entries_list.insert(tk.END, f"{i+1}. {in_str} -> (active)")

    def delete_entry(self):
        selection = self.entries_list.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an entry to delete", parent=self)
            return
        
        index = selection[0]
        entries = self.task.get('time_entries', [])
        
        if index >= len(entries):
            return
        
        if messagebox.askyesno("Delete Entry", "Delete this time entry?", parent=self):
            result = delete_time_entry(self.task['id'], index)
            if result['success']:
                self.task = result['task']
                self.populate_entries()
                self.refresh_callback()
            else:
                messagebox.showerror("Error", result['error'], parent=self)


def run():
    """Entry point for tkinter app"""
    HoneyBadgerApp()
