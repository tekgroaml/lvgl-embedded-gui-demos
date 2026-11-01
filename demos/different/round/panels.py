"""Round introduction panels use the common brand/application composition."""
from demos.shared.panels import ShowcasePanel,fitted_text


class LeftPanel(ShowcasePanel):
    def __init__(self):super().__init__(0)


class RightPanel(ShowcasePanel):
    def __init__(self):super().__init__(1)
