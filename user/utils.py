import os

#-----------------------------------
#-------------IMAGES----------------
#-----------------------------------
from PIL import Image
from django.contrib.auth import forms

# Returns the name of the current avatar
def get_upload_path_avatars(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{instance.user.id}_avatar.{ext}'
    return os.path.join('avatars/', filename)

# Function to crop the avatar into a square
def crop_to_square(image):
    width, height = image.size
    new_size = min(width, height)
    left = (width - new_size) / 2
    top = (height - new_size) / 2
    right = (width + new_size) / 2
    bottom = (height + new_size) / 2

    return image.crop((left, top, right, bottom))

# Delete an image

def delete_image(file_path):
    try:
        # Check if the file exists
        if os.path.exists(file_path):
            # Attempt to remove the file
            os.remove(file_path)
            return True, None  # Deletion successful
        else:
            return False, "File not found"  # File does not exist
    except Exception as e:
        return False, str(e)  # An error occurred while deleting the file

from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import json, base64

def encrypt(public_key, data):
    public_key = RSA.import_key(public_key)
    session_key = get_random_bytes(16)
    # Encrypting the session key
    cipher_rsa = PKCS1_OAEP.new(public_key)
    enc_session_key = cipher_rsa.encrypt(session_key)
    # Encrypt data with AES
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data.encode('utf-8'))

    encrypted = {
        'enc_session_key':base64.b64encode(enc_session_key).decode('utf-8'),
        'nonce':base64.b64encode(cipher_aes.nonce).decode('utf-8'),
        'tag':base64.b64encode(tag).decode('utf-8'),
        'ciphertext':base64.b64encode(ciphertext).decode('utf-8')
        }

    return json.dumps(encrypted)

def decrypt(private_key, data):
    private_key = RSA.import_key(private_key)
    data = json.loads(data)
    for d in data:
        data[d] = base64.b64decode(data[d].encode('utf-8'))
    # Decrypting session key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(data['enc_session_key'])

    # Decrypting data with AES
    cipher_aes = AES.new(session_key, AES.MODE_EAX, data['nonce'])
    data = cipher_aes.decrypt_and_verify(data['ciphertext'], data['tag'])
    return data.decode('utf-8')
