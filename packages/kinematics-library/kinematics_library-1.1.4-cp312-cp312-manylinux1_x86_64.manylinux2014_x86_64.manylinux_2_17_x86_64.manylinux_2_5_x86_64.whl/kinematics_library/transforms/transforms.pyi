from typing import overload

import numpy as np
from kinematics_library import KinematicVector

@overload
def aer_to_ned(aer: KinematicVector, ned: KinematicVector = None, /) -> KinematicVector:
    """Converts Azimuth-Elevation-Range (AER) to North-East-Down (NED).

    Args:
        aer: Vector of AER coordinates [radians-radians-meters]
        ned: Optional vector to store NED coordinates [meters-meters-meters]

    Returns:
        ned: Vector of NED coordinates [meters-meters-meters]
    """

@overload
def aer_to_ned(aer: np.ndarray, ned: np.ndarray = None, /) -> np.ndarray:
    """Converts Azimuth-Elevation-Range (AER) to North-East-Down (NED).

    Args:
        aer: Array of shape (3,) or (n, 3) of AER coordinates [radians-radians-meters]
        ned: Optional array of shape (3,) or (n, 3) to store NED coordinates [meters-meters-meters]

    Returns:
        ned: Array of shape (3,) or (n, 3) of NED coordinates [meters-meters-meters]
    """

@overload
def ecef_to_lla(ecef: KinematicVector, lla: KinematicVector = None, /) -> KinematicVector:
    """Converts Earth-Centered-Earth-Fixed (ECEF) to Latitude-Longitude-Altitude (LLA). This function uses an elliptical
    earth model, where altitude corresponds to height above the ellipsoid.

    Args:
        ecef: Vector of ECEF coordinates [meters-meters-meters]
        lla: Optional vector to store LLA coordinates [radians-radians-meters]

    Returns:
        lla: Vector of LLA coordinates [radians-radians-meters]
    """

@overload
def ecef_to_lla(ecef: np.ndarray, lla: np.ndarray = None, /) -> np.ndarray:
    """Converts Earth-Centered-Earth-Fixed (ECEF) to Latitude-Longitude-Altitude (LLA). This function uses an elliptical
    earth model, where altitude corresponds to height above the ellipsoid.

    Args:
        ecef: Array of shape (3,) or (n, 3) of ECEF coordinates [radians-radians-meters]
        lla: Optional array of shape (3,) or (n, 3) to store LLA coordinates [radians-radians-meters]

    Returns:
        lla: Array of shape (3,) or (n, 3) of LLA coordinates [radians-radians-meters]
    """

@overload
def ecef_to_ned(ecef: KinematicVector, lla_ref: KinematicVector, ned: KinematicVector = None, /) -> KinematicVector:
    """Converts Earth-Centered-Earth-Fixed (ECEF) to North-East-Down (NED). This function uses an elliptical earth
    model, where altitude corresponds to height above the ellipsoid.

    Args:
        ecef: Vector of ECEF coordinates [meters-meters-meters]
        lla_ref: Vector of LLA reference coordinates [radians-radians-meters]
        ned: Optional vector to store NED coordinates [meters-meters-meters]

    Returns:
        ned: Vector of NED coordinates [meters-meters-meters]
    """

@overload
def ecef_to_ned(ecef: np.ndarray, lla_ref: np.ndarray, ned: np.ndarray = None, /) -> np.ndarray:
    """Converts Earth-Centered-Earth-Fixed (ECEF) to North-East-Down (NED). This function uses an elliptical earth
    model, where altitude corresponds to height above the ellipsoid.

    Args:
        ecef: Array of shape (3,) or (n, 3) of ECEF coordinates [meters-meters-meters]
        lla_ref: Array of shape (3,) or (n, 3) of LLA reference coordinates [radians-radians-meters]
        ned: Optional array of shape (3,) or (n, 3) to store NED coordinates [meters-meters-meters]

    Returns:
        ned: Array of shape (3,) or (n, 3) of NED coordinates [meters-meters-meters]
    """

@overload
def lla_to_ecef(lla: KinematicVector, ecef: KinematicVector = None, /) -> KinematicVector:
    """Converts Latitude-Longitude-Altitude (LLA) to Earth-Centered-Earth-Fixed (ECEF). This function uses an elliptical
    earth model, where altitude corresponds to height above the ellipsoid.

    Args:
        lla: Vector of LLA coordinates [radians-radians-meters]
        ecef: Optional vector to store ECEF coordinates [meters-meters-meters]

    Returns:
        ecef: Vector of ECEF coordinates [meters-meters-meters]
    """

@overload
def lla_to_ecef(lla: np.ndarray, ecef: np.ndarray = None, /) -> np.ndarray:
    """Converts Latitude-Longitude-Altitude (LLA) to Earth-Centered-Earth-Fixed (ECEF). This function uses an elliptical
    earth model, where altitude corresponds to height above the ellipsoid.

    Args:
        lla: Array of shape (3,) or (n, 3) of LLA coordinates [radians-radians-meters]
        ecef: Optional array of shape (3,) or (n, 3) to store ECEF coordinates [meters-meters-meters]

    Returns:
        ecef: Array of shape (3,) or (n, 3) of ECEF coordinates [meters-meters-meters]
    """

