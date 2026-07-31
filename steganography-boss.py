import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import threading
import os
import sys
import struct
import subprocess
import io
import datetime
import shutil
import json
import base64
import zlib
import hashlib
import secrets
import binascii
import gzip
import zipfile
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

# Print Redirector for GUI console
class PrintRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        
    def write(self, string):
        try:
            if self.text_widget and self.text_widget.winfo_exists():
                self.text_widget.insert(tk.END, string)
                self.text_widget.see(tk.END)
                self.text_widget.update()
        except:
            pass
        
    def flush(self):
        pass

# Steganography Core Functions
replacable_bits = ('0','1', '2', '3', '4', '5', '6','7','8','9','a','b','c','d','e','f')
special_char = '10000101000000001000110010010000100101010111100010011000101010001010000010100101011111'

def rgb2hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def hex2rgb(hexcode):
    h = hexcode.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def str2bin(message):
    if isinstance(message, str):
        message = message.encode('utf-8')
    binary = ''.join(format(byte, '08b') for byte in message)
    return binary

def bin2str(binary):
    padding = 8 - (len(binary) % 8)
    if padding != 8:
        binary = binary + '0' * padding
    
    bytes_data = []
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:
            bytes_data.append(int(byte, 2))
    
    try:
        return bytes(bytes_data).decode('utf-8', errors='ignore')
    except:
        return bytes(bytes_data).decode('latin-1', errors='ignore')

def encode(hexcode, digit):
    r, g, b = hexcode[1:3], hexcode[3:5], hexcode[5:7]
    if g[-1] in replacable_bits:
        g = g[:-1] + digit
        hexcode = '#' + r + g + b
        return hexcode
    else:
        return None

def detect_encode(hexcode, digit):
    r, g, b = hexcode[1:3], hexcode[3:5], hexcode[5:7]
    if g[-1] in replacable_bits:
        return hexcode, True
    else:
        return None, False

def decode(hexcode):
    r, g, b = hexcode[1:3], hexcode[3:5], hexcode[5:7]
    if g[-1] in ('0', '1'):
        return g[-1]
    else:
        return None

def hide(datas, message):
    binary = message + special_char
    newData = []
    digit = 0
    
    for item in datas:
        if digit < len(binary):
            r, g, b = item[0], item[1], item[2]
            newpix = encode(rgb2hex(r, g, b), binary[digit])
            if newpix is None:
                newData.append(item)
            else:
                r, g, b = hex2rgb(newpix)
                newData.append((r, g, b))
                digit += 1
        else:
            newData.append(item)
    return newData

def detect(datas, message):
    binary = message + special_char
    digit = 0
    
    for item in datas:
        r, g, b = item[0], item[1], item[2]
        newpix, status = detect_encode(rgb2hex(r, g, b), 'a')
        if status:
            digit += 1
    
    storage_capacity = digit
    data_length = len(binary)
    total_storage_capacity = len(datas)
    return storage_capacity, data_length, total_storage_capacity

def isFeasible(datas, message):
    storage_capacity, data_length, _ = detect(datas, message)
    return storage_capacity >= data_length

def retr(datas):
    binary = ''
    for item in datas:
        r, g, b = item[0], item[1], item[2]
        digit = decode(rgb2hex(r, g, b))
        if digit is not None:
            binary = binary + digit
            if len(binary) >= 86 and binary[-86:] == special_char:
                return binary[:-86]
    return ''

# Password Management System
class PasswordManager:
    @staticmethod
    def generate_key(password):
        """Generate encryption key from password"""
        salt = b'steganography_salt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    @staticmethod
    def encrypt_data(data, password):
        """Encrypt data with password"""
        key = PasswordManager.generate_key(password)
        f = Fernet(key)
        return f.encrypt(data)
    
    @staticmethod
    def decrypt_data(encrypted_data, password):
        """Decrypt data with password"""
        try:
            key = PasswordManager.generate_key(password)
            f = Fernet(key)
            return f.decrypt(encrypted_data)
        except:
            raise Exception("Incorrect password or corrupted data!")
    
    @staticmethod
    def hash_password(password):
        """Create password hash for verification"""
        return hashlib.sha256(password.encode()).hexdigest()

# Advanced Tools Classes
class FileCompressor:
    @staticmethod
    def compress_file(input_path, output_path=None, compression_level=6):
        """Compress a file using gzip"""
        if output_path is None:
            output_path = input_path + '.gz'
        
        with open(input_path, 'rb') as f_in:
            with gzip.open(output_path, 'wb', compresslevel=compression_level) as f_out:
                f_out.write(f_in.read())
        
        return output_path
    
    @staticmethod
    def decompress_file(input_path, output_path=None):
        """Decompress a gzip file"""
        if output_path is None:
            output_path = input_path.replace('.gz', '')
        
        with gzip.open(input_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                f_out.write(f_in.read())
        
        return output_path
    
    @staticmethod
    def compress_folder(folder_path, output_path=None):
        """Compress a folder to zip"""
        if output_path is None:
            output_path = folder_path + '.zip'
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)
        
        return output_path
    
    @staticmethod
    def decompress_folder(input_path, output_path=None):
        """Decompress a zip file"""
        if output_path is None:
            output_path = input_path.replace('.zip', '')
        
        with zipfile.ZipFile(input_path, 'r') as zipf:
            zipf.extractall(output_path)
        
        return output_path

class SteganalysisTool:
    @staticmethod
    def analyze_lsb(image_path):
        """Analyze LSB steganography in image"""
        try:
            from PIL import Image
            import numpy as np
            
            img = Image.open(image_path)
            img_array = np.array(img)
            
            results = {
                'filename': os.path.basename(image_path),
                'size': img.size,
                'mode': img.mode,
                'lsb_analysis': {}
            }
            
            # Analyze each color channel
            if len(img_array.shape) == 3:
                for i, channel in enumerate(['Red', 'Green', 'Blue']):
                    channel_data = img_array[:, :, i]
                    lsb = channel_data & 1
                    lsb_ratio = np.mean(lsb)
                    results['lsb_analysis'][channel] = {
                        'lsb_mean': float(lsb_ratio),
                        'suspicious': abs(lsb_ratio - 0.5) < 0.1
                    }
            
            # Check for hidden data patterns
            pixels = list(img.getdata())
            extracted = retr(pixels)
            results['hidden_data_detected'] = bool(extracted)
            
            return results
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def analyze_file_signatures(file_path):
        """Analyze file for hidden data signatures"""
        signatures = {
            b'\x89PNG': 'PNG Image',
            b'\xFF\xD8\xFF': 'JPEG Image',
            b'GIF8': 'GIF Image',
            b'%PDF': 'PDF Document',
            b'PK\x03\x04': 'ZIP Archive',
            b'RIFF': 'WAV/AVI File',
            b'\x1F\x8B': 'GZIP Archive',
        }
        
        results = []
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                
            for sig, filetype in signatures.items():
                if sig in data:
                    positions = []
                    pos = 0
                    while True:
                        pos = data.find(sig, pos)
                        if pos == -1:
                            break
                        positions.append(pos)
                        pos += 1
                    
                    if positions:
                        results.append({
                            'type': filetype,
                            'signature': sig.hex(),
                            'occurrences': len(positions),
                            'positions': positions[:5]  # First 5 positions
                        })
            
            return results
        except Exception as e:
            return [{'error': str(e)}]

