"""Register square product playback using the standard single-window lifecycle."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('product-showcase-square','Square home, PC and industrial showcase',
                      ('square','square'),'product-showcase-square-sbs',('showcase-left','showcase-right'),
                      ('demos.different.square.panels:LeftPanel','demos.different.square.panels:RightPanel'),
                      'demos.different.square.playback:SquareShowcaseSource',native_dual480=True,
                      package='demos.different.square')
