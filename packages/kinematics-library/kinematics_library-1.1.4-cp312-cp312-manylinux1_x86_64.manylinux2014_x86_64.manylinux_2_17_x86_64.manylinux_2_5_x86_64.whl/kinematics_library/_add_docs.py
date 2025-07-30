from ._helpers import add_newdoc

add_newdoc(
    "kinematics_library",
    "DCM",
    """
    DCM(a1=0.0, a2=0.0, a3=0.0, seq=0)

    A direction cosine matrix (DCM) is a 3 x 3 matrix for coordinate frame transforms
    and vector rotations in kinematic applications. This library uses the a standard right-handed convention with
    pre-multiplication of kinematic vectors (i.e., DCM * v) for coordinate frame transformations and post-multiplication
    (i.e., v * DCM) for vector rotations.

    Parameters
    ----------

    a1 : float, optional
         First rotation angle [radians].
    a2 : float, optional
         Second rotation angle [radians].
    a3 : float, optional
         Third rotation angle [radians].
    seq : int, :class:`RotationSequence`
          Rotation sequence.

    Attributes
    ----------

    e00 : float, optional
          DCM component 00 (row 0, column 0).
    e01 : float, optional
          DCM component 01 (row 0, column 1).
    e02 : float, optional
          DCM component 02 (row 0, column 2).
    e10 : float, optional
          DCM component 10 (row 1, column 0).
    e11 : float, optional
          DCM component 11 (row 1, column 1).
    e12 : float, optional
          DCM component 12 (row 1, column 2).
    e20 : float, optional
          DCM component 20 (row 2, column 0).
    e21 : float, optional
          DCM component 21 (row 2, column 1).
    e22 : float, optional
          DCM component 22 (row 2, column 2).
    """,
)

add_newdoc("kinematics_library", "DCM", ("e00", """DCM component 00 (row 0, column 0)"""))

add_newdoc("kinematics_library", "DCM", ("e01", """DCM component 01 (row 0, column 1)"""))

add_newdoc("kinematics_library", "DCM", ("e02", """DCM component 02 (row 0, column 2)"""))

add_newdoc("kinematics_library", "DCM", ("e10", """DCM component 10 (row 1, column 0)"""))

add_newdoc("kinematics_library", "DCM", ("e11", """DCM component 11 (row 1, column 1)"""))

add_newdoc("kinematics_library", "DCM", ("e12", """DCM component 12 (row 1, column 2)"""))

add_newdoc("kinematics_library", "DCM", ("e20", """DCM component 20 (row 2, column 0)"""))

add_newdoc("kinematics_library", "DCM", ("e21", """DCM component 21 (row 2, column 1)"""))

add_newdoc("kinematics_library", "DCM", ("e22", """DCM component 22 (row 2, column 2)"""))

add_newdoc(
    "kinematics_library",
    "DCM",
    (
        "rotate",
        """
    rotate(kv)

    Rotates a vector within a coordinate frame. This function performs an active vector rotation, such that the
    original vector is rotated within a single coordinate frame, according to the rotation specified by the
    direction cosine matrix.

    Parameters
    ----------

    kv : :class:`KinematicVector`
         Kinematic vector.

    Returns
    -------
    y : :class:`KinematicVector`
        Rotated vector in the same coordinate frame as the original vector.

    """,
    ),
)

add_newdoc(
    "kinematics_library",
    "DCM",
    (
        "transform",
        """
    transform(kv)

    Performs a coordinate transformation to a vector. This function performs a passive vector rotation, such that
    the original vector is represented in a new coordinate frame, according to the rotation specified by the
    direction cosine matrix.

    Parameters
    ----------

    kv : :class:`KinematicVector`
         Kinematic vector.

    Returns
    -------
    y : :class:`KinematicVector`
        Vector representation in new coordinate frame.

    """,
    ),
)

add_newdoc(
    "kinematics_library",
    "DCM",
    (
        "transpose",
        """
    transpose()

    Calculates the transpose the direction cosine matrix. This is equivalent to taking the inverse.

    Returns
    -------
    y : :class:`DCM`
        Transpose of the direction cosine matrix.

    """,
    ),
)

