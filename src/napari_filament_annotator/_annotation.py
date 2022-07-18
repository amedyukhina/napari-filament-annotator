import numpy as np
from scipy import ndimage

from .utils.geom import compute_polygon_intersection
from .utils.postproc import sort_points, snap_to_brightest


def annotate_filaments(annotation_layer, params, output_fn=None, image_layer=None):
    near_points = []  # store near points of the currently drawn polygon
    far_points = []  # store far points of the currently drawn polygon
    polygons = []  # store near and far points of the last 1-2 polygons (to compute intersections)
    img = None

    def __convert_sigma(sigma, shape):
        """Convert the sigma value to fit the image shape"""
        sigma = np.ravel(sigma)
        if len(sigma) < 3:
            sigma = [sigma[0]] * 3
        if len(shape) > 3:
            sigma = [0] * (len(shape) - len(sigma)) + sigma
        return sigma

    if image_layer is not None:
        img = image_layer.data.copy()
        sigma = __convert_sigma(params.sigma, img.shape)
        img = ndimage.gaussian_filter(img, sigma=sigma)  # smooth the image

    @annotation_layer.mouse_drag_callbacks.append
    def draw_polygon_shape(layer, event):
        """
        Draw a line over the current 3D view of the filament.
        Extend the line into a polygon restricted by the near and far intersection points.
        """
        yield
        if 'Control' in event.modifiers:  # draw a polygon if "Control" is pressed
            # get the near a far points of the mouse position
            near_point, far_point = layer.get_ray_intersections(
                event.position,
                event.view_direction,
                event.dims_displayed
            )
            # append to the array of near and far points
            if (near_point is not None) and (far_point is not None):
                near_points.append(near_point)
                far_points.append(far_point)

            # draw a polygon from the array of near and far points
            if len(near_points) > 0 and len(far_points) > 0:
                draw_polygon(layer, near_points.copy(), far_points.copy(), line_width=params.line_width)

        yield

    @annotation_layer.mouse_drag_callbacks.append
    def calculate_intersection(layer, event):
        """
        Calculate the intersection of two polygons, if the length of the polygons array == 2.
        """
        yield
        while event.type == 'mouse_move':
            if 'Control' not in event.modifiers:  # Only execute if "Control" is not pressed
                # add the last annotation to the polygon array and clear the annotation arrays
                if len(near_points) > 0:
                    polygons.append([near_points.copy(), far_points.copy()])
                near_points.clear()
                far_points.clear()

                # if there are 2 or more polygons, calculate their intersection
                if len(polygons) >= 2:
                    npt1 = polygons[0][0]
                    npt2 = polygons[1][0]
                    fpt1 = polygons[0][1]
                    fpt2 = polygons[1][1]
                    mt = compute_polygon_intersection(npt1, npt2, fpt1, fpt2)

                    # snap to the brightest point
                    if image_layer is not None:
                        mt = np.array(mt)
                        if len(img.shape) > 3:
                            mt[:, 1:] = snap_to_brightest(mt[:, 1:], img=img[mt[0][0]],
                                                          rad=params.neighborhood_radius,
                                                          decay_sigma=params.decay_sigma)
                        else:
                            mt = snap_to_brightest(mt, img=img, rad=params.neighborhood_radius,
                                                   decay_sigma=params.decay_sigma)

                    mt = sort_points(mt)  # make sure the filament coordinates are sorted

                    # remove the 2 polygons from the shapes layer
                    layer.selected_data = set(range(layer.nshapes - 2, layer.nshapes))
                    layer.remove_selected()

                    # add the calculated filament
                    layer.add(mt, shape_type='path', edge_color='green', edge_width=params.line_width)

                    # clear the polygons array
                    polygons.pop()
                    polygons.pop()

            yield

    @annotation_layer.bind_key('p')
    def delete_the_last_shape(layer, show_message=True):
        """
        Remove the last added shape (polygon or filament)

        """
        if layer.nshapes > 1:
            msg = 'delete the last added shape'

            # delete the last shape in the annotation layer
            layer.selected_data = set(range(layer.nshapes - 1, layer.nshapes))
            layer.remove_selected()

            if len(near_points) > 0:  # if any points in the near/far points array, clear them
                near_points.clear()
                far_points.clear()

            elif len(polygons) > 0:  # otherwise, clear the polygons array
                polygons.pop()
        else:
            msg = 'no shapes to delete'

        if show_message:
            layer.status = msg
            print(msg)

    @annotation_layer.bind_key('d')
    def delete_the_last_point(layer):
        """
        Remove the last added point

        """
        if len(near_points) > 0 and len(far_points) > 0:
            near_points.pop()
            far_points.pop()
            if len(near_points) > 0:
                draw_polygon(layer, near_points.copy(), far_points.copy())
            else:
                delete_the_last_shape(layer, show_message=False)


def draw_polygon(layer, near_points: list, far_points: list, color: str = 'red', line_width=1):
    """
    Draw a polygon between provided near and far points.

    Parameters
    ----------
    layer : napari shapes layer
        napari shapes layer with annotations
    near_points : list
        List of polygon coordinates nearer to the viewer.
    far_points : list
        List of polygon coordinates further from the viewer.
    color : str, optional
        Color of the polygon
    line_width : scalar
        Point and line size for display.
        Default is 1.

    Returns
    -------
    Updated shapes layer
    """
    if len(near_points) < 2:  # if only one point, add a temporary point for display purposes
        near_points.append(np.array(near_points[0]) + line_width)
        far_points.append(np.array(far_points[0]) + line_width)

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
        edge_width=line_width,
        edge_color=color
    )
    return layer
