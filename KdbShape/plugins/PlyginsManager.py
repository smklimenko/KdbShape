import importlib
import os
import re
import sys

import KdbShape

PluginFolder = "./plugins"
MainModule = "__init__"


def initialize():
    folder = [PluginFolder]
    if "plugins" in KdbShape.args:
        folder = KdbShape.args.plugins

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
