"""
Utility for handling SentencePiece installation issues.
This module provides functions to help users install SentencePiece
when standard pip installation methods fail.
"""
import os
import sys
import platform
import subprocess
import tempfile
import shutil
from pathlib import Path
import logging
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)

def check_sentencepiece() -> Tuple[bool, Optional[str]]:
    """
    Check if SentencePiece is installed and working
    
    Returns:
        Tuple of (installed, version)
    """
    try:
        import sentencepiece
        return True, sentencepiece.__version__
    except ImportError:
        return False, None

def system_requirements_met() -> bool:
    """
    Check if system meets requirements for building SentencePiece
    
    Returns:
        True if requirements met, False otherwise
    """
    if platform.system() == "Windows":
        # Check for Visual Studio
        vs_path = os.environ.get("VS140COMNTOOLS")
        if not vs_path:
            return False
        return True
    elif platform.system() == "Linux":
        # Check for build tools
        try:
            subprocess.run(["cmake", "--version"], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE, 
                           check=True)
            subprocess.run(["g++", "--version"], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE, 
                           check=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    elif platform.system() == "Darwin":  # macOS
        # Check for Xcode command line tools
        try:
            subprocess.run(["xcode-select", "-p"], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE, 
                           check=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    return False

def install_system_dependencies() -> bool:
    """
    Install system dependencies required for building SentencePiece
    
    Returns:
        True if successful, False otherwise
    """
    if platform.system() == "Linux":
        # Check for apt-get (Debian/Ubuntu)
        try:
            # Check for apt
            subprocess.run(["apt-get", "--version"], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE, 
                           check=True)
            
            print("Installing system dependencies...")
            cmd = [
                "sudo", "apt-get", "update", "&&",
                "sudo", "apt-get", "install", "-y",
                "cmake", "build-essential", "pkg-config", "libprotobuf-dev", 
                "protobuf-compiler", "libgoogle-perftools-dev"
            ]
            
            # Run as a single shell command with &&
            result = subprocess.run(" ".join(cmd), shell=True, check=False)
            
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
            
        # Check for yum (RedHat/CentOS)
        try:
            subprocess.run(["yum", "--version"], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE, 
                           check=True)
            
            print("Installing system dependencies using yum...")
            cmd = [
                "sudo", "yum", "install", "-y",
                "cmake", "gcc-c++", "make", "protobuf-devel"
            ]
            
            result = subprocess.run(cmd, check=False)
            
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
    
    elif platform.system() == "Darwin":  # macOS
        try:
            # Check for brew
            subprocess.run(["brew", "--version"], 
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE, 
                           check=True)
            
            print("Installing system dependencies using brew...")
            cmd = ["brew", "install", "cmake", "protobuf"]
            
            result = subprocess.run(cmd, check=False)
            
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
    
    # If we get here, we couldn't install dependencies
    print("Could not automatically install system dependencies.")
    print("Please install the required dependencies manually.")
    if platform.system() == "Linux":
        print("For Debian/Ubuntu: sudo apt-get install cmake build-essential pkg-config libprotobuf-dev protobuf-compiler libgoogle-perftools-dev")
        print("For RedHat/CentOS: sudo yum install cmake gcc-c++ make protobuf-devel")
    elif platform.system() == "Darwin":
        print("Using Homebrew: brew install cmake protobuf")
    elif platform.system() == "Windows":
        print("Install Visual Studio with C++ support and CMake")
    
    return False

def build_from_source() -> bool:
    """
    Build SentencePiece from source
    
    Returns:
        True if successful, False otherwise
    """
    print("Building SentencePiece from source...")
    
    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir)
            
            # Clone the repository
            print("Cloning SentencePiece repository...")
            subprocess.run(
                ["git", "clone", "https://github.com/google/sentencepiece.git", str(temp_path)],
                check=True
            )
            
            # Create build directory
            build_dir = temp_path / "build"
            build_dir.mkdir(exist_ok=True)
            
            # Run CMake
            print("Configuring with CMake...")
            subprocess.run(
                ["cmake", ".."],
                cwd=str(build_dir),
                check=True
            )
            
            # Build
            print("Building (this may take a while)...")
            subprocess.run(
                ["cmake", "--build", ".", "--config", "Release", "-j4"],
                cwd=str(build_dir),
                check=True
            )
            
            # Install
            print("Installing...")
            if platform.system() == "Windows":
                subprocess.run(
                    ["cmake", "--build", ".", "--config", "Release", "--target", "INSTALL"],
                    cwd=str(build_dir),
                    check=True
                )
            else:
                subprocess.run(
                    ["sudo", "make", "install"],
                    cwd=str(build_dir),
                    check=True
                )
            
            # Build Python package
            print("Building Python package...")
            subprocess.run(
                [sys.executable, "setup.py", "build"],
                cwd=str(temp_path / "python"),
                check=True
            )
            
            # Install Python package
            print("Installing Python package...")
            subprocess.run(
                [sys.executable, "setup.py", "install"],
                cwd=str(temp_path / "python"),
                check=True
            )
            
            return True
    except Exception as e:
        print(f"Error building SentencePiece from source: {e}")
        return False

def fix_sentencepiece_installation() -> bool:
    """
    Main function to fix SentencePiece installation
    
    Returns:
        True if fixed successfully, False otherwise
    """
    # Check if already installed
    installed, version = check_sentencepiece()
    if installed:
        print(f"SentencePiece is already installed (version {version})")
        return True
    
    print("SentencePiece is not installed. Attempting to fix...")
    
    # Try pip install first
    print("Trying to install with pip...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "sentencepiece>=0.1.97"],
            check=True
        )
        
        # Verify installation
        installed, version = check_sentencepiece()
        if installed:
            print(f"Successfully installed SentencePiece (version {version})")
            return True
    except subprocess.SubprocessError:
        print("Pip installation failed")
    
    # If pip failed, check system requirements
    if not system_requirements_met():
        print("System requirements not met for building from source")
        
        # Try to install system dependencies
        if install_system_dependencies():
            print("Successfully installed system dependencies")
        else:
            print("Could not install system dependencies")
            return False
    
    # Try building from source
    if build_from_source():
        print("Successfully built and installed SentencePiece from source")
        
        # Verify installation
        installed, version = check_sentencepiece()
        if installed:
            print(f"Verified SentencePiece installation (version {version})")
            return True
    
    # If all methods failed
    print("""
    Failed to install SentencePiece after trying multiple methods.
    
    Possible solutions:
    1. Install system dependencies manually
    2. Try installing from a pre-built wheel: pip install --find-links https://github.com/kpu/kenlm/releases/tag/sentencepiece sentencepiece
    3. Try installing an older version: pip install sentencepiece==0.1.95
    """)
    
    return False

if __name__ == "__main__":
    """Run as a standalone script"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fix SentencePiece installation issues"
    )
    
    parser.add_argument("--build-from-source", action="store_true",
                      help="Build SentencePiece from source")
    
    parser.add_argument("--install-deps", action="store_true",
                      help="Install system dependencies")
    
    args = parser.parse_args()
    
    if args.install_deps:
        install_system_dependencies()
    elif args.build_from_source:
        build_from_source()
    else:
        fix_sentencepiece_installation()