add_newdoc(
    "kinematics_library",
    "KinematicVector",
    """
    KinematicVector(x=0.0, y=0.0, z=0.0)

    A vector designed for kinematic applications. At the core, a kinematic vector is a vector of length 3 which
    has arbitrary x, y, and z components.

    Parameters
    ----------

    x : float, optional
        X component of the kinematic vector.
    y : float, optional
        y component of the kinematic vector.
    z : float, optional
        z component of the kinematic vector.

    Attributes
    ----------

    x : float, optional
        X component of the kinematic vector.
    y : float, optional
        y component of the kinematic vector.
    z : float, optional
        z component of the kinematic vector.
    """,
)

add_newdoc("kinematics_library", "KinematicVector", ("x", """X component of the kinematic vector"""))

add_newdoc("kinematics_library", "KinematicVector", ("y", """Y component of the kinematic vector"""))

add_newdoc("kinematics_library", "KinematicVector", ("z", """Z component of the kinematic vector"""))

add_newdoc(
    "kinematics_library",
    "KinematicVector",
    (
        "angle_between",
        """
    angle_between(rhs)

    Calculates the angle between two kinematic vectors. For vectors with 0 magnitude, small magnitude is
    assigned instead. No protections for arccos ![-1, 1]

    Parameters
    ----------

    rhs : kinematics_library.KinematicVector
          Kinematic vector.

    Returns
    -------
    y : float
        The angle betwen the two vectors in radians.

    """,
    ),
)

add_newdoc(
    "kinematics_library",
    "KinematicVector",
    (
        "azimuth_angle",
        """
    azimuth_angle()

    Calculates the azimuth angle (i.e., the angle between the x-axis and the xy projection of the kinematic
    vector). Note that convention implies a positive rotation about the z-axis, such that vectors with
    xy-projections in quadrant 1 and 2 (positive y-values) have positive azimuth angles, while vectors with
    xy-projections in quadrant 3 and 4  (negative y-values) have negative azimuth angles.

    Parameters
    ----------

    None

    Returns
    -------
    y : float
        Azimuth angle in the interval [-pi, +pi] [radians]

    """,
    ),
)

add_newdoc(
    "kinematics_library",
    "KinematicVector",
    (
        "cross",
        """
    cross(rhs)

    Calculates the cross product of two kinematic vectors.

    Parameters
    ----------

    rhs : kinematics_library.KinematicVector
          Kinematic vector.

    Returns
    -------
    vector : KinematicVector
             Result of cross product

    """,
    ),
)

add_newdoc(
    "kinematics_library",
    "KinematicVector",
    (
        "dot",
        """
    dot(rhs)

    Calculates the dot product of two kinematic vectors.

    Parameters
    ----------

    rhs : kinematics_library.KinematicVector
          Kinematic vector.

    Returns
    -------
    y : float
        Result of dot product

    """,
    ),
)

add_newdoc(
    "kinematics_library",
    "KinematicVector",
    (
        "elevation_angle",
        """
    elevation_angle()

    Calculates the elevation angle (i.e., the angle between the xy projection of the kinematic vector and the
    kinematic vector). Note that convention implies that vectors above the xy-plane (i.e., positive z-component)
    have negative elevation angles and vectors below the xy-plane (i.e., negative z-component) have positive
    elevation angles.

    Parameters
    ----------

    None

    Returns
    -------
    y : float
        Elevation angle in the interval [-pi/2, +pi/2] [radians]

    """,
    ),
)

add_newdoc(
    "kinematics_library",
    "KinematicVector",
    (
        "magnitude",
        """
    magnitude()

    Calculates the magnitude of the kinematic vector.

    Parameters
    ----------

    None

    Returns
    -------
    y : float
        Magnitude of the vector

    """,
    ),
)

add_newdoc(
    "kinematics_library",
    "KinematicVector",
    (
        "polar_angle",
        """
    polar_angle()

    Calculates the polar angle (i.e., angle between the z-axis and the kinematic vector). Note that convention
    implies that a vector aligned with the z-axis has a polar angle of 0.0 degrees, a vector in the xy-plane has a
    polar angle of 90.0 degrees, and a vector aligned with the negative z-axis has a polar angle of 180.0 degrees.

    Parameters
    ----------

    None

    Returns
    -------
    y : float
        Polar angle in the interval [0, pi] [radians]

    """,
    ),
)

