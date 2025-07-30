# conics - Python library for dealing with conics
#
# Copyright 2024 Sergiu Deitsch <sergiu.deitsch@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ._conic import Conic
from .geometry import rot2d
from scipy.optimize import least_squares
import numpy as np


class Parabola:
    R"""Represents a parabola given in the standard form by :math:`y^2=2px`
    (i.e., opening to the right) in general position obtained by rotating the
    canonic parbola by angle :math:`-\pi\leq\alpha<\pi` and shifting the vertex
    by :math:`\vec x_c\in\mathbb{R}^2`.

    Parameters
    ----------
    vertex : numpy.ndarray
        The 2-D coordinate of the parabola vertex.
    p : float
        The distance of the vertex to the focus.
    alpha : float
        The orientation of the parabola in the :math:`xy` plane.

    """

    def __init__(self, vertex, p, alpha):
        self.vertex = np.asarray(vertex)
        self.p = p
        self.alpha = alpha
        # if len(args) == 3:
        #    self.vertex, self.p, self.alpha = args
        # elif len(*args) == 3:
        #    self.vertex, self.p, self.alpha = tuple(*args)
        # self.vertex = args[0]
        # self.p = args[1]
        # self.alpha = args[2]
        # self.vertex, self.p, self.alpha = *args

    def contact(self, pts, **kwargs):
        R"""Computes the contact points on the parabola from the coordinates
        `pts`.

        Parameters
        ----------
        pts : numpy.ndarray
            :math:`N\times2` matrix of 2-D coordinates whose contact
            points are to be determined.
        **kwargs
            Additional arguments passed to
            :func:`scipy.optimize.least_squares`.

        Returns
        -------
        numpy.ndarray
            :math:`N\times2` matrix of 2-D coordinates representing the
            contact points.
        """

        pts = np.atleast_2d(pts)

        R = rot2d(self.alpha)
        pts1 = R.T @ (pts - self.vertex[..., np.newaxis])

        def jac(xy, xi, yi):
            x, y = xy
            J = np.block([[-self.p, y], [-y, xi - x - self.p]])

            return J

        def fun(xy, xi, yi):
            x, y = xy
            f5 = np.ravel(0.5 * (y**2 - 2 * self.p * x))
            f6 = np.ravel(y * (xi - x) + self.p * (yi - y))

            return np.ravel([f5, f6])  # np.stack((f5, f6)).ravel()

        pts2 = np.empty_like(pts1)

        for i, xiyi in enumerate(pts1.T):
            xi, yi = xiyi
            mask = xi < 0
            y2s = np.sqrt(2 * self.p * xi, out=np.zeros_like(xi), where=~mask)

            other = np.stack((xi, np.copysign(y2s, yi)))
            x0 = np.where(mask, np.zeros_like(xiyi), other)

            r = least_squares(fun, x0, args=(xi, yi), jac=jac, **kwargs)
            # TODO check convergence

            pts2[:, i] = r.x

        return R @ pts2 + self.vertex[..., np.newaxis]

    def refine(self, pts, **kwargs):
        """Refines the parabola parameters with respect to some reference 2-D
        coordinates.

        The refinement is performed by minimizing the distances between the
        orthogonal contact points on the parabola and the observed points `pts`.

        The method implements the approach from :cite:`Ahn2001`.

        Parameters
        ----------
        pts : numpy.ndarray
            Observed 2-D coordinates of the parabola.
        **kwargs
            Additional arguments passed to
            :func:`scipy.optimize.least_squares`.

        Returns
        -------
        conics.Parabola
            The refined parabola.
        """

        def fun(a, pts):
            xc, yc, p, alpha = a
            pp = Parabola([xc, yc], p, alpha)

            xy = pp.contact(pts)

            residuals = xy - pts

            # Stack residuals for x and y component after each other
            return np.ravel(residuals, order='F')

        def jac(a, pts):
            xc, yc, p, alpha = a
            pp = Parabola([xc, yc], p, alpha)

            xy = pp.contact(pts)

            R = rot2d(alpha)
            c, s = R[0]

            vertex = np.array([[xc], [yc]])
            x, y = R.T @ (xy - vertex)
            xi, yi = R.T @ (pts - vertex)

            ones = np.ones_like(x)
            zeros = np.zeros_like(x)

            Q = np.array([[-p * ones, y], [-y, xi - x - p]])
            J2 = np.array(
                [
                    [zeros, zeros, x, zeros],
                    [y * c - p * s, y * s + p * c, y - yi, -y * yi + p * xi],
                ]
            )
            J3 = np.array(
                [
                    [ones, zeros, zeros, -x * s - y * c],
                    [zeros, ones, zeros, +x * c - y * s],
                ]
            )

            Q = np.moveaxis(Q, -1, 0)
            J2 = np.moveaxis(J2, -1, 0)
            J3 = np.moveaxis(J3, -1, 0)

            J = R @ np.linalg.solve(Q, J2) + J3

            return J.reshape(-1, 4, order='C')

        x0 = np.stack((*self.vertex, self.p, self.alpha))

        r = least_squares(fun, x0, args=(pts,), jac=jac, **kwargs)

        return Parabola(r.x[:2], r.x[2], r.x[3])

    def to_conic(self):
        """Converts the parabola to its general algebraic form.

        Returns
        -------
        conics.Conic
            The conic representation of the parabola.
        """
        return Conic.from_parabola(self.vertex, self.p, self.alpha)

    @staticmethod
    def from_conic(C):
        """Constructs a parabola from its general algebraic form.

        Returns
        -------
        conics.Parabola
            The geometric representation of the parabola.
        """
        return Parabola(*C.to_parabola())
