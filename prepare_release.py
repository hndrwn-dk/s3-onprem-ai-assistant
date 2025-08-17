#!/usr/bin/env python3
"""
Prepare GitHub Release for S3 AI Assistant
Creates packaged executables and release notes
"""

import subprocess
import sys
import os
import shutil
import zipfile
import json
from pathlib import Path
from datetime import datetime

VERSION = "1.0.0"
RELEASE_NAME = f"S3 AI Assistant v{VERSION}"

def install_dependencies():
    """Install required packaging dependencies"""
    print("📦 Installing packaging dependencies...")
    dependencies = ['pyinstaller', 'customtkinter']
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} already installed")
        except ImportError:
            print(f"🔧 Installing {dep}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])

def create_spec_file():
    """Create PyInstaller spec file for the release"""
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['ultra_modern_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.py', '.'),
        ('s3ai_query.py', '.'),
        ('streamlit_ui.py', '.'),
        ('api.py', '.'),
        ('model_cache.py', '.'),
        ('bucket_index.py', '.'),
        ('response_cache.py', '.'),
        ('utils.py', '.'),
        ('build_embeddings_all.py', '.'),
        ('validation.py', '.'),
        ('desktop_app.py', '.'),
        ('requirements.txt', '.'),
        ('README.md', '.'),
        ('LICENSE', '.'),
    ] + ([('docs', 'docs')] if os.path.exists('docs') else []) + 
    ([('cache', 'cache')] if os.path.exists('cache') else []) + 
    ([('documentation', 'documentation')] if os.path.exists('documentation') else []) +
    ([('s3_all_docs', 's3_all_docs')] if os.path.exists('s3_all_docs') else []),
    hiddenimports=[
        'customtkinter',
        'tkinter',
        'PIL',
        'streamlit',
        'uvicorn',
        'langchain',
        'langchain_community',
        'sentence_transformers',
        'faiss',
        'faiss-cpu',
        'PyPDF2',
        'pypdf',
        'ollama',
        'requests',
        'numpy',
        'pandas',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='S3AIAssistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='S3AIAssistant',
)
'''
    
    with open('release.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✅ Created release spec file")

def build_executable():
    """Build the executable"""
    print("🔨 Building executable...")
    
    # Clean previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # Build executable
    cmd = ['pyinstaller', '--clean', '--noconfirm', 'release.spec']
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Executable built successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def create_portable_package():
    """Create portable ZIP package"""
    print("📦 Creating portable package...")
    
    if not os.path.exists('dist/S3AIAssistant'):
        print("❌ Executable not found!")
        return False
    
    # Create release directory
    release_dir = f"S3AIAssistant-v{VERSION}"
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    
    # Copy executable files
    shutil.copytree('dist/S3AIAssistant', release_dir)
    
    # Add release files
    release_files = [
        'README.md',
        'LICENSE', 
        'requirements.txt'
    ]
    
    for file in release_files:
        if os.path.exists(file):
            shutil.copy2(file, release_dir)
    
    # Create startup script
    startup_script = f"""@echo off
title S3 AI Assistant v{VERSION}
echo.
echo ========================================
echo   S3 AI Assistant v{VERSION}
echo ========================================
echo.
echo Prerequisites:
echo 1. Ollama must be installed and running
echo 2. At least one model downloaded (e.g., phi3:mini)
echo.
echo Quick setup:
echo   ollama pull phi3:mini
echo.
echo Starting application...
echo.

cd /d "%~dp0"
S3AIAssistant.exe

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo Application encountered an error!
    echo ========================================
    echo.
    echo Troubleshooting:
    echo 1. Make sure Ollama is installed and running
    echo 2. Check that you have a model: ollama list
    echo 3. Try: ollama pull phi3:mini
    echo.
    pause
) else (
    echo.
    echo Application closed normally.
)
"""
    
    with open(f'{release_dir}/START_HERE.bat', 'w', encoding='utf-8') as f:
        f.write(startup_script)
    
    # Create a simple README for users
    user_readme = f"""# S3 AI Assistant v{VERSION}

## Quick Start

1. **Install Ollama** (if not already installed):
   - Download from: https://ollama.ai
   - Install and make sure it's running

2. **Download a model**:
   ```
   ollama pull phi3:mini
   ```

3. **Run the application**:
   - Double-click `START_HERE.bat` 
   - Or run `S3AIAssistant.exe` directly

## First Use

1. Click "📁 Add Documents" to upload your PDFs/TXT files
2. Click "🏗️ Build Index" to process your documents
3. Ask questions in natural language
4. Get AI-powered answers!

## Troubleshooting

### "Missing files" error:
- Make sure you extracted the entire ZIP file
- Run from the extracted folder, not from inside the ZIP

### "No response" from AI:
- Check Ollama is running: `ollama ps`
- Make sure you have a model: `ollama list`
- Try: `ollama pull phi3:mini`

### Application won't start:
- Try running `S3AIAssistant.exe` directly
- Check Windows Defender hasn't blocked the file
- Make sure you have admin rights if needed

## Features

- 🖥️ Modern desktop interface
- 🤖 AI-powered document search
- 📁 Multiple document formats (PDF, TXT, MD, JSON)
- 🌐 Web interface available
- 🔗 REST API included
- ⚙️ Customizable settings

## Support

For issues or questions, visit:
https://github.com/your-repo/s3-ai-assistant/issues
"""
    
    with open(f'{release_dir}/README.txt', 'w', encoding='utf-8') as f:
        f.write(user_readme)
    
    # Create ZIP package
    zip_name = f"{release_dir}-Windows.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, release_dir)
                zipf.write(file_path, f"{release_dir}/{arcname}")
    
    print(f"✅ Created portable package: {zip_name}")
    return zip_name

def create_installer_script():
    """Create NSIS installer script"""
    print("💿 Creating installer script...")
    
    nsis_script = f'''!define APPNAME "S3 AI Assistant"
