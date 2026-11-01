"""The square same-content lineup is distinct from all round use cases."""
from pathlib import Path
from demos.shared.playback import ShowcaseSource,load_playlist

PLAYLIST=Path(__file__).with_name('playlist.json')
VIEWS=('store-signage','meeting-room','parcel-status')
ICONS={'store-signage':'store','meeting-room':'room','parcel-status':'parcel'}


class SquareSameSource(ShowcaseSource):
    shapes=('square','square')
    content_mode='same'
    def load_configuration(self):return load_playlist(PLAYLIST,views=VIEWS,icons=ICONS)
