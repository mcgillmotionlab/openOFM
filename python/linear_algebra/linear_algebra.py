import numpy as np


def static2dynamic(o_dyn, x_dyn, y_dyn, z_dyn, mrk_lcl_av):
    """
    Creates virtual dynamic version of static marker in global coordinate system of dynamic trial.

    Arguments:
    o_dyn: numpy array of shape (n, 3) representing the origin of the LCS of dynamic trial.
    x_dyn: numpy array of shape (n, 3) representing the anterior axis of the LCS of dynamic trial.
    y_dyn: numpy array of shape (n, 3) representing the lateral axis of the LCS of dynamic trial.
    z_dyn: numpy array of shape (n, 3) representing the proximal axis of the LCS of dynamic trial.
    mrk_lcl_av: numpy array of shape (n, 3) representing the virtual markers in LCS of static trial.

    Returns:
    - mrk_dyn: numpy array of shape (n, 3) representing the dynamic version of the static marker.
    """
    mrk_dyn = np.zeros_like(o_dyn)
    for i in range(len(mrk_dyn)):
        # create LCS for dynamic trial at each frame
        x_prime = makeunit(x_dyn[i, :] - o_dyn[i, :])
        y_prime = makeunit(y_dyn[i, :] - o_dyn[i, :])
        z_prime = makeunit(z_dyn[i, :] - o_dyn[i, :])
        lcs_prime = np.vstack([x_prime, y_prime, z_prime])

        # transform marker from lcs_prime to gcs
        mrk_lcl_prime = ctransform(lcs_prime, gunit(), mrk_lcl_av)

        # translate marker position from 0 to origin of LCS dynamic
        mrk_dyn[i, :] = mrk_lcl_prime + np.expand_dims(o_dyn[i, :], axis=0)

    return mrk_dyn

def create_lcs(O, vec1, vec2, order):
    """
     creates a local coordinate system.
     ARGUMENTS
       O            ...  n x 3 array: origin of the local coordinate system
       vec1         ...  n x 3 array: vector representing the first axis
       vec2         ...  n x 3 array: second vector used to create the axes

     RETURNS
       O            ...  n x 3 array: origin of the local coordinate system
       lcs1         ...  n x 3 array: marker on the first axis of the local
                         coordinate system
       lcs2         ...  n x 3 array: marker on the second axis of the local
                         coordinate system
       lcs3         ...  n x 3 array: marker on the third axis of the local
                         coordinate system
       axes_system  ...  axes system composed of the 3 axes created
    """

    # error check for n x 3 arrays
    if np.ndim(O) == 1:
        O = np.expand_dims(O, 1).T        # fix (3,) to (1,3)
    if np.ndim(vec1) == 1:
        vec1 = np.expand_dims(vec1, 1).T  # fix (3,) to (1,3)
    if np.ndim(vec2) == 1:
        vec2 = np.expand_dims(vec2, 1).T  # fix (3,) to (1,3)

    if order == 'xyz':
        axis1 = makeunit(vec1)
        axis2 = makeunit(np.cross(vec2, axis1))
        axis3 = makeunit(np.cross(axis1, axis2))
    elif order == 'xzy':
        axis1 = makeunit(vec1)
        axis3 = makeunit(np.cross(axis1, vec2))
        axis2 = makeunit(np.cross(axis3, axis1))
    elif order == 'zxy':
        axis3 = makeunit(vec1)  # z - anterior
        axis1 = makeunit(np.cross(vec2, axis3))  # x - proximal
        axis2 = makeunit(np.cross(axis3, axis1))  # y - medial for right
    elif order == 'zyx':
        axis3 = makeunit(vec1)  # z - anterior
        axis2 = makeunit(np.cross(vec2, axis3))  # y - medial for right
        axis1 = makeunit(np.cross(axis3, axis2))  # x - proximal
    elif order == 'yzx':
        axis2 = makeunit(vec1)  # y - up
        axis3 = makeunit(np.cross(axis2, vec2))  # y - medial for right
        axis1 = makeunit(np.cross(axis2, axis3))  # x - anterior
    elif order == 'yxz':
        axis2 = makeunit(vec1)  # y - up
        axis1 = makeunit(np.cross(vec2, axis2))  # x - forward
        axis3 = makeunit(np.cross(axis1, axis2))  # z - lateral for right
    else:
        raise ValueError("Invalid order. Must be 'xyz', 'xzy', 'zxy', 'zyx', 'yzx', or 'yxz'.")

    lcs1 = O + axis1
    lcs2 = O + axis2
    lcs3 = O + axis3
    axes_system = np.vstack((axis1, axis2, axis3))

    return O, lcs1, lcs2, lcs3, axes_system


