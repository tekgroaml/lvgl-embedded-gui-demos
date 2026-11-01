"""Default hardware-clone showcase and an explicit double-width SBS variant."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('product-showcase-same','Same-content round product showcase',
                      ('round','round'),'product-showcase-same-clone',('showcase','showcase'),
                      ('demos.same.round.panels:SamePanel','demos.same.round.panels:SamePanel'),
                      'demos.same.round.playback:SameShowcaseSource',package='demos.same.round',
                      content_modes=('same',),topology='single-link-clone',
                      refresh_overrides=((480,(60,62.811001)),))
SBS_SCENE=SceneDefinition('product-showcase-same-sbs','Software-duplicated round product showcase',
                      SCENE.shapes,'product-showcase-same-sbs',SCENE.panel_ids,SCENE.panel_factories,SCENE.demo_factory,
                      native_dual480=True,package='demos.same.round',content_modes=('same',))