add_newdoc(
    "kinematics_library",
    "KinematicVector",
    (
        "unit",
        """
    unit()

    Calculates the unit vector pointing in the direction of the kinematic vector.

    Parameters
    ----------

    None

    Returns
    -------
    vector : KinematicVector
             Unit vector corresponding to the kinematic vector

    """,
    ),
)

add_newdoc(
    "kinematics_library",
    "KinematicVector",
    (
        "zero",
        """
    zero()

    Sets all vector components to zero.

    """,
    ),
)

add_newdoc(
    "kinematics_library",
    "Quaternion",
    """
    Quaternion(a1=0.0, a2=0.0, a3=0.0, seq=0)

    A quaternion contains a scalar and vector component to represent a rotation. This library uses
    the convention where a is the scalar component and b, c, and d are the vector component. The convention takes the
    form of a + bi + cj + dk, where a, b, c, and d are real numbers, and i, j, and k are basis elements.

    Parameters
    ----------

    a1 : float, optional
         First rotation angle [radians].
    a2 : float, optional
         Second rotation angle [radians].
    a3 : float, optional
         Third rotation angle [radians].
    seq : int, :class:`RotationSequence`
          Rotation sequence.

    Attributes
    ----------

    a : float, optional
        Scalar component.
    b : float, optional
        Component corresponding to i basis element.
    c : float, optional
        Component corresponding to j basis element.
    d : float, optional
        Component corresponding to k basis element.
    """,
)

add_newdoc("kinematics_library", "Quaternion", ("a", """Scalar component"""))

add_newdoc("kinematics_library", "Quaternion", ("b", """Component corresponding to i basis element"""))

add_newdoc("kinematics_library", "Quaternion", ("c", """Component corresponding to j basis element"""))

add_newdoc("kinematics_library", "Quaternion", ("d", """Component corresponding to k basis element"""))

add_newdoc(
    "kinematics_library",
    "Quaternion",
    (
        "angle",
        """
    angle()

    Calculates the rotation angle associated with the quaternion.

    Returns
    -------
    angle : float
            Quaternion rotation angle [radians]

    """,
    ),
)

add_newdoc(
    "kinematics_library.transforms",
    "aer_to_ned",
    """
    aer_to_ned(aer, ned=None)

    Converts Azimuth-Elevation-Range (AER) to North-East-Down (NED).

    Parameters
    ----------

    aer : :class:`KinematicVector`, array_like
        Input AER kinematic vector or array. If using an array, it have the shape (3,) or (n, 3).
    ned : :class:`KinematicVector`, array_like, optional
        An optional output kinematic vector or array that matches the shape of `aer`.
    """,
)

add_newdoc(
    "kinematics_library.transforms",
    "ecef_to_lla",
    """
    ecef_to_lla(ecef, lla=None)

    Converts Earth-Centered-Earth-Fixed (ECEF) to Latitude-Longitude-Altitude (LLA). This function uses an elliptical
    earth model, where altitude corresponds to height above the ellipsoid.

    Parameters
    ----------

    ecef : :class:`KinematicVector`, array_like
        Input ECEF kinematic vector or array. If using an array, it have the shape (3,) or (n, 3).
    lla : :class:`KinematicVector`, array_like, optional
        An optional output kinematic vector or array that matches the shape of `ecef`.
    """,
)

add_newdoc(
    "kinematics_library.transforms",
    "ecef_to_ned",
    """
    ecef_to_ned(ecef, lla_ref, ned=None)

    Converts Earth-Centered-Earth-Fixed (ECEF) to North-East-Down (NED). This function uses an elliptical earth
    model, where altitude corresponds to height above the ellipsoid.

    Parameters
    ----------

    ecef : :class:`KinematicVector`, array_like
        Input ECEF kinematic vector or array. If using an array, it have the shape (3,) or (n, 3).
    lla_ref : :class:`KinematicVector`, array_like
        Input LLA reference kinematic vector or array. If using an array, it have the shape (3,) or (n, 3).
    lla : :class:`KinematicVector`, array_like, optional
        An optional output kinematic vector or array that matches the shape of `ecef`.
    """,
)

