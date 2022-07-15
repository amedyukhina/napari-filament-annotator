import itertools

import numpy as np


class Annotation():
    def __init__(self, viewer, image_layer):
        self.viewer = viewer
        self.image_layer = image_layer
        bbox = self.__get_frame_box(image_layer.data.shape)

        self.annotation_layer = self.viewer.add_shapes(bbox,
                                                       name='annotations',
                                                       shape_type='path',
                                                       edge_width=0,
                                                       scale=image_layer.scale
                                                       )

    def __get_frame_box(self, shape):
        # add a bounding box to set the coordinates range
        bbox = list(itertools.product(*[np.arange(2)
                                        for i in range(len(shape[-3:]))]))
        if len(shape) > 3:
            bbox = [(0,) + b for b in bbox]
        bbox = bbox * np.array(shape)
        return bbox
