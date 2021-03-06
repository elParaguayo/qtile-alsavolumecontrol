import re
import subprocess

from libqtile.widget import base
from libqtile import bar, images


RE_VOL = re.compile(r"Playback\s[0-9]+\s\[([0-9]+)%\]\s\[(on|off)\]")


class ALSAVolumeControl(object):

    def __init__(self, step=5, device="Master", callback=None):
        self.muted = False
        self.step = step
        self.device = device
        self.volume = -1
        self.callback = callback
        self.widget_callback = None
        self.oldvol = -1
        self.oldmute = False
        self.get_volume()

    def _run(self, cmd):

        # Run the amixer command and use regex to capture volume line
        proc = subprocess.run(cmd.split(), capture_output=True)
        matched = RE_VOL.search(proc.stdout.decode())

        # If we find a match, extract volume and mute status
        if matched:
            self.volume = int(matched.groups()[0])
            self.muted = matched.groups()[1] == "off"

        # If volume or mute status has changed
        # then we need to trigger callbacks
        if any([self.volume != self.oldvol, self.muted != self.oldmute]):

            if self.callback:
                self.callback(self.volume, self.muted)

            if self.widget_callback:
                self.widget_callback(self.volume, self.muted)

            # Record old values
            self.oldvol = self.volume
            self.oldmute = self.muted

    def get_volume(self):
        cmd = "amixer get {}".format(self.device)
        self._run(cmd)

    def volume_up(self, *args, **kwargs):
        cmd = "amixer set {} {}%+".format(self.device, self.step)
        self._run(cmd)

    def volume_down(self, *args, **kwargs):
        cmd = "amixer set {} {}%-".format(self.device, self.step)
        self._run(cmd)

    def toggle_mute(self, *args, **kwargs):
        cmd = "amixer set {} toggle".format(self.device)
        self._run(cmd)

    def Widget(self, **config):

        # Create a widget and attach the callback
        widget = ALSAWidget(helper=self, **config)
        self.widget_callback = widget.status_change

        return widget


