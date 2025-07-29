import subprocess
import socket
import click

COMMON_PORTS = [9000, 8000, 3000, 5000, 8080]

def is_port_open(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(('localhost', port)) == 0

def find_open_port():
    for port in COMMON_PORTS:
        if is_port_open(port):
            return port
    return None

@click.command()
def tunnel():
    port = find_open_port()
    if not port:
        print("❌ No known localhost service is running on common ports (9000, 8000, 3000, etc).")
        return

    try:
        print(f"🚀 Detected service on localhost:{port}")
        print(f"🔗 Creating Cloudflare tunnel...")
        subprocess.run(
            ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
            check=True
        )
    except FileNotFoundError:
        print("❌ cloudflared not found. Install it from: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/")
    except subprocess.CalledProcessError:
        print("❌ Tunnel failed. Make sure no other tunnel is already running.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")