"""Reuse the ready-anchored39s timeline, validating same-content demo scenes."""
from pathlib import Path
from demos.shared.playback import ShowcaseSource,load_playlist

PLAYLIST=Path(__file__).with_name('playlist.json')
VIEWS=('music-ambient','ambient-light','ambient-clock')
ICONS={'music-ambient':'music','ambient-light':'light','ambient-clock':'clock'}


class SameShowcaseSource(ShowcaseSource):
    content_mode='same'
    def load_configuration(self):return load_playlist(PLAYLIST,views=VIEWS,icons=ICONS)
