"""Round different-content playlist using the shared showcase timeline."""
from pathlib import Path
from demos.shared.playback import Timeline,ShowcaseData,ShowcaseSource as BaseShowcaseSource
from demos.shared.playback import load_playlist as read_playlist

PLAYLIST=Path(__file__).with_name('playlist.json')
VIEWS=('flight','automotive','pc-monitor')
ICONS={'flight':'aircraft','automotive':'vehicle','pc-monitor':'computer'}


def load_playlist(path=PLAYLIST,views=VIEWS,icons=ICONS):return read_playlist(path,views=views,icons=icons)


class ShowcaseSource(BaseShowcaseSource):
    def load_configuration(self):return load_playlist()
