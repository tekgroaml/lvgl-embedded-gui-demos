"""Same-content RGB light profiles for SBS and hardware-clone boards."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('ambient-light','Circular RGB ambient-light display',('round','round'),
                      'ambient-light-sbs',('light','light'),
                      ('scenes.same.round.ambient_light.panels:LightPanel','scenes.same.round.ambient_light.panels:LightPanel'),
                      'scenes.same.round.ambient_light.model:LightDemo',native_dual480=True,content_modes=('same',))
CLONE_SCENE=SceneDefinition('ambient-light-clone','Hardware-cloned RGB ambient light',
                      SCENE.shapes,'ambient-light-clone',SCENE.panel_ids,SCENE.panel_factories,SCENE.demo_factory,
                      package='scenes.same.round.ambient_light',content_modes=('same',),topology='single-link-clone',
                      refresh_overrides=((480,(60,62.811001,71.295249)),),layout_versions=((480,'1.1.0'),))
