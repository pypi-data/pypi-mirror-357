import os
import json


class Servers:
    """
    Extrae las credenciales de cada uno de los servers en la configuracion `.config.json`. Aternativamente puede pasarse otro archivo `.json`
    como argumento `config_file_path`
    """

    def __init__(self, config_file_path: str = "config.json"):
        self.config_file_path: str = config_file_path
        self.mcp_servers: dict[str, dict] | None = {}
        self.load_servers()

    def load_servers(self):
        """Carga cada uno de los credenciales de los servidores que se le conectan desde el `.config`"""
        with open(f"{os.getcwd()}{os.path.sep}{self.config_file_path}", "r") as file:
            json_config: dict = json.loads(file.read())
        self.mcp_servers = json_config["mcp_servers"]
