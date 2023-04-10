from ipywidgets import DOMWidget
from traitlets import Unicode
from ._frontend import module_name, module_version

class PaddyWidget(DOMWidget):
    """TODO: Add docstring here
    """
    _model_name = Unicode('PaddyModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('PaddyView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    value = Unicode('Paddy Widget from python').tag(sync=True)
