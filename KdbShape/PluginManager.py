import importlib
import os
import re
import sys

PluginFolder = "./plugins"
MainModule = "__init__"


def initialize():
    try:
        folder = sys.argv[1 + sys.argv.index('-plugins')]
    except Exception:
        folder = PluginFolder

    pysearchre = re.compile('.py$', re.IGNORECASE)
    pluginfiles = filter(pysearchre.search, os.listdir(folder))
    form_module = lambda fp: '.' + os.path.splitext(fp)[0]
    plugins = map(form_module, pluginfiles)

    # import parent module / namespace
    importlib.import_module('plugins')
    modules = []
    for plugin in plugins:
        if not plugin.startswith('__'):
            modules.append(importlib.import_module(plugin, package="plugins"))

    return modules
    # plugins = getPlugins()
    # print(plugins)
