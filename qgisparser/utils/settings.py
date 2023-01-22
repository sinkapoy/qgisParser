import json
import os


class _SelfExplainMixin:
    def __repr__(self) -> str:
        return str(self.__dict__)

    def __str__(self) -> str:
        return self.__repr__()


def _checkPath(path: str):
    absolute = True if path[0] == "/" else False
    parts = path.replace("./", "/").split("/")
    path = "/" if absolute else "./"
    for part in parts:
        fullpath = os.path.join(path, part)
        if(not os.path.exists(fullpath)):
            os.mkdir(fullpath)
        path = fullpath


class _HeightSettings(_SelfExplainMixin):
    max_ack_tile_size = 1024
    heightPath = "images/height/"


class Settings(_SelfExplainMixin):
    qgis_path: str
    sample_per_m: int
    chunk_size: int
    images_path: str
    project_path: str

    height_settings: _HeightSettings

    def __init__(self) -> None:
        self.sample_per_m = 4
        self.chunk_size = 128
        self.images_path = "images/HR/"
        self.project_path = "./project.qgis"
        self.height_settings = _HeightSettings()
        self.qgis_path = "/usr/bin/qgis"

        file = open("config.json")
        config: dict = json.loads(file.read())
        file.close()
        if (config.get("qgisPath")):
            self.qgis_path = config.get("qgisPath")
        if (config.get("project")):
            self.project_path = config.get("project")
        if (config.get("chunkSize")):
            self.chunk_size = config.get("chunkSize")
        if (config.get("samplePerMeter")):
            self.sample_per_m = config.get("samplePerMeter")

        if (config.get("heightSettings")):
            heightSettings: dict = config.get("heightSettings")
            if (heightSettings.get("maxAckTileSize")):
                self.height_settings.max_ack_tile_size = heightSettings.get(
                    "maxAckTileSize")
            if (heightSettings.get("heightPath")):
                self.height_settings.heightPath = heightSettings.get(
                    "heightPath")

        self.__checkPaths()

    def __checkPaths(self):
        if (not os.path.exists(self.images_path)):
            _checkPath(self.images_path)
        if (not os.path.exists(self.height_settings.heightPath)):
            _checkPath(self.height_settings.heightPath)
