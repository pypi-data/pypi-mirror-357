"""
Kinematics library.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Iterable, Union, overload

import numpy as np

class RotationSequence(Enum):
    """
    Rotation sequences.
    """

    BODY_XYX = 0  # Body x-y-x rotation (i.e., roll-pitch-roll or 1-2-1)
    BODY_XYZ = 1  # Body x-y-z rotation (i.e., roll-pitch-yaw or 1-2-3)
    BODY_XZX = 2  # Body x-z-x rotation (i.e., roll-yaw-roll or 1-3-1)
    BODY_XZY = 3  # Body x-z-y rotation (i.e., roll-yaw-pitch or 1-3-2)
    BODY_YXY = 4  # Body y-x-y rotation (i.e., pitch-roll-pitch or 2-1-2)
    BODY_YXZ = 5  # Body y-x-z rotation (i.e., pitch-roll-yaw or 2-1-3)
    BODY_YZX = 6  # Body y-z-x rotation (i.e., pitch-yaw-roll or 2-3-1)
    BODY_YZY = 7  # Body y-z-y rotation (i.e., pitch-yaw-pitch or 2-3-2)
    BODY_ZXY = 8  # Body z-x-y rotation (i.e., yaw-roll-pitch or 3-1-2)
    BODY_ZXZ = 9  # Body z-x-z rotation (i.e., yaw-roll-yaw or 3-1-3)
    BODY_ZYX = 10  # Body z-y-x rotation (i.e., yaw-pitch-roll or 3-2-1)
    BODY_ZYZ = 11  # Body z-y-z rotation (i.e., yaw-pitch-yaw or 3-2-3)

class KinematicVector:
    """A vector designed for kinematic applications. At the core, a kinematic vector is a vector of length 3 which
    has arbitrary x, y, and z components.
    """

    x: float
    y: float
    z: float

    @overload
    def __init__(self, xyz: Iterable[float], /) -> None:
        """Kinematic vector.

        Args:
            xyz: Components of kinematic vector as an iterable of length 3.
        """

    @overload
    def __init__(self, xyz: np.ndarray, /) -> None:
        """Kinematic vector.

        Args:
            xyz: Components of kinematic vector as a numpy array of length 3.
        """

    @overload
    def __init__(self, x: float, y: float, z: float, /) -> None:
        """Kinematic vector.

        Args:
            x: Component along x-axis
            y: Component along y-axis
            z: Component along z-axis
        """

    def angle_between(self, rhs: KinematicVector, /) -> float:
        """Calculates the angle between two kinematic vectors. For vectors with 0 magnitude, small magnitude is
        assigned instead. No protections for arccos ![-1, 1]

        Args:
            rhs: Kinematic vector

        Returns:
            angle: Angle between vectors [radians]
        """

    def azimuth_angle(self) -> float:
        """Calculates the azimuth angle (i.e., the angle between the x-axis and the xy projection of the kinematic
        vector). Note that convention implies a positive rotation about the z-axis, such that vectors with
        xy-projections in quadrant 1 and 2 (positive y-values) have positive azimuth angles, while vectors with
        xy-projections in quadrant 3 and 4  (negative y-values) have negative azimuth angles.

        Returns:
            azimuth: Azimuth angle in the interval [-pi, +pi] [radians]
        """

    def dot(self, rhs: KinematicVector, /) -> float:
        """Calculates the dot product of two kinematic vectors.

        Args:
            rhs: Kinematic vector

        Returns:
            dot: Result of dot product
        """

    def elevation_angle(self) -> float:
        """Calculates the elevation angle (i.e., the angle between the xy projection of the kinematic vector and the
        kinematic vector). Note that convention implies that vectors above the xy-plane (i.e., positive z-component)
        have negative elevation angles and vectors below the xy-plane (i.e., negative z-component) have positive
        elevation angles.

        Returns:
            elevation: Elevation angle in the interval [-pi/2, +pi/2] [radians]
        """

    def magnitude(self) -> float:
        """Calculates the magnitude of the kinematic vector.

        Returns:
            magnitude: Magnitude of the vector
        """

    def polar_angle(self) -> float:
        """Calculates the polar angle (i.e., angle between the z-axis and the kinematic vector). Note that convention
        implies that a vector aligned with the z-axis has a polar angle of 0.0 degrees, a vector in the xy-plane has a
        polar angle of 90.0 degrees, and a vector aligned with the negative z-axis has a polar angle of 180.0 degrees.

        Returns:
            polar: Polar angle in the interval [0, pi] [radians]
        """

    def unit(self) -> KinematicVector:
        """Calculates the unit vector pointing in the direction of the kinematic vector.

        Returns:
            vector: Unit vector corresponding to the kinematic vector
        """

    def zero(self) -> None:
        """Sets all vector components to zero."""

class Quaternion:
    """A quaternion contains a scalar and vector component to represent a rotation. This library uses
    the convention where a is the scalar component and b, c, and d are the vector component. The convention takes the
    form of a + bi + cj + dk, where a, b, c, and d are real numbers, and i, j, and k are basis elements.
    """

    @property
    def a(self) -> float:
        """scalar component."""

    @property
    def b(self) -> float:
        """Component corresponding to i basis element."""

    @property
    def c(self) -> float:
        """Component corresponding to j basis element."""

    @property
    def d(self) -> float:
        """Component corresponding to k basis element."""

    @overload
    def __init__(self) -> None:
        """Initializes an identity quaternion."""

    @overload
    def __init__(self, dcm: DCM) -> None:
        """Initializes a quaternion from a direction cosine matrix."""

    @overload
    def __init__(self, a1: float, a2: float, a3: float, seq: Union[int, RotationSequence], /) -> None:
        """Initializes a quaternion using the specified rotation sequence.

        Args:
            a1: First rotation angle [radians]
            a2: Second rotation angle [radians]
            a3: Third rotation angle [radians]
            seq: Rotation sequence
        """

    def angle(self) -> float:
        """Calculates the rotation angle associated with the quaternion.

        Returns:
            angle: Quaternion rotation angle [radians]
        """

    def axis(self) -> KinematicVector:
        """Calculates the rotation axis associated with the quaternion.

        Returns:
            vector: Quaternion rotation axis as a kinematic unit vector
        """

    def conjugate(self) -> Quaternion:
        """Calculates the conjugate the quaternion.

        Returns:
            quat: Conjugate of the quaternion
        """

    def inverse(self) -> Quaternion:
        """Calculates the inverse the quaternion.

        Returns:
            quat: Inverse of the quaternion
        """

    def norm(self) -> float:
        """Calculates the norm of the quaternion.

        Returns:
            norm: Quaternion norm
        """

    def rotate(self, kv: KinematicVector, /) -> KinematicVector:
        """Rotates a vector within a coordinate frame. This function performs an active vector rotation, such that the
        original vector is rotated within a single coordinate frame, according to the rotation specified by the
        quaternion.

        Args:
            kv: Vector to rotate

        Returns:
            kv_rotated: Rotated vector in the same coordinate frame as the original vector
        """

    def square(self) -> float:
        """Calculates the squared norm of the quaternion.

        Returns:
            square: Quaternion norm squared
        """

    def transform(self, kv: KinematicVector, /) -> KinematicVector:
        """Performs a coordinate transformation to a vector. This function performs a passive vector rotation, such that
        the original vector is represented in a new coordinate frame, according to the rotation specified by the
        quaternion.

        Args:
            kv: Vector to perform coordinate transformation

        Returns:
            kv_transformed: Vector representation in new coordinate frame
        """

class DCM:
    """Direction cosine matrix (DCM). A direction cosine matrix is a 3 x 3 matrix for coordinate frame transforms
    and vector rotations in kinematic applications. This library uses the a standard right-handed convention with
    pre-multiplication of kinematic vectors (i.e., DCM * v) for coordinate frame transformations and post-multiplication
    (i.e., v * DCM) for vector rotations.
    """

    @property
    def e00(self) -> float:
        """DCM component 00 (row 0, column 0)."""

    @property
    def e01(self) -> float:
        """DCM component 01 (row 0, column 1)."""

    @property
    def e02(self) -> float:
        """DCM component 02 (row 0, column 2)."""

    @property
    def e10(self) -> float:
        """DCM component 10 (row 1, column 0)."""

    @property
    def e11(self) -> float:
        """DCM component 11 (row 1, column 1)."""

    @property
    def e12(self) -> float:
        """DCM component 12 (row 1, column 2)."""

    @property
    def e20(self) -> float:
        """DCM component 20 (row 2, column 0)."""

    @property
    def e21(self) -> float:
        """DCM component 21 (row 2, column 1)."""

    @property
    def e22(self) -> float:
        """DCM component 22 (row 2, column 2)."""

    @overload
    def __init__(self) -> None:
        """Initializes a direction cosine matrix as an identity matrix."""

    @overload
    def __init__(self, quat: Quaternion, /) -> None:
        """Initializes a direction cosine matrix from a quaternion."""

    @overload
    def __init__(self, a1: float, a2: float, a3: float, seq: Union[int, RotationSequence], /) -> None:
        """Initializes a direction cosine matrix using the specified rotation sequence.

        Args:
            a1: First rotation angle [radians]
            a2: Second rotation angle [radians]
            a3: Third rotation angle [radians]
            seq: Rotation sequence
        """

    def rotate(self, kv: KinematicVector, /) -> KinematicVector:
        """Rotates a vector within a coordinate frame. This function performs an active vector rotation, such that the
        original vector is rotated within a single coordinate frame, according to the rotation specified by the
        direction cosine matrix.

        Args:
            kv: Vector to rotate

        Returns:
            kv_roated: Rotated vector in the same coordinate frame as the original vector
        """

    def transform(self, kv: KinematicVector, /) -> KinematicVector:
        """Performs a coordinate transformation to a vector. This function performs a passive vector rotation, such that
        the original vector is represented in a new coordinate frame, according to the rotation specified by the
        direction cosine matrix.

        Args:
            kv: Vector to perform coordinate transformation

        Returns:
            kv_transformed: Vector representation in new coordinate frame
        """

    def transpose(self) -> DCM:
        """Calculates the transpose the direction cosine matrix. This is equivalent to taking the inverse.

        Returns:
            dcm: Transpose of the direction cosine matrix
        """

@overload
def vincenty_direct(
    lat_deg: float, lon_deg: float, range_m: float, bearing_deg: float, abs_tol: float, /
) -> tuple[float, float]:
    """Calculates the latitiude and longitude point B that is a fixed range and bearing from a another latitiude and
    longitude point A. This function uses an iterative solution to determine outputs using the WGS84 ellipsoidal Earth
    model. See reference: https://en.wikipedia.org/wiki/Vincenty%27s_formulae.

    Args:
        lat_deg: Latitude point A [degrees].
        lon_deg: Longitude point A [degrees].
        range_m: Range (i.e., distance) from point A to point B [meters].
        bearing_deg: Bearing (i.e., azimuth) from point A to point B relative to true north [degrees].
        abs_tol: Absolute tolerance used for convergence.

    Returns:
        lat_lon_deg: Latitude and longitude point B [degrees].
    """

@overload
def vincenty_direct(
    lat_deg: np.ndarray,
    lon_deg: np.ndarray,
    range_m: np.ndarray,
    bearing_deg: np.ndarray,
    abs_tol: float,
    /,
) -> np.ndarray:
    """Calculates the latitiude and longitude point B that is a fixed range and bearing from a another latitiude and
    longitude point A. This function uses an iterative solution to determine outputs using the WGS84 ellipsoidal Earth
    model. See reference: https://en.wikipedia.org/wiki/Vincenty%27s_formulae.

    Args:
        lat_deg: Latitude point A [degrees]. Shape (n,).
        lon_deg: Longitude point A [degrees]. Shape (n,).
        range_m: Range (i.e., distance) from point A to point B [meters]. Shape (n,).
        bearing_deg: Bearing (i.e., azimuth) from point A to point B relative to true north [degrees]. Shape (n,).
        abs_tol: Absolute tolerance used for convergence

    Returns:
        lat_lon_deg: Latitude and longitude point B [degrees]. Shape (n, 2).
    """

@overload
def vincenty_direct(
    lat_deg: Iterable[float],
    lon_deg: Iterable[float],
    range_m: Iterable[float],
    bearing_deg: Iterable[float],
    abs_tol: float,
    /,
) -> list[tuple[float, float]]:
    """Calculates the latitiude and longitude point B that is a fixed range and bearing from a another latitiude and
    longitude point A. This function uses an iterative solution to determine outputs using the WGS84 ellipsoidal Earth
    model. See reference: https://en.wikipedia.org/wiki/Vincenty%27s_formulae.

    Args:
        lat_deg: Latitude point A [degrees]. Length n.
        lon_deg: Longitude point A [degrees]. Length n.
        range_m: Range (i.e., distance) from point A to point B [meters]. Length n.
        bearing_deg: Bearing (i.e., azimuth) from point A to point B relative to true north [degrees]. Length n.
        abs_tol: Absolute tolerance used for convergence.

    Returns:
        lat_lon_deg: Latitude and longitude point B [degrees]. Length n.
    """

@overload
def vincenty_inverse(
    lat_a_deg: float, lon_a_deg: float, lat_b_deg: float, lon_b_deg: float, abs_tol: float, /
) -> tuple[float, float, float]:
    """Calculates range and bearings between two latitude-longitude points. This function uses an iterative solution to
    determine outputs using the WGS84 ellipsoidal Earth model. See reference:
    https://en.wikipedia.org/wiki/Vincenty%27s_formulae.

    Args:
        lat_a_deg: Latitude point A [degrees]. Shape (n,).
        lon_a_deg: Longitude point A [degrees].
        lat_b_deg: Latitude point A [degrees].
        lon_b_deg: Longitude point A [degrees].
        abs_tol: Absolute tolerance used for convergence.

    Returns:
        range_bearing_bearing: Range, bearing AB, and bearing BA [meters, degrees, degrees].
    """

@overload
def vincenty_inverse(
    lat_a_deg: np.ndarray, lon_a_deg: np.ndarray, lat_b_deg: np.ndarray, lon_b_deg: np.ndarray, abs_tol: float, /
) -> np.ndarray:
    """Calculates range and bearings between two latitude-longitude points. This function uses an iterative solution to
    determine outputs using the WGS84 ellipsoidal Earth model. See reference:
    https://en.wikipedia.org/wiki/Vincenty%27s_formulae.

    Args:
        lat_a_deg: Latitude point A [degrees]. Shape (n,).
        lon_a_deg: Longitude point A [degrees]. Shape (n,).
        lat_b_deg: Latitude point A [degrees]. Shape (n,).
        lon_b_deg: Longitude point A [degrees]. Shape (n,).
        abs_tol: Absolute tolerance used for convergence.

    Returns:
        range_bearing_bearing: Range, bearing AB, and bearing BA [meters, degrees, degrees]. Shape (n, 3).
    """

@overload
def vincenty_inverse(
    lat_a_deg: Iterable[float],
    lon_a_deg: Iterable[float],
    lat_b_deg: Iterable[float],
    lon_b_deg: Iterable[float],
    abs_tol: float,
    /,
) -> list[tuple[float, float, float]]:
    """Calculates range and bearings between two latitude-longitude points. This function uses an iterative solution to
    determine outputs using the WGS84 ellipsoidal Earth model. See reference:
    https://en.wikipedia.org/wiki/Vincenty%27s_formulae.

    Args:
        lat_a_deg: Latitude point A [degrees]. Length n.
        lon_a_deg: Longitude point A [degrees]. Length n.
        lat_b_deg: Latitude point A [degrees]. Length n.
        lon_b_deg: Longitude point A [degrees]. Length n.
        abs_tol: Absolute tolerance used for convergence..

    Returns:
        range_bearing_bearing: Range, bearing AB, and bearing BA [meters, degrees, degrees]. Length n.
    """

def add_docstring(  # pylint: disable=missing-function-docstring
    obj: Callable[..., Any], docstring: str, /  # pylint: disable=unused-argument
) -> None: ...
