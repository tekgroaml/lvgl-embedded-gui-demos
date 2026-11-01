"""Register the independent product demonstration using the shared lifecycle."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('product-showcase','Aircraft, vehicle and PC product-use showcase',
                      ('round','round'),'product-showcase-sbs',('showcase-left','showcase-right'),
                      ('demos.product_showcase.panels:LeftPanel','demos.product_showcase.panels:RightPanel'),
                      'demos.product_showcase.playback:ShowcaseSource',native_dual480=True,
                      package='demos.product_showcase')
