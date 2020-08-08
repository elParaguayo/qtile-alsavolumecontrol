# ALSA Volume Control and Widget

This module provides basic volume controls and a simple icon widget showing volume level for Qtile.

## About

The module is very simple and, so far, just allows controls for volume up, down and mute.

Volume control is handled by running the appropriate amixer command. The widget is updated instantly when volume is changed via this code, but will also update on an interval (i.e. it will reflect changes to volume made by other programs).

The widget displays volume level via an icon, bar or both. The icon is permanently visible while the bar only displays when the volume is changed and will hide after a user-defined period.

## Demo

Here is a screenshot from my HTPC showing the widget in the bar. The icon theme currently shown is called "Paper".

_"Icon" mode:_</br>
![Screenshot](images/volumecontrol-icon.gif?raw=true)

_"Bar" mode:_</br>
![Screenshot](images/volumecontrol-bar.gif?raw=true)

_"Both" mode:_</br>
![Screenshot](images/volumecontrol-both.gif?raw=true)


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
            <td>mode</td>
            <td>Display mode: 'icon', 'bar', 'both'.</td>
    </tr>
    <tr>
            <td>hide_interval</td>
            <td>Timeout before bar is hidden after update</td>
    </tr>
    <tr>
            <td>text_format</td>
            <td>String format</td>
    </tr>
    <tr>
            <td>bar_width</td>
            <td>Width of display bar</td>
    </tr>
    <tr>
            <td>bar_colour_normal</td>
            <td>Colour of bar in normal range</td>
    </tr>
    <tr>
            <td>bar_colour_high</td>
            <td>Colour of bar if high range</td>
    </tr>
    <tr>
            <td>bar_colour_loud</td>
            <td>Colour of bar in loud range</td>
    </tr>
    <tr>
            <td>bar_colour_mute</td>
            <td>Colour of bar if muted</td>
    </tr>
    <tr>
            <td>limit_normal</td>
            <td>Max percentage for normal range</td>
    </tr>
    <tr>
            <td>limit_high</td>
            <td>Max percentage for high range</td>
    </tr>
    <tr>
            <td>limit_loud</td>
            <td>Max percentage for loud range</td>
    </tr>
    <tr>
            <td>update_interval</td>
            <td>Interval to update widget (e.g. if changes made in other apps).</td>
    </tr>
    <tr>
            <td>theme_path</td>
            <td>Path to theme icons.</td>
    </tr>
</table>

Note: it may be preferable to set the "theme_path" via the "widget_defaults" variable in your config.py so that themes are applied consistently across widgets.

## Contributing

If you've used this (great, and thank you) you will find bugs so please [file an issue](https://github.com/elParaguayo/qtile-alsavolumecontrol/issues/new).
