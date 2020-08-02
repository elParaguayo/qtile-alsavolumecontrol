# ALSA Volume Control and Widget

This module provides basic volume controls and a simple icon widget showing volume level for Qtile.

## About

The module is very simple and, so far, just allows controls for volume up, down and mute.

Volume control is handled by running the appropriate amixer command. The widget is updated instantly when volume is changed via this code, but will also update on an interval (i.e. it will reflect changes to volume made by other programs).

## Demo

Here is a screenshot from my HTPC showing the widget in the bar. The theme currently shown is called "Paper".

![Screenshot](images/alsavolumecontrol-screenshot.png?raw=true)

## Installation

You can clone the repository and run:

```
python setup.py install
```
or, for Arch users, just copy the PKGBUILD file to your machine and build.

## Configuration

Add the code to your config (`~/.config/qtile/config.py`):

```python
from alsavolumecontrol import ALSAVolumeControl
...
vc = ALSAVolumeControl()
...
keys = [
...
Key([], "XF86AudioRaiseVolume", lazy.function(vc.volume_up)),
Key([], "XF86AudioLowerVolume", lazy.function(vc.volume_down)),
Key([], "XF86AudioMute", lazy.function(vc.toggle_mute)),
...
]
...
screens = [
    Screen(
        top=bar.Bar(
            [
                widget.CurrentLayout(),
                widget.GroupBox(),
                widget.Prompt(),
                widget.WindowName(),
                vc.Widget(),
                widget.Clock(format='%Y-%m-%d %a %I:%M %p'),
                widget.QuickExit(),
            ],
            24,
        ),
    ),
]
```

Note: event if you are controlling volume differently, the widget must be created via the "Widget" method of an ALSAVolumeControl instance.

## Customising

The volume control assumes the "Master" device is being updated and that volume is changed by 5%. In addition, the volume control class accepts a callback function. The function passed should expect to receive two arguments when called (volume, muted). These can be altered as follows:

```python
def my_volume_callback(volume, muted):
    # Do something with those values here
    ...

vc = ALSAVolumeControl(device="MyDevice",
                       step=10,
                       callback=my_volume_callback)
```



The widget can be customised with the following arguments:

<table>
    <tr>
            <td>font</td>
            <td>Default font</td>
    </tr>
    <tr>
            <td>fontsize</td>
            <td>Font size</td>
    </tr>
    <tr>
            <td>update_interval</td>
            <td>How regularly (in seconds) to check for updates made by other programs</td>
    </tr>
    <tr>
            <td>theme_path</td>
            <td>Path to icons to use.</td>
    </tr>
</table>

Note: it may be preferable to set the "theme_path" via the "widget_defaults" variable in your config.py so that themes are applied consistently across widgets.

## Contributing

If you've used this (great, and thank you) you will find bugs so please [file an issue](https://github.com/elParaguayo/qtile-alsavolumecontrol/issues/new).
