"""Square title frames; reuse the brand/application split and effect factories."""
from demos.product_showcase.panels import ShowcasePanel
from common.theme import PANEL,CYAN


class SquareShowcasePanel(ShowcasePanel):
    display_label='DUAL SQUARE DISPLAYS'

    def frame(self,p):
        p.rect(PANEL,(14,14,452,452),width=2,radius=16)
        p.line(CYAN,(36,35),(118,35),3)
        p.line(CYAN,(362,445),(444,445),3)


class LeftPanel(SquareShowcasePanel):
    def __init__(self):super().__init__(0)


class RightPanel(SquareShowcasePanel):
    def __init__(self):super().__init__(1)
