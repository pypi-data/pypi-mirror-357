import os
import json

def cargar_json_usuario(nombre_archivo="input_params.json"):
    """
    Carga un archivo JSON desde el directorio actual de trabajo del usuario.
    Lanza FileNotFoundError si no se encuentra.

    Parámetros:
        nombre_archivo (str): Nombre del archivo JSON (por defecto: "input_params.json")

    Retorna:
        dict: Diccionario con los datos del archivo JSON.

    Uso típico:
        config = cargar_json_usuario()
    """
    ruta = os.path.abspath(nombre_archivo)
    
    if not os.path.isfile(ruta):
        raise FileNotFoundError(f"No se encontró '{nombre_archivo}' en: {ruta}")
    
    with open(ruta, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error al parsear '{nombre_archivo}': {e}")