add_newdoc(
    "kinematics_library.transforms",
    "lla_to_ecef",
    """
    lla_to_ecef(lla, ecef=None)

    Converts Latitude-Longitude-Altitude (LLA) to Earth-Centered-Earth-Fixed (ECEF). This function uses an elliptical
    earth model, where altitude corresponds to height above the ellipsoid.

    Parameters
    ----------

    lla : :class:`KinematicVector`, array_like
        Input LLA kinematic vector or array. If using an array, it have the shape (3,) or (n, 3).
    ecef : :class:`KinematicVector`, array_like, optional
        An optional output kinematic vector or array that matches the shape of `lla`.
    """,
)

add_newdoc(
    "kinematics_library.transforms",
    "lla_to_ned",
    """
    lla_to_ned(lla, lla_ref, ned=None)

    Converts Latitude-Longitude-Altitude (LLA) to North-East-Down (NED). This function uses an elliptical earth
    model, where altitude corresponds to height above the ellipsoid.

    Parameters
    ----------

    lla : :class:`KinematicVector`, array_like
        Input LLA kinematic vector or array. If using an array, it have the shape (3,) or (n, 3).
    lla_ref : :class:`KinematicVector`, array_like
        Input LLA reference kinematic vector or array. If using an array, it have the shape (3,) or (n, 3).
    ned : :class:`KinematicVector`, array_like, optional
        An optional output kinematic vector or array that matches the shape of `lla`.
    """,
)

add_newdoc(
    "kinematics_library.transforms",
    "ned_to_aer",
    """
    ned_to_aer(ned, aer=None)

    Converts North-East-Down (NED) to Azimuth-Elevation-Range (AER).

    Parameters
    ----------

    ned : :class:`KinematicVector`, array_like
        Input NED kinematic vector or array. If using an array, it have the shape (3,) or (n, 3).
    aer : :class:`KinematicVector`, array_like, optional
        An optional output kinematic vector or array that matches the shape of `ned`.
    """,
)

add_newdoc(
    "kinematics_library.transforms",
    "ned_to_ecef",
    """
    ned_to_ecef(ned, lla_ref, ecef=None)

    Converts North-East-Down (NED) to Earth-Centered-Earth-Fixed (ECEF). This function uses an elliptical earth
    model, where altitude corresponds to height above the ellipsoid.

    Parameters
    ----------

    ned : :class:`KinematicVector`, array_like
        Input NED kinematic vector or array. If using an array, it have the shape (3,) or (n, 3).
    lla_ref : :class:`KinematicVector`, array_like
        Input LLA reference kinematic vector or array. If using an array, it have the shape (3,) or (n, 3).
    ecef : :class:`KinematicVector`, array_like, optional
        An optional output kinematic vector or array that matches the shape of `ned`.
    """,
)

add_newdoc(
    "kinematics_library.transforms",
    "ned_to_lla",
    """
    ned_to_lla(ned, lla_ref, lla=None)

    Converts North-East-Down (NED) to Latitude-Longitude-Altitude (LLA). This function uses an elliptical earth
    model, where altitude corresponds to height above the ellipsoid.

    Parameters
    ----------

    ned : :class:`KinematicVector`, array_like
        Input NED kinematic vector or array. If using an array, it have the shape (3,) or (n, 3).
    lla_ref : :class:`KinematicVector`, array_like
        Input LLA reference kinematic vector or array. If using an array, it have the shape (3,) or (n, 3).
    lla : :class:`KinematicVector`, array_like, optional
        An optional output kinematic vector or array that matches the shape of `ned`.
    """,
)

