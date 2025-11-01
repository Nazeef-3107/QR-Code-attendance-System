"""
QR Attendance System - Kivy Mobile App
Main entry point for the mobile application
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
import requests
import json
import qrcode
import io
import base64
from datetime import datetime

# Configure window for mobile
Window.clearcolor = (0.4, 0.49, 0.92, 1)  # Purple gradient color

# API Base URL - Change this to your deployed Flask API
API_BASE_URL = "http://127.0.0.1:5000"

class QRAttendanceApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user = None
        self.token = None
    
    def build(self):
        self.title = "QR Attendance System"
        self.sm = ScreenManager(transition=SlideTransition())
        
        # Add screens
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(SignupScreen(name='signup'))
        self.sm.add_widget(StudentDashboard(name='student_dashboard'))
        self.sm.add_widget(FacultyDashboard(name='faculty_dashboard'))
        self.sm.add_widget(AdminDashboard(name='admin_dashboard'))
        self.sm.add_widget(ProfileScreen(name='profile'))
        
        return self.sm
    
    def login(self, username, password):
        """Handle user login"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/login",
                json={'username': username, 'password': password},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.current_user = data
                self.token = data.get('access_token')
                return True, data.get('role')
            else:
                return False, response.json().get('msg', 'Login failed')
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def logout(self):
        """Handle user logout"""
        self.current_user = None
        self.token = None
        self.sm.current = 'login'


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Add background color
        with layout.canvas.before:
            Color(0.4, 0.49, 0.92, 1)
            self.rect = Rectangle(size=Window.size, pos=(0, 0))
        
        # Title
        title_label = Label(
            text='🎓 QR Attendance',
            font_size='32sp',
            size_hint=(1, 0.2),
            bold=True,
            color=(1, 1, 1, 1)
        )
        layout.add_widget(title_label)
        
        # Login form container
        form_layout = BoxLayout(
            orientation='vertical',
            padding=dp(30),
            spacing=dp(15),
            size_hint=(1, 0.6)
        )
        
        # Add white background to form
        with form_layout.canvas.before:
            Color(1, 1, 1, 1)
            self.form_rect = RoundedRectangle(
                size=form_layout.size,
                pos=form_layout.pos,
                radius=[dp(15)]
            )
        
        form_layout.bind(
            size=lambda *args: setattr(self.form_rect, 'size', form_layout.size),
            pos=lambda *args: setattr(self.form_rect, 'pos', form_layout.pos)
        )
        
        # Username
        form_layout.add_widget(Label(
            text='Username',
            size_hint=(1, None),
            height=dp(30),
            color=(0.2, 0.2, 0.2, 1),
            halign='left'
        ))
        
        self.username_input = TextInput(
            hint_text='Enter your username',
            multiline=False,
            size_hint=(1, None),
            height=dp(50),
            font_size='16sp',
            padding=[dp(15), dp(15)]
        )
        form_layout.add_widget(self.username_input)
        
        # Password
        form_layout.add_widget(Label(
            text='Password',
            size_hint=(1, None),
            height=dp(30),
            color=(0.2, 0.2, 0.2, 1),
            halign='left'
        ))
        
        self.password_input = TextInput(
            hint_text='Enter your password',
            password=True,
            multiline=False,
            size_hint=(1, None),
            height=dp(50),
            font_size='16sp',
            padding=[dp(15), dp(15)]
        )
        form_layout.add_widget(self.password_input)
        
        # Login button
        login_btn = Button(
            text='Login',
            size_hint=(1, None),
            height=dp(50),
            background_color=(0.4, 0.49, 0.92, 1),
            font_size='18sp',
            bold=True
        )
        login_btn.bind(on_press=self.do_login)
        form_layout.add_widget(login_btn)
        
        # Error message
        self.error_label = Label(
            text='',
            size_hint=(1, None),
            height=dp(30),
            color=(1, 0, 0, 1)
        )
        form_layout.add_widget(self.error_label)
        
        layout.add_widget(form_layout)
        
        # Signup link
        signup_btn = Button(
            text="Don't have an account? Sign Up",
            size_hint=(1, 0.1),
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1),
            font_size='14sp'
        )
        signup_btn.bind(on_press=self.goto_signup)
        layout.add_widget(signup_btn)
        
        self.add_widget(layout)
    
    def do_login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username or not password:
            self.error_label.text = 'Please enter username and password'
            return
        
        app = App.get_running_app()
        success, result = app.login(username, password)
        
        if success:
            # Navigate to appropriate dashboard
            if result == 'student':
                app.sm.current = 'student_dashboard'
            elif result == 'faculty':
                app.sm.current = 'faculty_dashboard'
            elif result == 'admin':
                app.sm.current = 'admin_dashboard'
        else:
            self.error_label.text = str(result)
    
    def goto_signup(self, instance):
        self.manager.current = 'signup'


