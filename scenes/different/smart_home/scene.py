"""Smart-home scene capabilities, separate from product-showcase orchestration."""
from common.definition import SceneDefinition

SCENE=SceneDefinition('smart-home','Home environment and energy',('square','square'),'smart-home-sbs',
                      ('home-climate','home-energy'),
                      ('scenes.different.smart_home.panels:ClimatePanel','scenes.different.smart_home.panels:EnergyPanel'),
                      'scenes.different.smart_home.model:HomeDemo',native_dual480=True)
