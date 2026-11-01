"""Clock profiles for same-content software and hardware duplication."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('ambient-clock','Round desktop clock and sample weather',('round','round'),
                      'ambient-clock-sbs',('clock','clock'),
                      ('scenes.same.round.ambient_clock.panels:ClockPanel','scenes.same.round.ambient_clock.panels:ClockPanel'),
                      'scenes.same.round.ambient_clock.model:ClockDemo',native_dual480=True,content_modes=('same',))
CLONE_SCENE=SceneDefinition('ambient-clock-clone','Hardware-cloned desktop information clock',
                      SCENE.shapes,'ambient-clock-clone',SCENE.panel_ids,SCENE.panel_factories,SCENE.demo_factory,
                      package='scenes.same.round.ambient_clock',content_modes=('same',),topology='single-link-clone',
                      refresh_overrides=((480,(60,62.811001,71.295249)),),layout_versions=((480,'1.1.0'),))
