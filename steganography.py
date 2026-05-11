from PIL import Image
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# The delimiter signals the end of the hidden message
DELIMITER = "====EOF===="

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
    """Hides an encrypted message inside an image using LSB steganography."""
    # 1. Encrypt the message
    encrypted_msg = encrypt_message(message, password)
    
    # 2. Convert encrypted message to binary
    binary_msg = text_to_binary(encrypted_msg)
    msg_length = len(binary_msg)
    
    # 3. Read image
    try:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
    except Exception as e:
        raise FileNotFoundError(f"Could not open or find the image {image_path}: {e}")
        
    width, height = img.size
    pixels = img.load()
    
    # Calculate max bytes we can hide (Rows * Cols * 3 color channels)
    max_bytes = width * height * 3
    if msg_length > max_bytes:
        raise ValueError("Error: Message is too large to fit in this image.")
    
    # 4. Hide data in the Least Significant Bit (LSB)
    data_index = 0
    
    for y in range(height):
        for x in range(width):
            if data_index < msg_length:
                pixel = list(pixels[x, y])
                
                # Modify R, G, B values
                for i in range(3):
                    if data_index < msg_length:
                        bit_to_hide = int(binary_msg[data_index])
                        # Use bitwise operations to clear the last bit and set it to bit_to_hide
                        pixel[i] = (pixel[i] & 254) | bit_to_hide
                        data_index += 1
                        
                pixels[x, y] = tuple(pixel)
            else:
                break
        if data_index >= msg_length:
            break
            
    # Save the new image (must save as PNG to prevent compression loss)
    img.save(output_path, "PNG")
    return True

def decode_image(image_path: str, password: str) -> str:
    """Extracts and decrypts a hidden message from an image."""
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
