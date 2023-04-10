# Copyright (c) Bloomberg.
# Distributed under the terms of the Modified BSD License.

from ._version import __version__
from .paddy_widget import PaddyWidget

def _jupyter_nbextension_paths():
    return [
        {
            "section": "notebook",
            "src": "nbextension",
            "dest": "ipydatagrid",
            "require": "ipydatagrid/extension",
        }
    ]


def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": "ipydatagrid"}]


__all__ = [
    "__version__",
    "PaddyWidget"
]
