"""Reuse the product timeline, with a separate square-only validated playlist."""
from pathlib import Path
from demos.shared.playback import ShowcaseSource,load_playlist

PLAYLIST=Path(__file__).with_name('playlist.json')
VIEWS=('smart-home','pc-monitor-square','industrial')
ICONS={'smart-home':'home','pc-monitor-square':'computer','industrial':'factory'}


class SquareShowcaseSource(ShowcaseSource):
    shapes=('square','square')

    def load_configuration(self):
        return load_playlist(PLAYLIST,views=VIEWS,icons=ICONS)
