"""Same-content music scene, isolated from the existing different-content demos."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('music-ambient','Dual-round music and ambient light',('round','round'),
                      'music-ambient-sbs',('music','music'),
                      ('scenes.same.round.music_ambient.panels:MusicPanel','scenes.same.round.music_ambient.panels:MusicPanel'),
                      'scenes.same.round.music_ambient.model:MusicDemo',native_dual480=True,
                      content_modes=('same',))

# Some dual-screen boards duplicate a single square input in hardware. They
# must not receive the double-width signal used by SBS boards.
CLONE_SCENE=SceneDefinition('music-ambient-clone','Hardware-cloned dual-round music',
                      ('round','round'),'music-ambient-clone',('music','music'),
                      SCENE.panel_factories,SCENE.demo_factory,
                      package='scenes.same.round.music_ambient',content_modes=('same',),
                      topology='single-link-clone',refresh_overrides=((480,(60,62.811001)),))
