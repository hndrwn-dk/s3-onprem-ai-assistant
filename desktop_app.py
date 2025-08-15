#!/usr/bin/env python3
"""
Desktop GUI Application for S3 AI Assistant
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import subprocess
import sys
import os
import webbrowser
from pathlib import Path

class S3AIDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("S3 AI Assistant")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Set icon (if available)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        self.setup_ui()
        self.check_dependencies()
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Header
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="🚀 S3 AI Assistant", 
            font=("Arial", 18, "bold"), 
            fg='white', 
            bg='#2c3e50'
        )
        title_label.pack(pady=20)
        
        # Main content area
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Query section
        query_frame = tk.LabelFrame(main_frame, text="Ask a Question", font=("Arial", 12, "bold"))
        query_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.query_var = tk.StringVar()
        query_entry = tk.Entry(
            query_frame, 
            textvariable=self.query_var, 
            font=("Arial", 11),
            width=80
        )
        query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
        
        ask_button = tk.Button(
            query_frame,
            text="Ask",
            command=self.ask_question,
            bg='#3498db',
            fg='white',
            font=("Arial", 11, "bold"),
            width=10
        )
        ask_button.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Results area
        results_frame = tk.LabelFrame(main_frame, text="Answer", font=("Arial", 12, "bold"))
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            height=15,
            font=("Arial", 10),
            bg='white',
            fg='black'
        )
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status bar
        status_frame = tk.Frame(main_frame, bg='#f0f0f0')
        status_frame.pack(fill=tk.X)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Arial", 9),
            fg='#666666',
            bg='#f0f0f0'
        )
        status_label.pack(side=tk.LEFT)
        
        # Control buttons
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Web UI button
        web_button = tk.Button(
            button_frame,
            text="🌐 Open Web UI",
            command=self.open_web_ui,
            bg='#2ecc71',
            fg='white',
            font=("Arial", 10, "bold")
        )
        web_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Add documents button
        docs_button = tk.Button(
            button_frame,
            text="📁 Add Documents",
            command=self.add_documents,
            bg='#e67e22',
            fg='white',
            font=("Arial", 10, "bold")
        )
        docs_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Build index button
        build_button = tk.Button(
            button_frame,
            text="🏗️ Build Index",
            command=self.build_index,
            bg='#9b59b6',
            fg='white',
            font=("Arial", 10, "bold")
        )
        build_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Settings button
        settings_button = tk.Button(
            button_frame,
            text="⚙️ Settings",
            command=self.open_settings,
            bg='#95a5a6',
            fg='white',
            font=("Arial", 10, "bold")
        )
        settings_button.pack(side=tk.RIGHT)
        
        # Bind Enter key to ask question
        query_entry.bind('<Return>', lambda event: self.ask_question())
    
    def check_dependencies(self):
        """Check if required files exist"""
        required_files = [
            'config.py', 's3ai_query.py', 'model_cache.py', 
            'requirements.txt', 'build_embeddings_all.py'
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            messagebox.showwarning(
                "Missing Files",
                f"Some required files are missing:\n{', '.join(missing_files)}\n\n"
                "Please ensure you're running this from the S3 AI Assistant directory."
            )
    
    def ask_question(self):
        """Ask a question using the CLI backend"""
        question = self.query_var.get().strip()
        if not question:
            messagebox.showwarning("Empty Question", "Please enter a question.")
            return
        
        self.status_var.set("Processing...")
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "🤔 Thinking...\n\n")
        self.root.update()
        
        # Run query in background thread
        threading.Thread(target=self._run_query, args=(question,), daemon=True).start()
    
    def _run_query(self, question):
        """Run the query in background thread"""
        try:
            # Use the CLI backend
            result = subprocess.run(
                [sys.executable, 's3ai_query.py', question],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Update UI in main thread
            self.root.after(0, self._update_results, result.stdout, result.stderr, result.returncode)
            
        except subprocess.TimeoutExpired:
            self.root.after(0, self._update_results, "", "Query timed out after 5 minutes", 1)
        except Exception as e:
            self.root.after(0, self._update_results, "", f"Error: {str(e)}", 1)
    
    def _update_results(self, stdout, stderr, returncode):
        """Update results in main thread"""
        self.results_text.delete(1.0, tk.END)
        
        if returncode == 0 and stdout:
            # Extract just the answer part from stdout
            lines = stdout.split('\n')
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
                clean_answer = '\n'.join(answer_lines).strip()
                self.results_text.insert(tk.END, clean_answer)
            else:
                self.results_text.insert(tk.END, stdout)
            
            self.status_var.set("✅ Answer ready")
        else:
            error_msg = stderr if stderr else "No response received"
            self.results_text.insert(tk.END, f"❌ Error: {error_msg}")
            self.status_var.set("❌ Error occurred")
    
    def open_web_ui(self):
        """Open the Streamlit web interface"""
        self.status_var.set("Starting web interface...")
        
        def start_streamlit():
            try:
                subprocess.Popen([
                    sys.executable, '-m', 'streamlit', 'run', 'streamlit_ui.py',
                    '--server.headless', 'true',
                    '--server.port', '8501'
                ])
                
                # Wait a moment then open browser
                threading.Timer(3.0, lambda: webbrowser.open('http://localhost:8501')).start()
                self.root.after(3000, lambda: self.status_var.set("🌐 Web UI opened"))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to start web UI: {e}"))
        
        threading.Thread(target=start_streamlit, daemon=True).start()
    
    def add_documents(self):
        """Add documents to the docs folder"""
        files = filedialog.askopenfilenames(
            title="Select Documents to Add",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("Text files", "*.txt"),
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
                    f"Added {len(copied_files)} documents:\n" + "\n".join(copied_files) +
                    "\n\nDon't forget to rebuild the index!"
                )
                self.status_var.set(f"📁 Added {len(copied_files)} documents")
    
    def build_index(self):
        """Build the vector index"""
        result = messagebox.askyesno(
            "Build Index", 
            "This will rebuild the vector index for all documents.\n"
            "This may take several minutes. Continue?"
        )
        
        if result:
            self.status_var.set("🏗️ Building index...")
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Building vector index...\nThis may take several minutes.\n\n")
            
            def build():
                try:
                    result = subprocess.run(
                        [sys.executable, 'build_embeddings_all.py'],
                        capture_output=True,
                        text=True,
                        timeout=1800  # 30 minute timeout
                    )
                    
                    self.root.after(0, self._update_build_results, result.stdout, result.stderr, result.returncode)
                except Exception as e:
                    self.root.after(0, self._update_build_results, "", f"Error: {str(e)}", 1)
            
            threading.Thread(target=build, daemon=True).start()
    
    def _update_build_results(self, stdout, stderr, returncode):
        """Update build results"""
        if returncode == 0:
            self.results_text.insert(tk.END, "✅ Index built successfully!\n\n")
            self.results_text.insert(tk.END, stdout)
            self.status_var.set("✅ Index built successfully")
        else:
            self.results_text.insert(tk.END, f"❌ Build failed:\n{stderr}")
            self.status_var.set("❌ Build failed")
    
    def open_settings(self):
        """Open settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Settings content
        tk.Label(settings_window, text="Settings", font=("Arial", 14, "bold")).pack(pady=10)
        
        # Model selection
        model_frame = tk.LabelFrame(settings_window, text="LLM Model")
        model_frame.pack(fill=tk.X, padx=20, pady=10)
        
        models = ["phi3:mini", "qwen:latest", "mistral:latest"]
        model_var = tk.StringVar(value="phi3:mini")
        model_combo = ttk.Combobox(model_frame, textvariable=model_var, values=models)
        model_combo.pack(fill=tk.X, padx=10, pady=10)
        
        # Buttons
        button_frame = tk.Frame(settings_window)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Button(
            button_frame, 
            text="Save", 
            command=lambda: self._save_settings(model_var.get(), settings_window)
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        tk.Button(
            button_frame, 
            text="Cancel", 
            command=settings_window.destroy
        ).pack(side=tk.RIGHT)
    
    def _save_settings(self, model, window):
        """Save settings"""
        # Here you could save settings to config file
        messagebox.showinfo("Settings", f"Model set to: {model}")
        window.destroy()

def main():
    root = tk.Tk()
    app = S3AIDesktopApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()