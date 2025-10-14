# PomodoroTimer.py
import tkinter as tk
from tkinter import ttk, messagebox
import json
import threading
import time
from datetime import datetime
import os

# ============================================================================
# BASE CLASSES AND INHERITANCE IMPLEMENTATION
# ============================================================================

class BaseTimer:
    """
    Base timer class.
    This class provides the structure for all timer implementations.
    """
    # Main Constructor
    def __init__(self, name):
        self._name = name
        self._is_running = False
        self._total_sessions = 0
        self._current_time = 0
        
    # Getter
    def get_name(self):
        return self._name
    
    def get_total_sessions(self):
        return self._total_sessions
    
    def is_timer_running(self):
        return self._is_running
    
    # Setter
    def set_running_state(self, state):
        self._is_running = state
    
    # This method needs to be overridden by subclasses
    def start_timer(self):
        print("Base timer started - this should be overridden")

class PomodoroTimer(BaseTimer):
    """
    Pomodoro Timer class inheriting from BaseTimer.
    Implements a simple Pomodoro timer with work and break sessions.
    """
    
    # Main Constructor with default parameters
    def __init__(self, work_duration=25, short_break=5, long_break=15):
        super().__init__("Pomodoro Timer")  # Call parent constructor
        
        # Timer configuration using dictionary
        self._timer_config = {
            'work_duration': work_duration,
            'short_break': short_break, 
            'long_break': long_break,
            'sessions_until_long_break': 4
        }
        
        # Session tracking using lists and sets
        self._completed_sessions = []  # List to store session history
        self._session_types = {'work', 'short_break', 'long_break'}  # Set of valid session types
        
        # Default timer state
        self._current_session_type = 'work'
        self._sessions_completed = 0
        self._remaining_time = work_duration * 60  # Convert to seconds
        
    def get_timer_config(self):
        return self._timer_config.copy()  # Return copy to prevent external modification
    
    def update_config(self, new_config):
        # Make sure work_duration and short_break are at least 1 minute
        if new_config['work_duration'] <= 0 or new_config['short_break'] <= 0:
            print("Error: Duration values must be positive")
            return False
        
        self._timer_config.update(new_config)
        
        # Reset current timer if not running
        if not self._is_running:
            self._remaining_time = self._timer_config['work_duration'] * 60
            
        return True
    
    # @Override
    def start_timer(self):
        self._is_running = True
        
    def get_next_session_type(self):
        """
        Determine next session type based on completed sessions.
        Returns the type of session that should follow the current one.
        """
        if self._current_session_type == 'work':
            """
            Check if it's time for a long break using modulo operator.
            So after work session 4, you get a long break.
            """
            if (self._sessions_completed + 1) % self._timer_config['sessions_until_long_break'] == 0:
                return 'long_break'
            else:
                return 'short_break'
        else:
            return 'work'
    
    def complete_session(self):
        """Mark current session as completed and prepare for next session"""
        # Create session record using dictionary
        session_record = {
            'type': self._current_session_type,
            'duration': self._get_session_duration(self._current_session_type),
            'completed_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'session_number': self._sessions_completed + 1 if self._current_session_type == 'work' else self._sessions_completed
        }
        
        # Add to completed sessions list
        self._completed_sessions.append(session_record)
        
        # Update session counter for work sessions only
        if self._current_session_type == 'work':
            self._sessions_completed += 1
            self._total_sessions += 1
        
        # Move to next session type
        self._current_session_type = self.get_next_session_type()
        self._remaining_time = self._get_session_duration(self._current_session_type) * 60
    
    def _get_session_duration(self, session_type):
        """Return duration in minutes for given session type"""
        if session_type == 'work':
            return self._timer_config['work_duration']
        elif session_type == 'short_break':
            return self._timer_config['short_break']
        elif session_type == 'long_break':
            return self._timer_config['long_break']
        else:
            return self._timer_config['work_duration']  # Default case
    
    def get_current_session_info(self):
        """Return current session information as tuple"""
        return (
            self._current_session_type,
            self._remaining_time,
            self._sessions_completed
        )
    
    def get_statistics(self):
        """Generate session statistics"""
        if not self._completed_sessions:
            return {'total_sessions': 0, 'total_time': 0, 'completed_sessions': 0}
        
        # Calculate statistics using list operations
        work_sessions = []
        total_time = 0  
        
        # Process the sessions
        for session in self._completed_sessions:
            if session['type'] == 'work':
                work_sessions.append(session)
            total_time += session['duration']
        
        # Return the processed statistics as a dictionary
        return {
            'total_sessions': len(work_sessions),
            'total_time': total_time,
            'completed_sessions': len(self._completed_sessions)
        }

