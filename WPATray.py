import platform
import subprocess
import os
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as Item
from mastodon import Mastodon
import re
import pyperclip

# Configurer les informations de l'application et de l'utilisateur (ps: c'est que du read only)
client_id = 'xmn50IcsGkY5p_1iHvU0GMfE1uQL6_kw9flmfnaUrzI'
client_secret = '5y5QgmXlLO3-fUtZdonr3dYPfEystaBOhUXP62zSDSw'
access_token = 'YKymxAqT_VOqW1XnddSwn_h4kJZy01nh1tbVydVlXHM'
api_base_url = 'https://mastodon.insa.lol'

if platform.system() == "Linux":
    pyperclip.set_clipboard("xclip")

# Initialiser Mastodon
mastodon = Mastodon(
    client_id=client_id,
    client_secret=client_secret,
    access_token=access_token,
    api_base_url=api_base_url
)


def get_latest_wifi_password():
    try:
        user = mastodon.account_search('@wifi@mastodon.insa.lol')[0]
        toots = mastodon.account_statuses(user['id'])
        for toot in toots:
            match = re.search(r'Mot de passe:\s*([A-Za-z0-9-]+)', toot['content'])
            if match:
                return match.group(1)
    except Exception as e:
        icon.notify("Erreur: Impossible de récupérer le mot de passe")
    return None


def copy_password(icon, item):
    password = get_latest_wifi_password()
    if password:
        pyperclip.copy(password)
        icon.notify('Mot de passe copié dans le presse-papier')
    else:
        icon.notify("Erreur: Impossible de récupérer le mot de passe")


def refresh_password(icon, item):
    icon.icon = create_image()
    icon.notify('Le mot de passe a été actualisé')


def apply_password(icon, item):
    ssid = "WIFI-WPA"
    password = get_latest_wifi_password()
    if not password:
        icon.notify("Erreur: Impossible de récupérer le mot de passe")
        return

    os_system = platform.system()

    try:
        if os_system == "Darwin":
            subprocess.run(["networksetup", "-setairportnetwork", "en0", ssid, password])
            icon.notify("Mot de passe appliqué avec succès")
        elif os_system == "Windows":
            subprocess.run(["netsh", "wlan", "set", "profile", "name=" + ssid, "key=" + password])
            icon.notify("Mot de passe appliqué avec succès")
        elif os_system == "Linux":
            subprocess.run(["nmcli", "device", "wifi", "connect", ssid, "password", password])
            icon.notify("Mot de passe appliqué avec succès")
        else:
            icon.notify(f"OS non supporté: {os_system}")
    except Exception as e:
        icon.notify(f"Erreur lors de l'application du mot de passe: {e}")


def create_image():
    """TODO: Icone"""
    width, height = 64, 64
    image = Image.new("RGB", (width, height), "white")
    dc = ImageDraw.Draw(image)
    dc.text((16, 32), "WPA", fill="black", align="center")
    return image


icon = pystray.Icon("WPATray")
icon.icon = create_image()
icon.menu = pystray.Menu(
    Item("MDP: " + (get_latest_wifi_password() or "Inconnu"), copy_password),
    Item("Actualiser le mot de passe", refresh_password),
    Item("Appliquer le mot de passe", apply_password),
    Item("Quitter", lambda icon, item: icon.stop())
)
icon.title = "WPATray"
icon.run()
