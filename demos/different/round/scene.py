"""Register the independent product demonstration using the shared lifecycle."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('product-showcase','Aircraft, vehicle and PC product-use showcase',
                      ('round','round'),'product-showcase-sbs',('showcase-left','showcase-right'),
                      ('demos.different.round.panels:LeftPanel','demos.different.round.panels:RightPanel'),
                      'demos.different.round.playback:ShowcaseSource',native_dual480=True,
                      package='demos.different.round')
