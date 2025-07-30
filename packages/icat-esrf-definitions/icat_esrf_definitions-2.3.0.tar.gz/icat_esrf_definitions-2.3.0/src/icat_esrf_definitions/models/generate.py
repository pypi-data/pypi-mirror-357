import datetime

from .dataset import IcatDataset


def generate_dataset(counter: int = 0) -> IcatDataset:
    icat_dict = dict()

    for icat_name, icat_field_info in IcatDataset.icat_fields().items():
        value_type = icat_field_info.value_type
        if issubclass(value_type, bool):
            value = bool(counter % 2)
        elif issubclass(value_type, int):
            value = counter
        elif issubclass(value_type, float):
            value = counter + 0.1
        elif issubclass(value_type, str):
            value = f"{icat_name!r} value"
        elif issubclass(value_type, datetime.datetime):
            value = datetime.datetime.fromtimestamp(1_700_000_000 + counter)
        else:
            raise NotImplementedError(f"Unsupported field type: {value_type}")

        unit_info = icat_field_info.unit_info
        if unit_info is not None and unit_info.units is not None:
            value = value, unit_info.units

        icat_dict[icat_name] = value
        counter += 1

    return IcatDataset.from_icat_dict(icat_dict)
