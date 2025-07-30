# Tell python that there are more sub-packages present, physically located elsewhere.
# See: https://stackoverflow.com/questions/8936884/python-import-path-packages-with-the-same-name-in-different-folders
import pkgutil

__path__ = pkgutil.extend_path(__path__, __name__)

from .model_to_cloud import Model2CloudConnector