class ALSAWidget(base._Widget, base.PaddingMixin, base.MarginMixin):

    orientations = base.ORIENTATION_HORIZONTAL
    defaults = [
        ("font", "sans", "Default font"),
        ("fontsize", None, "Font size"),
        ("mode", "both", "Display mode: 'icon', 'bar', 'both'."),
        ("hide_interval", 5, "Timeout before bar is hidden after update"),
        ("text_format", "{volume}%", "String format"),
        ("bar_width", 75, "Width of display bar"),
        ("bar_colour_normal", "009900", "Colour of bar in normal range"),
        ("bar_colour_high", "999900", "Colour of bar if high range"),
        ("bar_colour_loud", "990000", "Colour of bar in loud range"),
        ("bar_colour_mute", "999999", "Colour of bar if muted"),
        ("limit_normal", 70, "Max percentage for normal range"),
        ("limit_high", 90, "Max percentage for high range"),
        ("limit_loud", 100, "Max percentage for loud range"),
        ("update_interval", 5,
            "Interval to update widget (e.g. if changes made in other apps)."),
        ("theme_path", None, "Path to theme icons.")
    ]

    icon_map = []

    def __init__(self, helper, **config):
        base._Widget.__init__(self, bar.CALCULATED, **config)
        self.add_defaults(ALSAWidget.defaults)
        self.add_defaults(base.PaddingMixin.defaults)
        self.add_defaults(base.MarginMixin.defaults)

        # Link to the VolumeControl module and initial status
        self.helper = helper
        self.muted = self.helper.muted
        self.volume = self.helper.volume

        # Variable to store icons
        self.surfaces = {}

        # Work out what we need to display
        self.show_bar = self.mode in ["bar", "both"]
        self.show_icon = self.mode in ["icon", "both"]

        # Define some variables to prevent early errors
        self.iconsize = 0
        self.text_width = 0

        # Variables for the timers we need
        self.update_timer = None
        self.hide_timer = None

        # Start of with bar hidden
        self.hidden = True

        # Map bar colours for volume level
        self.colours = [
            (self.limit_normal, self.bar_colour_normal),
            (self.limit_high, self.bar_colour_high),
            (self.limit_loud, self.bar_colour_loud)
        ]

    def _configure(self, qtile, bar):
        base._Widget._configure(self, qtile, bar)
        if self.show_icon:
            self.setup_images()

        # Minimum size needed to display text
        self.text_width = self.max_text_width()

        # Bar size is bigger of needed space and user-defined size
        self.bar_size = max(self.text_width, self.bar_width)

        # Start the refresh timer (to check if volume changed elsewhere)
        self.set_refresh_timer()

    def max_text_width(self):
        # Calculate max width of text given defined layout
        txt_width, _ = self.drawer.max_layout_size(
                                [self.text_format.format(volume=100)],
                                self.font,
                                self.fontsize)

        return txt_width

    def calculate_length(self):
        # Size depends on what's being shown
        # Start with zero width and add to it
        width = 0

        # Showing icons?
        if self.show_icon:
            width += self.iconsize

        # Showing bar?
        if self.show_bar and not self.hidden:
            width += self.bar_size

        return width

    def status_change(self, vol, muted):
        # Something's changed so let's update display
        # Unhide bar
        self.hidden = False

        # Get new values
        self.volume = vol
        self.muted = muted

        # Restart timer
        self.set_refresh_timer()

        # If we're showing the bar then set timer to hide it
        if self.show_bar:
            self.set_hide_timer()

        # Draw
        self.bar.draw()

    def setup_images(self):
        # Load icons
        names = (
            "audio-volume-muted",
            "audio-volume-low",
            "audio-volume-medium",
            "audio-volume-high"
        )
        d_images = images.Loader(self.theme_path)(*names)

        for name, img in d_images.items():
            new_height = self.bar.height - 1
            img.resize(height=new_height)
            self.iconsize = img.width
            self.surfaces[name] = img.pattern

    def draw(self):
        # Define an offset for x placement
        x_offset = 0

        # Clear the widget
        self.drawer.clear(self.background or self.bar.background)

        # Which icon do we need?
        if self.show_icon:
            if self.muted or self.volume == 0:
                img_name = "audio-volume-muted"
            elif self.volume <= 35:
                img_name = "audio-volume-low"
            elif self.volume <= 70:
                img_name = "audio-volume-medium"
            else:
                img_name = "audio-volume-high"

            # Draw icon
            self.drawer.ctx.set_source(self.surfaces[img_name])
            self.drawer.ctx.paint()

            # Increase offset
            x_offset += self.iconsize

        # Does bar need to be displayed
        if self.show_bar and not self.hidden:

            # Text and colour depends on mute status and volume level
            if not self.muted:
                text = self.text_format.format(volume=self.volume)
                fill = next(x[1] for x in self.colours if self.volume <= x[0])
            else:
                text = "X"
                fill = self.bar_colour_mute

            # Set bar colours
            self.drawer.set_source_rgb(fill)

            # Draw the bar
            self.drawer.fillrect(x_offset,
                                 0,
                                 self.bar_size * (self.volume / 100),
                                 self.height,
                                 1)

            # Create a text box
            layout = self.drawer.textlayout(text,
                                            "ffffff",
                                            self.font,
                                            self.fontsize,
                                            None,
                                            wrap=False)

            # We want to centre this vertically
            y_offset = (self.bar.height - layout.height) / 2

            # Set the layout as wide as the widget so text is centred
            layout.width = self.bar_size

            # Add the text to our drawer
            layout.draw(x_offset, y_offset)

        self.drawer.draw(offsetx=self.offset, width=self.length)

    def refresh(self):
        # Check the volume levels to see if they've changed
        # Callback will be triggered if they have
        self.helper.get_volume()

        # Restart timer
        self.set_refresh_timer()

    def set_refresh_timer(self):

        # Delete old timer
        if self.update_timer:
            self.update_timer.cancel()

        # Start new timer
        self.update_timer = self.timeout_add(self.update_interval,
                                             self.refresh)

    def set_hide_timer(self):
        # Cancel old timer
        if self.hide_timer:
            self.hide_timer.cancel()

        # Set new timer
        self.hide_timer = self.timeout_add(self.hide_interval, self.hide)

    def hide(self):
        # Hide the widget
        self.hidden = True
        self.bar.draw()
