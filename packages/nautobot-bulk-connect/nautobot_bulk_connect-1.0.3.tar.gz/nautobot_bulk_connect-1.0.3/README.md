# nautobot-bulk-connect

is a plugin for connecting rear ports in bulk.

Please note that this plugin uses internal Nautobot components, which is
explicitly discouraged by the documentation. We promise to keep the plugin up
to date, but the latest version might break on unsupported Nautobot version.
Your mileage may vary.

## Installation

The plugin can be found on [pypi](https://pypi.org/project/nautobot-bulk-connect).
You should therefore be able to install it using `pip`:

```
pip install nautobot-bulk-connect
```

Make sure to use the same version of `pip` that manages Nautobot, so if you’ve
set up a virtual environment, you will have to use `<venv>/bin/pip` instead.

After that, you should be able to install the plugin as described in [the
Nautobot documentation](https://nautbot.readthedocs.io/en/stable/plugins/). You’ll
have to add this to your `PLUGINS_CONFIG`:

```python
PLUGINS_CONFIG = {
    'nautobot_bulk_connect': {
        'device_role': None,
    }
}
```

Set `device_role` to a role name if you only want that role name to have the
plugin functionality.

## Usage

The plugin will add a button to your device view that allows you to connect
rear ports to other rear ports in bulk, by specifying starting ports and
a number/count of ports.

<img alt="The button" src="./docs/button.png" width="150">

The form you will be presented with looks like the form you are used to from
cable connections already.

![The cabling form](./docs/form.png)

The plugin will perform basic sanity checks on your input: if any rear port
inside the range is already connected, or the count goes outside of the range
of available rear ports on either side, an error message will be
returned.

<hr/>

Have fun!
