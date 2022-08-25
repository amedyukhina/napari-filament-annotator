import itertools

import numpy as np
from scipy import ndimage

from .utils.geom import compute_polygon_intersection
from .utils.postproc import snap_to_bright, gradient


class Annotator:
    """
    Annotator
    """

    def __init__(self, viewer, img_layer, params):
        self.params = params
        img = img_layer.data.copy().astype(np.float32)
        img = ndimage.gaussian_filter(img, sigma=params.sigma)
        self.grad = gradient(img, img_layer.scale)  # calculate the gradient for the active contour

        self.near_points = []  # store near points of the currently drawn polygon
        self.far_points = []  # store far points of the currently drawn polygon
        self.polygons = []  # store near and far points of the last 1-2 polygons (to compute intersections)
        self.annotation_layer = viewer.add_shapes(_get_bbox(img_layer.data.shape),
                                                  name='annotations',
                                                  shape_type='path',
                                                  edge_width=0,
                                                  scale=img_layer.scale,
                                                  blending='additive'
                                                  )
        self.viewer = viewer
        self.add_callbacks()

    def add_callbacks(self):
        self.annotation_layer.mouse_drag_callbacks.append(self._draw_polygon)
        self.annotation_layer.mouse_drag_callbacks.append(self._calculate_intersection)
        self.annotation_layer.bind_key('d', self.delete_the_last_shape)
        self.annotation_layer.bind_key('p', self.delete_the_last_point)
        self.annotation_layer.bind_key('f', self.delete_the_first_filament_point)
        self.annotation_layer.bind_key('l', self.delete_the_last_filament_point)

    def _draw_polygon(self, layer, event):
        """
        Draw a polygon under the current annotation curve.
        At each point of the annotation curve, we extend a line perpendicualar to the image view, and calculate
            the points intersection of this line with the near and far image border.
        These points of intersection - the near and far points - constitute the boundary of the polygon.
        """
        yield
        if 'Control' in event.modifiers:  # draw a polygon if "Control" is pressed
            # get the near and far points at the mouse position
            near_point, far_point = layer.get_ray_intersections(
                event.position,
                event.view_direction,
                event.dims_displayed
            )
            # append to the array of near and far points
            if (near_point is not None) and (far_point is not None):
                self.near_points.append(near_point)
                self.far_points.append(far_point)

            # draw a polygon from the array of near and far points
            if len(self.near_points) > 0 and len(self.far_points) > 0:
                self.draw_polygon(layer)

        yield

    def draw_polygon(self, layer, color: str = 'red'):
        """
        Draw a polygon between provided near and far points.

        Parameters
        ----------
        layer : napari.layers.Shapes
            napari shapes layer with annotations
        color : str, optional
            Color of the polygon

        Returns
        -------
        Updated shapes layer
        """
        near_points = self.near_points.copy()
        far_points = self.far_points.copy()
        if len(near_points) < 2:  # if only one point, add a temporary point for display purposes
            near_points.append(np.array(near_points[0]) + self.params.line_width)
            far_points.append(np.array(far_points[0]) + self.params.line_width)

        # reverse the far points and combine near and far points into a polygon
        far_points_reverse = far_points.copy()
        far_points_reverse.reverse()
        polygon = np.array(near_points + far_points_reverse)

        # remove the old polygon belonging to the same annotation
        if np.array((layer.data[-1][0] == polygon[0])).all():
            layer.selected_data = set(range(layer.nshapes - 1, layer.nshapes))
            layer.remove_selected()

        # add the updated polygon
        layer.add(
            polygon,
            shape_type='polygon',
            edge_width=self.params.line_width,
            edge_color=color
        )

    def _calculate_intersection(self, layer, event):
        """
        Calculate the intersection of two polygons, if the length of the polygons array == 2.
        """
        yield
        while event.type == 'mouse_move':
            if 'Control' not in event.modifiers:  # Only execute if "Control" is not pressed
                # add the last annotation to the polygon array and clear the annotation arrays
                self.calculate_intersection(layer)

            yield

    def calculate_intersection(self, layer):
        if len(self.near_points) > 0:
            self.polygons.append([self.near_points.copy(), self.far_points.copy()])
        self.near_points.clear()
        self.far_points.clear()

        # if there are 2 or more polygons, calculate their intersection
        if len(self.polygons) >= 2:
            filament = compute_polygon_intersection(self.polygons, layer.scale)
            filament = snap_to_bright(snake=filament, grad=self.grad,
                                      spacing=layer.scale, **vars(self.params))

            # remove the 2 polygons from the shapes layer
            layer.selected_data = set(range(layer.nshapes - 2, layer.nshapes))
            layer.remove_selected()

            # add the calculated filament
            layer.add(filament, shape_type='path', edge_color='green', edge_width=self.params.line_width)

            # clear the polygons array
            self.polygons.pop()
            self.polygons.pop()

    def delete_the_last_shape(self, layer, show_message=True):
        """
        Remove the last added shape (polygon or filament)

        """
        if layer.nshapes > 1:
            msg = 'delete the last added shape'

            # delete the last shape in the annotation layer
            layer.selected_data = set(range(layer.nshapes - 1, layer.nshapes))
            layer.remove_selected()

            if len(self.near_points) > 0:  # if any points in the near/far points array, clear them
                self.near_points.clear()
                self.far_points.clear()

            elif len(self.polygons) > 0:  # otherwise, clear the polygons array
                self.polygons.pop()
        else:
            msg = 'no shapes to delete'

        if show_message:
            layer.status = msg
            print(msg)

    def delete_the_last_point(self, layer):
        """
        Remove the last added point

        """
        if len(self.near_points) > 0 and len(self.far_points) > 0:
            self.near_points.pop()
            self.far_points.pop()
            if len(self.near_points) > 0:
                self.draw_polygon(layer)
            else:
                self.delete_the_last_shape(layer, show_message=False)

    def delete_the_last_filament_point(self, layer):
        """Remove the last point in the last filament"""
        if layer.nshapes > 1:
            data = layer.data[-1][:-1]
            layer.data = layer.data[:-1] + [data]

    def delete_the_first_filament_point(self, layer):
        """Remove the first point in the last filament"""
        if layer.nshapes > 1:
            data = layer.data[-1][1:]
            layer.data = layer.data[:-1] + [data]


def _get_bbox(shape):
    bbox = list(itertools.product(*[np.arange(2)
                                    for i in range(len(shape[-3:]))]))
    if len(shape) > 3:
        bbox = [(0,) + b for b in bbox]
    bbox = bbox * np.array(shape)
    return bbox
