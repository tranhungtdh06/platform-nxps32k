from platformio.managers.platform import PlatformBase

class Nxps32kPlatform(PlatformBase):
    def configure_default_packages(self, variables, targets):
        return super().configure_default_packages(variables, targets)