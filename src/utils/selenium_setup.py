import os
import platform
import undetected_chromedriver as uc
import ssl

# Deshabilitar verificación de certificados SSL globalmente
ssl._create_default_https_context = ssl._create_unverified_context

def get_default_chrome_profile():
    """
    Obtiene la ruta al perfil por defecto de Chrome según el sistema operativo
    """
    system = platform.system()
    home = os.path.expanduser('~')
    
    if system == "Darwin":  # macOS
        return os.path.join(home, "Library", "Application Support", "Google", "Chrome", "Default")
    elif system == "Windows":
        return os.path.join(home, "AppData", "Local", "Google", "Chrome", "User Data", "Default")
    elif system == "Linux":
        return os.path.join(home, ".config", "google-chrome", "Default")
    else:
        raise OSError(f"Sistema operativo no soportado: {system}")


def get_chrome_user_data_dir():
    """
    Detecta dinámicamente el directorio de datos de usuario de Google Chrome según el sistema operativo.
    """
    os_name = platform.system()
    if os_name == "Windows":
        return os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data")
    elif os_name == "Darwin":  # macOS
        return os.path.expanduser("~/Library/Application Support/Google/Chrome")
    elif os_name == "Linux":
        return os.path.expanduser("~/.config/google-chrome")
    else:
        raise OSError("Sistema operativo no soportado")

def get_chrome_profile_directory(user_profile="Profile 1"):
    """
    Devuelve la ruta completa al directorio del perfil de Chrome especificado.
    """
    user_data_dir = get_chrome_user_data_dir()
    profile_path = os.path.join(user_data_dir, user_profile)
    if not os.path.exists(profile_path):
        raise FileNotFoundError(f"No se encontró el perfil {user_profile} en {user_data_dir}")
    return profile_path

import undetected_chromedriver as uc

def create_webdriver(headless=False, pos="maximizada"):
    try:
        # Obtener la ruta del perfil por defecto
        user_data_dir = os.path.dirname(get_default_chrome_profile())
        print(f"[INFO] Usando perfil de Chrome en: {user_data_dir}")
        
        # Crear el driver usando el perfil por defecto
        driver = uc.Chrome(
            user_data_dir=user_data_dir,
            use_subprocess=True,
            version_main=None
        )
        
        print("[INFO] WebDriver creado exitosamente.")

        # Configurar ventana
        if not headless:
            driver.maximize_window()
            if pos != "maximizada":
                ancho, alto = driver.get_window_size().values()
                if pos == "izquierda":
                    driver.set_window_rect(x=0, y=0, width=ancho // 2, height=alto)
                elif pos == "derecha":
                    driver.set_window_rect(x=ancho // 2, y=0, width=ancho // 2, height=alto)

        return driver
        
    except Exception as e:
        print(f"[ERROR] Error al crear WebDriver: {e}")
        raise