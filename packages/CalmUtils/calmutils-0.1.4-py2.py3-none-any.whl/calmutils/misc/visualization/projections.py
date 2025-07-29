import warnings
import numpy as np
from skimage.exposure import rescale_intensity
from skimage.transform import resize


def _get_projection_function(name):
    try:
        return {
            'max': np.max,
            'min': np.min,
            'mean': np.mean,
        }[name]
    except KeyError:
        warnings.warn(f'projection function \'{name}\' not available')
        raise


def get_orthogonal_projections_8bit(img, pixel_size=None, projection_type='max', intensity_range='auto', auto_range_quantiles = (0.02, 0.999)):

    # if no pixel size given, assume 1 (equal xyz)
    if pixel_size is None:
        pixel_size = np.ones(3)

    # parse projection function
    proj_fun = _get_projection_function(projection_type)

    # to relative pixel size
    rel_size = np.array(pixel_size, dtype=float)
    rel_size /= rel_size.min()

    # project
    proj_z = proj_fun(img, axis=0)
    proj_y = proj_fun(img, axis=1)
    proj_x = proj_fun(img, axis=2)

    # shape in smallest pixels (larger distance will be interpolated)
    scaled_shape = np.ceil(np.array(img.shape) * rel_size).astype(int)
    proj_z = resize(proj_z, scaled_shape[np.arange(3) != 0], clip=False, preserve_range=True)
    proj_y = resize(proj_y, scaled_shape[np.arange(3) != 1], clip=False, preserve_range=True)
    proj_x = resize(proj_x, scaled_shape[np.arange(3) != 2], clip=False, preserve_range=True)

    # rescale intensity based on projections
    # NOTE: all projections will be scaled the same, thus, e.g., x&y mean projections
    # might be darker than z (in a stack with z-slices << x/y extent)
    # TODO: maybe add option to scale individually?
    if intensity_range == 'auto':
        intensity_range = tuple(np.quantile(np.concatenate([proj_z.flat, proj_y.flat, proj_x.flat]), auto_range_quantiles))

    # normalize intensity
    proj_z = rescale_intensity(proj_z, in_range=intensity_range, out_range='uint8').astype(np.uint8)
    proj_y = rescale_intensity(proj_y, in_range=intensity_range, out_range='uint8').astype(np.uint8)
    proj_x = rescale_intensity(proj_x, in_range=intensity_range, out_range='uint8').astype(np.uint8)

    # allocate array of necessary output shape
    # (x+z, y+z) + 1 (extra row/col for lines between images)
    out_shape = (scaled_shape[1] + scaled_shape[0] + 1, scaled_shape[2] + scaled_shape[0] + 1)
    out_img = np.zeros(out_shape, dtype=np.uint8)

    # paste projections to out image
    out_img[:scaled_shape[1], :scaled_shape[2]] = proj_z
    out_img[scaled_shape[1]+1:, :scaled_shape[2]] = proj_y
    out_img[:scaled_shape[1], scaled_shape[2]+1:] = proj_x.T

    # white lines to separate prohections
    out_img[scaled_shape[1]+1] = 255
    out_img[:,scaled_shape[2]+1] = 255

    return out_img