!define COMPANYNAME "S3 AI Assistant"
!define DESCRIPTION "AI Assistant for S3 Storage Systems"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define VERSION "{VERSION}"

!define HELPURL "https://github.com/your-repo/s3-ai-assistant"
!define UPDATEURL "https://github.com/your-repo/s3-ai-assistant/releases"
!define ABOUTURL "https://github.com/your-repo/s3-ai-assistant"

!define INSTALLSIZE 500000

RequestExecutionLevel admin
InstallDir "$PROGRAMFILES\\${{APPNAME}}"

Name "${{APPNAME}} v${{VERSION}}"
OutFile "S3AIAssistant-v{VERSION}-Setup.exe"
Icon "icon.ico"

Page directory
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles

Section "install"
    SetOutPath $INSTDIR
    File /r "S3AIAssistant-v{VERSION}\\*"
    
    WriteUninstaller "$INSTDIR\\uninstall.exe"
    
    CreateDirectory "$SMPROGRAMS\\${{APPNAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APPNAME}}\\${{APPNAME}}.lnk" "$INSTDIR\\S3AIAssistant.exe"
    CreateShortCut "$SMPROGRAMS\\${{APPNAME}}\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
    CreateShortCut "$DESKTOP\\${{APPNAME}}.lnk" "$INSTDIR\\S3AIAssistant.exe"
    
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "DisplayName" "${{APPNAME}} v${{VERSION}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "UninstallString" "$\\"$INSTDIR\\uninstall.exe$\\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "QuietUninstallString" "$\\"$INSTDIR\\uninstall.exe$\\" /S"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "InstallLocation" "$\\"$INSTDIR$\\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "DisplayIcon" "$\\"$INSTDIR\\S3AIAssistant.exe$\\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "Publisher" "${{COMPANYNAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "HelpLink" "${{HELPURL}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "URLUpdateInfo" "${{UPDATEURL}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "URLInfoAbout" "${{ABOUTURL}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "DisplayVersion" "${{VERSION}}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "VersionMajor" ${{VERSIONMAJOR}}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "VersionMinor" ${{VERSIONMINOR}}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "EstimatedSize" ${{INSTALLSIZE}}
SectionEnd

Section "uninstall"
    Delete "$SMPROGRAMS\\${{APPNAME}}\\${{APPNAME}}.lnk"
    Delete "$SMPROGRAMS\\${{APPNAME}}\\Uninstall.lnk"
    Delete "$DESKTOP\\${{APPNAME}}.lnk"
    RMDir "$SMPROGRAMS\\${{APPNAME}}"
    
    RMDir /r $INSTDIR
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}"
SectionEnd
'''
    
    with open(f'S3AIAssistant-v{VERSION}-installer.nsi', 'w', encoding='utf-8') as f:
        f.write(nsis_script)
    
    print(f"✅ Created installer script: S3AIAssistant-v{VERSION}-installer.nsi")

def create_release_notes():
    """Create release notes"""
    print("📝 Creating release notes...")
    
    release_notes = f"""# 🚀 S3 AI Assistant v{VERSION}

**Release Date:** {datetime.now().strftime('%B %d, %Y')}

## 🎉 What's New

### ✨ **Modern Desktop Application**
- **Beautiful Dark Theme Interface** - Contemporary UI with CustomTkinter
- **Sidebar Navigation** - Easy access to all features
- **Progress Indicators** - Real-time feedback on operations
- **Theme Switching** - Light, Dark, and System modes
- **UI Scaling** - Adjustable from 80% to 120%

### 🔥 **Core Features**
- **AI-Powered Search** - Ask questions in natural language
- **Multi-Format Support** - PDF, TXT, MD, JSON documents
- **Vector Search** - Fast semantic search through documentation
- **Clean Answers** - LLM processes raw text into readable responses
- **Multiple Interfaces** - Desktop GUI, CLI, Web UI, REST API

### 🛠️ **Technical Improvements**
- **Enhanced Vector Loading** - Separate timeout for large indices
- **Improved Error Handling** - Better fallback mechanisms
- **Organized Project Structure** - Clean, professional layout
- **Comprehensive Documentation** - Setup, usage, and deployment guides

## 📦 **Download Options**

### 🖥️ **For End Users (Recommended)**
- **Windows Installer**: `S3AIAssistant-v{VERSION}-Setup.exe`
  - Professional installation with Start Menu and Desktop shortcuts
  - Automatic uninstaller included
  
- **Portable ZIP**: `S3AIAssistant-v{VERSION}-Windows.zip`
  - Extract and run anywhere
  - No installation required
  - Includes startup script

### 👨‍💻 **For Developers**
- **Source Code**: Download the source code to customize or contribute

## 🚀 **Quick Start**

### **Windows Installer:**
1. Download `S3AIAssistant-v{VERSION}-Setup.exe`
2. Run installer (admin rights required)
3. Launch from Start Menu or Desktop shortcut

### **Portable Version:**
1. Download `S3AIAssistant-v{VERSION}-Windows.zip`
2. Extract to desired folder
3. Run `START_HERE.bat` or `S3AIAssistant.exe`

### **First Use:**
1. **Install Ollama** - Download from [ollama.ai](https://ollama.ai)
2. **Pull a model**: `ollama pull phi3:mini`
3. **Add Documents** - Click "📁 Add Documents" in the app
4. **Build Index** - Click "🏗️ Build Index"
5. **Ask Questions** - Type your questions and get AI answers!

## 🔧 **System Requirements**

### **Minimum:**
- Windows 10/11 (64-bit)
- 4GB RAM
- 2GB disk space
- Internet connection (for initial setup)

### **Recommended:**
- Windows 11 (64-bit)
- 8GB+ RAM
- SSD storage
- Ollama installed locally

## 🎯 **Perfect For**

✅ **DevOps Teams** - Quick access to infrastructure documentation  
✅ **Storage Administrators** - S3, MinIO, Cloudian, IBM Cloud Object Storage  
✅ **Enterprise Users** - Professional desktop application  
✅ **Air-gapped Environments** - Works offline after setup  

## 🐛 **Bug Fixes**

- Fixed vector search timeout issues with large indices
- Resolved LLM hanging problems
- Improved text formatting from PDF extraction
- Enhanced error messages and troubleshooting

## 🔄 **Breaking Changes**

- Minimum Python version: 3.8+
- CustomTkinter required for modern desktop interface
- New configuration parameters for timeouts

## 📚 **Documentation**

- **Setup Guide**: `documentation/DEPLOYMENT.md`
- **Packaging Guide**: `documentation/PACKAGING.md`
- **Testing Guide**: `documentation/TESTING.md`

## 🤝 **Contributing**

See `documentation/CONTRIBUTING.md` for development setup and contribution guidelines.

## 📄 **License**

This project is licensed under the MIT License - see the `LICENSE` file for details.

---

**🎉 Enjoy your new AI-powered S3 documentation assistant!**

For support, issues, or feature requests, please visit our [GitHub Issues](https://github.com/your-repo/s3-ai-assistant/issues) page.
"""
    
    with open(f'RELEASE_NOTES_v{VERSION}.md', 'w', encoding='utf-8') as f:
        f.write(release_notes)
    
    print(f"✅ Created release notes: RELEASE_NOTES_v{VERSION}.md")
    return f'RELEASE_NOTES_v{VERSION}.md'

def create_github_release_info():
    """Create GitHub release information"""
    print("📋 Creating GitHub release info...")
    
    release_info = {
        "tag_name": f"v{VERSION}",
        "target_commitish": "main",
        "name": RELEASE_NAME,
        "body": f"See RELEASE_NOTES_v{VERSION}.md for detailed information.",
        "draft": True,
        "prerelease": False
    }
    
    with open('github_release.json', 'w', encoding='utf-8') as f:
        json.dump(release_info, f, indent=2, ensure_ascii=False)
    
    print("✅ Created GitHub release info: github_release.json")

def main():
    print(f"🚀 Preparing GitHub Release: {RELEASE_NAME}")
    print("=" * 60)
    
    # Install dependencies
    install_dependencies()
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if not build_executable():
        print("❌ Failed to build executable!")
        return False
    
    # Create packages
    zip_file = create_portable_package()
    if not zip_file:
        print("❌ Failed to create portable package!")
        return False
    
    # Create installer script
    create_installer_script()
    
    # Create release notes
    release_notes_file = create_release_notes()
    
    # Create GitHub release info
    create_github_release_info()
    
    print("\n🎉 Release preparation completed!")
    print("=" * 60)
    print(f"📦 Portable Package: {zip_file}")
    print(f"💿 Installer Script: S3AIAssistant-v{VERSION}-installer.nsi")
    print(f"📝 Release Notes: {release_notes_file}")
    print(f"📋 GitHub Info: github_release.json")
    
    print("\n📋 Next Steps:")
    print("1. Test the executable in dist/S3AIAssistant/")
    print("2. (Optional) Compile installer with NSIS")
    print("3. Create GitHub release:")
    print("   - Go to GitHub → Releases → New Release")
    print(f"   - Tag: v{VERSION}")
    print(f"   - Title: {RELEASE_NAME}")
    print(f"   - Upload: {zip_file}")
    print("   - Copy content from RELEASE_NOTES file")
    print("4. Publish release!")
    
    return True

if __name__ == "__main__":
    main()