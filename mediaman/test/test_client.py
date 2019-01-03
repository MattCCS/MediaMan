
from mediaman.core import client
from mediaman.services import loader

c = client.Client(loader.load_drive())
