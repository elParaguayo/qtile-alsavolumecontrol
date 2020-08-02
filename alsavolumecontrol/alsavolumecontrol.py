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
        proc = subprocess.run(cmd.split(), capture_output=True)
        matched = RE_VOL.search(proc.stdout.decode())

        if matched:
            self.volume = int(matched.groups()[0])
            self.muted = matched.groups()[1] == "off"

        if any([self.volume != self.oldvol, self.muted != self.oldmute]):

            if self.callback:
                self.callback(self.volume, self.muted)

            if self.widget_callback:
                self.widget_callback(self.volume, self.muted)

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
        widget = ALSAWidget(helper=self, **config)
        self.widget_callback = widget.status_change
        return widget


class ALSAWidget(base._Widget, base.PaddingMixin, base.MarginMixin):

    orientations = base.ORIENTATION_HORIZONTAL
    defaults = [
        ("font", "sans", "Default font"),
        ("fontsize", None, "Font size"),
        ("update_interval", 5, "Interval to update widget (e.g. if changes made in other apps)."),
        ("theme_path", None, "Path to theme icons.")
    ]

    icon_map = []

    def __init__(self, helper, **config):
        base._Widget.__init__(self, 0, **config)
        self.add_defaults(ALSAWidget.defaults)
        self.add_defaults(base.PaddingMixin.defaults)
        self.add_defaults(base.MarginMixin.defaults)
        self.helper = helper
        self.surfaces = {}
        self.muted = self.helper.muted
        self.volume = self.helper.volume
        self.iconsize = 0
        self.length = 0
        self.update_timer = None

    def status_change(self, vol, muted):
        self.volume = vol
        self.muted = muted
        if self.update_timer:
            self.update_timer.cancel()
            self.set_timer()

        self.update()

    def setup_images(self):
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
            if img.width > self.length:
                self.length = img.width
                self.iconsize = self.length
            self.surfaces[name] = img.pattern

    def update(self):
        if self.muted or self.volume == 0:
            img_name = "audio-volume-muted"
        elif self.volume <= 35:
            img_name = "audio-volume-low"
        elif self.volume <= 70:
            img_name = "audio-volume-medium"
        else:
            img_name = "audio-volume-high"

        self.drawer.clear(self.background or self.bar.background)
        self.drawer.ctx.set_source(self.surfaces[img_name])
        self.drawer.ctx.paint()
        self.bar.draw()

    def _configure(self, qtile, bar):
        base._Widget._configure(self, qtile, bar)
        self.setup_images()
        self.set_timer()
        self.update()

    def refresh(self):
        self.helper.get_volume()
        self.set_timer()

    def set_timer(self):
        self.update_timer = self.timeout_add(self.update_interval, self.refresh)

    def calculate_length(self):
        return self.iconsize if self.iconsize else 0

    def draw(self):
        self.drawer.draw(offsetx=self.offset, width=self.length)