@overload
def lla_to_ned(lla: KinematicVector, lla_ref: KinematicVector, ned: KinematicVector = None, /) -> KinematicVector:
    """Converts Latitude-Longitude-Altitude (LLA) to North-East-Down (NED). This function uses an elliptical earth
    model, where altitude corresponds to height above the ellipsoid.

    Args:
        lla: Vector of LLA coordinates [radians-radians-meters]
        lla_ref: Vector of LLA reference coordinates [radians-radians-meters]
        ned: Optional vector to store NED coordinates [meters-meters-meters]

    Returns:
        ned: Vector of NED coordinates [meters-meters-meters]
    """

@overload
def lla_to_ned(lla: np.ndarray, lla_ref: np.ndarray, ned: np.ndarray = None, /) -> np.ndarray:
    """Converts Latitude-Longitude-Altitude (LLA) to North-East-Down (NED). This function uses an elliptical earth
    model, where altitude corresponds to height above the ellipsoid.

    Args:
        lla: Array of shape (3,) or (n, 3) of LLA coordinates [radians-radians-meters]
        lla_ref: Array of shape (3,) or (n, 3) of LLA reference coordinates [radians-radians-meters]
        ned: Optional array of shape (3,) or (n, 3) to store NED coordinates [meters-meters-meters]

    Returns:
        ned: Array of shape (3,) or (n, 3) of NED coordinates [meters-meters-meters]
    """

@overload
def ned_to_aer(ned: KinematicVector, aer: KinematicVector = None, /) -> KinematicVector:
    """Converts North-East-Down (NED) to Azimuth-Elevation-Range (AER).


    Args:
        ned: Vector of NED coordinates [meters-meters-meters]
        aer: Optional vector to store AER coordinates [radians-radians-meters]

    Returns:
        aer: Vector of AER coordinates [radians-radians-meters]
    """

@overload
def ned_to_aer(ned: np.ndarray, aer: np.ndarray = None, /) -> np.ndarray:
    """Converts North-East-Down (NED) to Azimuth-Elevation-Range (AER).

    Args:
        ned: Array of shape (3,) or (n, 3) of NED coordinates [meters-meters-meters]
        aer: Optional array of shape (3,) or (n, 3) to store AER coordinates [radians-radians-meters]

    Returns:
        aer: Array of shape (3,) or (n, 3) of NED coordinates [mradians-radians-meters]
    """

@overload
def ned_to_ecef(ned: KinematicVector, lla_ref: KinematicVector, ecef: KinematicVector = None, /) -> KinematicVector:
    """Converts North-East-Down (NED) to Earth-Centered-Earth-Fixed (ECEF). This function uses an elliptical earth
    model, where altitude corresponds to height above the ellipsoid.

    Args:
        ned: Vector of NED coordinates [meters-meters-meters]
        lla_ref: Vector of LLA reference coordinates [radians-radians-meters]
        ecef: Optional vector to store ECEF coordinates [meters-meters-meters]

    Returns:
        ecef: Vector of ECEF coordinates [meters-meters-meters]
    """

@overload
def ned_to_ecef(ned: np.ndarray, lla_ref: np.ndarray, ecef: np.ndarray = None, /) -> np.ndarray:
    """Converts North-East-Down (NED) to Earth-Centered-Earth-Fixed (ECEF). This function uses an elliptical earth
    model, where altitude corresponds to height above the ellipsoid.

    Args:
        ned: Array of shape (3,) or (n, 3) of NED coordinates [meters-meters-meters]
        lla_ref: Array of shape (3,) or (n, 3) of LLA reference coordinates [radians-radians-meters]
        ecef: Optional array of shape (3,) or (n, 3) to store ECEF coordinates [meters-meters-meters]

    Returns:
        ecef: Array of shape (3,) or (n, 3) of ECEF coordinates [meters-meters-meters]
    """

@overload
def ned_to_lla(ned: KinematicVector, lla_ref: KinematicVector, lla: KinematicVector = None, /) -> KinematicVector:
    """Converts North-East-Down (NED) to Latitude-Longitude-Altitude (LLA). This function uses an elliptical earth
    model, where altitude corresponds to height above the ellipsoid.

    Args:
        ned: Vector of NED coordinates [meters-meters-meters]
        lla_ref: Vector of LLA reference coordinates [radians-radians-meters]
        lla: Optional vector to store LLA coordinates [radians-radians-meters]

    Returns:
       lla: Vector of LLA coordinates [radians-radians-meters]
    """

@overload
def ned_to_lla(ned: np.ndarray, lla_ref: np.ndarray, lla: np.ndarray = None, /) -> np.ndarray:
    """Converts North-East-Down (NED) to Latitude-Longitude-Altitude (LLA). This function uses an elliptical earth
    model, where altitude corresponds to height above the ellipsoid.

    Args:
        ned: Array of shape (3,) or (n, 3) of NED coordinates [meters-meters-meters]
        lla_ref: Array of shape (3,) or (n, 3) of LLA reference coordinates [radians-radians-meters]
        lla: Optional array of shape (3,) or (n, 3) to store LLA coordinates [radians-radians-meters]

    Returns:
        lla: Array of shape (3,) or (n, 3) of LLA coordinates [radians-radians-meters]
    """
