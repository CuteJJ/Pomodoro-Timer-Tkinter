import tkinter as tk
from tkinter import messagebox
from PomodoroTimer import StudyTimer, DataManager, PomodoroApplication
# ============================================================================
# GUI APPLICATION IMPLEMENTATION
# ============================================================================

class MainApplication:
    """
    Main application class implementing the complete GUI for the Assistant App.
    """
    
    def __init__(self):
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("Student Assistant App")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # Configure styling
        self.setup_styles()
        
        # Initialize timer and data manager
        self.timer = StudyTimer()
        self.data_manager = DataManager()

        # Initialize Pomodoro App
        self.pomodoro_app = PomodoroApplication(self, self.timer, self.data_manager)

        # Timer control variables
        self.timer_thread = None
        self.is_timer_active = False
        
        # GUI state variables
        self.current_frame = None
        
        # Load saved data if available
        self.load_saved_data()
        
        # Create main interface
        self.create_main_menu()
        
    def setup_styles(self):
        """Configure clean, consistent styling for the application"""
        # Define simple color scheme
        self.colors = {
            'primary': '#4A90E2',      # Blue
            'secondary': '#7B68EE',    # Purple
            'success': '#5CB85C',      # Green
            'background': '#F8F9FA',   # Light gray
            'text': '#343A40',         # Dark gray
            'danger': '#D9534F'        # Red
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['background'])
    
    def create_main_menu(self):
        """
        Create the Assistant App interface with three program options.
        """
        # Clear current frame if exists
        if self.current_frame:
            self.current_frame.destroy()
        
        # Create main frame
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill='both', expand=True, padx=40, pady=40)
        self.current_frame = main_frame
        
        # Application title
        title_label = tk.Label(main_frame, 
                              text="Student Assistant App",
                              font=('Arial', 20, 'bold'),
                              bg=self.colors['background'],
                              fg=self.colors['text'])
        title_label.pack(pady=(0, 10))
        
        # Subtitle
        subtitle_label = tk.Label(main_frame,
                                 text="Choose an application to begin",
                                 font=('Arial', 12),
                                 bg=self.colors['background'],
                                 fg=self.colors['text'])
        subtitle_label.pack(pady=(0, 40))
        
        # Application buttons
        button_frame = tk.Frame(main_frame, bg=self.colors['background'])
        button_frame.pack(expand=True)
        
        # Button 1: Pomodoro Timer
        pomodoro_btn = tk.Button(button_frame,
                                text="📚 Study Pomodoro Timer",
                                font=('Arial', 12),
                                bg=self.colors['primary'],
                                fg='white',
                                padx=40,
                                pady=15,
                                command=self.open_pomodoro_timer,
                                cursor='hand2',
                                relief='flat',
                                borderwidth=0)
        pomodoro_btn.pack(pady=10, fill='x')
        
        # Statistics display (if data exists)
        self.create_statistics_display(main_frame)
        
        # Footer
        footer_label = tk.Label(main_frame,
                               text="Student Assistant Application",
                               font=('Arial', 10),
                               bg=self.colors['background'],
                               fg=self.colors['text'])
        footer_label.pack(side='bottom', pady=(40, 0))

    def create_statistics_display(self, parent_frame):
        """Create a simple statistics display if data exists"""
        stats = self.timer.get_statistics()
        
        # Only show statistics if there are completed sessions
        if stats['total_sessions'] > 0:
            stats_frame = tk.Frame(parent_frame, bg=self.colors['background'])
            stats_frame.pack(pady=(30, 0))
            
            stats_title = tk.Label(stats_frame,
                                  text="Your Progress",
                                  font=('Arial', 12, 'bold'),
                                  bg=self.colors['background'],
                                  fg=self.colors['text'])
            stats_title.pack()
            
            # Create statistics text
            stats_text = f"Work Sessions: {stats['total_sessions']} | Study Time: {stats['total_time']} minutes"
            
            stats_label = tk.Label(stats_frame,
                                  text=stats_text,
                                  font=('Arial', 10),
                                  bg=self.colors['background'],
                                  fg=self.colors['text'])
            stats_label.pack(pady=(5, 0))
    
    def open_pomodoro_timer(self):
        """Open the Pomodoro Timer interface"""
        self.pomodoro_app.create_pomodoro_interface()
    
    def load_saved_data(self):
        """Load previously saved data"""
        try:
            data = self.data_manager.load_timer_data()
            
            if data:
                # Restore timer configuration
                if 'timer_config' in data:
                    self.timer.update_config(data['timer_config'])
                
                # Restore session data
                if 'completed_sessions' in data:
                    self.timer._completed_sessions = data['completed_sessions']
                
                if 'sessions_completed' in data:
                    self.timer._sessions_completed = data['sessions_completed']
                    self.timer._total_sessions = data['sessions_completed']
                
                # Restore other data
                if 'study_notes' in data:
                    self.timer._study_notes = data['study_notes']
                
                if 'daily_goal_minutes' in data:
                    self.timer._daily_goal_minutes = data['daily_goal_minutes']
                
        except Exception as e:
            print(f"Error loading saved data: {e}")
    
    def run(self):
        """Start the GUI application"""
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start the GUI event loop
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing - save data and cleanup"""
        if hasattr(self.pomodoro_app, 'is_timer_active') and self.pomodoro_app.is_timer_active:
            # Ask user if they want to stop the timer
            if messagebox.askyesno("Timer Running", 
                                 "Timer is currently running. Do you want to exit anyway?\n\n" +
                                 "Your progress will be saved automatically."):
                self.pomodoro_app.is_timer_active = False
            else:
                return  # Don't close if user chooses to continue
        
        # Auto-save before closing
        try:
            self.pomodoro_app.save_data(show_message=False)
        except Exception as e:
            print(f"Error saving data on exit: {e}")
        
        # Destroy the window
        self.root.destroy()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main function to run the Assistant App.
    """
    try:
        # Create and run the main application
        app = MainApplication()
        app.run()
        
    except Exception as e:
        # Handle Error
        print(f"Error starting application: {e}")
        messagebox.showerror("Application Error", 
                           f"A fatal error occurred: {e}\n\n" +
                           "Please restart the application.")

if __name__ == "__main__":
    main()