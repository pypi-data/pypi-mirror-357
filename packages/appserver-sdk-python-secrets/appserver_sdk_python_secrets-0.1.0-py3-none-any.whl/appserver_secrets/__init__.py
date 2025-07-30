"""
Appserver SDK

Gerenciador de segredos local usando `keyring`, com índice em JSON.
"""

__version__ = "0.1.1"
__author__ = "Appserver SDK"
__email__ = "suporte@appserver.com.br"

from .secrets import set_secret, get_secret, list_secrets, delete_secret