import pandas as pd
from napari_filament_annotator.utils.const import COL_NAME
from napari_filament_annotator.utils.io import annotation_to_pandas, pandas_to_annotations


def test_conversion(paths):
    df = annotation_to_pandas(paths)
    assert isinstance(df, pd.DataFrame)
    paths2, labels = pandas_to_annotations(df)
    assert isinstance(paths2, list)
    assert len(labels) == len(paths2) == len(paths) == len(df[COL_NAME].unique())
    assert sum([len(path) for path in paths2]) == len(df)
    assert sum([len(path) for path in paths]) == len(df)
    for i in range(len(paths)):
        assert (paths[i] == paths2[i]).all()
