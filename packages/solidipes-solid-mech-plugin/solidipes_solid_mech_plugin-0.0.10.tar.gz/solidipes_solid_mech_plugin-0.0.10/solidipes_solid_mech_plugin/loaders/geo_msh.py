from solidipes.utils import solidipes_logging as logging
from solidipes_core_plugin.loaders.code_snippet import CodeSnippet

print = logging.invalidPrint
logger = logging.getLogger()


class GeoMsh(CodeSnippet):
    """GEO file converted to mesh and then loaded with pyvista"""

    supported_mime_types = {"meshing/GEO": "geo"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def data_info(self):
        """Trigger loading of Pyvista mesh and return info"""
        self.load_all()
        return super().data_info