add_newdoc(
    "kinematics_library",
    "vincenty_direct",
    """
    vincenty_direct(lat_deg, lon_deg, range_m, bearing_deg, abs_tol)

    Calculates the latitiude and longitude point B that is a fixed range and bearing from a another latitiude and
    longitude point A. This function uses an iterative solution to determine outputs using the WGS84 ellipsoidal Earth
    model. See reference: https://en.wikipedia.org/wiki/Vincenty%27s_formulae.

    .. versionadded:: 1.1.0

    Parameters
    ----------
    lat_deg : float, array_like
        Latitude point A [degrees].
    lon_deg : float, array_like
        Longitude point A [degrees].
    range_m : float, array_like
        Range (i.e., distance) from point A to point B [meters].
    bearing_deg : float, array_like
        Bearing (i.e., azimuth) from point A to point B relative to true north [degrees].
    abs_tol : float, array_like
        Absolute tolerance used for convergence.

    Returns
    -------
    lat_lon_deg : float, array_like
        Latitude point B [degrees].
        Longitude point B [degrees].

    Examples
    --------
    >>> from kinematics_library import vincenty_direct
    >>> lat_deg, lon_deg, range_m, bearing_deg, abs_tol = 45., 120., 50000., 30., 1.0e-13
    >>> vincenty_direct(lat_deg, lon_deg, range_m, bearing_deg, abs_tol)
    (45.38918149119183, 120.31923736117137)

    >>> import numpy as np
    >>> lat_deg = np.array((45., 15., -8.))              # Any iterable of floats
    >>> lon_deg = np.array((120., 175., -42.))           # Any iterable of floats
    >>> range_m = np.array((50000., 120000., 10000000.)) # Any iterable of floats
    >>> bearing_deg = np.array((30., -135., 60.))        # Any iterable of floats
    >>> vincenty_direct(lat_deg, lon_deg, range_m, bearing_deg, abs_tol)
    array([[ 45.38918149, 120.31923736],
           [ 14.23176866, 174.21380049],
           [ 29.78058582,  43.28342045]])
    """,
)

add_newdoc(
    "kinematics_library",
    "vincenty_inverse",
    """
    vincenty_inverse(lat_a_deg, lon_a_deg, lat_b_deg, lon_b_deg, abs_tol)

    Calculates range and bearings between two latitude-longitude points. This function uses an iterative solution to
    determine outputs using the WGS84 ellipsoidal Earth model. See reference:
    https://en.wikipedia.org/wiki/Vincenty%27s_formulae.

    .. versionadded:: 1.1.0

    Parameters
    ----------
    lat_a_deg : float, array_like
        Latitude point A [degrees].
    lon_a_deg : float, array_like
        Longitude point A [degrees].
    lat_b_deg : float, array_like
        Latitude point B [degrees].
    lon_b_deg : float, array_like
        Longitude point B [degrees].
    abs_tol : float, array_like
        Absolute tolerance used for convergence.

    Returns
    -------
    range_bearing_bearing : float, array_like
        Range (i.e., distance) from point A to point B [meters].
        Bearing (i.e., azimuth) from point A to point B relative to true north [degrees].
        Bearing (i.e., azimuth) from point B to point A relative to true north [degrees].

    Examples
    --------
    >>> from kinematics_library import vincenty_inverse
    >>> lat_a_deg, lon_a_deg, lat_b_deg, lon_b_deg, abs_tol = -60.0, 24.0, -64.0, 26.0, 1.0e-13
    >>> vincenty_inverse(lat_a_deg, lon_a_deg, lat_b_deg, lon_b_deg, abs_tol)
    (457876.0925901428, 167.6505768264915, -14.11643524048833)

    >>> import numpy as np
    >>> lat_a_deg = np.array((-60., 15., -8.))   # Any iterable of floats
    >>> lon_a_deg = np.array((24., 175., -42.))  # Any iterable of floats
    >>> lat_b_deg = np.array((-64., 19., 80.))   # Any iterable of floats
    >>> lon_b_deg = np.array((26., -120., -15.)) # Any iterable of floats
    >>> vincenty_inverse(lat_a_deg, lon_a_deg, lat_b_deg, lon_b_deg, abs_tol)
    [[ 4.57876093e+05  1.67650577e+02 -1.41164352e+01]
     [ 6.89802568e+06  7.61791807e+01 -8.26917782e+01]
     [ 9.88987580e+06  4.54067012e+00 -1.53254562e+02]]
    """,
)
