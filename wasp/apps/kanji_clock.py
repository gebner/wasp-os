# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Kanji clock
~~~~~~~~~~~~~~~~

Shows a time (as HHMM) together with a battery meter and the date.
"""

import wasp

import icons
from fonts import kanji55, kanji25

class KanjiClockApp():
    """Simple digital clock application."""
    NAME = 'Clock'
    ICON = icons.clock

    def foreground(self):
        """Activate the application.

        Configure the status bar, redraw the display and request a periodic
        tick callback every second.
        """
        wasp.system.bar.clock = False
        self._draw(True)
        wasp.system.request_tick(1000)

    def sleep(self):
        """Prepare to enter the low power mode.

        :returns: True, which tells the system manager not to automatically
                  switch to the default application before sleeping.
        """
        return True

    def wake(self):
        """Return from low power mode.

        Time will have changes whilst we have been asleep so we must
        udpate the display (but there is no need for a full redraw because
        the display RAM is preserved during a sleep.
        """
        self._draw()

    def tick(self, ticks):
        """Periodic callback to update the display."""
        self._draw()

    def _draw(self, redraw=False):
        """Draw or lazily update the display.

        The updates are as lazy by default and avoid spending time redrawing
        if the time on display has not changed. However if redraw is set to
        True then a full redraw is be performed.
        """
        draw = wasp.watch.drawable
        hi =  wasp.system.theme('bright')

        if redraw:
            now = wasp.watch.rtc.get_localtime()

            # Clear the display and draw that static parts of the watch face
            draw.fill()

            # Redraw the status bar
            wasp.system.bar.draw()
        else:
            # The update is doubly lazy... we update the status bar and if
            # the status bus update reports a change in the time of day 
            # then we compare the minute on display to make sure we 
            # only update the main clock once per minute.
            now = wasp.system.bar.update()
            if not now or self._min == now[4]:
                # Skip the update
                return

        large_font = kanji55
        draw.set_font(large_font)
        w = large_font.max_width()
        def draw_daiji(i, x, y):
            nonlocal draw, w
            draw.string(chr(ord('a') + i), x, y, w)

        # Draw the changeable parts of the watch face
        draw.set_color(hi)
        draw_daiji(now[4]  % 10, 3*w + 1, 80)
        draw_daiji(now[4] // 10, 2*w + 1, 80)
        draw_daiji(now[3]  % 10, 1*w + 1, 80)
        draw_daiji(now[3] // 10, 0*w + 1, 80)

        draw.set_font(kanji25)
        draw.set_color(hi)
        draw.string('{}Y {}M {}D'.format(now[0], now[1], now[2]),
                1, 180, width=240)

        # Record the minute that is currently being displayed
        self._min = now[4]
