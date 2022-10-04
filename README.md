# 3D Filament Annotator

[![DOI](https://zenodo.org/badge/513980347.svg)](https://zenodo.org/badge/latestdoi/513980347)
[![License Apache Software License 2.0](https://img.shields.io/pypi/l/napari-filament-annotator.svg?color=green)](https://github.com/amedyukhina/napari-filament-annotator/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-filament-annotator.svg?color=green)](https://pypi.org/project/napari-filament-annotator)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-filament-annotator.svg?color=green)](https://python.org)
[![tests](https://github.com/amedyukhina/napari-filament-annotator/workflows/tests/badge.svg)](https://github.com/amedyukhina/napari-filament-annotator/actions)
[![codecov](https://codecov.io/gh/amedyukhina/napari-filament-annotator/branch/main/graph/badge.svg)](https://codecov.io/gh/amedyukhina/napari-filament-annotator)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-filament-annotator)](https://napari-hub.org/plugins/napari-filament-annotator)

3D Filament Annotator is a tool for annotating filaments and other curvilinear structures in 3D. 
The 3D annotation is done by annotating the filament in two different projections, 
calculating intersection, and refining the filament position with active contours.

![demo](docs/demo_09.gif)


## Installation

### Install napari

    pip install napari[all]

### Install the filament annotator

<!--
You can install `napari-filament-annotator` via [pip]:

    pip install napari-filament-annotator


To install latest development version :
-->
    pip install git+https://github.com/amedyukhina/napari-filament-annotator.git

## Usage

For detailed usage instructions, please refer to the [usage tutorial](docs/tutorial.md).

## Contributing

Contributions are very welcome both with regard to plugin functionality, and
tips on using it and setting parameters. 

Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [Apache Software License 2.0] license,
"napari-filament-annotator" is free and open source software

## Dependencies

- [napari](https://github.com/napari/napari)
- [scikit-image](https://scikit-image.org/)
- [scikit-learn](https://github.com/scikit-learn/scikit-learn)
- [NetworkX](https://networkx.org/documentation/stable/index.html)
- [Geometry3D](https://github.com/GouMinghao/Geometry3D)


## Issues

If you encounter any problems, please [file an issue] along with a detailed description.


----------------------------------

This [napari] plugin was generated with [Cookiecutter] using [@napari]'s [cookiecutter-napari-plugin] template.


<!--
Don't miss the full getting started guide to set up your new package:
https://github.com/napari/cookiecutter-napari-plugin#getting-started

and review the napari docs for plugin developers:
https://napari.org/plugins/index.html
-->


[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin

[file an issue]: https://github.com/amedyukhina/napari-filament-annotator/issues

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
