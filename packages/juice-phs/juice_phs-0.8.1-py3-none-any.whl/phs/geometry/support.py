import spiceypy as spice
import numpy as np
import logging
from astroquery.simbad import Simbad
from PyAstronomy import pyasl

def fov_expanded_boundaries(fov, maxlen=40000, mid_points=1):

    fov_shape, fov_frame, fov_bsight, fov_n, fov_bounds = spice.getfvn(fov, maxlen, maxlen, maxlen)
    if fov_n < 2:
        logging.error('FOV Circular or Ellipsoidal, full target on FOV not modeled.')
        return None, None

    # calculate the FOV bound mid-points as well.
    expanded_fov_bounds = []

    for i in range(len(fov_bounds) - 1):
        current_vector = fov_bounds[i]
        next_vector = fov_bounds[i + 1]

        # Append the current vector to the expanded array
        expanded_fov_bounds.append(current_vector)

        for j in range(mid_points):
            # Calculate the middle vector
            middle_vector = (np.array(current_vector) + np.array(next_vector)) / (2+j)

            # Append the  jth-middle vector to the expanded array
            expanded_fov_bounds.append(middle_vector)

        # Append the last vector in the original array to the expanded array
        expanded_fov_bounds.append(fov_bounds[-1])

    # Convert the expanded array to a NumPy array
    expanded_fov_bounds = np.array(expanded_fov_bounds)

    return expanded_fov_bounds, fov_frame

def star2kpool(star, verbose=False):
    '''Obtain star coordinates and add them to the kernel pool.'''

    try:
        star_simbad = Simbad.query_object(star)
        # Convert coordinates from h:m:s to degrees
        ra, dec = pyasl.coordsSexaToDeg(f"{star_simbad['RA'][0]} {star_simbad['DEC'][0]}")
        if verbose:
            logging.info(f'Star {star} found in DB with RA {ra} deg, DEC {dec} deg')
        # Add star to kernel pool
        if len(star.split()) > 1:
            star = '-'.join(star.split())
        spice.pdpool(f"{star.upper()}_COORDS",  [ra, dec])
    except BaseException:
        logging.exception(f"Star {star} not found in Simbad.")
        raise

    return ra, dec