def angle(m1, m2, ref='deg'):
    """
    Calculates the smallest angle between two vectors, m1 and m2

    ARGUMENTS
      m1    ...      list, 1st n x 3 vector
      m2    ...      list, 2nd n x 3 vector

    RETURNS
      r    ...       list, default = ref, angle n x 3 vector

    """

    dotp = np.diag(np.matmul(m1, np.conj(m2).T))
    r = np.arcsin(dotp)

    # convert from rad to degree
    if ref == 'deg':
        r = np.rad2deg(r)

    return r


def makeunit(vec):
    """ create a unit vector for n x 3 matrix vec
    arguments:
       vec ... N by 3 matrix of vectors. rows are the number of vectors,
                  columns are XYZ
    return:
        unt   ... unit vector
    """

    # check input shape
    # todo : do we want this here?
    if np.ndim(vec) == 1:
        vec = np.expand_dims(vec, axis=0)

    mag = np.sqrt(np.diag(np.dot(vec, vec.T)))
    unt = np.divide(vec.T, mag).T
    return unt


def magnitude(r, axis=1):
    """ compute magnitude of a vector
     ARGUMENTS
       r        ...     n x 3 signal or  n x 1 signal
       axis     ...     int. axis along which to take magnitude. Default = 1 is for magnitude along
                        each row of an n x 3 signal
     RETURNS
       m        ...     np.array. n x 1 or 1. magnitude of the signal
    """
    return np.linalg.norm(r, axis=axis)


def gunit():
    """ Returns the 3x3 identity matrix """
    return np.identity(3)


def ctransform(c1, c2, vec):
    """
    coordinate system transformation of vector vec from coordinate system c1 to c2

    ARGUMENTS
      c1    ... initial coordinate system 3 by 3 matrix rows = i,j,k columns = X,Y,Z
      c2    ... final coordinate system 3 by 3 matrix rows = i,j,k columns = X,Y,Z
      vec   ... n x 3 matrix in c1 rows = samples; columns X Y Z

    RETURNS
      vout  ... n x 3 matrix in c2 rows = samples; columns X Y Z
    """

    # Use isinstance for more robust type checking (handles subclasses)
    if not (isinstance(c1, np.ndarray) and isinstance(c2, np.ndarray)):
        print(f'type of c1: {type(c1)}')
        print(f'type of c2: {type(c2)}')
        raise TypeError('inputs must be numpy arrays')

    t = np.matmul(c1, c2.T)

    # Apply the transformation.
    vec2 = np.matmul(vec, t)
    
    return vec2


