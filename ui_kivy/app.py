"""Kivy Android Application"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock

import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calculators import (
    calculate_key_crest, calculate_point_to_point,
    create_task, punch_in, punch_out, get_active_tasks, get_archived_tasks,
    archive_task, unarchive_task, update_task, delete_task, delete_time_entry,
    calculate_total_time, format_time, get_currently_active_task,
    PRIORITY_LEVELS, PRIORITY_COLORS
)


def get_save_path():
    """Get the appropriate save path for the platform"""
    if platform == 'android':
        # On Android, save to Downloads folder
        try:
            from android.storage import primary_external_storage_path
            return os.path.join(primary_external_storage_path(), 'Download')
        except ImportError:
            return os.path.join(os.path.expanduser('~'), 'Download')
    else:
        # On desktop, save to user's home/Documents
        return os.path.join(os.path.expanduser('~'), 'Documents')

# Set dark theme colors
Window.clearcolor = (0, 0, 0, 1)  # Black background

# Colors
GREEN = (0, 1, 0, 1)
BLUE = (0, 0.5, 1, 1)
GRAY = (0.5, 0.5, 0.5, 1)
RED = (1, 0, 0, 1)
ORANGE = (1, 0.5, 0, 1)
DARK_BG = (0.1, 0.1, 0.1, 1)
CARD_BG = (0.12, 0.12, 0.12, 1)


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        title = Label(
            text='Honey Badger.',
            font_size='24sp',
            color=GREEN,
            size_hint_y=0.2
        )
        layout.add_widget(title)
        
        # Key Crest Button
        key_crest_btn = Button(
            text='1. Key Crest Calculator',
            background_color=DARK_BG,
            color=GREEN,
            size_hint_y=0.12
        )
        key_crest_btn.bind(on_press=lambda x: self.go_to_screen('key_crest'))
        layout.add_widget(key_crest_btn)
        
        # Point to Point Button
        p2p_btn = Button(
            text='2. Point to Point Calculator',
            background_color=DARK_BG,
            color=GREEN,
            size_hint_y=0.12
        )
        p2p_btn.bind(on_press=lambda x: self.go_to_screen('point_to_point'))
        layout.add_widget(p2p_btn)
        
        # Task Tracker Button
        task_btn = Button(
            text='3. Task Tracker',
            background_color=DARK_BG,
            color=GREEN,
            size_hint_y=0.12
        )
        task_btn.bind(on_press=lambda x: self.go_to_screen('task_tracker'))
        layout.add_widget(task_btn)
        
        # Spacer
        layout.add_widget(Label(size_hint_y=0.44))
        
        self.add_widget(layout)
    
    def go_to_screen(self, screen_name):
        self.manager.current = screen_name


class KeyCrestScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        title = Label(
            text='Key Crest Calculator',
            font_size='20sp',
            color=GREEN,
            size_hint_y=0.15
        )
        layout.add_widget(title)
        
        # Shaft Diameter
        layout.add_widget(Label(text='Shaft Diameter:', color=GREEN, size_hint_y=0.1))
        self.shaft_input = TextInput(
            multiline=False,
            input_filter='float',
            background_color=DARK_BG,
            foreground_color=BLUE,
            cursor_color=GREEN,
            size_hint_y=0.1
        )
        layout.add_widget(self.shaft_input)
        
        # Key Width
        layout.add_widget(Label(text='Key Width:', color=GREEN, size_hint_y=0.1))
        self.key_input = TextInput(
            multiline=False,
            input_filter='float',
            background_color=DARK_BG,
            foreground_color=BLUE,
            cursor_color=GREEN,
            size_hint_y=0.1
        )
        layout.add_widget(self.key_input)
        
        # Calculate Button
        calc_btn = Button(
            text='Calculate',
            background_color=DARK_BG,
            color=GREEN,
            size_hint_y=0.1
        )
        calc_btn.bind(on_press=self.calculate)
        layout.add_widget(calc_btn)
        
        # Result
        self.result_label = Label(
            text='',
            color=BLUE,
            size_hint_y=0.15
        )
        layout.add_widget(self.result_label)
        
        # Back Button
        back_btn = Button(
            text='Back to Menu',
            background_color=DARK_BG,
            color=GREEN,
            size_hint_y=0.1
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def calculate(self, instance):
        try:
            shaft = float(self.shaft_input.text)
            key = float(self.key_input.text)
            
            result = calculate_key_crest(shaft, key)
            
            if result['success']:
                self.result_label.text = f"Crest: {result['crest']:.4f}"
                self.result_label.color = BLUE
            else:
                self.result_label.text = result['error']
                self.result_label.color = RED
        except ValueError:
            self.result_label.text = 'Please enter valid numbers'
            self.result_label.color = RED
    
    def go_back(self):
        self.shaft_input.text = ''
        self.key_input.text = ''
        self.result_label.text = ''
        self.manager.current = 'menu'


class PointToPointScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
        
        # Title
        title = Label(
            text='Point to Point Calculator',
            font_size='18sp',
            color=GREEN,
            size_hint_y=0.1
        )
        main_layout.add_widget(title)
        
        # Input fields in a grid-like layout
        input_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=0.45)
        
        # Point 1 Y
        row1 = BoxLayout(orientation='horizontal', spacing=5)
        row1.add_widget(Label(text='Point 1 Y:', color=GREEN, size_hint_x=0.4))
        self.p1y_input = TextInput(multiline=False, input_filter='float',
                                    background_color=DARK_BG,
                                    foreground_color=BLUE, size_hint_x=0.6)
        row1.add_widget(self.p1y_input)
        input_layout.add_widget(row1)
        
        # Point 1 Z
        row2 = BoxLayout(orientation='horizontal', spacing=5)
        row2.add_widget(Label(text='Point 1 Z:', color=GREEN, size_hint_x=0.4))
        self.p1z_input = TextInput(multiline=False, input_filter='float',
                                    background_color=DARK_BG,
                                    foreground_color=BLUE, size_hint_x=0.6)
        row2.add_widget(self.p1z_input)
        input_layout.add_widget(row2)
        
        # Point 2 Y
        row3 = BoxLayout(orientation='horizontal', spacing=5)
        row3.add_widget(Label(text='Point 2 Y:', color=GREEN, size_hint_x=0.4))
        self.p2y_input = TextInput(multiline=False, input_filter='float',
                                    background_color=DARK_BG,
                                    foreground_color=BLUE, size_hint_x=0.6)
        row3.add_widget(self.p2y_input)
        input_layout.add_widget(row3)
        
        # Point 2 Z
        row4 = BoxLayout(orientation='horizontal', spacing=5)
        row4.add_widget(Label(text='Point 2 Z:', color=GREEN, size_hint_x=0.4))
        self.p2z_input = TextInput(multiline=False, input_filter='float',
                                    background_color=DARK_BG,
                                    foreground_color=BLUE, size_hint_x=0.6)
        row4.add_widget(self.p2z_input)
        input_layout.add_widget(row4)
        
        # Steps
        row5 = BoxLayout(orientation='horizontal', spacing=5)
        row5.add_widget(Label(text='Steps:', color=GREEN, size_hint_x=0.4))
        self.steps_input = TextInput(multiline=False, input_filter='int',
                                      background_color=DARK_BG,
                                      foreground_color=BLUE, size_hint_x=0.6)
        row5.add_widget(self.steps_input)
        input_layout.add_widget(row5)
        
        main_layout.add_widget(input_layout)
        
        # Calculate Button
        calc_btn = Button(
            text='Calculate',
            background_color=DARK_BG,
            color=GREEN,
            size_hint_y=0.08
        )
        calc_btn.bind(on_press=self.calculate)
        main_layout.add_widget(calc_btn)
        
        # Results area with scroll
        scroll = ScrollView(size_hint_y=0.25)
        self.result_label = Label(
            text='',
            color=BLUE,
            size_hint_y=None,
            text_size=(None, None),
            halign='left',
            valign='top'
        )
        self.result_label.bind(texture_size=lambda instance, size: setattr(instance, 'height', size[1]))
        scroll.add_widget(self.result_label)
        main_layout.add_widget(scroll)
        
        # Save Button
        self.save_btn = Button(
            text='Save Results',
            background_color=(0.2, 0.2, 0.2, 1),
            color=GRAY,
            size_hint_y=0.08,
            disabled=True
        )
        self.save_btn.bind(on_press=self.save_results)
        main_layout.add_widget(self.save_btn)
        
        # Back Button
        back_btn = Button(
            text='Back to Menu',
            background_color=DARK_BG,
            color=GREEN,
            size_hint_y=0.08
        )
        back_btn.bind(on_press=lambda x: self.go_back())
        main_layout.add_widget(back_btn)
        
        # Store last result for saving
        self.last_result = None
        
        self.add_widget(main_layout)
    
    def calculate(self, instance):
        try:
            p1y = float(self.p1y_input.text)
            p1z = float(self.p1z_input.text)
            p2y = float(self.p2y_input.text)
            p2z = float(self.p2z_input.text)
            steps = int(self.steps_input.text)
            
            result = calculate_point_to_point(p1y, p1z, p2y, p2z, steps)
            
            if result['success']:
                output = f"Rate of change Y: {result['rate_of_change_y']:.4f}\n"
                output += f"Rate of change Z: {result['rate_of_change_z']:.4f}\n\n"
                
                for point in result['points']:
                    output += f"Step {point['step']}: ({point['y']:.4f}, {point['z']:.4f})\n"
                
                self.result_label.text = output
                self.result_label.color = BLUE
                self.last_result = output
                
                # Enable save button
                self.save_btn.disabled = False
                self.save_btn.color = GREEN
                self.save_btn.background_color = DARK_BG
            else:
                self.result_label.text = result['error']
                self.result_label.color = RED
        except ValueError:
            self.result_label.text = 'Please enter valid numbers'
            self.result_label.color = RED
    
    def save_results(self, instance):
        if not self.last_result:
            return
        
        try:
            save_path = get_save_path()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"PtoP_{timestamp}.txt"
            file_path = os.path.join(save_path, filename)
            
            with open(file_path, 'w') as f:
                f.write("===============Slope Plotting==============\n")
                f.write(self.last_result)
            
            # Show success popup
            popup = Popup(
                title='Saved!',
                content=Label(text=f'Saved to:\n{filename}\n\nIn Downloads folder'),
                size_hint=(0.8, 0.4)
            )
            popup.open()
            
            # Disable save button after saving
            self.save_btn.disabled = True
            self.save_btn.color = GRAY
            
        except Exception as e:
            popup = Popup(
                title='Error',
                content=Label(text=f'Could not save:\n{str(e)}'),
                size_hint=(0.8, 0.4)
            )
            popup.open()
    
    def go_back(self):
        self.p1y_input.text = ''
        self.p1z_input.text = ''
        self.p2y_input.text = ''
        self.p2z_input.text = ''
        self.steps_input.text = ''
        self.result_label.text = ''
        self.last_result = None
        self.save_btn.disabled = True
        self.save_btn.color = GRAY
        self.manager.current = 'menu'


class TaskTrackerScreen(Screen):
    """Task Tracker main screen - shows active tasks"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
        
        # Header row
        header = BoxLayout(orientation='horizontal', size_hint_y=0.08)
        header.add_widget(Label(text='Task Tracker', font_size='18sp', color=GREEN, size_hint_x=0.5))
        self.status_label = Label(text='', font_size='12sp', color=GREEN, size_hint_x=0.5)
        header.add_widget(self.status_label)
        main_layout.add_widget(header)
        
        # Button bar
        btn_bar = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=5)
        
        new_btn = Button(text='+ New', background_color=DARK_BG, color=GREEN, size_hint_x=0.33)
        new_btn.bind(on_press=self.new_task)
        btn_bar.add_widget(new_btn)
        
        archive_btn = Button(text='Archive', background_color=DARK_BG, color=GREEN, size_hint_x=0.33)
        archive_btn.bind(on_press=lambda x: self.go_to_archive())
        btn_bar.add_widget(archive_btn)
        
        back_btn = Button(text='Menu', background_color=DARK_BG, color=GREEN, size_hint_x=0.33)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        btn_bar.add_widget(back_btn)
        
        main_layout.add_widget(btn_bar)
        
        # Scrollable task list
        scroll = ScrollView(size_hint_y=0.82)
        self.task_list = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, padding=5)
        self.task_list.bind(minimum_height=self.task_list.setter('height'))
        scroll.add_widget(self.task_list)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def on_enter(self):
        """Called when screen is displayed"""
        self.refresh()
    
    def refresh(self):
        """Refresh the task list"""
        self.task_list.clear_widgets()
        
        tasks = get_active_tasks()
        
        # Update status
        active = get_currently_active_task()
        if active:
            name = active['name'][:20] + '...' if len(active['name']) > 20 else active['name']
            self.status_label.text = f"[Clocked: {name}]"
        else:
            self.status_label.text = ""
        
        if not tasks:
            self.task_list.add_widget(Label(
                text="No active tasks.\nTap '+ New' to create one.",
                color=GREEN,
                size_hint_y=None,
                height=100
            ))
            return
        
        for task in tasks:
            self.add_task_card(task)
    
    def add_task_card(self, task):
        """Create a task card"""
        # Get priority
        priority = task.get('priority', 'Normal')
        priority_color_name = PRIORITY_COLORS.get(priority, 'green')
        # Convert color name to RGBA tuple
        priority_colors_map = {
            'gray': (0.5, 0.5, 0.5, 1),
            'green': GREEN,
            'orange': ORANGE,
            'red': RED
        }
        priority_color = priority_colors_map.get(priority_color_name, GREEN)
        
        card = BoxLayout(orientation='vertical', size_hint_y=None, height=160, 
                        padding=10, spacing=5)
        card.canvas.before.clear()
        from kivy.graphics import Color, Rectangle
        with card.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            card.rect = Rectangle(pos=card.pos, size=card.size)
        card.bind(pos=lambda obj, val: setattr(card.rect, 'pos', val))
        card.bind(size=lambda obj, val: setattr(card.rect, 'size', val))
        
        # Priority and Name row with time
        name_row = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        
        # Priority badge (if not Normal)
        if priority != 'Normal':
            priority_lbl = Label(text=f'[{priority}]', color=priority_color,
                                font_size='12sp', size_hint_x=0.25)
            name_row.add_widget(priority_lbl)
            name_hint = 0.45
        else:
            name_hint = 0.7
        
        name_text = task['name']
        if task['is_active']:
            name_text = ">> " + name_text
        
        name_lbl = Label(text=name_text, 
                        color=GREEN if task['is_active'] else (0.8, 0.8, 0.8, 1),
                        font_size='14sp', halign='left', size_hint_x=name_hint)
        name_lbl.bind(size=name_lbl.setter('text_size'))
        name_row.add_widget(name_lbl)
        
        total_hours = calculate_total_time(task)
        time_lbl = Label(text=format_time(total_hours), color=BLUE, font_size='14sp', size_hint_x=0.3)
        name_row.add_widget(time_lbl)
        card.add_widget(name_row)
        
        # Notes row (if any)
        if task.get('notes'):
            notes = task['notes'][:50] + '...' if len(task['notes']) > 50 else task['notes']
            notes_lbl = Label(text=notes, color=GRAY, font_size='12sp', 
                             halign='left', size_hint_y=0.25)
            notes_lbl.bind(size=notes_lbl.setter('text_size'))
            card.add_widget(notes_lbl)
        else:
            card.add_widget(Label(size_hint_y=0.25))
        
        # Button row
        btn_row = BoxLayout(orientation='horizontal', size_hint_y=0.4, spacing=5)
        
        if task['is_active']:
            punch_btn = Button(text='Out', background_color=DARK_BG, color=ORANGE)
            punch_btn.bind(on_press=lambda x, t=task: self.do_punch_out(t['id']))
        else:
            punch_btn = Button(text='In', background_color=DARK_BG, color=GREEN)
            punch_btn.bind(on_press=lambda x, t=task: self.do_punch_in(t['id']))
        btn_row.add_widget(punch_btn)
        
        detail_btn = Button(text='Detail', background_color=DARK_BG, color=GREEN)
        detail_btn.bind(on_press=lambda x, t=task: self.show_details(t))
        btn_row.add_widget(detail_btn)
        
        edit_btn = Button(text='Edit', background_color=DARK_BG, color=GREEN)
        edit_btn.bind(on_press=lambda x, t=task: self.edit_task(t))
        btn_row.add_widget(edit_btn)
        
        if not task['is_active']:
            arch_btn = Button(text='Arch', background_color=DARK_BG, color=GRAY)
            arch_btn.bind(on_press=lambda x, t=task: self.do_archive(t['id']))
            btn_row.add_widget(arch_btn)
        
        card.add_widget(btn_row)
        self.task_list.add_widget(card)
    
    def new_task(self, instance):
        """Show new task popup"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(Label(text='Task Name:', color=GREEN, size_hint_y=0.12))
        name_input = TextInput(multiline=False, background_color=DARK_BG, 
                              foreground_color=BLUE, size_hint_y=0.15)
        content.add_widget(name_input)
        
        content.add_widget(Label(text='Priority:', color=GREEN, size_hint_y=0.12))
        
        # Priority buttons
        priority_row = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=5)
        priority_buttons = {}
        selected_priority = ['Normal']  # Use list to allow modification in closure
        
        priority_colors_map = {
            'Low': (0.5, 0.5, 0.5, 1),
            'Normal': GREEN,
            'High': ORANGE,
            'Urgent': RED
        }
        
        def select_priority(p):
            selected_priority[0] = p
            for name, btn in priority_buttons.items():
                if name == p:
                    btn.background_color = priority_colors_map.get(p, GREEN)
                else:
                    btn.background_color = DARK_BG
        
        for p in PRIORITY_LEVELS:
            btn = Button(text=p, background_color=DARK_BG if p != 'Normal' else GREEN,
                        color=priority_colors_map.get(p, GREEN))
            btn.bind(on_press=lambda x, pr=p: select_priority(pr))
            priority_buttons[p] = btn
            priority_row.add_widget(btn)
        
        content.add_widget(priority_row)
        
        content.add_widget(Label(text='Notes (optional):', color=GREEN, size_hint_y=0.12))
        notes_input = TextInput(multiline=False, background_color=DARK_BG,
                               foreground_color=BLUE, size_hint_y=0.15)
        content.add_widget(notes_input)
        
        btn_row = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=10)
        
        popup = Popup(title='New Task', content=content, size_hint=(0.95, 0.65))
        
        def save(x):
            name = name_input.text.strip()
            if name:
                create_task(name, notes_input.text.strip(), selected_priority[0])
                popup.dismiss()
                self.refresh()
        
        save_btn = Button(text='Save', background_color=DARK_BG, color=GREEN)
        save_btn.bind(on_press=save)
        btn_row.add_widget(save_btn)
        
        cancel_btn = Button(text='Cancel', background_color=DARK_BG, color=GREEN)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        btn_row.add_widget(cancel_btn)
        
        content.add_widget(btn_row)
        popup.open()
    
    def edit_task(self, task):
        """Show edit task popup"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content.add_widget(Label(text='Task Name:', color=GREEN, size_hint_y=0.12))
        name_input = TextInput(text=task['name'], multiline=False, 
                              background_color=DARK_BG, foreground_color=BLUE, size_hint_y=0.15)
        content.add_widget(name_input)
        
        content.add_widget(Label(text='Priority:', color=GREEN, size_hint_y=0.12))
        
        # Priority buttons
        priority_row = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=5)
        priority_buttons = {}
        current_priority = task.get('priority', 'Normal')
        selected_priority = [current_priority]
        
        priority_colors_map = {
            'Low': (0.5, 0.5, 0.5, 1),
            'Normal': GREEN,
            'High': ORANGE,
            'Urgent': RED
        }
        
        def select_priority(p):
            selected_priority[0] = p
            for name, btn in priority_buttons.items():
                if name == p:
                    btn.background_color = priority_colors_map.get(p, GREEN)
                else:
                    btn.background_color = DARK_BG
        
        for p in PRIORITY_LEVELS:
            is_selected = (p == current_priority)
            btn = Button(text=p, 
                        background_color=priority_colors_map.get(p, GREEN) if is_selected else DARK_BG,
                        color=priority_colors_map.get(p, GREEN))
            btn.bind(on_press=lambda x, pr=p: select_priority(pr))
            priority_buttons[p] = btn
            priority_row.add_widget(btn)
        
        content.add_widget(priority_row)
        
        content.add_widget(Label(text='Notes:', color=GREEN, size_hint_y=0.12))
        notes_input = TextInput(text=task.get('notes', ''), multiline=False,
                               background_color=DARK_BG, foreground_color=BLUE, size_hint_y=0.15)
        content.add_widget(notes_input)
        
        btn_row = BoxLayout(orientation='horizontal', size_hint_y=0.15, spacing=10)
        
        popup = Popup(title='Edit Task', content=content, size_hint=(0.95, 0.65))
        
        def save(x):
            name = name_input.text.strip()
            if name:
                update_task(task['id'], name, notes_input.text.strip(), selected_priority[0])
                popup.dismiss()
                self.refresh()
        
        save_btn = Button(text='Save', background_color=DARK_BG, color=GREEN)
        save_btn.bind(on_press=save)
        btn_row.add_widget(save_btn)
        
        cancel_btn = Button(text='Cancel', background_color=DARK_BG, color=GREEN)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        btn_row.add_widget(cancel_btn)
        
        content.add_widget(btn_row)
        popup.open()
    
    def do_punch_in(self, task_id):
        # Check if already punched in elsewhere
        active = get_currently_active_task()
        if active and active['id'] != task_id:
            content = BoxLayout(orientation='vertical', spacing=10, padding=10)
            content.add_widget(Label(
                text=f"Already clocked into:\n'{active['name']}'\n\nSwitch tasks?",
                color=GREEN
            ))
            
            btn_row = BoxLayout(orientation='horizontal', size_hint_y=0.3, spacing=10)
            popup = Popup(title='Switch Task?', content=content, size_hint=(0.9, 0.4))
            
            def switch(x):
                punch_out(active['id'])
                punch_in(task_id)
                popup.dismiss()
                self.refresh()
            
            yes_btn = Button(text='Yes', background_color=DARK_BG, color=GREEN)
            yes_btn.bind(on_press=switch)
            btn_row.add_widget(yes_btn)
            
            no_btn = Button(text='No', background_color=DARK_BG, color=GREEN)
            no_btn.bind(on_press=lambda x: popup.dismiss())
            btn_row.add_widget(no_btn)
            
            content.add_widget(btn_row)
            popup.open()
        else:
            result = punch_in(task_id)
            if result['success']:
                self.refresh()
    
    def do_punch_out(self, task_id):
        result = punch_out(task_id)
        if result['success']:
            self.refresh()
    
    def do_archive(self, task_id):
        result = archive_task(task_id)
        if result['success']:
            self.refresh()
    
    def show_details(self, task):
        """Show task time entries detail"""
        content = BoxLayout(orientation='vertical', spacing=5, padding=10)
        
        # Header
        total_hours = calculate_total_time(task)
        content.add_widget(Label(
            text=f"Total: {format_time(total_hours)}",
            color=BLUE, font_size='16sp', size_hint_y=0.1
        ))
        
        # Entries list
        scroll = ScrollView(size_hint_y=0.8)
        entries_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        entries_layout.bind(minimum_height=entries_layout.setter('height'))
        
        entries = task.get('time_entries', [])
        if not entries:
            entries_layout.add_widget(Label(text='No time entries', color=GRAY, size_hint_y=None, height=40))
        else:
            for i, entry in enumerate(entries):
                punch_in_dt = datetime.fromisoformat(entry['punch_in'])
                in_str = punch_in_dt.strftime('%m/%d %I:%M%p')
                
                if entry['punch_out']:
                    punch_out_dt = datetime.fromisoformat(entry['punch_out'])
                    out_str = punch_out_dt.strftime('%I:%M%p')
                    delta = punch_out_dt - punch_in_dt
                    hours = delta.total_seconds() / 3600
                    entry_text = f"{i+1}. {in_str} - {out_str} ({format_time(hours)})"
                else:
                    entry_text = f"{i+1}. {in_str} - (active)"
                
                entry_lbl = Label(text=entry_text, color=GREEN, size_hint_y=None, height=30,
                                 halign='left')
                entry_lbl.bind(size=entry_lbl.setter('text_size'))
                entries_layout.add_widget(entry_lbl)
        
        scroll.add_widget(entries_layout)
        content.add_widget(scroll)
        
        # Close button
        close_btn = Button(text='Close', background_color=DARK_BG, color=GREEN, size_hint_y=0.1)
        popup = Popup(title=task['name'], content=content, size_hint=(0.95, 0.7))
        close_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(close_btn)
        
        popup.open()
    
    def go_to_archive(self):
        self.manager.current = 'task_archive'


