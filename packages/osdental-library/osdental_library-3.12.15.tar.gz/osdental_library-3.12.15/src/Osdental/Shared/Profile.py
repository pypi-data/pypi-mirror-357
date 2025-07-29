from enum import Enum

class Profile(str, Enum):
    SUPER_ADMIN_PROFILE = 'SPAU'
    ADMIN_OSD_PROFILE = 'OSDA'
    MARKETING_PROFILE = 'OSDMK'

    def __str__(self):
        return self.value