def replace4(p1, p2, p3, p4):
    n = p1.shape[0]

    # Buffers for local coordinates (p1 in system 234, p2 in 341, p3 in 412, p4 in 123)
    p1_vec_lcl = np.zeros_like(p1)
    p2_vec_lcl = np.zeros_like(p2)
    p3_vec_lcl = np.zeros_like(p3)
    p4_vec_lcl = np.zeros_like(p4)

    # First pass: compute local coordinates for each point-system pair, one loop over frames
    for i in range(n):
        # system 234 (origin p3): axes built from vectors p2-p3 and p3-p4
        _, _, _, _, s234 = create_lcs(p3[i, :], p2[i, :] - p3[i, :], p3[i, :] - p4[i, :], 'xyz')
        p1_vec_lcl[i, :] = ctransform(gunit(), s234, np.expand_dims(p1[i, :] - p3[i, :], axis=0))[0]
        _, _, _, _, s341 = create_lcs(p4[i, :], p3[i, :] - p4[i, :], p4[i, :] - p1[i, :], 'xyz')
        p2_vec_lcl[i, :] = ctransform(gunit(), s341, np.expand_dims(p2[i, :] - p4[i, :], axis=0))[0]
        _, _, _, _, s412 = create_lcs(p1[i, :], p4[i, :] - p1[i, :], p1[i, :] - p2[i, :], 'xyz')
        p3_vec_lcl[i, :] = ctransform(gunit(), s412, np.expand_dims(p3[i, :] - p1[i, :], axis=0))[0]
        _, _, _, _, s123 = create_lcs(p2[i, :], p1[i, :] - p2[i, :], p2[i, :] - p3[i, :], 'xyz')
        p4_vec_lcl[i, :] = ctransform(gunit(), s123, np.expand_dims(p4[i, :] - p2[i, :], axis=0))[0]

    # Compute average local positions (over frames) for each point
    if n > 1:
        p1_vec_lcl_av = np.mean(p1_vec_lcl, axis=0)
        p2_vec_lcl_av = np.mean(p2_vec_lcl, axis=0)
        p3_vec_lcl_av = np.mean(p3_vec_lcl, axis=0)
        p4_vec_lcl_av = np.mean(p4_vec_lcl, axis=0)
    else:
        # keep shape (1,3) semantics consistent with original: leave as row vectors
        p1_vec_lcl_av = p1_vec_lcl.reshape(3,)
        p2_vec_lcl_av = p2_vec_lcl.reshape(3,)
        p3_vec_lcl_av = p3_vec_lcl.reshape(3,)
        p4_vec_lcl_av = p4_vec_lcl.reshape(3,)

    # Buffers for reconstructed global positions and final replacements
    p1_vec_gbl = np.zeros_like(p1)
    new_p1 = np.zeros_like(p1)
    rep_p1 = np.zeros_like(p1)

    p2_vec_gbl = np.zeros_like(p2)
    new_p2 = np.zeros_like(p2)
    rep_p2 = np.zeros_like(p2)

    p3_vec_gbl = np.zeros_like(p3)
    new_p3 = np.zeros_like(p3)
    rep_p3 = np.zeros_like(p3)

    p4_vec_gbl = np.zeros_like(p4)
    new_p4 = np.zeros_like(p4)
    rep_p4 = np.zeros_like(p4)

    # Second pass: transform averaged local positions back to global and compute replacements
    for i in range(n):
        # s234 -> place averaged p1 back into global (origin p3)
        _, _, _, _, s234 = create_lcs(p3[i, :], p2[i, :] - p3[i, :], p3[i, :] - p4[i, :], 'xyz')
        p1_vec_gbl[i, :] = ctransform(s234, gunit(), np.expand_dims(p1_vec_lcl_av, axis=0))[0]
        new_p1[i, :] = p1_vec_gbl[i, :] + p3[i, :]
        rep_p1[i, :] = (new_p1[i, :] + p1[i, :]) / 2
        _, _, _, _, s341 = create_lcs(p4[i, :], p3[i, :] - p4[i, :], p4[i, :] - p1[i, :], 'xyz')
        p2_vec_gbl[i, :] = ctransform(s341, gunit(), np.expand_dims(p2_vec_lcl_av, axis=0))[0]
        new_p2[i, :] = p2_vec_gbl[i, :] + p4[i, :]
        rep_p2[i, :] = (new_p2[i, :] + p2[i, :]) / 2
        _, _, _, _, s412 = create_lcs(p1[i, :], p4[i, :] - p1[i, :], p1[i, :] - p2[i, :], 'xyz')
        p3_vec_gbl[i, :] = ctransform(s412, gunit(), np.expand_dims(p3_vec_lcl_av, axis=0))[0]
        new_p3[i, :] = p3_vec_gbl[i, :] + p1[i, :]
        rep_p3[i, :] = (new_p3[i, :] + p3[i, :]) / 2
        _, _, _, _, s123 = create_lcs(p2[i, :], p1[i, :] - p2[i, :], p2[i, :] - p3[i, :], 'xyz')
        p4_vec_gbl[i, :] = ctransform(s123, gunit(), np.expand_dims(p4_vec_lcl_av, axis=0))[0]
        new_p4[i, :] = p4_vec_gbl[i, :] + p2[i, :]
        rep_p4[i, :] = (new_p4[i, :] + p4[i, :]) / 2

    return rep_p1, rep_p2, rep_p3, rep_p4


def point_to_plane(p1, p2, p3, p4):
    """
     proj_p1 = POINT_TO_PLANE(p1,p2,p3,p4) projects marker p1 into a plane
     defined by p2, p3, p4

     ARGUMENTS
       p1         ... n x 3 array
                      Point to be projected onto a plane
       p2, p3, p4 ... n x 3 arrays defining a plane

     RETURNS
       proj_p1     ... p1 projected orthogonally onto the plane of p2, p3,
                       and p4
     create a vector from a point on the plane that points to p1
    """
    w = p1 - p2
    a = p2 - p4
    b = p3 - p4
    # create vector normal to the plane
    n = makeunit(np.cross(a, b))

    # make each row of n a unit vector and calculate t
    t = np.zeros(n.shape)
    for i in range(n.shape[0]):
        t[i, :] = np.dot(w[i, :], n[i, :]) * n[i, :]

    # subtract t from w and add back p2 to get coordinates of projected point
    proj_p1 = (w - t) + p2
    return proj_p1


