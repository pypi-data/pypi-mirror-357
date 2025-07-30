# AccessCount

IP、PV、Endpoint统计插件

## Installation

### Development

`pip install git+https://github.com/saintic/flask-pluginkit-accesscount@master`

### PypI Release

`pip install flask-pluginkit-accesscount`

## Usage

```python
from flask_pluginkit import PluginManager

PluginManager(
    plugin_packages=["flask_pluginkit_accesscount"],
    # If Flask-PluginKit version >= 3.10.0, otherwise pip install it.
    install_packages=dict(pkgs=["flask-pluginkit-accesscount"]),
)
```