class StudyTimer(PomodoroTimer):
    """
    Extended Study Timer inheriting from PomodoroTimer.
    Adds study-specific features.
    """
    
    def __init__(self, work_duration=25, short_break=5, long_break=15):
        super().__init__(work_duration, short_break, long_break)
    
        self._daily_goal_minutes = 120  # Default 2 hours
        self._study_notes = []  # List to store study notes
    
    def add_study_note(self, note):
        """Add a study note to the list"""
        if note and len(note.strip()) > 0:
            self._study_notes.append(note.strip())
    
    def get_study_notes(self):
        """Return list of study notes"""
        return self._study_notes.copy()

class RevisionTimer(BaseTimer):
    """
    A Revision Timer that inherits from BaseTimer.
    Focuses on a single study session without breaks.
    """
    def __init__(self, duration=60):  # default 60 min revision block
        super().__init__("Revision Timer")
        self._duration = duration * 60
        self._remaining_time = self._duration
        self._completed_sessions = []  
        self._current_session_type = 'revision' 
        self._sessions_completed = 0 
        self._total_sessions = 0 
        self._timer_config = {'duration': duration}

    def start_timer(self):
        """Override: start revision session"""
        self._is_running = True
        print(f"Revision session started for {self._duration // 60} minutes.")

    def get_current_session_info(self):
        """Consistent interface like PomodoroTimer"""
        return ("revision", self._remaining_time, self._total_sessions)
    
    def get_timer_config(self):
        """Return revision timer config"""
        return {
            'duration': self._duration // 60  # convert to minutes
        }

    def update_config(self, new_config):
        """Update revision timer duration"""
        if 'duration' in new_config and new_config['duration'] > 0:
            self._duration = new_config['duration'] * 60
            if not self._is_running:
                self._remaining_time = self._duration
            return True
        return False
    
    def complete_session(self):
        """Mark current session as completed"""
        # Create session record using dictionary
        session_record = {
            'type': 'revision',
            'duration': self._duration // 60,
            'completed_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'session_number': self._sessions_completed + 1
        }
        
        # Add to completed sessions list
        self._completed_sessions.append(session_record)
        
        # Update session counter
        self._sessions_completed += 1
        self._total_sessions += 1
        
        # Reset for next session
        self._remaining_time = self._duration
    
    def get_next_session_type(self):
        """Revision timer always stays in revision mode"""
        return 'revision'
    
    def get_statistics(self):
        """Generate session statistics for revision timer"""
        if not self._completed_sessions:
            return {'total_sessions': 0, 'total_time': 0, 'completed_sessions': 0}
        
        total_time = 0  
        
        # Process the sessions
        for session in self._completed_sessions:
            total_time += session['duration']
        
        # Return the processed statistics as a dictionary
        return {
            'total_sessions': len(self._completed_sessions),
            'total_time': total_time,
            'completed_sessions': len(self._completed_sessions)
        }


# ============================================================================
# FILE OPERATIONS
# ============================================================================

