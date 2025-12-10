from .base import BaseConfig
from .dev import DevConfig
from .prod import ProdConfig

config_dict = {
    "dev": DevConfig,
    "prod": ProdConfig
}
