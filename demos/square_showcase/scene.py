"""Register square product playback using the standard single-window lifecycle."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('product-showcase-square','Square home, PC and industrial showcase',
                      ('square','square'),'product-showcase-square-sbs',('showcase-left','showcase-right'),
                      ('demos.square_showcase.panels:LeftPanel','demos.square_showcase.panels:RightPanel'),
                      'demos.square_showcase.playback:SquareShowcaseSource',native_dual480=True,
                      package='demos.square_showcase')
