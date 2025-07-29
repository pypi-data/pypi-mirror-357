from ..models.user_settings_models import DbSetting, SocketSettings
from ..models.settings_base_class import SettingsBaseClass, SettingsTypeEnum


def settings_from_dict(record: dict) -> SettingsBaseClass:
    raw_type = record["Type"]


    try:
        if isinstance(raw_type, str):
            if raw_type.isdigit():
                set_type = SettingsTypeEnum(int(raw_type))
            else:
                set_type = SettingsTypeEnum[raw_type.upper()]  # enum by name
        elif isinstance(raw_type, int):
            set_type = SettingsTypeEnum(raw_type)
        elif isinstance(raw_type, SettingsTypeEnum):
            set_type = raw_type
        else:
            raise ValueError("Unrecognized enum format")
    except (KeyError, ValueError, TypeError) as e:
        raise ValueError(f"Invalid setting type '{raw_type}': {e}")


    type_map = {
        SettingsTypeEnum.SOCKET: SocketSettings,
        SettingsTypeEnum.PATH: DbSetting,
        # aggiungi le altre
    }

    cls = type_map.get(set_type)
    if not cls:
        raise ValueError(f"No subclass for setting type {set_type}")

    return cls.from_dict(record)