def pointonline(p1, p2, pos):
    # p1: first point m x 3 matrix
    # p2: second point m x 3 matrix
    # pos: distance from p1

    ln = p2 - p1
    [r, _] = ln.shape

    if r == 1:
        pt = np.zeros((1, 3))
        pt[0] = p1[0] + ln[0] * pos
        pt[1] = p1[1] + ln[1] * pos
        pt[2] = p1[2] + ln[2] * pos
    else:
        pt = np.zeros(ln.shape)
        pt[:, 0] = p1[:, 0] + ln[:, 0] * pos
        pt[:, 1] = p1[:, 1] + ln[:, 1] * pos
        pt[:, 2] = p1[:, 2] + ln[:, 2] * pos

    return pt


def nrmse(a, b):
    """
    r = NRMSE(a,b) computes the  root mean squared error between two vectors
    normalised to the range of signal a

     ARGUMENTS
       a   ...  1st vector of data
       b   ...  2nd vector of data

     RETURN
       r   ...  NRMSE between a and b
    """

    r = rmse(a, b)
    g = max(a)
    p = min(a)
    return r / (g - p)


def rmse(a, b):
    """
    rmse (a,b) computes the root mean squared error between two vectors
    ARGUMENTS
      a   ...  1st vector of data
      b   ...  2nd vector of data

     RETURN
          ...  RMSE between a and b
    """
    s = 0
    m = np.size(a)
    n = np.size(b)
    if m == n:
        for k in range(len(a)):
            s = s + ((a[k] - b[k]) ** 2)

        return np.sqrt(s / m)
    else:
        print('the two vectors are not the same size')


def move_marker_gcs_2_lcs(O, A, L, P, M):
    """
    Moves marker from GCS to lcs_static for each available frame.

    Arguments:
    O -- n x 3 array, Origin of the technical axes
    A -- n x 3 array, Anterior axis of the segment
    L -- n x 3 array, Lateral axis of the segment (medial for right side)
    P -- n x 3 array, Proximal axis of the segment
    M -- n x 3 array, Marker coordinates in GCS

    Returns:
    m_lcs_static -- n x 3 array, Marker moved from GCS to LCS
    """
    m_lcs_static = np.zeros_like(O)

    for i in range(len(m_lcs_static)):
        # Create LCS for static trial at each frame
        a = makeunit(np.expand_dims(A[i, :] - O[i, :], axis=0))
        l = makeunit(np.expand_dims(L[i, :] - O[i, :], axis=0))
        p = makeunit(np.expand_dims(P[i, :] - O[i, :], axis=0))
        lcs_static = np.vstack((a, l, p))

        # Translate marker to origin of GCS
        m_static = np.expand_dims(M[i, :] - O[i, :], axis=0)

        # Transform marker position from GCS to lcs_static
        m_lcs_static[i, :] = ctransform(gunit(), lcs_static, m_static)

    return m_lcs_static



def rotate_axes(axes, theta, axis):
    """
    Rotate a local coordinate system (axes) by an angle `theta` (in degrees)
    about one of its local axes ('x', 'y', or 'z').

    Parameters:
        axes : ndarray, shape (3, 3)
            Local coordinate system, where each row represents an axis vector.
        theta : float
            Rotation angle in degrees.
        axis : str
            Axis of rotation ('x', 'y', or 'z').

    Returns:
        rot_axes : ndarray, shape (3, 3)
            Rotated coordinate system.
    """
    axis = axis.lower()
    if axis not in ('x', 'y', 'z'):
        raise ValueError("Invalid axis. Must be 'x', 'y', or 'z'.")

    # Extract axis vector
    axis_vector = axes['xyz'.index(axis), :]
    L = np.linalg.norm(axis_vector)
    a, b, c = axis_vector
    V = np.sqrt(b**2 + c**2)

    # Handle the degenerate case when rotation axis aligns with global x
    if np.isclose(V, 0):
        V = 1e-12  # avoid division by zero

    cos_t, sin_t = np.cos(np.deg2rad(theta)), np.sin(np.deg2rad(theta))

    rot_x = np.array([[1, 0, 0], [0, c / V, b / V], [0, -b / V, c / V]])

    rot_y = np.array([[V / L, 0, a / L], [0, 1, 0], [-a / L, 0, V / L]])

    rot_z = np.array([[cos_t, sin_t, 0], [-sin_t, cos_t, 0], [0, 0, 1]])

    rev_rot_y = np.array([[V / L, 0, -a / L], [0, 1, 0], [a / L, 0, V / L]])

    rev_rot_x = np.array([[1, 0, 0], [0, c / V, -b / V], [0, b / V, c / V]])

    # Combined rotation
    t = np.matmul(np.matmul(np.matmul(np.matmul(rot_x, rot_y), rot_z), rev_rot_y), rev_rot_x)

    return np.matmul(axes, t)