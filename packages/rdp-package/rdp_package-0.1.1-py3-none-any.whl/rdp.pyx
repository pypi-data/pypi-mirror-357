# cython: boundscheck=False, wraparound=False, cdivision=True
import numpy as np
cimport numpy as np
from libc.stdlib cimport malloc, free, realloc
from libc.math cimport fabs, sqrt, atan, cos, sin, atan2

cdef extern from "math.h":
    double fabs(double x)
    double sqrt(double x)
    double atan(double x)
    double cos(double x)
    double sin(double x)

def rdp_by_count(points, int target_count):
    cdef int n = points.shape[0]

    cdef double* x = <double*> malloc(n * sizeof(double))
    cdef double* y = <double*> malloc(n * sizeof(double))
    cdef int i

    for i in range(n):
        x[i] = points[i, 0]
        y[i] = points[i, 1]

    cdef np.ndarray[np.float64_t, ndim=1] weights = np.zeros(n, dtype=np.float64)
    weights[0] = float("inf")
    weights[n - 1] = float("inf")

    cdef int stack_capacity = 1024
    cdef int* stack = <int*> malloc(stack_capacity * 2 * sizeof(int))
    cdef int sp = 0
    stack[0] = 0
    stack[1] = n - 1
    sp = 1

    cdef int st, ed, index
    cdef double dx, dy, norm, t, px, py, projx, projy, dist2, max_dist

    while sp > 0:
        sp -= 1
        st = stack[sp * 2]
        ed = stack[sp * 2 + 1]

        if ed <= st + 1:
            continue

        dx = x[ed] - x[st]
        dy = y[ed] - y[st]
        norm = dx * dx + dy * dy

        max_dist = -1
        index = -1

        for i in range(st + 1, ed):
            px = x[i]
            py = y[i]
            if norm == 0:
                dist2 = (px - x[st])**2 + (py - y[st])**2
            else:
                t = ((px - x[st]) * dx + (py - y[st]) * dy) / norm
                if t < 0:
                    projx = x[st]
                    projy = y[st]
                elif t > 1:
                    projx = x[ed]
                    projy = y[ed]
                else:
                    projx = x[st] + t * dx
                    projy = y[st] + t * dy
                dist2 = (px - projx)**2 + (py - projy)**2

            if dist2 > max_dist:
                max_dist = dist2
                index = i

        if index != -1:
            weights[index] = max_dist
            if sp + 2 >= stack_capacity:
                stack_capacity *= 2
                stack = <int*> realloc(stack, stack_capacity * 2 * sizeof(int))
            stack[sp * 2] = st
            stack[sp * 2 + 1] = index
            sp += 1
            stack[sp * 2] = index
            stack[sp * 2 + 1] = ed
            sp += 1

    free(stack)
    free(x)
    free(y)

    cdef np.ndarray[np.intp_t, ndim=1] indices = np.argpartition(weights, -target_count)[-target_count:]
    indices = np.sort(indices)

    return points[indices]

cdef double compute_epsilon(double dx, double dy):
    cdef double s = sqrt(dx * dx + dy * dy)
    if s == 0:
        return 0.0
    cdef double inv_s = 1.0 / s
    cdef double phi = atan2(dy, dx)
    cdef double cos_phi = cos(phi)
    cdef double sin_phi = sin(phi)
    cdef double t_max = inv_s * (fabs(cos_phi) + fabs(sin_phi))
    cdef double poly = 1.0 - t_max + t_max * t_max
    cdef double dphi1 = atan(inv_s * fabs(sin_phi + cos_phi) * poly)
    cdef double dphi2 = atan(inv_s * fabs(sin_phi - cos_phi) * poly)
    cdef double d_phi_max = dphi1 if dphi1 > dphi2 else dphi2
    cdef double d_max = s * d_phi_max
    return d_max * d_max

cdef double point_to_segment_distance_sq(double x, double y,
                                            double x1, double y1,
                                            double x2, double y2):
    cdef double dx = x2 - x1
    cdef double dy = y2 - y1
    cdef double px = x - x1
    cdef double py = y - y1
    cdef double proj = dx * dx + dy * dy
    cdef double t

    if proj == 0.0:
        return (x - x1) ** 2 + (y - y1) ** 2

    t = (px * dx + py * dy) / proj
    t = max(0.0, min(1.0, t))

    cdef double proj_x = x1 + t * dx
    cdef double proj_y = y1 + t * dy

    dx = x - proj_x
    dy = y - proj_y
    return dx * dx + dy * dy

cdef void _rdp_modified(double* x, double* y, int n, char* mask):
    cdef int i, index_max
    cdef double d_max_sq, d_sq
    cdef double dx, dy, epsilon

    if n <= 2:
        return

    dx = x[n-1] - x[0]
    dy = y[n-1] - y[0]
    epsilon = compute_epsilon(dx, dy)

    d_max_sq = 0.0
    index_max = 0

    for i in range(1, n-1):
        d_sq = point_to_segment_distance_sq(x[i], y[i], x[0], y[0], x[n-1], y[n-1])
        if d_sq > d_max_sq:
            d_max_sq = d_sq
            index_max = i

    if d_max_sq <= epsilon:
        for i in range(1, n-1):
            mask[i] = 0
    else:
        _rdp_modified(x, y, index_max + 1, mask)
        _rdp_modified(x + index_max, y + index_max, n - index_max, mask + index_max)

def rdp_modified(points):
    cdef int i, n = len(points)
    if n == 0:
        return []

    cdef double *x = <double*> malloc(n * sizeof(double))
    cdef double *y = <double*> malloc(n * sizeof(double))
    cdef char *mask = <char*> malloc(n * sizeof(char))

    for i in range(n):
        x[i] = points[i][0]
        y[i] = points[i][1]
        mask[i] = 1

    _rdp_modified(x, y, n, mask)

    result = []
    for i in range(n):
        if mask[i]:
            result.append((x[i], y[i]))

    free(x)
    free(y)
    free(mask)

    return result

def rdp(points, int target_count = -1):
    cdef int n = points.shape[0]
    if n == 0:
        return np.empty((0, 2), dtype=np.float64)
    if points.shape[1] != 2:
        raise ValueError("points must be of shape (n_points, 2)")
    if target_count >= n:
        return np.asarray(points)
    if target_count >= 2:
        return rdp_by_count(points, target_count)
    else:
        return rdp_modified(points)
