import socket
import ssl
import certifi

def check_ssl(host, port):
    print(f"Checking SSL connection to {host}:{port}")
    print(f"Certifi location: {certifi.where()}")
    
    context = ssl.create_default_context(cafile=certifi.where())
    
    try:
        with socket.create_connection((host, port)) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                print(f"SSL Status: SUCCESS")
                print(f"Version: {ssock.version()}")
                print(f"Cipher: {ssock.cipher()}")
                cert = ssock.getpeercert()
                print(f"Certificate: {cert}")
    except Exception as e:
        print(f"SSL Status: FAILED")
        print(f"Error: {e}")
        
if __name__ == "__main__":
    check_ssl("smtp.gmail.com", 587) # This might fail if it's STARTTLS, let's try 465 just for cert check
    print("-" * 20)
    check_ssl("smtp.gmail.com", 465)
