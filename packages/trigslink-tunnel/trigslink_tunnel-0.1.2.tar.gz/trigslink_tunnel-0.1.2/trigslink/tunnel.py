import subprocess
import click
from .ascii_logo import TRIGSLINK_ASCII  
@click.command()
@click.argument("port")
def tunnel(port):
    print(TRIGSLINK_ASCII)
    click.echo("\033[38;5;201m Welcome to Trigslink Tunnel\033[0m\n")

    try:
        port = int(port)
        click.echo(f"🚀 Creating Cloudflare tunnel for http://localhost:{port}...\n")
        subprocess.run(
            ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
            check=True
        )
    except ValueError:
        click.echo("❌ Invalid port. Please enter a number like 8000 or 9000.")
    except FileNotFoundError:
        click.echo("❌ cloudflared not found. Install it from:")
        click.echo("   https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/")
    except subprocess.CalledProcessError:
        click.echo("❌ Tunnel failed. Make sure the port is correct and not already tunneled.")
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    tunnel()