import argparse

from KdbShape import kdbshapeapp_rc

APPLICATION_NAME = __name__

__all__ = ['kdbshapeapp_rc']

__parser = argparse.ArgumentParser(prog='PROG')
__parser.add_argument('-plugins', type=str, default="./plugins", help='Path to a plugins folder. By default ./plugins')
args = __parser.parse_args()
