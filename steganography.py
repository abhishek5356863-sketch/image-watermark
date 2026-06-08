from PIL import Image
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# The delimiter signals the end of the hidden message
DELIMITER = "====EOF===="
EOF_MARKER = b"====STEALTHGUARD===="

def generate_key(password: str, salt: bytes = b'cybersecurity_salt') -> bytes:
    """Generates a cryptographic key from a password using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def encrypt_message(message: str, password: str) -> str:
    """Encrypts a string message using AES (Fernet) and a password."""
    key = generate_key(password)
    f = Fernet(key)
    encrypted_bytes = f.encrypt(message.encode())
    # Return as base64 string and append delimiter so it can be found during extraction
    return encrypted_bytes.decode('utf-8') + DELIMITER

def decrypt_message(encrypted_str: str, password: str) -> str:
    """Decrypts a message using the password."""
    key = generate_key(password)
    f = Fernet(key)
    try:
        # Delimiter should already be stripped by decode_image, but just in case
        if encrypted_str.endswith(DELIMITER):
            encrypted_str = encrypted_str[:-len(DELIMITER)]
            
        decrypted_bytes = f.decrypt(encrypted_str.encode())
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        # Decryption failed (wrong password or corrupted data)
        raise ValueError("Invalid password or corrupted data.")

def text_to_binary(text: str) -> str:
    """Converts a string to a sequence of 8-bit binary numbers."""
    return ''.join(format(ord(char), '08b') for char in text)

def binary_to_text(binary_str: str) -> str:
    """Converts a sequence of 8-bit binary numbers back to a string."""
    text = ""
    for i in range(0, len(binary_str), 8):
        byte = binary_str[i:i+8]
        if len(byte) == 8:
            text += chr(int(byte, 2))
    return text

def encode_image(image_path: str, message: str, password: str, output_path: str) -> bool:
    """Hides an encrypted message inside an image without changing its file size."""
    # 1. Encrypt the message
    encrypted_msg = encrypt_message(message, password)
    
    # 2. Read the original image bytes
    with open(image_path, "rb") as f:
        img_bytes = f.read()
        
    # 3. Append the marker and encrypted message to the end of the image file
    # This prevents the file size from blowing up, keeping it exactly the same as original (+ a few bytes)
    with open(output_path, "wb") as f:
        f.write(img_bytes)
        f.write(EOF_MARKER)
        f.write(encrypted_msg.encode('utf-8'))
        
    return True

def decode_image(image_path: str, password: str) -> str:
    """Extracts and decrypts a hidden message from an image."""
    # First, try the EOF method which preserves file size
    with open(image_path, "rb") as f:
        img_bytes = f.read()
        
    marker_index = img_bytes.find(EOF_MARKER)
    if marker_index != -1:
        encrypted_bytes = img_bytes[marker_index + len(EOF_MARKER):]
        try:
            extracted_text = encrypted_bytes.decode('utf-8')
            if extracted_text.endswith(DELIMITER):
                encrypted_msg = extracted_text.split(DELIMITER)[0]
                return decrypt_message(encrypted_msg, password)
        except Exception:
            pass # Fallback to LSB if EOF extraction fails

    # --- FALLBACK TO OLD LSB METHOD ---
    # 1. Read image
    try:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
    except Exception as e:
        raise FileNotFoundError(f"Could not open or find the image {image_path}: {e}")
        
    width, height = img.size
    pixels = img.load()
    
    binary_data = ""
    extracted_text = ""
    
    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            
            # Extract LSB from R, G, B
            for i in range(3):
                binary_data += str(pixel[i] & 1)
                
                # Check every 8 bits
                if len(binary_data) >= 8 and len(binary_data) % 8 == 0:
                    byte = binary_data[-8:]
                    extracted_text += chr(int(byte, 2))
                    
                    # Check if we reached the delimiter
                    if extracted_text.endswith(DELIMITER):
                        encrypted_msg = extracted_text.split(DELIMITER)[0]
                        return decrypt_message(encrypted_msg, password)
                        
    # If delimiter isn't found, it might not be a valid stego image
    raise ValueError("No hidden message found in this image.")
