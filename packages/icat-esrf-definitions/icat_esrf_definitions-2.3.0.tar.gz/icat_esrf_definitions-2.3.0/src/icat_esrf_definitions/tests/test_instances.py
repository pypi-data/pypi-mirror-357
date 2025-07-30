from silx.io.dictdump import dicttonx

from ..models.generate import generate_dataset


def test_nexus(tmp_path):
    dataset = generate_dataset()
    treedict = dataset.to_hdf5_dict()
    filename = str(tmp_path / "dataset.h5")
    dicttonx(treedict, filename)