class DataManager:
    """
    Handles file operations for saving and loading timer data.
    """
    
    def __init__(self, filename="pomodoro_data.json"):
        self.filename = filename
        self.backup_filename = filename + ".bak"
    
    def save_timer_data(self, timer):
        """
        Save timer data to file.
        Returns True if successful, False otherwise.
        """
        try:
            # Prepare data dictionary for JSON serialization
            data = {
                'timer_config': timer.get_timer_config(),
                'sessions_completed': timer.get_total_sessions(),
                'completed_sessions': getattr(timer, '_completed_sessions', []),
                'last_saved': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if hasattr(timer, "_study_notes"):
                data['study_notes'] = timer._study_notes
            if hasattr(timer, "_daily_goal_minutes"):
                data['daily_goal_minutes'] = timer._daily_goal_minutes

            # Create backup of existing file if it exists
            if os.path.exists(self.filename):
                try:
                    # Read existing file and create backup
                    with open(self.filename, 'r') as existing_file:
                        backup_data = existing_file.read()
                    
                    with open(self.backup_filename, 'w') as backup_file:
                        backup_file.write(backup_data)
                        
                except Exception as backup_error:
                    print(f"Warning: Could not create backup: {backup_error}")

            # Write new data to file
            with open(self.filename, 'w') as file:
                json.dump(data, file, indent=4)
            
            return True
            
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def load_timer_data(self):
        """
        Load timer data from file.
        Returns data dictionary if successful, return none if unsuccessful.
        """
        try:
            # Check if file exists
            if not os.path.exists(self.filename):
                print(f"Data file {self.filename} not found")
                return None
            
            # Read and load JSON data
            with open(self.filename, 'r') as file:
                data = json.load(file)
            
            # Check if required keys exist in the JSON file
            required_keys = ['timer_config', 'sessions_completed', 'completed_sessions']
            
            # Run foreach loop to check
            for key in required_keys:
                if key not in data:
                    print(f"Invalid data format: missing {key}")
                    return None
            
            return data
            
        except Exception as e:
            print(f"Error loading data: {e}")
            # Try to load from backup
            return self._load_from_backup()
    
    def _load_from_backup(self):
        """
        Load data from backup file.
        In case the main file is corrupted or missing.
        """
        try:
            if os.path.exists(self.backup_filename):
                with open(self.backup_filename, 'r') as backup_file:
                    return json.load(backup_file)
        except Exception as e:
            print(f"Error loading backup: {e}")
        
        return None

# ============================================================================
# POMODORO GUI APPLICATION IMPLEMENTATION
# ============================================================================

class PomodoroApplication:
    """
    Pomodoro Timer GUI application that can be integrated into the main app.
    """
    
    def __init__(self, parent_app, timer, data_manager):
        self.parent_app = parent_app
        self.timer = timer
        self.data_manager = data_manager
        
        # Timer control variables
        self.timer_thread = None
        self.is_timer_active = False
        self.timer_type_var = tk.StringVar(value="Pomodoro")  # default
        # GUI state variables
        self.current_frame = None
        
    def create_pomodoro_interface(self):
        """
        Create Pomodoro Timer interface.
        """
        # Clear current frame
        if self.parent_app.current_frame:
            self.parent_app.current_frame.destroy()
        
        # Create main pomodoro frame
        pomodoro_frame = tk.Frame(self.parent_app.root, bg=self.parent_app.colors['background'])
        pomodoro_frame.pack(fill='both', expand=True, padx=40, pady=30)
        self.parent_app.current_frame = pomodoro_frame
        
        # Header with back button
        header_frame = tk.Frame(pomodoro_frame, bg=self.parent_app.colors['background'])
        header_frame.pack(fill='x', pady=(0, 30))
        
        back_btn = tk.Button(header_frame,
                            text="← Back to Menu",
                            font=('Arial', 10),
                            bg=self.parent_app.colors['text'],
                            fg='white',
                            padx=15,
                            pady=8,
                            command=self.parent_app.create_main_menu,
                            cursor='hand2',
                            relief='flat')
        back_btn.pack(side='left')
        
        title_label = tk.Label(header_frame,
                              text="Study Pomodoro Timer",
                              font=('Arial', 18, 'bold'),
                              bg=self.parent_app.colors['background'],
                              fg=self.parent_app.colors['text'])
        title_label.pack(side='right')
        
        # Timer type selection
        type_frame = tk.Frame(pomodoro_frame, bg=self.parent_app.colors['background'])
        type_frame.pack(pady=(0, 20))

        tk.Label(type_frame, 
                 text="Select Timer Type:", 
                 font=('Arial', 12, 'bold'),
                 bg=self.parent_app.colors['background'],
                 fg=self.parent_app.colors['text']).pack(side='left', padx=(0, 10))

        type_dropdown = ttk.Combobox(type_frame, 
                                     textvariable=self.timer_type_var,
                                     values=["Pomodoro", "Revision"],
                                     state="readonly",
                                     font=('Arial', 11))
        type_dropdown.pack(side='left')

        type_dropdown.bind("<<ComboboxSelected>>", self.switch_timer)

        # Timer display section - centered and prominent
        timer_frame = tk.Frame(pomodoro_frame, bg='white', relief='solid', borderwidth=1)
        timer_frame.pack(pady=20, padx=20, fill='x')
        
        # Session type display
        self.session_type_var = tk.StringVar()
        self.session_type_var.set(self._format_session_type(self.timer._current_session_type))
        
        session_label = tk.Label(timer_frame,
                                text="Current Session:",
                                font=('Arial', 12),
                                bg='white',
                                fg=self.parent_app.colors['text'])
        session_label.pack(pady=(20, 5))
        
        session_type_label = tk.Label(timer_frame,
                                     textvariable=self.session_type_var,
                                     font=('Arial', 16, 'bold'),
                                     bg='white',
                                     fg=self.parent_app.colors['primary'])
        session_type_label.pack()
        
        # Timer display - large and clear!
        self.time_var = tk.StringVar()
        self.update_timer_display()
        
        timer_display = tk.Label(timer_frame,
                                textvariable=self.time_var,
                                font=('Arial', 36, 'bold'),
                                bg='white',
                                fg=self.parent_app.colors['text'])
        timer_display.pack(pady=20)
        
        # Sessions completed display
        self.sessions_var = tk.StringVar()
        self.sessions_var.set(f"Sessions Completed: {self.timer.get_total_sessions()}")
        
        sessions_label = tk.Label(timer_frame,
                                 textvariable=self.sessions_var,
                                 font=('Arial', 11),
                                 bg='white',
                                 fg=self.parent_app.colors['text'])
        sessions_label.pack(pady=(0, 20))
        
        # Control buttons - start, pause, reset
        controls_frame = tk.Frame(pomodoro_frame, bg=self.parent_app.colors['background'])
        controls_frame.pack(pady=30)

        self.start_btn = tk.Button(controls_frame,
                                  text= "▶ Start Timer",
                                  font=('Arial', 12, 'bold'),
                                  bg=self.parent_app.colors['success'],
                                  fg='white',
                                  padx=25,
                                  pady=12,
                                  command=self.start_timer,
                                  cursor='hand2',
                                  relief='flat')
        self.start_btn.pack(side='left', padx=5)
        
        self.pause_btn = tk.Button(controls_frame,
                                  text="⏸ Pause",
                                  font=('Arial', 12),
                                  bg=self.parent_app.colors['danger'],
                                  fg='white',
                                  padx=25,
                                  pady=12,
                                  command=self.pause_timer,
                                  cursor='hand2',
                                  relief='flat',
                                  state='disabled')
        self.pause_btn.pack(side='left', padx=5)
        
        reset_btn = tk.Button(controls_frame,
                             text="↻ Reset",
                             font=('Arial', 12),
                             bg=self.parent_app.colors['text'],
                             fg='white',
                             padx=25,
                             pady=12,
                             command=self.reset_timer,
                             cursor='hand2',
                             relief='flat')
        reset_btn.pack(side='left', padx=5)
        
        # Validations - Check if timer is active
        if not self.is_timer_active and not self.timer.is_timer_running():
            self.start_btn.config(state='normal', text='▶ Start Timer') # Update button states
            self.pause_btn.config(state='disabled') # The disable state makes the button turn grey and unclickable
        elif not self.is_timer_active and self.timer.is_timer_running():
            self.start_btn.config(state='normal', text='▶ Resume')
            self.pause_btn.config(state='disabled')
        else:
            self.start_btn.config(state='disabled', text='⏳ Running...')
            self.pause_btn.config(state='normal')

        # Settings and features
        self.create_settings_section(pomodoro_frame)
        
    def _format_session_type(self, session_type):
        """Format session type for display using string processing"""
        # Replace underscores with spaces and capitalize
        # Formats to "Work", "Short Break", "Long Break"
        formatted = session_type.replace('_', ' ')
        return formatted.title()
    
    def create_settings_section(self, parent_frame):
        """Create settings section"""
        settings_frame = tk.Frame(parent_frame, bg=self.parent_app.colors['background'])
        settings_frame.pack(pady=20, fill='x')
        
        settings_title = tk.Label(settings_frame,
                                 text="Settings & Actions",
                                 font=('Arial', 14, 'bold'),
                                 bg=self.parent_app.colors['background'],
                                 fg=self.parent_app.colors['text'])
        settings_title.pack(pady=(0, 15))
        
        # Settings buttons in horizontal layout
        buttons_frame = tk.Frame(settings_frame, bg=self.parent_app.colors['background'])
        buttons_frame.pack()
        
        config_btn = tk.Button(buttons_frame,
                              text="⚙️ Timer Settings",
                              font=('Arial', 10),
                              bg=self.parent_app.colors['primary'],
                              fg='white',
                              padx=15,
                              pady=8,
                              command=self.open_settings_dialog,
                              cursor='hand2',
                              relief='flat')
        config_btn.pack(side='left', padx=5)

        stats_btn = tk.Button(buttons_frame,
                             text="📊 View Statistics",
                             font=('Arial', 10),
                             bg=self.parent_app.colors['secondary'],
                             fg='white',
                             padx=15,
                             pady=8,
                             command=self.show_detailed_stats,
                             cursor='hand2',
                             relief='flat')
        stats_btn.pack(side='left', padx=5)
    
    # def create_simple_statistics(self, parent_frame):
    #     """Create simple statistics display"""
    #     # Handle statistics differently depending on timer type
    #     if isinstance(self.timer, (PomodoroTimer, RevisionTimer)):
    #         stats = self.timer.get_statistics()
    #     else:
    #         stats = {'total_sessions': 0, 'total_time': 0, 'completed_sessions': 0}

    #     # Again, only shows if there are completed sessions
    #     if stats['total_sessions'] > 0:
    #         stats_frame = tk.Frame(parent_frame, bg='white', relief='solid', borderwidth=1)
    #         stats_frame.pack(pady=20, fill='x', padx=20)
            
    #         stats_title = tk.Label(stats_frame,
    #                             text="Your Progress Today",
    #                             font=('Arial', 12, 'bold'),
    #                             bg='white',
    #                             fg=self.parent_app.colors['text'])
    #         stats_title.pack(pady=(15, 10))
            
    #         # Simple statistics display
    #         # stats is the dictionary returned by get_statistics()
    #         stats_text = f"Total Sessions: {stats['total_sessions']}\n"
    #         stats_text += f"Total Study Time: {stats['total_time']} minutes\n"
            
    #         # Only show "All Sessions" for Pomodoro timer
    #         if isinstance(self.timer, PomodoroTimer):
    #             stats_text += f"All Sessions (with breaks): {stats['completed_sessions']}"
            
    #         stats_label = tk.Label(stats_frame,
    #                             text=stats_text,
    #                             font=('Arial', 10),
    #                             bg='white',
    #                             fg=self.parent_app.colors['text'],
    #                             justify='center')
    #         stats_label.pack(pady=(0, 15))
            
    #         # Simple statistics display
    #         # stats is the dictionary returned by get_statistics()
    #         stats_text = f"Total Sessions: {stats['total_sessions']}\n"
    #         stats_text += f"Total Study Time: {stats['total_time']} minutes\n"
    #         stats_text += f"All Sessions (with breaks): {stats['completed_sessions']}"
            
    #         stats_label = tk.Label(stats_frame,
    #                               text=stats_text,
    #                               font=('Arial', 10),
    #                               bg='white',
    #                               fg=self.parent_app.colors['text'],
    #                               justify='center')
    #         stats_label.pack(pady=(0, 15))
    
    def update_timer_display(self):
        """Update the timer display with current time remaining"""
        # Convert seconds to MM:SS format
        minutes = self.timer._remaining_time // 60
        seconds = self.timer._remaining_time % 60
        
        # Format time string with zero padding
        time_string = f"{minutes:02d}:{seconds:02d}"
        self.time_var.set(time_string)
    
    def switch_timer(self, event=None):
        """Switch between Pomodoro and Revision timers"""
        choice = self.timer_type_var.get()

        # Load saved config if exists
        saved_data = self.data_manager.load_timer_data()
        
        if choice == "Pomodoro":
            self.timer = PomodoroTimer()
        elif choice == "Revision":
            self.timer = RevisionTimer()
    
        # Restore config if exists
        if saved_data:
            if "timer_config" in saved_data:
                self.timer.update_config(saved_data["timer_config"])

            if "sessions_completed" in saved_data:
                self.timer._total_sessions = saved_data["sessions_completed"]

            if "completed_sessions" in saved_data:
                self.timer._completed_sessions = saved_data["completed_sessions"]

        # Update GUI
        if isinstance(self.timer, PomodoroTimer):
            self.session_type_var.set("Work")
        else:
            self.session_type_var.set("Revision")

        self.sessions_var.set(f"Sessions Completed: {self.timer.get_total_sessions()}")

        self.update_timer_display()


    def start_timer(self):
        """Start the pomodoro timer using threading"""
        if not self.is_timer_active:
            self.is_timer_active = True
            self.timer.start_timer()
            
            # Update button states
            self.start_btn.config(state='disabled', text='⏳ Running...')
            self.pause_btn.config(state='normal')
            
            # Start timer thread to prevent GUI freezing
            self.timer_thread = threading.Thread(target=self.timer_countdown, daemon=True)
            self.timer_thread.start()
    
    def pause_timer(self):
        """Pause or resume the timer"""
        if self.is_timer_active:
            # Pause timer
            self.is_timer_active = False
            self.timer.set_running_state(False)
            
            # Update button states
            self.start_btn.config(state='normal', text='▶ Resume')
            # The disable state makes the button turn grey and unclickable
            self.pause_btn.config(state='disabled')
        
    def reset_timer(self):
        """Reset the timer to initial state"""
        # Stop timer if running
        self.is_timer_active = False
        self.timer.set_running_state(False)
        
        # Reset timer based on type
        if isinstance(self.timer, PomodoroTimer):
            self.timer._current_session_type = 'work'
            self.timer._remaining_time = self.timer._timer_config['work_duration'] * 60
            self.session_type_var.set('Work')
            self.sessions_var.set(f"Sessions Completed: {self.timer.get_total_sessions()}")
            message = "Timer has been reset to work session."
        else:
            # Revision timer
            self.timer._remaining_time = self.timer._duration
            self.session_type_var.set('Revision')
            self.sessions_var.set(f"Sessions Completed: {self.timer.get_total_sessions()}")
            message = "Timer has been reset."
        
        # Update display
        self.update_timer_display()
        
        # Reset button states
        self.start_btn.config(state='normal', text='▶ Start Timer')
        self.pause_btn.config(state='disabled')
        
        messagebox.showinfo("Timer Reset", message)
    
    def timer_countdown(self):
        """
        Main timer countdown loop running in separate thread.
        
        Threading is used to keep the GUI responsive.
        Lets say I use loop and time.sleep right, while the time.sleep is running, the whole program is blocked.
        Users will be unable to click on buttons etc.
        Threading fixes that issue, it ticks in the background. 
        """
        while self.is_timer_active and self.timer._remaining_time > 0:
            # Sleep for 1 second
            time.sleep(1)
            
            if self.is_timer_active:  # Check if still active after sleep
                self.timer._remaining_time -= 1
                
                # Update GUI in main thread (thread-safe GUI updates)
                self.parent_app.root.after(0, self.update_timer_display)
        
        # Timer completed - handle session completion
        if self.is_timer_active and self.timer._remaining_time <= 0:
            self.parent_app.root.after(0, self.handle_session_completion)
    
    def handle_session_completion(self):
        """Handle completion of a timer session"""
        # Complete current session
        if isinstance(self.timer, PomodoroTimer):
            current_session = self.timer._current_session_type
            self.timer.complete_session()
            
            # Update display variables
            self.sessions_var.set(f"Sessions Completed: {self.timer.get_total_sessions()}")
            self.session_type_var.set(self._format_session_type(self.timer._current_session_type))
            
            # Show completion message using if-else statements
            if current_session == 'work':
                message = "Work session completed! Time for a break."
                title = "Work Session Complete"
            elif current_session == 'short_break':
                message = "Short break finished! Ready for another work session?"
                title = "Break Complete"
            elif current_session == 'long_break':
                message = "Long break finished! You've earned it. Ready to continue?"
                title = "Long Break Complete"
            else:
                message = "Session completed!"
                title = "Session Complete"
        else:
            # Revision timer
            self.timer.complete_session()
            
            # Update display variables
            self.sessions_var.set(f"Sessions Completed: {self.timer.get_total_sessions()}")
            self.session_type_var.set("Revision")
            
            message = "Revision session completed! Great job focusing."
            title = "Revision Session Complete"
        
        self.update_timer_display()
        
        # Reset timer state
        self.is_timer_active = False
        self.timer.set_running_state(False)
        
        # Update button states
        self.start_btn.config(state='normal', text='▶ Start Next Session')
        self.pause_btn.config(state='disabled')
        
        # Show completion message with auto-start option
        result = messagebox.askyesno(title, f"{message}\n\nWould you like to start the next session automatically?")
        
        if result:
            # Auto-start next session after brief delay
            self.parent_app.root.after(2000, self.start_timer)  # Start after 2 seconds
        
        # Auto-save progress after each completed session
        self.save_data(show_message=False)
    
    def open_settings_dialog(self):
        """Open simple settings configuration dialog"""
        # Create settings window
        settings_window = tk.Toplevel(self.parent_app.root)
        settings_window.title("Timer Settings")
        settings_window.geometry("340x400")
        settings_window.resizable(False, False)
        settings_window.configure(bg=self.parent_app.colors['background'])

        settings_window.transient(self.parent_app.root)
        settings_window.grab_set()
        
        # Main frame
        main_frame = tk.Frame(settings_window, bg=self.parent_app.colors['background'])
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title
        title_label = tk.Label(main_frame, 
                            text="Customize Timer Durations", 
                            font=('Arial', 14, 'bold'),
                            bg=self.parent_app.colors['background'],
                            fg=self.parent_app.colors['text'])
        title_label.pack(pady=(0, 20))
        
        # Depending on timer type, show different settings
        self._settings_vars = {}  # store vars by name

        if isinstance(self.timer, RevisionTimer):
            var = tk.StringVar(value=str(self.timer.get_timer_config()['duration']))
            self._settings_vars['duration'] = var
            label = tk.Label(main_frame, text="Revision Duration (minutes):",
                            bg=self.parent_app.colors['background'],
                            fg=self.parent_app.colors['text'])
            label.pack(anchor='w', pady=(5, 2))
            tk.Entry(main_frame, textvariable=var, font=('Arial', 11), width=20).pack(anchor='w', pady=(0, 10))

        else:  # Pomodoro
            config = self.timer.get_timer_config()
            for key, text in [
                ('work_duration', "Work Duration (minutes):"),
                ('short_break', "Short Break (minutes):"),
                ('long_break', "Long Break (minutes):")
            ]:
                var = tk.StringVar(value=str(config[key]))
                self._settings_vars[key] = var
                label = tk.Label(main_frame, text=text,
                                bg=self.parent_app.colors['background'],
                                fg=self.parent_app.colors['text'])
                label.pack(anchor='w', pady=(5, 2))
                tk.Entry(main_frame, textvariable=var, font=('Arial', 11), width=20).pack(anchor='w', pady=(0, 10))

        def save_settings():
            """Save settings by calling the save function"""
            try:
                if isinstance(self.timer, RevisionTimer):
                    duration = int(self._settings_vars['duration'].get())
                    if duration <= 0:
                        messagebox.showerror("Invalid Input", "Duration must be positive")
                        return
                    success = self.timer.update_config({'duration': duration})
                    
                    if success:
                        if not self.is_timer_active:
                            self.update_timer_display()
                        messagebox.showinfo("Settings Saved", "Timer settings updated successfully!")
                        settings_window.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to update settings")
                        
                else:  # Pomodoro
                    # Get and validate inputs
                    work = int(self._settings_vars['work_duration'].get())
                    shortbreak = int(self._settings_vars['short_break'].get())
                    longbreak = int(self._settings_vars['long_break'].get())
                    
                    # Validation
                    if work <= 0 or shortbreak <= 0 or longbreak <= 0:
                        messagebox.showerror("Invalid Input", "All durations must be positive numbers")
                        return
                    
                    if work > 120:
                        messagebox.showerror("Invalid Input", "Work duration should not exceed 120 minutes")
                        return
                    
                    # Update timer configuration
                    success = self.timer.update_config({
                        'work_duration': work,
                        'short_break': shortbreak,
                        'long_break': longbreak,
                        'sessions_until_long_break': 4
                    })
                    self.data_manager.save_timer_data(self.timer)

                    if success:
                        if not self.is_timer_active:
                            self.update_timer_display()
                        messagebox.showinfo("Settings Saved", "Timer settings updated successfully!")
                        settings_window.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to update settings")
                    
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid numbers only")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save settings: {e}")

        buttons_frame = tk.Frame(main_frame, bg=self.parent_app.colors['background'])
        buttons_frame.pack(pady=(15, 0))

        # Save button
        save_btn = tk.Button(buttons_frame,
                            text="💾 Save Settings",
                            font=('Arial', 10, 'bold'),
                            bg=self.parent_app.colors['success'],
                            fg='white',
                            padx=15,
                            pady=8,
                            command=save_settings,
                            cursor='hand2',
                            relief='flat')
        save_btn.pack(side='left', padx=(0, 10))

        # Cancel button
        cancel_btn = tk.Button(buttons_frame,
                            text="❌ Cancel",
                            font=('Arial', 10),
                            bg=self.parent_app.colors['text'],
                            fg='white',
                            padx=15,
                            pady=8,
                            command=settings_window.destroy,
                            cursor='hand2',
                            relief='flat')
        cancel_btn.pack(side='left')
                
        
    def save_data(self, show_message=True):
        """Save timer data to file"""
        try:
            # Makes it so that save_btn is disabled if it's revision timer
            if self.timer_type_var.get() == "Revision":
                if show_message:
                    messagebox.showinfo("Save Not Available", "Saving progress is not available in Revision mode.")
                return
            
            success = self.data_manager.save_timer_data(self.timer)
            
            if success and show_message:
                messagebox.showinfo("Data Saved", "Your progress has been saved successfully!")
            elif not success and show_message:
                messagebox.showerror("Save Failed", "Failed to save your progress. Please try again.")
                
        except Exception as e:
            if show_message:
                messagebox.showerror("Save Error", f"Error saving data: {e}")
    
    def show_detailed_stats(self):
        """Show detailed statistics in a clean window"""
        stats_window = tk.Toplevel(self.parent_app.root)
        stats_window.resizable(True, True)
        stats_window.title("Study Statistics")
        stats_window.geometry("500x700")
        stats_window.configure(bg=self.parent_app.colors['background'])
        
        # Make window modal
        stats_window.transient(self.parent_app.root)
        
        # Center window
        x = self.parent_app.root.winfo_rootx() + (self.parent_app.root.winfo_width() // 2) - 250
        y = self.parent_app.root.winfo_rooty() + (self.parent_app.root.winfo_height() // 2) - 200
        stats_window.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = tk.Frame(stats_window, bg=self.parent_app.colors['background'])
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="📊 Study Session Statistics", 
                              font=('Arial', 16, 'bold'),
                              bg=self.parent_app.colors['background'],
                              fg=self.parent_app.colors['text'])
        title_label.pack(pady=(0, 20))
        
        # Get statistics
        stats = self.timer.get_statistics()
        
        if stats['total_sessions'] == 0:
            # No data message
            no_data_frame = tk.Frame(main_frame, bg='white', relief='solid', borderwidth=1)
            no_data_frame.pack(fill='both', expand=True, pady=10)
            
            no_data_label = tk.Label(no_data_frame, 
                                    text="📚 No study sessions completed yet!\n\n"
                                         "Start your first Pomodoro session to see\n"
                                         "your statistics and progress here.",
                                    font=('Arial', 12),
                                    bg='white',
                                    fg=self.parent_app.colors['text'],
                                    justify='center')
            no_data_label.pack(expand=True, pady=40)
        else:
            # Statistics display
            stats_frame = tk.Frame(main_frame, bg='white', relief='solid', borderwidth=1)
            stats_frame.pack(fill='both', expand=True, pady=10)
            
            # Create statistics text using string processing
            stats_text = self.generate_simple_statistics(stats)
            
            stats_label = tk.Label(stats_frame,
                                  text=stats_text,
                                  font=('Arial', 11),
                                  bg='white',
                                  fg=self.parent_app.colors['text'],
                                  justify='left',
                                  padx=20,
                                  pady=20)
            stats_label.pack(fill='both', expand=True)
        
        # Close button
        close_btn = tk.Button(main_frame,
                             text="✅ Close",
                             font=('Arial', 11, 'bold'),
                             bg=self.parent_app.colors['primary'],
                             fg='white',
                             padx=25,
                             pady=10,
                             command=stats_window.destroy,
                             cursor='hand2',
                             relief='flat')
        close_btn.pack(pady=(20, 0))
    
    def generate_simple_statistics(self, stats):
        """Generate clean statistics text using string processing"""
        lines = []
        
        # Basic statistics
        lines.append("📈 OVERVIEW")
        lines.append("─" * 30)
        lines.append(f"Sessions Completed: {stats['total_sessions']}")
        lines.append(f"Total Study Time: {stats['total_time']} minutes")
        lines.append(f"All Sessions (with breaks): {stats['completed_sessions']}")
        lines.append("")
        
        # Calculate some additional stats if there are sessions
        if stats['total_sessions'] > 0:
            avg_study_time = stats['total_time'] / stats['total_sessions'] if stats['total_sessions'] > 0 else 0
            lines.append("📊 ADDITIONAL STATS")
            lines.append("─" * 30)
            lines.append(f"Average Work Session: {avg_study_time:.1f} minutes")
            lines.append(f"Study Hours Today: {stats['total_time']/60:.1f} hours")
            lines.append("")
        
        # Recent sessions info
        if len(self.timer._completed_sessions) > 0:
            lines.append("⏰ RECENT ACTIVITY")
            lines.append("─" * 30)
            
            # Get last few sessions using list slicing
            recent_sessions = self.timer._completed_sessions[-5:]  # Last 5 sessions
            
            for i, session in enumerate(reversed(recent_sessions), 1):
                session_type = self._format_session_type(session['type'])
                duration = session['duration']
                lines.append(f"{i}. {session_type} ({duration} min)")
            
            lines.append("")
        
        lines.append("🎯 Keep up the great work!")
        
        # Join all lines using string processing
        return '\n'.join(lines)