class HexEditor:
    @staticmethod
    def read_hex(file_path, offset=0, length=512):
        """Read file as hex dump"""
        try:
            with open(file_path, 'rb') as f:
                f.seek(offset)
                data = f.read(length)
            
            hex_lines = []
            for i in range(0, len(data), 16):
                chunk = data[i:i+16]
                hex_part = ' '.join(f'{b:02x}' for b in chunk)
                ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
                hex_lines.append(f'{offset+i:08x}  {hex_part:<48}  |{ascii_part}|')
            
            return '\n'.join(hex_lines)
        except Exception as e:
            return f"Error: {str(e)}"
    
    @staticmethod
    def search_hex(file_path, search_bytes):
        """Search for bytes in file"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            positions = []
            pos = 0
            while True:
                pos = data.find(search_bytes, pos)
                if pos == -1:
                    break
                positions.append(pos)
                pos += 1
            
            return positions
        except Exception as e:
            return []

class TextEncoderDecoder:
    @staticmethod
    def encode_base64(text):
        """Encode text to Base64"""
        return base64.b64encode(text.encode()).decode()
    
    @staticmethod
    def decode_base64(text):
        """Decode Base64 to text"""
        return base64.b64decode(text.encode()).decode()
    
    @staticmethod
    def encode_hex(text):
        """Encode text to Hex"""
        return text.encode().hex()
    
    @staticmethod
    def decode_hex(hex_str):
        """Decode Hex to text"""
        return bytes.fromhex(hex_str).decode()
    
    @staticmethod
    def encode_binary(text):
        """Encode text to Binary"""
        return ' '.join(format(ord(c), '08b') for c in text)
    
    @staticmethod
    def decode_binary(binary_str):
        """Decode Binary to text"""
        binary_values = binary_str.split()
        ascii_string = ''.join(chr(int(bv, 2)) for bv in binary_values)
        return ascii_string
    
    @staticmethod
    def encode_url(text):
        """URL encode text"""
        from urllib.parse import quote
        return quote(text)
    
    @staticmethod
    def decode_url(text):
        """URL decode text"""
        from urllib.parse import unquote
        return unquote(text)
    
    @staticmethod
    def encode_rot13(text):
        """ROT13 encode text"""
        return text.translate(str.maketrans(
            'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
            'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'))
    
    @staticmethod
    def decode_rot13(text):
        """ROT13 decode text (same as encode)"""
        return TextEncoderDecoder.encode_rot13(text)
    
    @staticmethod
    def encode_morse(text):
        """Encode text to Morse code"""
        morse_dict = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
            'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
            'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
            'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
            'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
            '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
            '8': '---..', '9': '----.', ' ': '/'
        }
        return ' '.join(morse_dict.get(c.upper(), c) for c in text)
    
    @staticmethod
    def decode_morse(morse_text):
        """Decode Morse code to text"""
        morse_dict = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F',
            '--.': 'G', '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
            '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R',
            '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
            '-.--': 'Y', '--..': 'Z', '-----': '0', '.----': '1', '..---': '2',
            '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7',
            '---..': '8', '----.': '9', '/': ' '
        }
        return ''.join(morse_dict.get(code, code) for code in morse_text.split())

class AdvancedSteganographyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ADVANCED STEGANOGRAPHY SYSTEM - By CHOWDHURY-VAI")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a2e')
        
        # Initialize variables that might be needed early
        self.status_text = tk.StringVar(value="Initializing...")
        self.console = None
        
        # Configure modern style
        self.configure_styles()
        
        # Main container
        self.main_frame = tk.Frame(root, bg='#1a1a2e')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create UI components
        self.create_header()
        self.create_notebook_interface()
        self.create_status_bar()
        self.create_system_explorer()
        
        # Set up stdout redirect after console is created
        if self.console:
            sys.stdout = PrintRedirector(self.console)
        
        # Initialize system after everything is created
        self.root.after(100, self.initialize_system)
        
    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        bg_dark = '#1a1a2e'
        bg_medium = '#16213e'
        bg_light = '#0f3460'
        accent = '#e94560'
        text_light = '#ffffff'
        
        style.configure('TNotebook', background=bg_dark, borderwidth=0)
        style.configure('TNotebook.Tab', background=bg_medium, foreground=text_light,
                       padding=[20, 10], font=('Arial', 11, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', bg_light)],
                 foreground=[('selected', accent)])
        
        style.configure('TFrame', background=bg_dark)
        style.configure('TLabel', background=bg_dark, foreground=text_light, font=('Arial', 10))
        style.configure('TButton', background=bg_light, foreground=text_light,
                       font=('Arial', 10, 'bold'), padding=10)
        style.map('TButton', background=[('active', accent)])
        
        style.configure('TEntry', fieldbackground=bg_medium, foreground=text_light, font=('Arial', 10))
        style.configure('TLabelframe', background=bg_dark, foreground=text_light)
        style.configure('TLabelframe.Label', background=bg_dark, foreground=accent,
                       font=('Arial', 11, 'bold'))
        
    def create_header(self):
        header_frame = tk.Frame(self.main_frame, bg='#0f3460', height=80)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, text="🔐 ADVANCED STEGANOGRAPHY SYSTEM",
                        font=('Arial', 24, 'bold'), bg='#0f3460', fg='#e94560')
        title.pack(pady=5)
        
        subtitle = tk.Label(header_frame, text="All Tools Unlocked | Video • Image • File System | Developed by CHOWDHURY-VAI",
                          font=('Arial', 10), bg='#0f3460', fg='#a0a0a0')
        subtitle.pack()
        
        self.clock_label = tk.Label(header_frame, text="", font=('Arial', 9),
                                   bg='#0f3460', fg='#a0a0a0')
        self.clock_label.place(relx=0.98, rely=0.1, anchor='ne')
        self.update_clock()
        
    def create_notebook_interface(self):
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Tab 1: Video Steganography
        self.video_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.video_tab, text="🎬 Video Steganography")
        self.create_video_tab()
        
        # Tab 2: Image Steganography
        self.image_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.image_tab, text="🖼️ Image Steganography")
        self.create_image_tab()
        
        # Tab 3: File System Explorer
        self.files_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.files_tab, text="📁 File System Explorer")
        self.create_file_explorer_tab()
        
        # Tab 4: Password Manager
        self.password_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.password_tab, text="🔑 Password Manager")
        self.create_password_tab()
        
        # Tab 5: Console & Logs
        self.console_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.console_tab, text="💻 Console & Logs")
        self.create_console_tab()
        
        # Tab 6: Settings & Tools
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="⚙️ Settings & Tools")
        self.create_settings_tab()
        
    def create_video_tab(self):
        left_panel = tk.Frame(self.video_tab, bg='#16213e')
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        file_frame = ttk.LabelFrame(left_panel, text="Video File Selection", padding=10)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(file_frame, text="Video File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.video_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.video_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="📂 Browse", command=self.browse_video).grid(row=0, column=2)
        
        ttk.Label(file_frame, text="Text File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.video_text_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.video_text_path, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(file_frame, text="📂 Browse", command=self.browse_video_text).grid(row=1, column=2)
        
        pass_frame = ttk.LabelFrame(left_panel, text="Password Protection", padding=10)
        pass_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(pass_frame, text="Password:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.video_password = tk.StringVar()
        self.video_pass_entry = ttk.Entry(pass_frame, textvariable=self.video_password, show="•", width=30)
        self.video_pass_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(pass_frame, text="Confirm:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.video_confirm_pass = tk.StringVar()
        self.video_confirm_entry = ttk.Entry(pass_frame, textvariable=self.video_confirm_pass, show="•", width=30)
        self.video_confirm_entry.grid(row=1, column=1, padx=5)
        
        self.show_video_pass = tk.BooleanVar()
        ttk.Checkbutton(pass_frame, text="Show Password", variable=self.show_video_pass,
                       command=self.toggle_video_password).grid(row=2, column=0, columnspan=2, pady=5)
        
        op_frame = ttk.LabelFrame(left_panel, text="Video Operations", padding=10)
        op_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(op_frame, text="🔒 Encode Text to Video", bg='#27ae60', fg='white',
                 font=('Arial', 11, 'bold'), command=self.encode_video_with_password, 
                 height=2).pack(fill=tk.X, pady=3)
        
        tk.Button(op_frame, text="🔓 Decode Text from Video", bg='#2980b9', fg='white',
                 font=('Arial', 11, 'bold'), command=self.decode_video_with_password, 
                 height=2).pack(fill=tk.X, pady=3)
        
        tk.Button(op_frame, text="📊 Check Capacity", bg='#f39c12', fg='white',
                 font=('Arial', 11, 'bold'), command=self.check_video_capacity, 
                 height=2).pack(fill=tk.X, pady=3)
        
        tk.Button(op_frame, text="🔍 Analyze Video", bg='#8e44ad', fg='white',
                 font=('Arial', 11, 'bold'), command=self.analyze_video, 
                 height=2).pack(fill=tk.X, pady=3)
        
        right_panel = tk.Frame(self.video_tab, bg='#16213e')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        info_frame = ttk.LabelFrame(right_panel, text="Video Information", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.video_info_text = scrolledtext.ScrolledText(info_frame, height=20, width=40,
                                                        bg='#1a1a2e', fg='#ecf0f1', font=('Courier', 9))
        self.video_info_text.pack(fill=tk.BOTH, expand=True)
        
    def create_image_tab(self):
        left_panel = tk.Frame(self.image_tab, bg='#16213e')
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        img_frame = ttk.LabelFrame(left_panel, text="Image Selection", padding=10)
        img_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(img_frame, text="Image File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.image_path = tk.StringVar()
        ttk.Entry(img_frame, textvariable=self.image_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(img_frame, text="📂 Browse", command=self.browse_image).grid(row=0, column=2)
        
        ttk.Label(img_frame, text="Text/File to Hide:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.image_text_path = tk.StringVar()
        ttk.Entry(img_frame, textvariable=self.image_text_path, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(img_frame, text="📂 Browse", command=self.browse_image_text).grid(row=1, column=2)
        
        pass_frame = ttk.LabelFrame(left_panel, text="Password Protection", padding=10)
        pass_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(pass_frame, text="Password:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.image_password = tk.StringVar()
        self.image_pass_entry = ttk.Entry(pass_frame, textvariable=self.image_password, show="•", width=30)
        self.image_pass_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(pass_frame, text="Confirm:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.image_confirm_pass = tk.StringVar()
        self.image_confirm_entry = ttk.Entry(pass_frame, textvariable=self.image_confirm_pass, show="•", width=30)
        self.image_confirm_entry.grid(row=1, column=1, padx=5)
        
        self.show_image_pass = tk.BooleanVar()
        ttk.Checkbutton(pass_frame, text="Show Password", variable=self.show_image_pass,
                       command=self.toggle_image_password).grid(row=2, column=0, columnspan=2, pady=5)
        
        img_op_frame = ttk.LabelFrame(left_panel, text="Image Operations", padding=10)
        img_op_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(img_op_frame, text="🔒 Hide Data in Image", bg='#27ae60', fg='white',
                 font=('Arial', 11, 'bold'), command=self.encode_image_with_password, 
                 height=2).pack(fill=tk.X, pady=3)
        
        tk.Button(img_op_frame, text="🔓 Extract Data from Image", bg='#2980b9', fg='white',
                 font=('Arial', 11, 'bold'), command=self.decode_image_with_password, 
                 height=2).pack(fill=tk.X, pady=3)
        
        tk.Button(img_op_frame, text="📊 Image Capacity", bg='#f39c12', fg='white',
                 font=('Arial', 11, 'bold'), command=self.check_image_capacity, 
                 height=2).pack(fill=tk.X, pady=3)
        
        tk.Button(img_op_frame, text="🖼️ Image Analysis", bg='#8e44ad', fg='white',
                 font=('Arial', 11, 'bold'), command=self.analyze_image, 
                 height=2).pack(fill=tk.X, pady=3)
        
        right_panel = tk.Frame(self.image_tab, bg='#16213e')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        preview_frame = ttk.LabelFrame(right_panel, text="Image Preview & Info", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.image_preview_label = tk.Label(preview_frame, text="No image selected",
                                           bg='#1a1a2e', fg='#a0a0a0', font=('Arial', 10))
        self.image_preview_label.pack(fill=tk.BOTH, expand=True)
        
        self.image_info_text = scrolledtext.ScrolledText(preview_frame, height=10, width=40,
                                                        bg='#1a1a2e', fg='#ecf0f1', font=('Courier', 9))
        self.image_info_text.pack(fill=tk.BOTH, expand=True)
        
    def create_password_tab(self):
        pass_frame = ttk.LabelFrame(self.password_tab, text="Password Management", padding=10)
        pass_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        gen_frame = ttk.LabelFrame(pass_frame, text="Password Generator", padding=10)
        gen_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(gen_frame, text="Length:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.pass_length = tk.IntVar(value=16)
        ttk.Spinbox(gen_frame, from_=8, to=64, textvariable=self.pass_length, 
                   width=10).grid(row=0, column=1, padx=5)
        
        self.pass_upper = tk.BooleanVar(value=True)
        self.pass_lower = tk.BooleanVar(value=True)
        self.pass_digits = tk.BooleanVar(value=True)
        self.pass_special = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(gen_frame, text="Uppercase (A-Z)", variable=self.pass_upper).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(gen_frame, text="Lowercase (a-z)", variable=self.pass_lower).grid(row=2, column=0, sticky=tk.W)
        ttk.Checkbutton(gen_frame, text="Digits (0-9)", variable=self.pass_digits).grid(row=1, column=1, sticky=tk.W)
        ttk.Checkbutton(gen_frame, text="Special Characters", variable=self.pass_special).grid(row=2, column=1, sticky=tk.W)
        
        self.generated_pass = tk.StringVar()
        ttk.Entry(gen_frame, textvariable=self.generated_pass, width=40, 
                 font=('Courier', 12)).grid(row=3, column=0, columnspan=2, pady=10)
        
        tk.Button(gen_frame, text="🔑 Generate Password", bg='#f39c12', fg='white',
                 font=('Arial', 11, 'bold'), command=self.generate_password,
                 height=2).grid(row=4, column=0, columnspan=2)
        
        tk.Button(gen_frame, text="📋 Copy to Clipboard", bg='#2980b9', fg='white',
                 command=lambda: self.copy_to_clipboard(self.generated_pass.get()),
                 height=2).grid(row=5, column=0, columnspan=2, pady=10)
        
        strength_frame = ttk.LabelFrame(pass_frame, text="Password Strength Checker", padding=10)
        strength_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(strength_frame, text="Enter Password:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.check_pass = tk.StringVar()
        ttk.Entry(strength_frame, textvariable=self.check_pass, width=40).grid(row=0, column=1, padx=5)
        
        self.strength_label = tk.Label(strength_frame, text="Strength: ", 
                                       bg='#16213e', fg='white', font=('Arial', 11))
        self.strength_label.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.strength_bar = ttk.Progressbar(strength_frame, length=300, mode='determinate')
        self.strength_bar.grid(row=2, column=0, columnspan=2, pady=5)
        
        tk.Button(strength_frame, text="🔍 Check Strength", bg='#8e44ad', fg='white',
                 font=('Arial', 10), command=self.check_password_strength,
                 height=2).grid(row=3, column=0, columnspan=2, pady=10)
        
    def create_file_explorer_tab(self):
        explorer_frame = ttk.LabelFrame(self.files_tab, text="File System Explorer", padding=10)
        explorer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        nav_frame = tk.Frame(explorer_frame, bg='#16213e')
        nav_frame.pack(fill=tk.X, pady=5)
        
        self.current_path = tk.StringVar(value=os.getcwd())
        ttk.Entry(nav_frame, textvariable=self.current_path, width=80).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="🏠 Home", command=self.go_home).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="⬆️ Up", command=self.go_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="🔄 Refresh", command=self.refresh_explorer).pack(side=tk.LEFT, padx=2)
        
        drives_frame = tk.Frame(explorer_frame, bg='#16213e')
        drives_frame.pack(fill=tk.X, pady=5)
        self.create_drive_buttons(drives_frame)
        
        list_frame = tk.Frame(explorer_frame, bg='#16213e')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        columns = ('Name', 'Size', 'Type', 'Modified')
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        self.file_tree.heading('Name', text='Name')
        self.file_tree.heading('Size', text='Size')
        self.file_tree.heading('Type', text='Type')
        self.file_tree.heading('Modified', text='Modified')
        
        self.file_tree.column('Name', width=300)
        self.file_tree.column('Size', width=100)
        self.file_tree.column('Type', width=100)
        self.file_tree.column('Modified', width=150)
        
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.file_tree.xview)
        self.file_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.file_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        self.file_tree.bind('<Double-1>', self.on_file_double_click)
        self.file_tree.bind('<Button-3>', self.show_context_menu)
        
    def create_console_tab(self):
        console_frame = ttk.LabelFrame(self.console_tab, text="System Console", padding=10)
        console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.console = scrolledtext.ScrolledText(console_frame, height=25, width=100,
                                                bg='#0a0a0a', fg='#00ff00', font=('Courier', 10),
                                                insertbackground='white')
        self.console.pack(fill=tk.BOTH, expand=True, pady=5)
        
        input_frame = tk.Frame(console_frame, bg='#16213e')
        input_frame.pack(fill=tk.X, pady=5)
        
        self.console_input = ttk.Entry(input_frame, width=80, font=('Courier', 10))
        self.console_input.pack(side=tk.LEFT, padx=5)
        self.console_input.bind('<Return>', self.execute_console_command)
        
        ttk.Button(input_frame, text="Execute", command=self.execute_console_command).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="Clear", command=self.clear_console).pack(side=tk.LEFT, padx=5)
        
    def create_settings_tab(self):
        settings_frame = ttk.LabelFrame(self.settings_tab, text="Settings & Tools", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        sys_info_frame = ttk.LabelFrame(settings_frame, text="System Information", padding=10)
        sys_info_frame.pack(fill=tk.X, pady=10)
        
        info_text = f"""
        🖥️ System: {os.name.upper()}
        📁 Current Directory: {os.getcwd()}
        💾 Disk Space: {self.get_disk_space()}
        🐍 Python Version: {sys.version.split()[0]}
        ⏰ Current Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        🔐 Encryption: AES-256 + Fernet
        🔧 All Tools: UNLOCKED
        """
        
        tk.Label(sys_info_frame, text=info_text, bg='#16213e', fg='#ecf0f1',
                font=('Courier', 10), justify=tk.LEFT).pack(anchor=tk.W)
        
        tools_frame = ttk.LabelFrame(settings_frame, text="Advanced Tools", padding=10)
        tools_frame.pack(fill=tk.X, pady=10)
        
        tools_buttons = [
            ("🔧 File Encryptor", self.open_file_encryptor),
            ("🔍 Steganalysis Tool", self.open_steganalysis),
            ("📊 Hex Editor", self.open_hex_editor),
            ("🗜️ File Compressor", self.open_compressor),
            ("🔑 Password Generator", self.open_password_gen),
            ("📝 Text Encoder/Decoder", self.open_text_encoder),
        ]
        
        for i, (text, command) in enumerate(tools_buttons):
            tk.Button(tools_frame, text=text, bg='#0f3460', fg='white',
                     font=('Arial', 10, 'bold'), command=command,
                     width=20, height=2).grid(row=i//3, column=i%3, padx=5, pady=5)
        
    def create_status_bar(self):
        status_frame = tk.Frame(self.main_frame, bg='#0f3460', height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        status_label = tk.Label(status_frame, textvariable=self.status_text,
                               bg='#0f3460', fg='white', font=('Arial', 9))
        status_label.pack(side=tk.LEFT, padx=10)
        
        self.status_progress = ttk.Progressbar(status_frame, length=200, mode='indeterminate')
        self.status_progress.pack(side=tk.RIGHT, padx=10)
        
    def create_system_explorer(self):
        directories = ['videos', 'images', 'data', 'temp', 'exports', 'logs', 'encrypted']
        for dir_name in directories:
            os.makedirs(dir_name, exist_ok=True)
            
    def initialize_system(self):
        self.log_message("=" * 60)
        self.log_message("ADVANCED STEGANOGRAPHY SYSTEM INITIALIZED")
        self.log_message("All Tools: UNLOCKED")
        self.log_message("Developed by CHOWDHURY-VAI")
        self.log_message(f"Time: {datetime.datetime.now()}")
        self.log_message("=" * 60)
        
        self.check_dependencies()
        self.refresh_explorer()
        
        self.status_text.set("Ready | All Tools Active | Developed by CHOWDHURY-VAI")
        
    def check_dependencies(self):
        dependencies = {
            'PIL': False, 'cv2': False, 'numpy': False,
            'ffmpeg': False, 'cryptography': False
        }
        
        try:
            from PIL import Image
            dependencies['PIL'] = True
            self.log_message("✅ PIL/Pillow - Available")
        except ImportError:
            self.log_message("⚠️ PIL/Pillow - Not available")
            
        try:
            import cv2
            dependencies['cv2'] = True
            self.log_message("✅ OpenCV - Available")
        except ImportError:
            self.log_message("⚠️ OpenCV - Not available")
            
        try:
            import numpy
            dependencies['numpy'] = True
            self.log_message("✅ NumPy - Available")
        except ImportError:
            self.log_message("⚠️ NumPy - Not available")
            
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            dependencies['ffmpeg'] = True
            self.log_message("✅ FFmpeg - Available")
        except:
            self.log_message("⚠️ FFmpeg - Not available")
            
        try:
            from cryptography.fernet import Fernet
            dependencies['cryptography'] = True
            self.log_message("✅ Cryptography - Available")
        except ImportError:
            self.log_message("❌ Cryptography - Not available")
            
        return dependencies
        
    def create_drive_buttons(self, parent):
        drives = []
        if os.name == 'nt':
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    drives.append(drive)
        else:
            drives = ['/', '/home', '/tmp', '/var']
            
        for drive in drives:
            btn = tk.Button(parent, text=f"💾 {drive}", bg='#0f3460', fg='white',
                          font=('Arial', 9), command=lambda d=drive: self.navigate_to(d))
            btn.pack(side=tk.LEFT, padx=2)
            
    def navigate_to(self, path):
        if os.path.exists(path):
            self.current_path.set(path)
            self.refresh_explorer()
            
    def go_home(self):
        home = os.path.expanduser('~')
        self.navigate_to(home)
        
    def go_up(self):
        current = self.current_path.get()
        parent = os.path.dirname(current)
        if os.path.exists(parent):
            self.navigate_to(parent)
            
    def refresh_explorer(self):
        try:
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
                
            current = self.current_path.get()
            if not os.path.exists(current):
                self.current_path.set(os.getcwd())
                current = os.getcwd()
                
            try:
                items = os.listdir(current)
                
                if current != os.path.abspath(os.sep):
                    self.file_tree.insert('', 'end', values=('..', '<DIR>', 'Directory', ''))
                    
                dirs = []
                files = []
                
                for item in items:
                    full_path = os.path.join(current, item)
                    if os.path.isdir(full_path):
                        dirs.append(item)
                    else:
                        files.append(item)
                        
                for dir_name in sorted(dirs):
                    try:
                        dir_path = os.path.join(current, dir_name)
                        stat = os.stat(dir_path)
                        modified = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                        self.file_tree.insert('', 'end', values=(dir_name, '<DIR>', 'Directory', modified))
                    except:
                        pass
                        
                for file_name in sorted(files):
                    try:
                        file_path = os.path.join(current, file_name)
                        stat = os.stat(file_path)
                        size = self.format_size(stat.st_size)
                        modified = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                        ext = os.path.splitext(file_name)[1].upper() + ' File'
                        self.file_tree.insert('', 'end', values=(file_name, size, ext, modified))
                    except:
                        pass
                        
                self.status_text.set(f"Explorer: {current}")
                
            except PermissionError:
                self.status_text.set(f"Permission denied: {current}")
            except Exception as e:
                self.status_text.set(f"Error reading directory: {str(e)}")
                
        except Exception as e:
            self.status_text.set(f"Explorer error: {str(e)}")
            
    def on_file_double_click(self, event):
        selected = self.file_tree.selection()
        if not selected:
            return
            
        item = self.file_tree.item(selected[0])
        name = item['values'][0]
        
        if name == '..':
            self.go_up()
            return
            
        current = self.current_path.get()
        full_path = os.path.join(current, name)
        
        if os.path.isdir(full_path):
            self.navigate_to(full_path)
        else:
            try:
                if os.name == 'nt':
                    os.startfile(full_path)
                else:
                    subprocess.run(['xdg-open', full_path])
            except Exception as e:
                self.status_text.set(f"Cannot open file: {str(e)}")
                
    def show_context_menu(self, event):
        selected = self.file_tree.selection()
        if not selected:
            return
            
        item = self.file_tree.item(selected[0])
        name = item['values'][0]
        
        if name == '..':
            return
            
        current = self.current_path.get()
        full_path = os.path.join(current, name)
        
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="📂 Open", command=lambda: self.open_file(full_path))
        context_menu.add_command(label="📋 Copy Path", command=lambda: self.copy_to_clipboard(full_path))
        context_menu.add_separator()
        
        if os.path.isfile(full_path):
            context_menu.add_command(label="🔒 Hide in Image", command=lambda: self.hide_in_image(full_path))
            context_menu.add_command(label="🎬 Hide in Video", command=lambda: self.hide_in_video(full_path))
            context_menu.add_separator()
            context_menu.add_command(label="🗜️ Compress File", command=lambda: self.compress_file_menu(full_path))
            context_menu.add_command(label="🔍 Analyze File", command=lambda: self.analyze_file_menu(full_path))
            context_menu.add_command(label="📊 Hex View", command=lambda: self.hex_view_menu(full_path))
            context_menu.add_separator()
            
        context_menu.add_command(label="🗑️ Delete", command=lambda: self.delete_file(full_path))
        context_menu.add_command(label="📝 Rename", command=lambda: self.rename_file(full_path))
        context_menu.add_separator()
        context_menu.add_command(label="ℹ️ Properties", command=lambda: self.file_properties(full_path))
        
        try:
            context_menu.post(event.x_root, event.y_root)
        except:
            pass
        
    def open_file(self, path):
        try:
            if os.name == 'nt':
                os.startfile(path)
            else:
                subprocess.run(['xdg-open', path])
        except Exception as e:
            self.status_text.set(f"Cannot open file: {str(e)}")
            
    def copy_to_clipboard(self, text):
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.status_text.set("Copied to clipboard")
        except:
            pass
        
    def delete_file(self, path):
        if messagebox.askyesno("Confirm Delete", f"Delete {os.path.basename(path)}?"):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.refresh_explorer()
                self.log_message(f"Deleted: {path}")
            except Exception as e:
                self.status_text.set(f"Cannot delete: {str(e)}")
                
    def rename_file(self, path):
        new_name = simpledialog.askstring("Rename", "Enter new name:", 
                                         initialvalue=os.path.basename(path))
        if new_name:
            new_path = os.path.join(os.path.dirname(path), new_name)
            try:
                os.rename(path, new_path)
                self.refresh_explorer()
                self.log_message(f"Renamed: {path} -> {new_path}")
            except Exception as e:
                self.status_text.set(f"Cannot rename: {str(e)}")
                
    def file_properties(self, path):
        try:
            stat = os.stat(path)
            info = f"""
            File Properties:
            📁 Name: {os.path.basename(path)}
            📍 Path: {path}
            📏 Size: {self.format_size(stat.st_size)}
            📅 Created: {datetime.datetime.fromtimestamp(stat.st_ctime)}
            📝 Modified: {datetime.datetime.fromtimestamp(stat.st_mtime)}
            🔐 Accessed: {datetime.datetime.fromtimestamp(stat.st_atime)}
            🏷️ Type: {'Directory' if os.path.isdir(path) else os.path.splitext(path)[1] + ' File'}
            """
            messagebox.showinfo("Properties", info)
        except Exception as e:
            self.status_text.set(f"Cannot get properties: {str(e)}")
            
    # Context menu tool methods
    def compress_file_menu(self, path):
        try:
            output = FileCompressor.compress_file(path)
            self.log_message(f"✅ File compressed: {output}")
            self.refresh_explorer()
            messagebox.showinfo("Success", f"File compressed!\nOutput: {output}")
        except Exception as e:
            messagebox.showerror("Error", f"Compression failed: {str(e)}")
            
    def analyze_file_menu(self, path):
        try:
            results = SteganalysisTool.analyze_file_signatures(path)
            info = f"Steganalysis Results for: {os.path.basename(path)}\n\n"
            if results:
                for r in results:
                    if 'error' in r:
                        info += f"Error: {r['error']}\n"
                    else:
                        info += f"Type: {r['type']}\n"
                        info += f"Occurrences: {r['occurrences']}\n"
                        info += f"First at: {r['positions'][:3]}\n\n"
            else:
                info += "No hidden signatures found."
            messagebox.showinfo("Steganalysis Results", info)
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
            
    def hex_view_menu(self, path):
        try:
            hex_dump = HexEditor.read_hex(path)
            
            # Create a new window for hex view
            hex_window = tk.Toplevel(self.root)
            hex_window.title(f"Hex View - {os.path.basename(path)}")
            hex_window.geometry("800x600")
            hex_window.configure(bg='#1a1a2e')
            
            hex_text = scrolledtext.ScrolledText(hex_window, bg='#0a0a0a', fg='#00ff00',
                                                font=('Courier', 10))
            hex_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            hex_text.insert(1.0, hex_dump)
            hex_text.config(state=tk.DISABLED)
            
            # Search frame
            search_frame = tk.Frame(hex_window, bg='#16213e')
            search_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(search_frame, text="Search Hex:").pack(side=tk.LEFT, padx=5)
            search_entry = ttk.Entry(search_frame, width=30)
            search_entry.pack(side=tk.LEFT, padx=5)
            
            def search_hex():
                search_str = search_entry.get()
                if search_str:
                    try:
                        search_bytes = bytes.fromhex(search_str.replace(' ', ''))
                        positions = HexEditor.search_hex(path, search_bytes)
                        if positions:
                            messagebox.showinfo("Search Results", 
                                f"Found at {len(positions)} positions:\n{positions[:10]}")
                        else:
                            messagebox.showinfo("Search Results", "Not found")
                    except:
                        messagebox.showerror("Error", "Invalid hex string")
            
            ttk.Button(search_frame, text="Search", command=search_hex).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Hex view failed: {str(e)}")
            
    # Password Management Methods
    def toggle_video_password(self):
        if self.show_video_pass.get():
            self.video_pass_entry.config(show="")
            self.video_confirm_entry.config(show="")
        else:
            self.video_pass_entry.config(show="•")
            self.video_confirm_entry.config(show="•")
            
    def toggle_image_password(self):
        if self.show_image_pass.get():
            self.image_pass_entry.config(show="")
            self.image_confirm_entry.config(show="")
        else:
            self.image_pass_entry.config(show="•")
            self.image_confirm_entry.config(show="•")
            
    def generate_password(self):
        chars = ""
        if self.pass_upper.get():
            chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if self.pass_lower.get():
            chars += "abcdefghijklmnopqrstuvwxyz"
        if self.pass_digits.get():
            chars += "0123456789"
        if self.pass_special.get():
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
            
        if not chars:
            messagebox.showerror("Error", "Select at least one character type!")
            return
            
        password = ''.join(secrets.choice(chars) for _ in range(self.pass_length.get()))
        self.generated_pass.set(password)
        self.log_message(f"Generated password: {password}")
        
    def check_password_strength(self):
        password = self.check_pass.get()
        if not password:
            messagebox.showerror("Error", "Enter a password to check!")
            return
            
        score = 0
        
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
            
        if any(c.isupper() for c in password):
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
            
        strength_levels = ["Very Weak", "Weak", "Fair", "Good", "Strong", "Very Strong", "Excellent"]
        colors = ["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#27ae60", "#2980b9", "#8e44ad"]
        
        score = min(score, 6)
        self.strength_label.config(text=f"Strength: {strength_levels[score]}", fg=colors[score])
        self.strength_bar['value'] = (score + 1) * 14.28
        
    def validate_password(self, password, confirm):
        if not password:
            raise Exception("Password cannot be empty!")
        if len(password) < 6:
            raise Exception("Password must be at least 6 characters!")
        if password != confirm:
            raise Exception("Passwords do not match!")
        return True
        
    # Image Steganography Methods
    def browse_image(self):
        filename = filedialog.askopenfilename(
            title="Select Image File",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
        )
        if filename:
            self.image_path.set(filename)
            self.show_image_preview(filename)
            
    def browse_image_text(self):
        filename = filedialog.askopenfilename(
            title="Select File to Hide",
            filetypes=[("All files", "*.*"), ("Text files", "*.txt"), 
                      ("Image files", "*.png *.jpg"), ("PDF files", "*.pdf")]
        )
        if filename:
            self.image_text_path.set(filename)
            
    def show_image_preview(self, path):
        try:
            from PIL import Image, ImageTk
            img = Image.open(path)
            img.thumbnail((300, 300))
            photo = ImageTk.PhotoImage(img)
            self.image_preview_label.config(image=photo, text="")
            self.image_preview_label.image = photo
            
            info = f"Size: {img.size}\nMode: {img.mode}\nFormat: {img.format}\n"
            info += f"Pixels: {img.size[0] * img.size[1]:,}"
            self.image_info_text.delete(1.0, tk.END)
            self.image_info_text.insert(1.0, info)
        except Exception as e:
            self.log_message(f"Error loading image preview: {str(e)}")
            
    def encode_image_with_password(self):
        if not self.image_path.get() or not self.image_text_path.get():
            messagebox.showerror("Error", "Please select both image and file!")
            return
            
        try:
            password = self.image_password.get()
            confirm = self.image_confirm_pass.get()
            self.validate_password(password, confirm)
        except Exception as e:
            messagebox.showerror("Password Error", str(e))
            return
            
        def encode_thread():
            try:
                from PIL import Image
                
                self.log_message("Starting password-protected image encoding...")
                self.status_progress.start()
                self.status_text.set("Encoding with password protection...")
                
                with open(self.image_text_path.get(), 'rb') as f:
                    data = f.read()
                    
                encrypted_data = PasswordManager.encrypt_data(data, password)
                password_hash = PasswordManager.hash_password(password)
                
                hash_bytes = password_hash.encode()
                package = struct.pack('>I', len(hash_bytes)) + hash_bytes + encrypted_data
                
                encoded_data = base64.b64encode(package).decode()
                binary_data = str2bin(encoded_data)
                
                img = Image.open(self.image_path.get())
                img = img.convert('RGB')
                pixels = list(img.getdata())
                
                capacity, _, _ = detect(pixels, "test")
                if capacity < len(binary_data):
                    raise Exception(f"Insufficient capacity! Need {len(binary_data)} bits, have {capacity} bits")
                    
                new_pixels = hide(pixels, binary_data)
                img.putdata(new_pixels)
                
                output_path = filedialog.asksaveasfilename(
                    title="Save Encoded Image",
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
                )
                
                if output_path:
                    img.save(output_path)
                    self.log_message(f"✅ Image encoded successfully: {output_path}")
                    self.status_text.set("Encoding completed successfully")
                    messagebox.showinfo("Success", 
                        f"Data hidden successfully with password protection!\n\n"
                        f"Output: {output_path}\n"
                        f"Original size: {self.format_size(len(data))}\n"
                        f"Encrypted size: {self.format_size(len(encrypted_data))}")
                    
            except Exception as e:
                self.log_message(f"❌ Error: {str(e)}")
                self.status_text.set("Encoding failed")
                messagebox.showerror("Error", str(e))
            finally:
                self.status_progress.stop()
                
        threading.Thread(target=encode_thread, daemon=True).start()
        
    def decode_image_with_password(self):
        if not self.image_path.get():
            messagebox.showerror("Error", "Please select an image file!")
            return
            
        password = self.image_password.get()
        if not password:
            messagebox.showerror("Error", "Please enter the password to decode!")
            return
            
        def decode_thread():
            try:
                from PIL import Image
                
                self.log_message("Starting password-protected image decoding...")
                self.status_progress.start()
                self.status_text.set("Decoding with password verification...")
                
                img = Image.open(self.image_path.get())
                img = img.convert('RGB')
                pixels = list(img.getdata())
                
                binary_data = retr(pixels)
                if not binary_data:
                    raise Exception("No hidden data found!")
                    
                encoded_data = bin2str(binary_data)
                package = base64.b64decode(encoded_data)
                
                hash_len = struct.unpack('>I', package[:4])[0]
                stored_hash = package[4:4+hash_len].decode()
                encrypted_data = package[4+hash_len:]
                
                if PasswordManager.hash_password(password) != stored_hash:
                    raise Exception("❌ Incorrect password! Access denied.")
                    
                data = PasswordManager.decrypt_data(encrypted_data, password)
                
                output_path = filedialog.asksaveasfilename(
                    title="Save Extracted Data",
                    defaultextension=".bin",
                    filetypes=[("All files", "*.*")]
                )
                
                if output_path:
                    with open(output_path, 'wb') as f:
                        f.write(data)
                    self.log_message(f"✅ Data extracted successfully: {output_path}")
                    self.status_text.set("Decoding completed successfully")
                    messagebox.showinfo("Success", 
                        f"Data extracted successfully!\n\n"
                        f"Output: {output_path}\n"
                        f"Size: {self.format_size(len(data))}\n"
                        f"Password: Verified ✅")
                    
            except Exception as e:
                self.log_message(f"❌ Error: {str(e)}")
                self.status_text.set("Decoding failed")
                messagebox.showerror("Error", str(e))
            finally:
                self.status_progress.stop()
                
        threading.Thread(target=decode_thread, daemon=True).start()
        
    def check_image_capacity(self):
        if not self.image_path.get():
            messagebox.showerror("Error", "Please select an image file!")
            return
            
        try:
            from PIL import Image
            
            img = Image.open(self.image_path.get())
            img = img.convert('RGB')
            pixels = list(img.getdata())
            
            capacity, _, total = detect(pixels, "test")
            
            info = f"""
            Image Capacity Analysis:
            📏 Total Pixels: {total:,}
            💾 Storage Capacity: {capacity:,} bits ({capacity//8:,} bytes)
            📊 Capacity: {capacity//8/1024:.2f} KB
            """
            
            self.image_info_text.delete(1.0, tk.END)
            self.image_info_text.insert(1.0, info)
            
            messagebox.showinfo("Capacity Analysis", 
                f"Image can store up to {capacity//8:,} bytes ({capacity//8/1024:.2f} KB)")
                
        except Exception as e:
            self.status_text.set(f"Analysis failed: {str(e)}")
            
    def analyze_image(self):
        if not self.image_path.get():
            messagebox.showerror("Error", "Please select an image file!")
            return
            
        try:
            from PIL import Image
            
            img = Image.open(self.image_path.get())
            img = img.convert('RGB')
            pixels = list(img.getdata())
            
            binary_data = retr(pixels)
            
            if binary_data:
                self.log_message("🔍 Hidden data detected in image!")
                
                try:
                    encoded_data = bin2str(binary_data)
                    package = base64.b64decode(encoded_data)
                    hash_len = struct.unpack('>I', package[:4])[0]
                    
                    self.log_message("🔐 Password protection detected!")
                    messagebox.showinfo("Analysis Result",
                        "Hidden data detected!\n\n"
                        "This image contains password-protected hidden data.\n"
                        "Use the decode function with correct password to extract.")
                except:
                    self.log_message("ℹ️ Unencrypted data detected")
                    messagebox.showinfo("Analysis Result",
                        "Hidden data detected!\n\n"
                        "This image contains unencrypted hidden data.")
            else:
                self.log_message("No hidden data detected")
                messagebox.showinfo("Analysis Result", "No hidden data detected in this image.")
                
        except Exception as e:
            self.status_text.set(f"Analysis failed: {str(e)}")
            
    # Video Steganography Methods
    def browse_video(self):
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov"), ("All files", "*.*")]
        )
        if filename:
            self.video_path.set(filename)
            self.analyze_video_info(filename)
            
    def browse_video_text(self):
        filename = filedialog.askopenfilename(
            title="Select Text File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.video_text_path.set(filename)
            
    def analyze_video_info(self, path=None):
        if not path:
            path = self.video_path.get()
            
        if not path or not os.path.exists(path):
            return
            
        try:
            info = f"File: {os.path.basename(path)}\n"
            info += f"Size: {self.format_size(os.path.getsize(path))}\n"
            
            try:
                result = subprocess.run(['ffprobe', '-v', 'quiet', '-print_format', 'json',
                                       '-show_format', '-show_streams', path],
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    if 'streams' in data:
                        for stream in data['streams']:
                            if stream['codec_type'] == 'video':
                                info += f"Resolution: {stream.get('width')}x{stream.get('height')}\n"
                                info += f"Codec: {stream.get('codec_name')}\n"
                                info += f"FPS: {stream.get('r_frame_rate')}\n"
                                if 'duration' in data.get('format', {}):
                                    duration = float(data['format']['duration'])
                                    info += f"Duration: {duration:.2f} seconds\n"
            except:
                pass
                
            self.video_info_text.delete(1.0, tk.END)
            self.video_info_text.insert(1.0, info)
            
        except Exception as e:
            self.log_message(f"Error analyzing video: {str(e)}")
            
    def encode_video_with_password(self):
        if not self.video_path.get() or not self.video_text_path.get():
            messagebox.showerror("Error", "Please select both video and text files!")
            return
            
        try:
            password = self.video_password.get()
            confirm = self.video_confirm_pass.get()
            self.validate_password(password, confirm)
        except Exception as e:
            messagebox.showerror("Password Error", str(e))
            return
            
        if not self.check_dependencies()['cv2'] or not self.check_dependencies()['ffmpeg']:
            messagebox.showerror("Error", "This feature requires OpenCV and FFmpeg!")
            return
            
        def encode_thread():
            try:
                import cv2
                import numpy as np
                from PIL import Image
                
                self.log_message("Starting password-protected video encoding...")
                self.status_progress.start()
                self.status_text.set("Encoding video with password...")
                
                with open(self.video_text_path.get(), 'r', encoding='utf-8') as f:
                    message = f.read()
                    
                encrypted_data = PasswordManager.encrypt_data(message.encode(), password)
                password_hash = PasswordManager.hash_password(password)
                
                hash_bytes = password_hash.encode()
                package = struct.pack('>I', len(hash_bytes)) + hash_bytes + encrypted_data
                encoded_data = base64.b64encode(package).decode()
                binary_message = str2bin(encoded_data)
                
                cap = cv2.VideoCapture(self.video_path.get())
                fps = cap.get(cv2.CAP_PROP_FPS)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                self.log_message(f"Video: {width}x{height}, {total_frames} frames, {fps} FPS")
                
                frame_count = 0
                encoded_bits = 0
                frames_dir = "temp/frames_encode"
                os.makedirs(frames_dir, exist_ok=True)
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                        
                    if encoded_bits < len(binary_message):
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        pil_img = Image.fromarray(frame_rgb)
                        pixels = list(pil_img.getdata())
                        
                        cap_check, _, _ = detect(pixels, "test")
                        if cap_check > 86:
                            chunk = binary_message[encoded_bits:encoded_bits + cap_check - 86]
                            if isFeasible(pixels, chunk):
                                new_pixels = hide(pixels, chunk)
                                pil_img.putdata(new_pixels)
                                frame_array = np.array(pil_img)
                                frame = cv2.cvtColor(frame_array, cv2.COLOR_RGB2BGR)
                                encoded_bits += len(chunk)
                                
                    cv2.imwrite(f"{frames_dir}/frame_{frame_count:06d}.png", frame)
                    frame_count += 1
                    
                    if frame_count % 100 == 0:
                        progress = min(100, int(encoded_bits * 100 / len(binary_message)))
                        self.status_text.set(f"Encoding: {progress}%")
                        
                cap.release()
                
                output_path = filedialog.asksaveasfilename(
                    title="Save Encoded Video",
                    defaultextension=".mp4",
                    filetypes=[("MP4 files", "*.mp4")]
                )
                
                if output_path:
                    self.log_message("\nCreating video file...")
                    subprocess.run(['ffmpeg', '-y', '-framerate', str(fps),
                                  '-i', f'{frames_dir}/frame_%06d.png',
                                  '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                                  output_path], capture_output=True)
                    
                    shutil.rmtree(frames_dir)
                    
                    self.log_message(f"✅ Video encoded with password: {output_path}")
                    self.status_text.set("Video encoded successfully")
                    messagebox.showinfo("Success", 
                        f"Video encoded with password protection!\n\n"
                        f"Output: {output_path}\n"
                        f"Frames processed: {frame_count}\n"
                        f"Data encoded: {encoded_bits} bits")
                    
            except Exception as e:
                self.log_message(f"❌ Error: {str(e)}")
                self.status_text.set("Encoding failed")
                messagebox.showerror("Error", str(e))
            finally:
                self.status_progress.stop()
                
        threading.Thread(target=encode_thread, daemon=True).start()
        
    def decode_video_with_password(self):
        if not self.video_path.get():
            messagebox.showerror("Error", "Please select a video file!")
            return
            
        password = self.video_password.get()
        if not password:
            messagebox.showerror("Error", "Please enter the password to decode!")
            return
            
        if not self.check_dependencies()['cv2']:
            messagebox.showerror("Error", "This feature requires OpenCV!")
            return
            
        def decode_thread():
            try:
                import cv2
                from PIL import Image
                
                self.log_message("Starting password-protected video decoding...")
                self.status_progress.start()
                self.status_text.set("Decoding video with password...")
                
                cap = cv2.VideoCapture(self.video_path.get())
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                
                total_binary = ''
                frame_count = 0
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                        
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(frame_rgb)
                    pixels = list(pil_img.getdata())
                    
                    extracted = retr(pixels)
                    if extracted:
                        total_binary += extracted
                        
                    frame_count += 1
                    if frame_count % 100 == 0:
                        self.status_text.set(f"Decoding: {int(frame_count*100/total_frames)}%")
                        
                cap.release()
                
                if not total_binary:
                    raise Exception("No hidden data found in video!")
                    
                encoded_data = bin2str(total_binary)
                package = base64.b64decode(encoded_data)
                
                hash_len = struct.unpack('>I', package[:4])[0]
                stored_hash = package[4:4+hash_len].decode()
                encrypted_data = package[4+hash_len:]
                
                if PasswordManager.hash_password(password) != stored_hash:
                    raise Exception("❌ Incorrect password! Access denied.")
                    
                data = PasswordManager.decrypt_data(encrypted_data, password)
                message = data.decode('utf-8')
                
                output_path = filedialog.asksaveasfilename(
                    title="Save Decoded Text",
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt")]
                )
                
                if output_path:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(message)
                        
                    self.log_message(f"✅ Text extracted successfully: {output_path}")
                    self.status_text.set("Decoding completed")
                    
                    preview = message[:200] + "..." if len(message) > 200 else message
                    messagebox.showinfo("Success", 
                        f"Text extracted successfully!\n\n"
                        f"Output: {output_path}\n"
                        f"Length: {len(message)} characters\n"
                        f"Password: Verified ✅\n\n"
                        f"Preview:\n{preview}")
                    
            except Exception as e:
                self.log_message(f"❌ Error: {str(e)}")
                self.status_text.set("Decoding failed")
                messagebox.showerror("Error", str(e))
            finally:
                self.status_progress.stop()
                
        threading.Thread(target=decode_thread, daemon=True).start()
        
    def check_video_capacity(self):
        if not self.video_path.get():
            messagebox.showerror("Error", "Please select a video file!")
            return
            
        if not self.check_dependencies()['cv2']:
            messagebox.showerror("Error", "This feature requires OpenCV!")
            return
            
        def check_thread():
            try:
                import cv2
                from PIL import Image
                
                self.log_message("Analyzing video capacity...")
                self.status_progress.start()
                
                cap = cv2.VideoCapture(self.video_path.get())
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                
                total_capacity = 0
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                        
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(frame_rgb)
                    pixels = list(pil_img.getdata())
                    
                    cap_check, _, _ = detect(pixels, "test")
                    if cap_check > 86:
                        total_capacity += cap_check - 86
                        
                cap.release()
                
                self.video_info_text.delete(1.0, tk.END)
                info = f"Video Capacity Analysis:\n"
                info += f"Total Frames: {total_frames}\n"
                info += f"Storage Capacity: {total_capacity:,} bits\n"
                info += f"Storage Capacity: {total_capacity//8:,} bytes\n"
                info += f"Storage Capacity: {total_capacity//8/1024:.2f} KB"
                self.video_info_text.insert(1.0, info)
                
                self.status_text.set("Capacity analysis complete")
                messagebox.showinfo("Capacity Analysis", 
                    f"Video can store up to {total_capacity//8:,} bytes ({total_capacity//8/1024:.2f} KB)")
                    
            except Exception as e:
                self.log_message(f"❌ Error: {str(e)}")
                self.status_text.set("Analysis failed")
            finally:
                self.status_progress.stop()
                
        threading.Thread(target=check_thread, daemon=True).start()
        
    def analyze_video(self):
        if not self.video_path.get():
            messagebox.showerror("Error", "Please select a video file!")
            return
            
        if not self.check_dependencies()['cv2']:
            messagebox.showerror("Error", "This feature requires OpenCV!")
            return
            
        def analyze_thread():
            try:
                import cv2
                from PIL import Image
                
                self.log_message("Analyzing video for hidden data...")
                self.status_progress.start()
                
                cap = cv2.VideoCapture(self.video_path.get())
                
                found_data = False
                frame_count = 0
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                        
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(frame_rgb)
                    pixels = list(pil_img.getdata())
                    
                    extracted = retr(pixels)
                    if extracted:
                        found_data = True
                        self.log_message(f"Hidden data found in frame {frame_count}!")
                        break
                        
                    frame_count += 1
                    
                cap.release()
                
                if found_data:
                    self.log_message("🔍 Hidden data detected in video!")
                    messagebox.showinfo("Analysis Result",
                        "Hidden data detected!\n\n"
                        "This video contains password-protected hidden data.\n"
                        "Use the decode function with correct password to extract.")
                else:
                    self.log_message("No hidden data detected")
                    messagebox.showinfo("Analysis Result", "No hidden data detected in this video.")
                    
            except Exception as e:
                self.log_message(f"❌ Error: {str(e)}")
                self.status_text.set("Analysis failed")
            finally:
                self.status_progress.stop()
                
        threading.Thread(target=analyze_thread, daemon=True).start()
        
    # Utility Methods
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
        
    def get_disk_space(self):
        try:
            if os.name == 'nt':
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                total_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(os.getcwd()), None, 
                    ctypes.pointer(total_bytes), ctypes.pointer(free_bytes))
                return f"{self.format_size(free_bytes.value)} free / {self.format_size(total_bytes.value)}"
            else:
                stat = os.statvfs(os.getcwd())
                free = stat.f_bavail * stat.f_frsize
                total = stat.f_blocks * stat.f_frsize
                return f"{self.format_size(free)} free / {self.format_size(total)}"
        except:
            return "Unknown"
            
    def update_clock(self):
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.clock_label.config(text=current_time)
        self.root.after(1000, self.update_clock)
        
    def log_message(self, message, end='\n'):
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {message}", end=end)
        
    def execute_console_command(self, event=None):
        command = self.console_input.get()
        if not command:
            return
            
        self.console_input.delete(0, tk.END)
        self.log_message(f"\n>>> {command}")
        
        try:
            if command.startswith('cd '):
                path = command[3:].strip()
                os.chdir(path)
                self.log_message(f"Changed directory to: {os.getcwd()}")
            elif command == 'dir' or command == 'ls':
                self.log_message("\n" + "\n".join(os.listdir('.')))
            elif command == 'pwd':
                self.log_message(os.getcwd())
            elif command == 'clear':
                self.clear_console()
            elif command == 'help':
                self.show_help()
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                if result.stdout:
                    self.log_message(result.stdout)
                if result.stderr:
                    self.log_message(f"Error: {result.stderr}")
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            
    def clear_console(self):
        try:
            self.console.delete(1.0, tk.END)
        except:
            pass
        
    def show_help(self):
        help_text = """
        Available Commands:
        cd <path> - Change directory
        dir/ls - List files
        pwd - Show current directory
        clear - Clear console
        help - Show this help
        Any system command can be executed directly
        """
        self.log_message(help_text)
        
    # Context menu methods
    def hide_in_image(self, file_path):
        self.image_text_path.set(file_path)
        self.notebook.select(self.image_tab)
        messagebox.showinfo("Ready", "File selected for hiding.\nSelect an image and encode.")
        
    def hide_in_video(self, file_path):
        self.video_text_path.set(file_path)
        self.notebook.select(self.video_tab)
        messagebox.showinfo("Ready", "File selected for hiding.\nSelect a video and encode.")
        
    # Advanced Tools - UNLOCKED
    def open_file_encryptor(self):
        """File Encryptor Tool"""
        encryptor_window = tk.Toplevel(self.root)
        encryptor_window.title("File Encryptor/Decryptor")
        encryptor_window.geometry("600x400")
        encryptor_window.configure(bg='#1a1a2e')
        
        frame = ttk.LabelFrame(encryptor_window, text="File Encryptor", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text="File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        file_var = tk.StringVar()
        ttk.Entry(frame, textvariable=file_var, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Browse", command=lambda: file_var.set(
            filedialog.askopenfilename())).grid(row=0, column=2)
        
        ttk.Label(frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        pass_var = tk.StringVar()
        ttk.Entry(frame, textvariable=pass_var, show="•", width=40).grid(row=1, column=1, padx=5)
        
        def encrypt_file():
            if not file_var.get() or not pass_var.get():
                messagebox.showerror("Error", "Select file and enter password!")
                return
            try:
                with open(file_var.get(), 'rb') as f:
                    data = f.read()
                encrypted = PasswordManager.encrypt_data(data, pass_var.get())
                output = file_var.get() + '.encrypted'
                with open(output, 'wb') as f:
                    f.write(encrypted)
                messagebox.showinfo("Success", f"File encrypted!\nOutput: {output}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
        def decrypt_file():
            if not file_var.get() or not pass_var.get():
                messagebox.showerror("Error", "Select file and enter password!")
                return
            try:
                with open(file_var.get(), 'rb') as f:
                    data = f.read()
                decrypted = PasswordManager.decrypt_data(data, pass_var.get())
                output = file_var.get().replace('.encrypted', '.decrypted')
                with open(output, 'wb') as f:
                    f.write(decrypted)
                messagebox.showinfo("Success", f"File decrypted!\nOutput: {output}")
            except Exception as e:
                messagebox.showerror("Error", f"Decryption failed: {str(e)}")
        
        tk.Button(frame, text="🔒 Encrypt File", bg='#27ae60', fg='white',
                 font=('Arial', 11), command=encrypt_file,
                 height=2).grid(row=2, column=0, columnspan=3, pady=10)
        
        tk.Button(frame, text="🔓 Decrypt File", bg='#2980b9', fg='white',
                 font=('Arial', 11), command=decrypt_file,
                 height=2).grid(row=3, column=0, columnspan=3, pady=5)
        
    def open_steganalysis(self):
        """Steganalysis Tool"""
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("Steganalysis Tool")
        analysis_window.geometry("700x500")
        analysis_window.configure(bg='#1a1a2e')
        
        frame = ttk.LabelFrame(analysis_window, text="Steganalysis", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text="File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        file_var = tk.StringVar()
        ttk.Entry(frame, textvariable=file_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Browse", command=lambda: file_var.set(
            filedialog.askopenfilename(filetypes=[("All files", "*.*"),
                                                   ("Images", "*.png *.jpg *.jpeg"),
                                                   ("Videos", "*.mp4 *.avi")]))).grid(row=0, column=2)
        
        result_text = scrolledtext.ScrolledText(frame, height=15, width=70,
                                               bg='#0a0a0a', fg='#00ff00', font=('Courier', 10))
        result_text.grid(row=1, column=0, columnspan=3, pady=10)
        
        def run_analysis():
            if not file_var.get():
                messagebox.showerror("Error", "Select a file!")
                return
                
            result_text.delete(1.0, tk.END)
            result_text.insert(1.0, "Running steganalysis...\n\n")
            
            path = file_var.get()
            
            # Check file signatures
            sig_results = SteganalysisTool.analyze_file_signatures(path)
            result_text.insert(tk.END, "=== File Signature Analysis ===\n")
            if sig_results:
                for r in sig_results:
                    if 'error' not in r:
                        result_text.insert(tk.END, f"Found: {r['type']} ({r['occurrences']} times)\n")
                        result_text.insert(tk.END, f"First positions: {r['positions'][:3]}\n\n")
            else:
                result_text.insert(tk.END, "No hidden signatures found.\n\n")
            
            # If image, do LSB analysis
            if path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                result_text.insert(tk.END, "=== LSB Analysis ===\n")
                lsb_results = SteganalysisTool.analyze_lsb(path)
                if 'lsb_analysis' in lsb_results:
                    for channel, data in lsb_results['lsb_analysis'].items():
                        status = "⚠️ SUSPICIOUS" if data['suspicious'] else "✅ Normal"
                        result_text.insert(tk.END, 
                            f"{channel}: LSB Mean={data['lsb_mean']:.4f} - {status}\n")
                
                if lsb_results.get('hidden_data_detected'):
                    result_text.insert(tk.END, "\n⚠️ Hidden data detected!\n")
            
            result_text.insert(tk.END, "\n=== Analysis Complete ===")
        
        tk.Button(frame, text="🔍 Run Analysis", bg='#f39c12', fg='white',
                 font=('Arial', 11, 'bold'), command=run_analysis,
                 height=2).grid(row=2, column=0, columnspan=3, pady=10)
        
    def open_hex_editor(self):
        """Hex Editor Tool"""
        hex_window = tk.Toplevel(self.root)
        hex_window.title("Hex Editor")
        hex_window.geometry("900x600")
        hex_window.configure(bg='#1a1a2e')
        
        frame = ttk.LabelFrame(hex_window, text="Hex Editor", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text="File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        file_var = tk.StringVar()
        ttk.Entry(frame, textvariable=file_var, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Browse", command=lambda: file_var.set(
            filedialog.askopenfilename())).grid(row=0, column=2)
        
        # Offset
        ttk.Label(frame, text="Offset (hex):").grid(row=1, column=0, sticky=tk.W, pady=5)
        offset_var = tk.StringVar(value="0")
        ttk.Entry(frame, textvariable=offset_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        hex_text = scrolledtext.ScrolledText(frame, height=20, width=100,
                                            bg='#0a0a0a', fg='#00ff00', font=('Courier', 10))
        hex_text.grid(row=2, column=0, columnspan=3, pady=10)
        
        def load_hex():
            if not file_var.get():
                messagebox.showerror("Error", "Select a file!")
                return
            try:
                offset = int(offset_var.get(), 16)
                hex_dump = HexEditor.read_hex(file_var.get(), offset, 1024)
                hex_text.delete(1.0, tk.END)
                hex_text.insert(1.0, hex_dump)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(frame, text="📖 Load Hex", command=load_hex).grid(row=1, column=2, pady=5)
        
        # Search
        search_frame = tk.Frame(frame, bg='#16213e')
        search_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Label(search_frame, text="Search Hex:").pack(side=tk.LEFT, padx=5)
        search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=search_var, width=30).pack(side=tk.LEFT, padx=5)
        
        def search_hex_data():
            if not file_var.get() or not search_var.get():
                return
            try:
                search_bytes = bytes.fromhex(search_var.get().replace(' ', ''))
                positions = HexEditor.search_hex(file_var.get(), search_bytes)
                if positions:
                    messagebox.showinfo("Search Results", 
                        f"Found at {len(positions)} positions:\nFirst: {positions[:10]}")
                else:
                    messagebox.showinfo("Search Results", "Not found")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(search_frame, text="🔍 Search", command=search_hex_data).pack(side=tk.LEFT, padx=5)
        
    def open_compressor(self):
        """File Compressor Tool"""
        compressor_window = tk.Toplevel(self.root)
        compressor_window.title("File Compressor")
        compressor_window.geometry("600x400")
        compressor_window.configure(bg='#1a1a2e')
        
        frame = ttk.LabelFrame(compressor_window, text="File Compressor/Decompressor", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text="File/Folder:").grid(row=0, column=0, sticky=tk.W, pady=5)
        path_var = tk.StringVar()
        ttk.Entry(frame, textvariable=path_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Browse File", command=lambda: path_var.set(
            filedialog.askopenfilename())).grid(row=0, column=2)
        ttk.Button(frame, text="Browse Folder", command=lambda: path_var.set(
            filedialog.askdirectory())).grid(row=0, column=3)
        
        # Compression level
        ttk.Label(frame, text="Compression Level:").grid(row=1, column=0, sticky=tk.W, pady=5)
        level_var = tk.IntVar(value=6)
        ttk.Spinbox(frame, from_=1, to=9, textvariable=level_var, width=5).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        def compress():
            if not path_var.get():
                messagebox.showerror("Error", "Select a file or folder!")
                return
            try:
                path = path_var.get()
                if os.path.isfile(path):
                    output = FileCompressor.compress_file(path, compression_level=level_var.get())
                else:
                    output = FileCompressor.compress_folder(path)
                self.log_message(f"✅ Compressed: {output}")
                messagebox.showinfo("Success", f"Compressed!\nOutput: {output}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
        def decompress():
            if not path_var.get():
                messagebox.showerror("Error", "Select a compressed file!")
                return
            try:
                path = path_var.get()
                if path.endswith('.gz'):
                    output = FileCompressor.decompress_file(path)
                elif path.endswith('.zip'):
                    output = FileCompressor.decompress_folder(path)
                else:
                    messagebox.showerror("Error", "Unsupported format! Use .gz or .zip")
                    return
                self.log_message(f"✅ Decompressed: {output}")
                messagebox.showinfo("Success", f"Decompressed!\nOutput: {output}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        tk.Button(frame, text="🗜️ Compress", bg='#27ae60', fg='white',
                 font=('Arial', 11, 'bold'), command=compress,
                 height=2).grid(row=2, column=0, columnspan=2, pady=10)
        
        tk.Button(frame, text="📂 Decompress", bg='#2980b9', fg='white',
                 font=('Arial', 11, 'bold'), command=decompress,
                 height=2).grid(row=2, column=2, columnspan=2, pady=10)
        
    def open_password_gen(self):
        self.notebook.select(self.password_tab)
        
    def open_text_encoder(self):
        """Text Encoder/Decoder Tool"""
        encoder_window = tk.Toplevel(self.root)
        encoder_window.title("Text Encoder/Decoder")
        encoder_window.geometry("800x600")
        encoder_window.configure(bg='#1a1a2e')
        
        frame = ttk.LabelFrame(encoder_window, text="Text Encoder/Decoder", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Input
        ttk.Label(frame, text="Input Text:").grid(row=0, column=0, sticky=tk.W, pady=5)
        input_text = scrolledtext.ScrolledText(frame, height=10, width=80,
                                              bg='#0a0a0a', fg='#00ff00', font=('Courier', 10))
        input_text.grid(row=1, column=0, columnspan=4, pady=5)
        
        # Encoding selection
        ttk.Label(frame, text="Encoding:").grid(row=2, column=0, sticky=tk.W, pady=5)
        encoding_var = tk.StringVar(value="Base64")
        encodings = ["Base64", "Hex", "Binary", "URL", "ROT13", "Morse"]
        encoding_menu = ttk.Combobox(frame, textvariable=encoding_var, values=encodings, width=15)
        encoding_menu.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Output
        ttk.Label(frame, text="Output:").grid(row=3, column=0, sticky=tk.W, pady=5)
        output_text = scrolledtext.ScrolledText(frame, height=10, width=80,
                                               bg='#0a0a0a', fg='#00ff00', font=('Courier', 10))
        output_text.grid(row=4, column=0, columnspan=4, pady=5)
        
        def encode_text():
            text = input_text.get(1.0, tk.END).strip()
            if not text:
                return
                
            encoding = encoding_var.get()
            try:
                if encoding == "Base64":
                    result = TextEncoderDecoder.encode_base64(text)
                elif encoding == "Hex":
                    result = TextEncoderDecoder.encode_hex(text)
                elif encoding == "Binary":
                    result = TextEncoderDecoder.encode_binary(text)
                elif encoding == "URL":
                    result = TextEncoderDecoder.encode_url(text)
                elif encoding == "ROT13":
                    result = TextEncoderDecoder.encode_rot13(text)
                elif encoding == "Morse":
                    result = TextEncoderDecoder.encode_morse(text)
                else:
                    result = "Unknown encoding"
                    
                output_text.delete(1.0, tk.END)
                output_text.insert(1.0, result)
            except Exception as e:
                output_text.delete(1.0, tk.END)
                output_text.insert(1.0, f"Error: {str(e)}")
                
        def decode_text():
            text = input_text.get(1.0, tk.END).strip()
            if not text:
                return
                
            encoding = encoding_var.get()
            try:
                if encoding == "Base64":
                    result = TextEncoderDecoder.decode_base64(text)
                elif encoding == "Hex":
                    result = TextEncoderDecoder.decode_hex(text)
                elif encoding == "Binary":
                    result = TextEncoderDecoder.decode_binary(text)
                elif encoding == "URL":
                    result = TextEncoderDecoder.decode_url(text)
                elif encoding == "ROT13":
                    result = TextEncoderDecoder.decode_rot13(text)
                elif encoding == "Morse":
                    result = TextEncoderDecoder.decode_morse(text)
                else:
                    result = "Unknown encoding"
                    
                output_text.delete(1.0, tk.END)
                output_text.insert(1.0, result)
            except Exception as e:
                output_text.delete(1.0, tk.END)
                output_text.insert(1.0, f"Error: {str(e)}")
        
        tk.Button(frame, text="🔒 Encode", bg='#27ae60', fg='white',
                 font=('Arial', 11, 'bold'), command=encode_text,
                 height=2, width=15).grid(row=2, column=2, pady=10, padx=5)
        
        tk.Button(frame, text="🔓 Decode", bg='#2980b9', fg='white',
                 font=('Arial', 11, 'bold'), command=decode_text,
                 height=2, width=15).grid(row=2, column=3, pady=10, padx=5)
        
        # Copy button
        def copy_output():
            text = output_text.get(1.0, tk.END).strip()
            if text:
                self.copy_to_clipboard(text)
                messagebox.showinfo("Copied", "Output copied to clipboard!")
        
        tk.Button(frame, text="📋 Copy Output", command=copy_output,
                 height=2).grid(row=5, column=0, columnspan=4, pady=5)

def main():
    root = tk.Tk()
    app = AdvancedSteganographyGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
