#!/usr/bin/env python3
"""
Flutter-Style Desktop App using Flet
Provides a mobile-app-like experience with Material Design
"""

import flet as ft
import threading
import subprocess
import sys
import os
import time
from pathlib import Path
from tkinter import filedialog
import tkinter as tk

class S3AIFlutterApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        self.build_ui()
    
    def setup_page(self):
        """Configure the page settings"""
        self.page.title = "S3 AI Assistant"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_min_width = 900
        self.page.window_min_height = 600
        
        # Modern color scheme
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.INDIGO,
            use_material3=True
        )
    
    def build_ui(self):
        """Build the main UI"""
        # App Bar
        self.page.appbar = ft.AppBar(
            title=ft.Text("🚀 S3 AI Assistant", size=24, weight=ft.FontWeight.BOLD),
            center_title=True,
            bgcolor=ft.Colors.INDIGO,
            color=ft.Colors.WHITE,
            actions=[
                ft.IconButton(
                    icon=ft.icons.SETTINGS,
                    tooltip="Settings",
                    on_click=self.open_settings
                ),
                ft.IconButton(
                    icon=ft.icons.INFO,
                    tooltip="About",
                    on_click=self.show_about
                )
            ]
        )
        
        # Status and progress
        self.status_text = ft.Text("Ready", size=14, color=ft.Colors.GREY_600)
        self.progress_bar = ft.ProgressBar(width=200, height=4, visible=False)
        
        # Query input
        self.query_input = ft.TextField(
            label="Ask a question about your S3 documentation",
            hint_text="e.g., How to purge bucket in Cloudian Hyperstore?",
            expand=True,
            multiline=False,
            on_submit=self.ask_question
        )
        
        self.ask_button = ft.ElevatedButton(
            text="Ask",
            icon=ft.icons.SEND,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.INDIGO,
                color=ft.Colors.WHITE,
                padding=ft.padding.all(16)
            ),
            on_click=self.ask_question
        )
        
        # Results area
        self.results_container = ft.Container(
            content=self.create_welcome_content(),
            expand=True,
            bgcolor=ft.Colors.GREY_50,
            border_radius=12,
            padding=20,
            border=ft.border.all(1, ft.Colors.GREY_300)
        )
        
        # Sidebar with actions
        sidebar = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.FOLDER_OPEN,
                    selected_icon=ft.icons.FOLDER,
                    label="Add Docs"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.BUILD,
                    selected_icon=ft.icons.BUILD_CIRCLE,
                    label="Build Index"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.WEB,
                    selected_icon=ft.icons.WEB_ASSET,
                    label="Web UI"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.API,
                    selected_icon=ft.icons.CLOUD,
                    label="API"
                ),
            ],
            on_change=self.handle_navigation
        )
        
        # Main layout
        main_content = ft.Column([
            ft.Row([
                self.query_input,
                self.ask_button
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            ft.Text("💬 AI Response", size=18, weight=ft.FontWeight.BOLD),
            self.results_container,
            ft.Row([
                self.status_text,
                self.progress_bar
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ], expand=True, spacing=10)
        
        # Add everything to page
        self.page.add(
            ft.Row([
                sidebar,
                ft.VerticalDivider(width=1),
                ft.Container(
                    content=main_content,
                    expand=True,
                    padding=20
                )
            ], expand=True)
        )
    
    def create_welcome_content(self):
        """Create welcome content"""
        return ft.Column([
            ft.Text("Welcome to S3 AI Assistant! 🎉", 
                   size=28, weight=ft.FontWeight.BOLD, 
                   text_align=ft.TextAlign.CENTER),
            ft.Text("Your intelligent companion for S3 storage documentation",
                   size=16, color=ft.Colors.GREY_600,
                   text_align=ft.TextAlign.CENTER),
            ft.Divider(height=40, color=ft.Colors.TRANSPARENT),
            
            # Feature cards
            ft.Row([
                self.create_feature_card("🤖", "AI-Powered", "Natural language queries"),
                self.create_feature_card("📚", "Multi-Format", "PDF, TXT, MD, JSON"),
                self.create_feature_card("⚡", "Fast Search", "Vector semantic search"),
                self.create_feature_card("🎨", "Modern UI", "Beautiful interface"),
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND, wrap=True),
            
            ft.Divider(height=40, color=ft.Colors.TRANSPARENT),
            ft.Text("🚀 Quick Start:", size=18, weight=ft.FontWeight.BOLD),
            ft.Text("1. Add Documents → 2. Build Index → 3. Ask Questions", 
                   size=14, color=ft.Colors.GREY_600)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
    
    def create_feature_card(self, icon, title, description):
        """Create a feature card"""
        return ft.Container(
            content=ft.Column([
                ft.Text(icon, size=32),
                ft.Text(title, size=16, weight=ft.FontWeight.BOLD),
                ft.Text(description, size=12, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            width=200,
            height=120,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            padding=15,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 5)
            )
        )
    
    def update_status(self, message, progress=None):
        """Update status and progress"""
        self.status_text.value = message
        if progress is not None:
            self.progress_bar.value = progress / 100
            self.progress_bar.visible = progress > 0
        self.page.update()
    
    def show_snackbar(self, message, bgcolor=ft.Colors.GREEN):
        """Show snackbar notification"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=bgcolor
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def handle_navigation(self, e):
        """Handle navigation rail clicks"""
        index = e.control.selected_index
        
        if index == 0:  # Add Documents
            self.add_documents()
        elif index == 1:  # Build Index
            self.build_index()
        elif index == 2:  # Web UI
            self.open_web_ui()
        elif index == 3:  # API
            self.start_api()
    
    def ask_question(self, e=None):
        """Ask a question"""
        question = self.query_input.value.strip()
        if not question:
            self.show_snackbar("Please enter a question", ft.Colors.ORANGE)
            return
        
        self.ask_button.disabled = True
        self.ask_button.text = "Processing..."
        self.update_status("🤔 Processing your question...", 10)
        
        self.results_container.content = ft.Container(
            content=ft.Column([
                ft.ProgressRing(),
                ft.Text("🤔 Thinking about your question...", size=16),
                ft.Text("This may take 30-60 seconds for complex queries", 
                       size=12, color=ft.Colors.GREY_600)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            padding=40
        )
        self.page.update()
        
        # Run in background thread
        threading.Thread(target=self._process_question, args=(question,), daemon=True).start()
    
    def _process_question(self, question):
        """Process question in background"""
        try:
            self.page.run_thread(lambda: self.update_status("🔍 Searching documents...", 30))
            
            # Check if running as executable or from source
            if getattr(sys, 'frozen', False):
                app_dir = sys._MEIPASS
                s3ai_script = os.path.join(app_dir, 's3ai_query.py')
                cmd = [sys.executable, s3ai_script, question]
                cwd = app_dir
            else:
                cmd = [sys.executable, 's3ai_query.py', question]
                cwd = os.getcwd()
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=cwd
            )
            
            def update_ui():
                if result.returncode == 0 and result.stdout:
                    # Extract clean answer
                    lines = result.stdout.split('\\n')
                    answer_started = False
                    answer_lines = []
                    
                    for line in lines:
                        if '🤖 AI-PROCESSED ANSWER' in line or 'Answer:' in line:
                            answer_started = True
                            continue
                        elif answer_started and ('=' * 50 in line or line.startswith('INFO:')):
                            break
                        elif answer_started:
                            answer_lines.append(line)
                    
                    if answer_lines:
                        clean_answer = '\\n'.join(answer_lines).strip()
                        self.results_container.content = ft.Container(
                            content=ft.Text(clean_answer, size=14, selectable=True),
                            padding=20
                        )
                    else:
                        self.results_container.content = ft.Container(
                            content=ft.Text(result.stdout, size=14, selectable=True),
                            padding=20
                        )
                    
                    self.update_status("✅ Answer ready!", 100)
                    self.show_snackbar("Answer generated successfully!")
                else:
                    error_msg = result.stderr if result.stderr else "No response received"
                    self.results_container.content = ft.Container(
                        content=ft.Column([
                            ft.Text("❌ Error:", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
                            ft.Text(error_msg, size=14),
                            ft.Divider(),
                            ft.Text("Troubleshooting:", weight=ft.FontWeight.BOLD),
                            ft.Text("• Make sure you've built the vector index"),
                            ft.Text("• Check that Ollama is running"),
                            ft.Text("• Verify your documents are in the docs/ folder")
                        ], spacing=5),
                        padding=20
                    )
                    self.update_status("❌ Error occurred", 0)
                    self.show_snackbar("Failed to get answer", ft.Colors.RED)
                
                self.ask_button.disabled = False
                self.ask_button.text = "Ask"
                self.page.update()
            
            self.page.run_thread(update_ui)
            
        except Exception as e:
            def error_ui():
                self.results_container.content = ft.Container(
                    content=ft.Text(f"❌ Error: {str(e)}", color=ft.Colors.RED),
                    padding=20
                )
                self.ask_button.disabled = False
                self.ask_button.text = "Ask"
                self.update_status("❌ Error occurred", 0)
                self.show_snackbar("Request failed", ft.Colors.RED)
            
            self.page.run_thread(error_ui)
    
    def add_documents(self):
        """Add documents"""
        def _add_docs():
            try:
                # Create hidden tkinter root for file dialog
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                
                files = filedialog.askopenfilenames(
                    title="Select Documents to Add",
                    filetypes=[
                        ("PDF files", "*.pdf"),
                        ("Text files", "*.txt"),
                        ("Markdown files", "*.md"),
                        ("JSON files", "*.json"),
                        ("All files", "*.*")
                    ]
                )
                
                root.destroy()
                
                if files:
                    docs_dir = Path("docs")
                    docs_dir.mkdir(exist_ok=True)
                    
                    copied_files = []
                    for file_path in files:
                        try:
                            import shutil
                            dest_path = docs_dir / Path(file_path).name
                            shutil.copy2(file_path, dest_path)
                            copied_files.append(Path(file_path).name)
                        except Exception as e:
                            self.page.run_thread(lambda: self.show_snackbar(f"Failed to copy {file_path}", ft.Colors.RED))
                            return
                    
                    def success_ui():
                        self.show_snackbar(f"Added {len(copied_files)} documents successfully!")
                        self.update_status(f"📁 Added {len(copied_files)} documents", 100)
                    
                    self.page.run_thread(success_ui)
                else:
                    self.page.run_thread(lambda: self.show_snackbar("No files selected", ft.Colors.ORANGE))
                    
            except Exception as e:
                self.page.run_thread(lambda: self.show_snackbar(f"Error: {str(e)}", ft.Colors.RED))
        
        self.update_status("📁 Opening file dialog...", 20)
        threading.Thread(target=_add_docs, daemon=True).start()
    
    def build_index(self):
        """Build vector index"""
        def confirm_build(e):
            if e.control.text == "Continue":
                dialog.open = False
                self.page.update()
                self._do_build_index()
            else:
                dialog.open = False
                self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Build Index"),
            content=ft.Text("This will rebuild the vector index for all documents.\\n\\nThis may take several minutes. Continue?"),
            actions=[
                ft.TextButton("Cancel", on_click=confirm_build),
                ft.TextButton("Continue", on_click=confirm_build),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _do_build_index(self):
        """Actually build the index"""
        def _build():
            try:
                self.page.run_thread(lambda: self.update_status("🏗️ Building vector index...", 10))
                
                self.page.run_thread(lambda: setattr(self.results_container, 'content', ft.Container(
                    content=ft.Column([
                        ft.ProgressRing(),
                        ft.Text("🏗️ Building vector index...", size=16),
                        ft.Text("This process:", weight=ft.FontWeight.BOLD),
                        ft.Text("• Reads all documents in docs/ folder"),
                        ft.Text("• Splits them into chunks"),
                        ft.Text("• Creates embeddings"),
                        ft.Text("• Builds searchable index"),
                        ft.Text("Please wait...", color=ft.Colors.GREY_600)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    padding=40
                )))
                self.page.run_thread(lambda: self.page.update())
                
                # Check if running as executable or from source
                if getattr(sys, 'frozen', False):
                    app_dir = sys._MEIPASS
                    build_script = os.path.join(app_dir, 'build_embeddings_all.py')
                    cmd = [sys.executable, build_script]
                    cwd = app_dir
                else:
                    cmd = [sys.executable, 'build_embeddings_all.py']
                    cwd = os.getcwd()
                
                self.page.run_thread(lambda: self.update_status("📚 Processing documents...", 30))
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=1800,  # 30 minutes
                    cwd=cwd
                )
                
                def finish_ui():
                    if result.returncode == 0:
                        self.results_container.content = ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=48),
                                ft.Text("✅ Vector index built successfully!", size=18, weight=ft.FontWeight.BOLD),
                                ft.Text("🎉 Your documents are now ready for AI-powered search."),
                                ft.Text("You can now ask questions about your S3 documentation and get intelligent answers."),
                                ft.Text("💡 Try asking a question above!", color=ft.Colors.INDIGO)
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                            padding=40
                        )
                        self.update_status("✅ Index built successfully!", 100)
                        self.show_snackbar("Index built successfully!")
                    else:
                        self.results_container.content = ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.icons.ERROR, color=ft.Colors.RED, size=48),
                                ft.Text("❌ Build failed:", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
                                ft.Text(result.stderr or "Unknown error"),
                                ft.Divider(),
                                ft.Text("Troubleshooting:", weight=ft.FontWeight.BOLD),
                                ft.Text("• Make sure you have documents in docs/ folder"),
                                ft.Text("• Check Python dependencies are installed"),
                                ft.Text("• Verify Ollama is running")
                            ], spacing=5),
                            padding=40
                        )
                        self.update_status("❌ Build failed", 0)
                        self.show_snackbar("Build failed", ft.Colors.RED)
                    
                    self.page.update()
                
                self.page.run_thread(finish_ui)
                
            except Exception as e:
                self.page.run_thread(lambda: self.show_snackbar(f"Build error: {str(e)}", ft.Colors.RED))
        
        threading.Thread(target=_build, daemon=True).start()
    
    def open_web_ui(self):
        """Open web UI"""
        self.update_status("🌐 Starting web interface...", 50)
        
        def _start_web():
            try:
                subprocess.Popen([
                    sys.executable, '-m', 'streamlit', 'run', 'streamlit_ui.py',
                    '--server.headless', 'true',
                    '--server.port', '8501'
                ])
                
                time.sleep(3)
                import webbrowser
                webbrowser.open('http://localhost:8501')
                
                self.page.run_thread(lambda: self.show_snackbar("Web UI opened in browser!"))
                self.page.run_thread(lambda: self.update_status("🌐 Web UI opened in browser", 100))
                
            except Exception as e:
                self.page.run_thread(lambda: self.show_snackbar(f"Failed to start web UI: {str(e)}", ft.Colors.RED))
        
        threading.Thread(target=_start_web, daemon=True).start()
    
    def start_api(self):
        """Start API"""
        self.update_status("🔗 Starting API server...", 50)
        
        def _start_api():
            try:
                subprocess.Popen([
                    sys.executable, '-m', 'uvicorn', 'api:app',
                    '--host', '0.0.0.0',
                    '--port', '8000',
                    '--reload'
                ])
                
                time.sleep(2)
                self.page.run_thread(lambda: self.show_snackbar("API server started on http://localhost:8000"))
                self.page.run_thread(lambda: self.update_status("🔗 API running on http://localhost:8000", 100))
                
            except Exception as e:
                self.page.run_thread(lambda: self.show_snackbar(f"Failed to start API: {str(e)}", ft.Colors.RED))
        
        threading.Thread(target=_start_api, daemon=True).start()
    
    def open_settings(self, e):
        """Open settings dialog"""
        def close_settings(e):
            settings_dialog.open = False
            self.page.update()
        
        settings_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("⚙️ Settings"),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("LLM Model:"),
                    ft.Dropdown(
                        options=[
                            ft.dropdown.Option("phi3:mini"),
                            ft.dropdown.Option("qwen:latest"),
                            ft.dropdown.Option("mistral:latest")
                        ],
                        value="phi3:mini",
                        width=300
                    ),
                    ft.Text("Theme:"),
                    ft.Dropdown(
                        options=[
                            ft.dropdown.Option("Dark"),
                            ft.dropdown.Option("Light"),
                            ft.dropdown.Option("System")
                        ],
                        value="Dark",
                        width=300,
                        on_change=self.change_theme
                    )
                ], spacing=10),
                width=400,
                height=200
            ),
            actions=[
                ft.TextButton("Close", on_click=close_settings)
            ]
        )
        
        self.page.dialog = settings_dialog
        settings_dialog.open = True
        self.page.update()
    
    def change_theme(self, e):
        """Change theme"""
        theme = e.control.value.lower()
        if theme == "dark":
            self.page.theme_mode = ft.ThemeMode.DARK
        elif theme == "light":
            self.page.theme_mode = ft.ThemeMode.LIGHT
        else:
            self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.update()
        self.show_snackbar(f"Switched to {theme} theme")
    
    def show_about(self, e):
        """Show about dialog"""
        def close_about(e):
            about_dialog.open = False
            self.page.update()
        
        about_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("About S3 AI Assistant"),
            content=ft.Container(
                content=ft.Column([
                    ft.Text("🚀 S3 AI Assistant v1.0.0", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Ultra-modern AI assistant for S3 storage documentation"),
                    ft.Divider(),
                    ft.Text("Features:", weight=ft.FontWeight.BOLD),
                    ft.Text("• AI-powered document search"),
                    ft.Text("• Multiple document formats"),
                    ft.Text("• Modern Flutter-style interface"),
                    ft.Text("• Vector semantic search"),
                    ft.Divider(),
                    ft.Text("Built with Flet (Flutter for Python)", color=ft.Colors.GREY_600)
                ], spacing=5),
                width=400,
                height=300
            ),
            actions=[
                ft.TextButton("Close", on_click=close_about)
            ]
        )
        
        self.page.dialog = about_dialog
        about_dialog.open = True
        self.page.update()

def main(page: ft.Page):
    app = S3AIFlutterApp(page)

def run_app():
    # Check if flet is available
    try:
        import flet as ft
    except ImportError:
        print("Installing flet for Flutter-style interface...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flet'])
        import flet as ft
    
    ft.app(target=main, view=ft.AppView.FLET_APP)

if __name__ == "__main__":
    run_app()