#!/usr/bin/env python3
"""
Build script for creating desktop packages of S3 AI Assistant
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not available"""
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])

def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['modern_desktop_app.py'],
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
        ('requirements.txt', '.'),
        ('README.md', '.'),
        ('docs', 'docs'),
        ('cache', 'cache'),
    ],
    hiddenimports=[
        'tiktoken_ext.openai_public',
        'tiktoken_ext',
        'streamlit',
        'uvicorn',
        'langchain',
        'langchain_community',
        'sentence_transformers',
        'faiss',
        'PyPDF2',
        'pypdf',
        'ollama',
    ],
    hookspath=[],
    hooksconfig={},
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
    
    with open('s3ai_assistant.spec', 'w') as f:
        f.write(spec_content)
    print("✅ Created PyInstaller spec file")

def build_executable():
    """Build the executable"""
    print("🔨 Building executable...")
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm',
        's3ai_assistant.spec'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        print(f"📁 Executable location: dist/S3AIAssistant/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def create_installer_script():
    """Create NSIS installer script for Windows"""
    if sys.platform != 'win32':
        return
    
    nsis_script = '''!define APPNAME "S3 AI Assistant"
!define COMPANYNAME "S3 AI Assistant"
!define DESCRIPTION "AI Assistant for S3 Storage Systems"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0

!define HELPURL "https://github.com/your-repo/s3-ai-assistant"
!define UPDATEURL "https://github.com/your-repo/s3-ai-assistant"
!define ABOUTURL "https://github.com/your-repo/s3-ai-assistant"

!define INSTALLSIZE 500000

RequestExecutionLevel admin

InstallDir "$PROGRAMFILES\\${APPNAME}"

Name "${APPNAME}"
OutFile "S3AIAssistant-Setup.exe"

Page directory
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles

Section "install"
    SetOutPath $INSTDIR
    File /r "dist\\S3AIAssistant\\*"
    
    WriteUninstaller "$INSTDIR\\uninstall.exe"
    
    CreateDirectory "$SMPROGRAMS\\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk" "$INSTDIR\\S3AIAssistant.exe"
    CreateShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\S3AIAssistant.exe"
    
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "UninstallString" "$\\"$INSTDIR\\uninstall.exe$\\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "QuietUninstallString" "$\\"$INSTDIR\\uninstall.exe$\\" /S"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "InstallLocation" "$\\"$INSTDIR$\\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayIcon" "$\\"$INSTDIR\\S3AIAssistant.exe$\\""
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
SectionEnd

Section "uninstall"
    Delete "$SMPROGRAMS\\${APPNAME}\\${APPNAME}.lnk"
    Delete "$DESKTOP\\${APPNAME}.lnk"
    RMDir "$SMPROGRAMS\\${APPNAME}"
    
    RMDir /r $INSTDIR
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}"
SectionEnd
'''
    
    with open('installer.nsi', 'w') as f:
        f.write(nsis_script)
    print("✅ Created NSIS installer script")

def create_launcher_scripts():
    """Create launcher scripts"""
    # Windows batch file
    batch_content = '''@echo off
cd /d "%~dp0"
S3AIAssistant.exe
pause
'''
    
    with open('dist/S3AIAssistant/launch.bat', 'w') as f:
        f.write(batch_content)
    
    # Linux/Mac shell script  
    if sys.platform in ['linux', 'darwin']:
        shell_content = '''#!/bin/bash
cd "$(dirname "$0")"
./S3AIAssistant
'''
        with open('dist/S3AIAssistant/launch.sh', 'w') as f:
            f.write(shell_content)
        os.chmod('dist/S3AIAssistant/launch.sh', 0o755)
    
    print("✅ Created launcher scripts")

def main():
    print("🚀 S3 AI Assistant Package Builder")
    print("=" * 50)
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if build_executable():
        create_launcher_scripts()
        create_installer_script()
        
        print("\n🎉 Package build completed!")
        print("=" * 50)
        print(f"📁 Executable: dist/S3AIAssistant/S3AIAssistant.exe")
        print(f"📁 Full package: dist/S3AIAssistant/")
        
        if sys.platform == 'win32':
            print(f"💿 Installer script: installer.nsi")
            print("   (Use NSIS to compile the installer)")
        
        print("\n📋 To distribute:")
        print("1. Copy the entire 'dist/S3AIAssistant' folder")
        print("2. Users can run S3AIAssistant.exe directly")
        print("3. Or create installer using NSIS (Windows)")
    else:
        print("❌ Package build failed!")

if __name__ == "__main__":
    main()