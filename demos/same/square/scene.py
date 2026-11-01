"""Square same-content showcases have independent profiles, playlist and geometry."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('product-showcase-same-square','Square same-content use-case showcase',
                      ('square','square'),'product-showcase-same-square-clone',('showcase','showcase'),
                      ('demos.same.square.panels:SquareSamePanel','demos.same.square.panels:SquareSamePanel'),
                      'demos.same.square.playback:SquareSameSource',package='demos.same.square',
                      content_modes=('same',),topology='single-link-clone')
SBS_SCENE=SceneDefinition('product-showcase-same-square-sbs','Square software-duplicated showcase',
                      SCENE.shapes,'product-showcase-same-square-sbs',SCENE.panel_ids,SCENE.panel_factories,
                      SCENE.demo_factory,package='demos.same.square',content_modes=('same',))
