#!/usr/bin/env python3
"""
Modern Desktop GUI Application for S3 AI Assistant
Using CustomTkinter for a contemporary, dark theme interface
"""

import customtkinter as ctk
import threading
import subprocess
import sys
import os
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox
import time

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class ModernS3AIApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.geometry("1000x700")
        self.root.title("S3 AI Assistant")
        
        # Set window icon if available
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        self.setup_ui()
        self.check_dependencies()
    
    def setup_ui(self):
        """Setup the modern user interface"""
        # Configure grid layout
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create sidebar frame
        self.sidebar_frame = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)
        
        # Sidebar logo and title
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="🚀 S3 AI Assistant", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Sidebar buttons
        self.add_docs_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="📁 Add Documents",
            command=self.add_documents,
            height=40
        )
        self.add_docs_btn.grid(row=1, column=0, padx=20, pady=10)
        
        self.build_index_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="🏗️ Build Index",
            command=self.build_index,
            height=40
        )
        self.build_index_btn.grid(row=2, column=0, padx=20, pady=10)
        
        self.web_ui_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="🌐 Web Interface",
            command=self.open_web_ui,
            height=40
        )
        self.web_ui_btn.grid(row=3, column=0, padx=20, pady=10)
        
        self.api_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="🔗 Start API",
            command=self.start_api,
            height=40
        )
        self.api_btn.grid(row=4, column=0, padx=20, pady=10)
        
        self.settings_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="⚙️ Settings",
            command=self.open_settings,
            height=40
        )
        self.settings_btn.grid(row=5, column=0, padx=20, pady=10)
        
        # Appearance mode option menu
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:")
        self.appearance_mode_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode_event
        )
        self.appearance_mode_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 10))
        
        # UI scaling option menu
        self.scaling_label = ctk.CTkLabel(self.sidebar_frame, text="UI Scaling:")
        self.scaling_label.grid(row=9, column=0, padx=20, pady=(10, 0))
        
        self.scaling_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["80%", "90%", "100%", "110%", "120%"],
            command=self.change_scaling_event
        )
        self.scaling_optionemenu.grid(row=10, column=0, padx=20, pady=(10, 20))
        
        # Main content area
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=(20, 20), pady=(20, 20))
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Query section
        self.query_frame = ctk.CTkFrame(self.main_frame)
        self.query_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        self.query_frame.grid_columnconfigure(0, weight=1)
        
        self.query_label = ctk.CTkLabel(
            self.query_frame,
            text="Ask a Question About Your S3 Documentation",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.query_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10))
        
        self.query_entry = ctk.CTkEntry(
            self.query_frame,
            placeholder_text="e.g., How to purge bucket in Cloudian Hyperstore?",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.query_entry.grid(row=1, column=0, sticky="ew", padx=(20, 10), pady=(0, 20))
        
        self.ask_button = ctk.CTkButton(
            self.query_frame,
            text="Ask",
            command=self.ask_question,
            height=40,
            width=80,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.ask_button.grid(row=1, column=1, padx=(0, 20), pady=(0, 20))
        
        # Results area
        self.results_frame = ctk.CTkFrame(self.main_frame)
        self.results_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        self.results_frame.grid_columnconfigure(0, weight=1)
        self.results_frame.grid_rowconfigure(1, weight=1)
        
        self.results_label = ctk.CTkLabel(
            self.results_frame,
            text="AI Response",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.results_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.results_textbox = ctk.CTkTextbox(
            self.results_frame,
            font=ctk.CTkFont(size=13),
            wrap="word"
        )
        self.results_textbox.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Status bar
        self.status_frame = ctk.CTkFrame(self.main_frame, height=40)
        self.status_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.status_frame.grid_columnconfigure(1, weight=1)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(self.status_frame)
        self.progress_bar.grid(row=0, column=1, padx=(10, 20), pady=10, sticky="ew")
        self.progress_bar.set(0)
        
        # Bind Enter key to ask question
        self.query_entry.bind('<Return>', lambda event: self.ask_question())
        
        # Set initial values
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")
        
        # Show welcome message
        self.show_welcome_message()
    
    def show_welcome_message(self):
        """Show welcome message in results area"""
        welcome_text = """🚀 Welcome to S3 AI Assistant!

This AI assistant helps you find information in your S3 storage documentation quickly and accurately.

🔥 Features:
• Ask questions in natural language
• Get AI-powered answers from your documents  
• Modern, dark-themed interface
• Multiple document formats supported (PDF, TXT, MD, JSON)

🚀 Quick Start:
1. Click "📁 Add Documents" to upload your S3 documentation
2. Click "🏗️ Build Index" to process your documents  
3. Ask questions in the text box above
4. Get instant, intelligent answers!

💡 Example Questions:
• "How to purge a bucket in Cloudian Hyperstore?"
• "What are the API endpoints for MinIO?"
• "How to configure bucket policies in IBM Cloud Object Storage?"

Ready to get started? Add your documents and start asking questions!"""
        
        self.results_textbox.delete("0.0", "end")
        self.results_textbox.insert("0.0", welcome_text)
    
    def change_appearance_mode_event(self, new_appearance_mode: str):
        """Change appearance mode"""
        ctk.set_appearance_mode(new_appearance_mode)
    
    def change_scaling_event(self, new_scaling: str):
        """Change UI scaling"""
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)
    
    def check_dependencies(self):
        """Check if required files exist"""
        required_files = [
            'config.py', 's3ai_query.py', 'model_cache.py', 
            'requirements.txt', 'build_embeddings_all.py'
        ]
        
        # Check in current directory or PyInstaller bundle
        base_dir = getattr(sys, '_MEIPASS', os.getcwd())
        missing_files = []
        
        for file in required_files:
            file_path = os.path.join(base_dir, file)
            if not os.path.exists(file_path) and not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files and not getattr(sys, 'frozen', False):
            # Only show warning if not running as executable
            messagebox.showwarning(
                "Missing Files",
                f"Some required files are missing:\\n{', '.join(missing_files)}\\n\\n"
                "Please ensure you're running this from the S3 AI Assistant directory."
            )
    
    def update_status(self, message: str, progress: float = None):
        """Update status message and progress bar"""
        self.status_label.configure(text=message)
        if progress is not None:
            self.progress_bar.set(progress)
        self.root.update()
    
    def ask_question(self):
        """Ask a question using the CLI backend"""
        question = self.query_entry.get().strip()
        if not question:
            messagebox.showwarning("Empty Question", "Please enter a question.")
            return
        
        self.update_status("🤔 Processing your question...", 0.1)
        self.results_textbox.delete("0.0", "end")
        self.results_textbox.insert("0.0", "🤔 Thinking about your question...\\n\\nThis may take 30-60 seconds for complex queries.")
        
        # Disable ask button during processing
        self.ask_button.configure(state="disabled")
        
        # Run query in background thread
        threading.Thread(target=self._run_query, args=(question,), daemon=True).start()
    
    def _run_query(self, question):
        """Run the query in background thread"""
        try:
            self.root.after(0, lambda: self.update_status("🔍 Searching documents...", 0.3))
            
            # Check if running as executable or from source
            if getattr(sys, 'frozen', False):
                # Running as PyInstaller executable
                app_dir = sys._MEIPASS
                s3ai_script = os.path.join(app_dir, 's3ai_query.py')
                cmd = [sys.executable, s3ai_script, question]
            else:
                # Running from source
                cmd = [sys.executable, 's3ai_query.py', question]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=getattr(sys, '_MEIPASS', os.getcwd())  # Set working directory
            )
            
            # Update UI in main thread
            self.root.after(0, self._update_results, result.stdout, result.stderr, result.returncode)
            
        except subprocess.TimeoutExpired:
            self.root.after(0, self._update_results, "", "Query timed out after 5 minutes", 1)
        except Exception as e:
            self.root.after(0, self._update_results, "", f"Error: {str(e)}", 1)
    
    def _update_results(self, stdout, stderr, returncode):
        """Update results in main thread"""
        self.results_textbox.delete("0.0", "end")
        
        if returncode == 0 and stdout:
            # Extract just the answer part from stdout
            lines = stdout.split('\\n')
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
                self.results_textbox.insert("0.0", clean_answer)
            else:
                self.results_textbox.insert("0.0", stdout)
            
            self.update_status("✅ Answer ready!", 1.0)
        else:
            error_msg = stderr if stderr else "No response received"
            self.results_textbox.insert("0.0", f"❌ Error: {error_msg}\\n\\nTroubleshooting:\\n• Make sure you've built the vector index\\n• Check that Ollama is running\\n• Verify your documents are in the docs/ folder")
            self.update_status("❌ Error occurred", 0.0)
        
        # Re-enable ask button
        self.ask_button.configure(state="normal")
    
    def add_documents(self):
        """Add documents to the docs folder"""
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
                    messagebox.showerror("Error", f"Failed to copy {file_path}: {e}")
            
            if copied_files:
                messagebox.showinfo(
                    "Documents Added", 
                    f"✅ Added {len(copied_files)} documents:\\n\\n" + "\\n".join(copied_files) +
                    "\\n\\n💡 Don't forget to rebuild the index to include these documents!"
                )
                self.update_status(f"📁 Added {len(copied_files)} documents", 0.0)
    
    def build_index(self):
        """Build the vector index"""
        result = messagebox.askyesno(
            "Build Index", 
            "🏗️ This will rebuild the vector index for all documents.\\n\\n"
            "⏱️ This may take several minutes depending on document size.\\n\\n"
            "Continue?"
        )
        
        if result:
            self.update_status("🏗️ Building vector index...", 0.1)
            self.results_textbox.delete("0.0", "end")
            self.results_textbox.insert("0.0", "🏗️ Building vector index...\\n\\nThis process:\\n• Reads all documents in docs/ folder\\n• Splits them into chunks\\n• Creates embeddings\\n• Builds searchable index\\n\\nPlease wait...")
            
            # Disable build button
            self.build_index_btn.configure(state="disabled")
            
            def build():
                try:
                    self.root.after(0, lambda: self.update_status("📚 Processing documents...", 0.3))
                    
                    # Check if running as executable or from source
                    if getattr(sys, 'frozen', False):
                        # Running as PyInstaller executable
                        app_dir = sys._MEIPASS
                        build_script = os.path.join(app_dir, 'build_embeddings_all.py')
                        cmd = [sys.executable, build_script]
                    else:
                        # Running from source
                        cmd = [sys.executable, 'build_embeddings_all.py']
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=1800,  # 30 minute timeout
                        cwd=getattr(sys, '_MEIPASS', os.getcwd())  # Set working directory
                    )
                    
                    self.root.after(0, self._update_build_results, result.stdout, result.stderr, result.returncode)
                except Exception as e:
                    self.root.after(0, self._update_build_results, "", f"Error: {str(e)}", 1)
            
            threading.Thread(target=build, daemon=True).start()
    
    def _update_build_results(self, stdout, stderr, returncode):
        """Update build results"""
        if returncode == 0:
            self.results_textbox.delete("0.0", "end")
            self.results_textbox.insert("0.0", "✅ Vector index built successfully!\\n\\n🎉 Your documents are now ready for AI-powered search.\\n\\nYou can now ask questions about your S3 documentation and get intelligent answers.\\n\\n💡 Try asking a question in the text box above!")
            self.update_status("✅ Index built successfully!", 1.0)
        else:
            self.results_textbox.delete("0.0", "end")
            self.results_textbox.insert("0.0", f"❌ Build failed:\\n\\n{stderr}\\n\\nTroubleshooting:\\n• Make sure you have documents in docs/ folder\\n• Check Python dependencies are installed\\n• Verify Ollama is running")
            self.update_status("❌ Build failed", 0.0)
        
        # Re-enable build button
        self.build_index_btn.configure(state="normal")
    
    def open_web_ui(self):
        """Open the Streamlit web interface"""
        self.update_status("🌐 Starting web interface...", 0.2)
        
        def start_streamlit():
            try:
                subprocess.Popen([
                    sys.executable, '-m', 'streamlit', 'run', 'streamlit_ui.py',
                    '--server.headless', 'true',
                    '--server.port', '8501'
                ])
                
                # Wait a moment then open browser
                time.sleep(3)
                webbrowser.open('http://localhost:8501')
                self.root.after(3000, lambda: self.update_status("🌐 Web UI opened in browser", 1.0))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to start web UI: {e}"))
                self.root.after(0, lambda: self.update_status("❌ Failed to start web UI", 0.0))
        
        threading.Thread(target=start_streamlit, daemon=True).start()
    
    def start_api(self):
        """Start the REST API server"""
        self.update_status("🔗 Starting API server...", 0.2)
        
        def start_api():
            try:
                subprocess.Popen([
                    sys.executable, '-m', 'uvicorn', 'api:app',
                    '--host', '0.0.0.0',
                    '--port', '8000',
                    '--reload'
                ])
                
                time.sleep(2)
                self.root.after(2000, lambda: self.update_status("🔗 API running on http://localhost:8000", 1.0))
                self.root.after(2000, lambda: messagebox.showinfo("API Started", "🔗 REST API is now running!\\n\\nEndpoint: http://localhost:8000\\nDocs: http://localhost:8000/docs"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to start API: {e}"))
                self.root.after(0, lambda: self.update_status("❌ Failed to start API", 0.0))
        
        threading.Thread(target=start_api, daemon=True).start()
    
    def open_settings(self):
        """Open settings dialog"""
        settings = ctk.CTkToplevel(self.root)
        settings.geometry("500x400")
        settings.title("Settings")
        settings.transient(self.root)
        settings.grab_set()
        
        # Settings content
        title_label = ctk.CTkLabel(settings, text="⚙️ Settings", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=20)
        
        # Model selection frame
        model_frame = ctk.CTkFrame(settings)
        model_frame.pack(fill="x", padx=20, pady=10)
        
        model_label = ctk.CTkLabel(model_frame, text="LLM Model:", font=ctk.CTkFont(size=14, weight="bold"))
        model_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        models = ["phi3:mini", "qwen:latest", "mistral:latest"]
        model_var = ctk.StringVar(value="phi3:mini")
        model_menu = ctk.CTkOptionMenu(model_frame, variable=model_var, values=models)
        model_menu.pack(fill="x", padx=20, pady=(0, 20))
        
        # Timeout settings
        timeout_frame = ctk.CTkFrame(settings)
        timeout_frame.pack(fill="x", padx=20, pady=10)
        
        timeout_label = ctk.CTkLabel(timeout_frame, text="Query Timeout (seconds):", font=ctk.CTkFont(size=14, weight="bold"))
        timeout_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        timeout_var = ctk.StringVar(value="120")
        timeout_entry = ctk.CTkEntry(timeout_frame, textvariable=timeout_var)
        timeout_entry.pack(fill="x", padx=20, pady=(0, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(settings)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        save_btn = ctk.CTkButton(
            button_frame, 
            text="💾 Save Settings", 
            command=lambda: self._save_settings(model_var.get(), timeout_var.get(), settings)
        )
        save_btn.pack(side="right", padx=(10, 20), pady=20)
        
        cancel_btn = ctk.CTkButton(
            button_frame, 
            text="❌ Cancel", 
            command=settings.destroy
        )
        cancel_btn.pack(side="right", pady=20)
    
    def _save_settings(self, model, timeout, window):
        """Save settings"""
        messagebox.showinfo("Settings Saved", f"✅ Settings saved!\\n\\nLLM Model: {model}\\nTimeout: {timeout}s")
        window.destroy()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    # Check if customtkinter is available
    try:
        import customtkinter
    except ImportError:
        print("🔧 Installing customtkinter for modern interface...")
        print("This will take a moment...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'customtkinter'])
            print("✅ Installation completed!")
            print("🔄 Please run the command again: python modern_desktop_app.py")
            return
        except Exception as e:
            print(f"❌ Failed to install customtkinter: {e}")
            print("📋 Please install manually:")
            print("   pip install customtkinter")
            print("   Then run: python modern_desktop_app.py")
            return
    
    app = ModernS3AIApp()
    app.run()

if __name__ == "__main__":
    main()