class TaskArchiveScreen(Screen):
    """Archived tasks screen"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        header.add_widget(Label(text='Archived Tasks', font_size='18sp', color=GREEN))
        
        back_btn = Button(text='Back', background_color=DARK_BG, color=GREEN, size_hint_x=0.3)
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'task_tracker'))
        header.add_widget(back_btn)
        
        main_layout.add_widget(header)
        
        # Scrollable list
        scroll = ScrollView(size_hint_y=0.9)
        self.task_list = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, padding=5)
        self.task_list.bind(minimum_height=self.task_list.setter('height'))
        scroll.add_widget(self.task_list)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def on_enter(self):
        self.refresh()
    
    def refresh(self):
        self.task_list.clear_widgets()
        
        tasks = get_archived_tasks()
        
        if not tasks:
            self.task_list.add_widget(Label(
                text="No archived tasks.",
                color=GREEN,
                size_hint_y=None,
                height=100
            ))
            return
        
        for task in tasks:
            self.add_archive_card(task)
    
    def add_archive_card(self, task):
        card = BoxLayout(orientation='vertical', size_hint_y=None, height=100, padding=10, spacing=5)
        from kivy.graphics import Color, Rectangle
        with card.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            card.rect = Rectangle(pos=card.pos, size=card.size)
        card.bind(pos=lambda obj, val: setattr(card.rect, 'pos', val))
        card.bind(size=lambda obj, val: setattr(card.rect, 'size', val))
        
        # Name row
        name_row = BoxLayout(orientation='horizontal', size_hint_y=0.5)
        name_lbl = Label(text=task['name'], color=GRAY, font_size='14sp', halign='left', size_hint_x=0.7)
        name_lbl.bind(size=name_lbl.setter('text_size'))
        name_row.add_widget(name_lbl)
        
        total_hours = calculate_total_time(task)
        time_lbl = Label(text=format_time(total_hours), color=BLUE, size_hint_x=0.3)
        name_row.add_widget(time_lbl)
        card.add_widget(name_row)
        
        # Button row
        btn_row = BoxLayout(orientation='horizontal', size_hint_y=0.5, spacing=10)
        
        restore_btn = Button(text='Restore', background_color=DARK_BG, color=GREEN)
        restore_btn.bind(on_press=lambda x, t=task: self.do_restore(t['id']))
        btn_row.add_widget(restore_btn)
        
        delete_btn = Button(text='Delete', background_color=DARK_BG, color=RED)
        delete_btn.bind(on_press=lambda x, t=task: self.do_delete(t['id']))
        btn_row.add_widget(delete_btn)
        
        card.add_widget(btn_row)
        self.task_list.add_widget(card)
    
    def do_restore(self, task_id):
        result = unarchive_task(task_id)
        if result['success']:
            self.refresh()
    
    def do_delete(self, task_id):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text='Permanently delete this task?', color=GREEN))
        
        btn_row = BoxLayout(orientation='horizontal', size_hint_y=0.4, spacing=10)
        popup = Popup(title='Confirm Delete', content=content, size_hint=(0.8, 0.35))
        
        def confirm(x):
            delete_task(task_id, from_archive=True)
            popup.dismiss()
            self.refresh()
        
        yes_btn = Button(text='Delete', background_color=DARK_BG, color=RED)
        yes_btn.bind(on_press=confirm)
        btn_row.add_widget(yes_btn)
        
        no_btn = Button(text='Cancel', background_color=DARK_BG, color=GREEN)
        no_btn.bind(on_press=lambda x: popup.dismiss())
        btn_row.add_widget(no_btn)
        
        content.add_widget(btn_row)
        popup.open()


class HoneyBadgerApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(KeyCrestScreen(name='key_crest'))
        sm.add_widget(PointToPointScreen(name='point_to_point'))
        sm.add_widget(TaskTrackerScreen(name='task_tracker'))
        sm.add_widget(TaskArchiveScreen(name='task_archive'))
        return sm


def run():
    """Entry point for Kivy app"""
    HoneyBadgerApp().run()


if __name__ == '__main__':
    run()