class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Title
        title = Label(
            text='Create Account',
            font_size='28sp',
            size_hint=(1, 0.1),
            bold=True,
            color=(1, 1, 1, 1)
        )
        layout.add_widget(title)
        
        # Scrollable form
        scroll = ScrollView(size_hint=(1, 0.8))
        form_layout = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(20)
        )
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Role selection
        form_layout.add_widget(Label(
            text='Select Role:',
            size_hint=(1, None),
            height=dp(30),
            color=(1, 1, 1, 1)
        ))
        
        self.role_spinner = Spinner(
            text='Student',
            values=('Student', 'Faculty', 'Admin'),
            size_hint=(1, None),
            height=dp(50),
            font_size='16sp'
        )
        form_layout.add_widget(self.role_spinner)
        
        # Username
        form_layout.add_widget(Label(
            text='Username:',
            size_hint=(1, None),
            height=dp(30),
            color=(1, 1, 1, 1)
        ))
        self.signup_username = TextInput(
            multiline=False,
            size_hint=(1, None),
            height=dp(50)
        )
        form_layout.add_widget(self.signup_username)
        
        # Email
        form_layout.add_widget(Label(
            text='Email:',
            size_hint=(1, None),
            height=dp(30),
            color=(1, 1, 1, 1)
        ))
        self.signup_email = TextInput(
            multiline=False,
            size_hint=(1, None),
            height=dp(50)
        )
        form_layout.add_widget(self.signup_email)
        
        # Password
        form_layout.add_widget(Label(
            text='Password:',
            size_hint=(1, None),
            height=dp(30),
            color=(1, 1, 1, 1)
        ))
        self.signup_password = TextInput(
            password=True,
            multiline=False,
            size_hint=(1, None),
            height=dp(50)
        )
        form_layout.add_widget(self.signup_password)
        
        # Signup button
        signup_btn = Button(
            text='Create Account',
            size_hint=(1, None),
            height=dp(50),
            background_color=(0.16, 0.65, 0.27, 1),
            font_size='18sp'
        )
        signup_btn.bind(on_press=self.do_signup)
        form_layout.add_widget(signup_btn)
        
        # Message label
        self.message_label = Label(
            text='',
            size_hint=(1, None),
            height=dp(40),
            color=(1, 1, 1, 1)
        )
        form_layout.add_widget(self.message_label)
        
        scroll.add_widget(form_layout)
        layout.add_widget(scroll)
        
        # Back to login
        back_btn = Button(
            text='Back to Login',
            size_hint=(1, 0.1),
            background_color=(0.86, 0.21, 0.27, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def do_signup(self, instance):
        # Implementation for signup
        self.message_label.text = 'Signup functionality - Connect to API'


class StudentDashboard(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header
        header = BoxLayout(size_hint=(1, 0.1), spacing=dp(10))
        header.add_widget(Label(
            text='📚 Student Dashboard',
            font_size='24sp',
            bold=True,
            color=(1, 1, 1, 1)
        ))
        logout_btn = Button(
            text='Logout',
            size_hint=(0.3, 1),
            background_color=(0.86, 0.21, 0.27, 1)
        )
        logout_btn.bind(on_press=self.do_logout)
        header.add_widget(logout_btn)
        layout.add_widget(header)
        
        # Scan QR button
        scan_btn = Button(
            text='📷 Scan QR Code',
            size_hint=(1, 0.15),
            background_color=(0.4, 0.49, 0.92, 1),
            font_size='20sp'
        )
        scan_btn.bind(on_press=self.scan_qr)
        layout.add_widget(scan_btn)
        
        # Stats
        stats_layout = GridLayout(cols=2, spacing=dp(10), size_hint=(1, 0.2))
        
        stats_layout.add_widget(self.create_stat_card('Total\nAttendance', '0'))
        stats_layout.add_widget(self.create_stat_card('This\nMonth', '0'))
        
        layout.add_widget(stats_layout)
        
        # Attendance history
        history_label = Label(
            text='Attendance History',
            size_hint=(1, 0.08),
            font_size='20sp',
            color=(1, 1, 1, 1)
        )
        layout.add_widget(history_label)
        
        self.history_scroll = ScrollView(size_hint=(1, 0.47))
        self.history_layout = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None
        )
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        self.history_scroll.add_widget(self.history_layout)
        layout.add_widget(self.history_scroll)
        
        self.add_widget(layout)
    
    def create_stat_card(self, label_text, value_text):
        card = BoxLayout(orientation='vertical', padding=dp(15))
        
        with card.canvas.before:
            Color(1, 1, 1, 1)
            self.card_rect = RoundedRectangle(
                size=card.size,
                pos=card.pos,
                radius=[dp(10)]
            )
        
        card.bind(
            size=lambda *args: setattr(self.card_rect, 'size', card.size),
            pos=lambda *args: setattr(self.card_rect, 'pos', card.pos)
        )
        
        card.add_widget(Label(
            text=label_text,
            font_size='14sp',
            color=(0.4, 0.49, 0.92, 1)
        ))
        card.add_widget(Label(
            text=value_text,
            font_size='32sp',
            bold=True,
            color=(0.4, 0.49, 0.92, 1)
        ))
        
        return card
    
    def scan_qr(self, instance):
        # QR scanning implementation
        pass
    
    def do_logout(self, instance):
        App.get_running_app().logout()


class FacultyDashboard(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header
        header = BoxLayout(size_hint=(1, 0.1), spacing=dp(10))
        header.add_widget(Label(
            text='🏫 Faculty Dashboard',
            font_size='24sp',
            bold=True,
            color=(1, 1, 1, 1)
        ))
        logout_btn = Button(
            text='Logout',
            size_hint=(0.3, 1),
            background_color=(0.86, 0.21, 0.27, 1)
        )
        logout_btn.bind(on_press=self.do_logout)
        header.add_widget(logout_btn)
        layout.add_widget(header)
        
        # Generate QR button
        generate_btn = Button(
            text='⚡ Generate QR Code',
            size_hint=(1, 0.12),
            background_color=(0.16, 0.65, 0.27, 1),
            font_size='20sp'
        )
        generate_btn.bind(on_press=self.generate_qr)
        layout.add_widget(generate_btn)
        
        # QR Code display
        self.qr_image = Image(
            size_hint=(1, 0.4)
        )
        layout.add_widget(self.qr_image)
        
        # View reports button
        reports_btn = Button(
            text='📊 View Attendance Reports',
            size_hint=(1, 0.12),
            background_color=(0.4, 0.49, 0.92, 1),
            font_size='18sp'
        )
        layout.add_widget(reports_btn)
        
        # Sessions list
        self.sessions_scroll = ScrollView(size_hint=(1, 0.26))
        self.sessions_layout = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None
        )
        self.sessions_layout.bind(minimum_height=self.sessions_layout.setter('height'))
        self.sessions_scroll.add_widget(self.sessions_layout)
        layout.add_widget(self.sessions_scroll)
        
        self.add_widget(layout)
    
    def generate_qr(self, instance):
        # Generate QR code
        try:
            response = requests.post(
                f"{API_BASE_URL}/faculty/session/create",
                json={'course_id': 'C001'},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                qr_data = data.get('qr_code')
                
                # Display QR code
                if qr_data:
                    # Decode base64 QR code
                    self.qr_image.source = qr_data
        except Exception as e:
            print(f"Error generating QR: {e}")
    
    def do_logout(self, instance):
        App.get_running_app().logout()


class AdminDashboard(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Header
        header = BoxLayout(size_hint=(1, 0.1), spacing=dp(10))
        header.add_widget(Label(
            text='👔 Admin Dashboard',
            font_size='24sp',
            bold=True,
            color=(1, 1, 1, 1)
        ))
        logout_btn = Button(
            text='Logout',
            size_hint=(0.3, 1),
            background_color=(0.86, 0.21, 0.27, 1)
        )
        logout_btn.bind(on_press=self.do_logout)
        header.add_widget(logout_btn)
        layout.add_widget(header)
        
        # Stats grid
        stats = GridLayout(cols=2, spacing=dp(10), size_hint=(1, 0.3))
        stats.add_widget(self.create_stat_card('Total\nStudents', '0'))
        stats.add_widget(self.create_stat_card('Total\nFaculty', '0'))
        stats.add_widget(self.create_stat_card('Total\nCourses', '0'))
        stats.add_widget(self.create_stat_card('Total\nSessions', '0'))
        layout.add_widget(stats)
        
        # Management buttons
        btn_layout = GridLayout(cols=2, spacing=dp(10), size_hint=(1, 0.3))
        
        users_btn = Button(text='👥 Manage Users', background_color=(0.4, 0.49, 0.92, 1))
        courses_btn = Button(text='📚 Manage Courses', background_color=(0.4, 0.49, 0.92, 1))
        sessions_btn = Button(text='📝 View Sessions', background_color=(0.4, 0.49, 0.92, 1))
        reports_btn = Button(text='📊 Generate Reports', background_color=(0.4, 0.49, 0.92, 1))
        
        btn_layout.add_widget(users_btn)
        btn_layout.add_widget(courses_btn)
        btn_layout.add_widget(sessions_btn)
        btn_layout.add_widget(reports_btn)
        
        layout.add_widget(btn_layout)
        
        # Recent activity
        layout.add_widget(Label(
            text='Recent Activity',
            size_hint=(1, 0.08),
            font_size='20sp',
            color=(1, 1, 1, 1)
        ))
        
        activity_scroll = ScrollView(size_hint=(1, 0.22))
        self.activity_layout = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None
        )
        self.activity_layout.bind(minimum_height=self.activity_layout.setter('height'))
        activity_scroll.add_widget(self.activity_layout)
        layout.add_widget(activity_scroll)
        
        self.add_widget(layout)
    
    def create_stat_card(self, label_text, value_text):
        card = BoxLayout(orientation='vertical', padding=dp(10))
        
        with card.canvas.before:
            Color(1, 1, 1, 1)
            self.card_rect = RoundedRectangle(
                size=card.size,
                pos=card.pos,
                radius=[dp(10)]
            )
        
        card.bind(
            size=lambda *args: setattr(self.card_rect, 'size', card.size),
            pos=lambda *args: setattr(self.card_rect, 'pos', card.pos)
        )
        
        card.add_widget(Label(
            text=label_text,
            font_size='12sp',
            color=(0.4, 0.49, 0.92, 1)
        ))
        card.add_widget(Label(
            text=value_text,
            font_size='28sp',
            bold=True,
            color=(0.4, 0.49, 0.92, 1)
        ))
        
        return card
    
    def do_logout(self, instance):
        App.get_running_app().logout()


class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        layout.add_widget(Label(
            text='👤 Profile',
            font_size='28sp',
            size_hint=(1, 0.1),
            bold=True,
            color=(1, 1, 1, 1)
        ))
        
        # Profile content will be dynamically loaded
        
        back_btn = Button(
            text='Back',
            size_hint=(1, 0.1),
            background_color=(0.86, 0.21, 0.27, 1)
        )
        back_btn.bind(on_press=lambda x: self.manager.transition.direction = 'right')
        layout.add_widget(back_btn)
        
        self.add_widget(layout)


if __name__ == '__main__':
    QRAttendanceApp().run()
