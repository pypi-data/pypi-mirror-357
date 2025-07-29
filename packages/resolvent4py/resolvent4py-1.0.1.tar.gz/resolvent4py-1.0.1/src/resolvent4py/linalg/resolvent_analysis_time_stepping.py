__all__ = ["resolvent_analysis_rsvd_dt"]

import typing

import math
import numpy as np
import scipy as sp
import time as tlib
from petsc4py import PETSc
from slepc4py import SLEPc

from ..linear_operators import LinearOperator
from ..utils.matrix import create_dense_matrix
from ..utils.miscellaneous import petscprint
from ..utils.vector import vec_real


def _reorder_list(Qlist: list[SLEPc.BV], Qlist_reordered: list[SLEPc.BV]):
    for j in range(Qlist[0].getSizes()[-1]):
        for i in range(len(Qlist)):
            Qij = Qlist[i].getColumn(j)
            Qlist_reordered[j].insertVec(i, Qij)
            Qlist[i].restoreColumn(j, Qij)
    return Qlist_reordered


def _ifft(
    Xhat: SLEPc.BV,
    x: PETSc.Vec,
    omegas: np.array,
    t: float,
    adjoint: typing.Optional[bool] = False,
):
    sign = -1 if adjoint else 1
    q = np.exp(1j * omegas * t * sign)
    if np.min(omegas) == 0.0:
        c = 2 * np.ones(len(q))
        c[0] = 1.0
        q *= c
        Xhat.multVec(1.0, 0.0, x, q)
        x = vec_real(x, True)
    else:
        Xhat.multVec(1.0, 0.0, x, q)
    return x


def _fft(
    X: SLEPc.BV,
    Xhat: SLEPc.BV,
    real: typing.Optional[bool] = True,
    adjoint: typing.Optional[bool] = False,
):
    n_omegas = Xhat.getSizes()[-1]
    n_tstore = X.getSizes()[-1]

    Xhat_mat = Xhat.getMat()
    Xhat_mat_a = Xhat_mat.getDenseArray()
    Xmat = X.getMat()
    Xmat_a = Xmat.getDenseArray().copy()
    Xmat_a = Xmat_a.conj() if adjoint else Xmat_a
    if real:
        Xhat_mat_a[:, :] = (
            np.fft.rfft(Xmat_a.real, axis=-1)[:, :n_omegas] / n_tstore
        )
    else:
        n_omegas = int((n_omegas - 1) // 2 + 1)
        idces_pos = np.arange(n_omegas)
        idces_neg = np.arange(-n_omegas + 1, 0)
        idces = np.concatenate((idces_pos, idces_neg))
        Xhat_mat_a[:, :] = np.fft.fft(Xmat_a, axis=-1)[:, idces] / n_tstore

    Xhat_mat_a[:, :] = Xhat_mat_a.conj() if adjoint else Xhat_mat_a
    X.restoreMat(Xmat)
    Xhat.restoreMat(Xhat_mat)
    return Xhat


def _action(
    L: LinearOperator,
    Laction: typing.Callable,
    tsim: np.array,
    tstore: np.array,
    omegas: np.array,
    x: PETSc.Vec,
    Fhat: SLEPc.BV,
    Xhat: SLEPc.BV,
    X: SLEPc.BV,
    tol: typing.Optional[float] = 1e-3,
    verbose: typing.Optional[int] = 0,
):
    dt = tsim[1] - tsim[0]
    dt_store = tstore[1] - tstore[0]
    T = tstore[-1] + dt_store
    n_save = round(dt_store / dt)
    n_save_per_period = round(T / dt_store)
    n_periods = round((tsim[-1] + dt) / T)

    rhs = L.create_left_vector()
    rhs_im1 = rhs.copy()
    rhs_temp = rhs.copy()
    Lx = x.copy()
    x0 = x.copy()

    adjoint = True if Laction == L.apply_hermitian_transpose else False
    save_idx = 0
    period = 0
    X.insertVec(0, x)
    for i in range(1, len(tsim)):
        rhs = _ifft(Fhat, rhs, omegas, tsim[i - 1], adjoint)
        rhs.axpy(1.0, Laction(x, Lx))
        if i == 1:
            rhs.copy(rhs_im1)
        else:
            rhs.copy(rhs_temp)
            rhs.scale(3 / 2)
            rhs.axpy(-1 / 2, rhs_im1)
            rhs_temp.copy(rhs_im1)
        x.axpy(dt, rhs)

        if np.mod(i, n_save) == 0:
            if math.isnan(x.norm()):
                raise ValueError(f"Code blew up at time step {i}")
            save_idx = np.mod(save_idx + 1, n_save_per_period)
            if save_idx == 0:
                period += 1
                x0.axpy(-1.0, x)
                error = 100 * x0.norm() / x.norm()
                x.copy(x0)
                if verbose > 1:
                    str = (
                        "Deviation from periodicity at period %d/%d = %1.5e"
                        % (
                            period,
                            n_periods,
                            error,
                        )
                    )
                    petscprint(PETSc.COMM_WORLD, str)
                if (
                    error < tol
                ):  # Reached limit cycle, no need to integrate further
                    break
            X.insertVec(save_idx, x)

    Xhat = _fft(X, Xhat, L.get_real_flag(), adjoint)
    objs = [rhs, rhs_im1, rhs_temp, Lx, x0]
    for obj in objs:
        obj.destroy()

    return Xhat


def _create_time_and_frequency_arrays(
    dt: float, omega: float, n_omegas: int, n_periods: int, real: bool
):
    T = 2 * np.pi / omega
    tstore = np.linspace(0, T, num=2 * n_omegas + 4, endpoint=False)
    dt_store = tstore[1] - tstore[0]
    dt = dt_store / round(dt_store / dt)
    n_tsteps_per_period = round(T / dt)
    tsim = dt * np.arange(0, n_periods * n_tsteps_per_period)
    nsave = round(dt_store / dt)
    tsim_check = tsim[(n_periods - 1) * n_tsteps_per_period :: nsave].copy()
    tsim_check -= tsim[(n_periods - 1) * n_tsteps_per_period]
    if np.linalg.norm(tsim_check - tstore) >= 1e-10:
        raise ValueError("Simulation and storage times are not matching.")

    omegas = np.arange(n_omegas + 1) * omega
    omegas = (
        omegas if real else np.concatenate((omegas, -np.flipud(omegas[1:])))
    )

    return tsim, tstore, omegas, len(omegas)


def resolvent_analysis_rsvd_dt(
    L: LinearOperator,
    dt: float,
    omega: float,
    n_omegas: int,
    n_periods: int,
    n_rand: int,
    n_loops: int,
    n_svals: int,
    tol: typing.Optional[float] = 1e-3,
    verbose: typing.Optional[int] = 0,
) -> typing.Tuple[SLEPc.BV, np.ndarray, SLEPc.BV]:
    r"""
    Perform resolvent analysis using randomized linear algebra and time
    stepping.
    In particular, it can be shown that

    .. math::

        x_\omega e^{i\omega t} = \left(i\omega I - A\right)^{-1}f_\omega
            e^{i\omega t}
            \to \int_0^t e^{A(t-\tau)}f_\omega e^{i\omega\tau} d\tau

    for sufficiently long time :math:`t \gg 1` and for any complex-valued
    forcing :math:`f(t) = f_\omega e^{i\omega t}` (assuming that :math:`A` is
    stable).
    Computing the integral on the right-hand side can be done by integrating

    .. math::

        \frac{d}{dt}x(t) = Ax(t) + f(t)

    forward in time with initial condition :math:`x(0) = 0`.
    Thus, the action of the resolvent operator
    :math:`R(i\omega) = \left(i\omega I - A\right)^{-1}` on a vector
    :math:`f_\omega` can be computed by time-stepping the ODE above.
    For now, time integration is performed explicitly via the
    Adams-Bashforth scheme.
    (See [Martini2021]_ and [Farghadan2025]_ for more details.)

    .. note::

        This function is meant for systems whose dimension is so large
        that linear systems of the form
        :math:`(i\omega I - A)x_\omega = f_\omega`
        cannot be solved easily. Typically, this happens when
        :math:`\text{dim}(x_\omega) \sim O(10^7)` or larger.
        If you have a "small enough" system, then we highly recommend using
        :func:`.randomized_svd.randomized_svd` instead for the singular
        value decomposition of the resolvent.

    :param L: linear operator representing :math:`A`
    :type L: LinearOperator

    :param dt: target time step :math:`\Delta t` to integrate the ODE
    :type dt: float

    :param omega: fundamental frequency :math:`\omega` of the forcing
    :type omega: float

    :param n_omegas: number of integer harmonics of :math:`\omega` to resolve
    :type n_omegas: int

    :param n_periods: number of periods :math:`T = 2\pi/\omega` to integrate
        the ODE through. (This number should be large enough that we can
        expect transients to have decayed.)
    :type n_periods: int

    :param n_rand: number of random forcing vectors for randomized SVD
    :type n_rand: int

    :param n_loops: number of power iterations for randomized SVD
    :type n_loops: int

    :param n_svals: number of singular values/vectors to output
    :type n_svals: int

    :param tol: integrate the ODE forward for :code:`n_periods` or until
        :math:`\lVert x(kT) - x((k-1)T) \rVert < \mathrm{tol}`.
    :type tol: Optional[float], default is :math:`10^{-3}`

    :param verbose: defines verbosity of output to terminal (useful to
        monitor progress during time stepping). = 0 no printout to terminal,
        = 1 monitor randomized SVD iterations, = 2 monitor randomized SVD
        iterations and time-stepping progress.
    :type verbose: Optional[int], default is 0

    :return: left singular vectors, singular values, and right singular vectors
        of the resolvent operators :math:`R(i\omega)` evaluated at frequencies
        :math:`\Omega = \omega\{0, 1, 2, \ldots, n_{\omega}\}` if
        the linear operator :math:`A` is real-valued; otherwise at frequencies
        :math:`\Omega = \omega\{0, 1, 2, \ldots, n_{\omega}, -n_{\omega},-(n_{\omega}-1) \ldots, -1\}`
    :rtype: Tuple[List[SLEPc.BV], List[np.ndarray], List[SLEPc.BV]]

    References
    ----------
    .. [Martini2021] Martini et al., *Efficient computation of global
        resolvent modes*, Journal of Fluid Mechanics, 2021
    .. [Farghadan2025] Farghadan et al., *Scalable resolvent analysis
        for three-dimensional flows*, Journal of Computational Physics, 2025
    """

    size = L.get_dimensions()[0]

    tsim, tstore, omegas, n_omegas = _create_time_and_frequency_arrays(
        dt, omega, n_omegas, n_periods, L.get_real_flag()
    )

    Qadj_hat_lst, Qfwd_hat_lst = [], []
    for _ in range(n_rand):
        # Set seed
        rank = L.get_comm().getRank()
        rand = PETSc.Random().create(comm=L.get_comm())
        rand.setType(PETSc.Random.Type.RAND)
        rand.setSeed(round(np.random.randint(1000, 100000) + rank))
        # Initialize Qadj_hat and Qfwd_hat with random BVs of size N x n_rand
        X = SLEPc.BV().create(comm=L.get_comm())
        X.setSizes(size, n_omegas)
        X.setType("mat")
        X.setRandomContext(rand)
        X.setRandomNormal()
        rand.destroy()
        if L.get_real_flag():
            v = X.getColumn(0)
            v = vec_real(v, True)
            X.restoreColumn(0, v)
        Qadj_hat_lst.append(X.copy())
        Qfwd_hat_lst.append(X.copy())
        X.destroy()

    # Initialize Qadj_hat and Qfwd_hat with BVs of size N x n_omegas
    X = SLEPc.BV().create(comm=L.get_comm())
    X.setSizes(size, n_rand)
    X.setType("mat")
    Qadj_hat_lst2 = [X.copy() for _ in range(n_omegas)]
    Qfwd_hat_lst2 = [X.copy() for _ in range(n_omegas)]
    X.destroy()

    Qadj = SLEPc.BV().create(comm=L.get_comm())
    Qadj.setSizes(size, len(tstore))
    Qadj.setType("mat")
    Qfwd = Qadj.duplicate()

    Qadj_hat_lst2 = _reorder_list(Qadj_hat_lst, Qadj_hat_lst2)
    for i in range(len(Qadj_hat_lst2)):
        Qadj_hat_lst2[i].orthogonalize(None)
    Qadj_hat_lst = _reorder_list(Qadj_hat_lst2, Qadj_hat_lst)

    x = L.create_left_vector()
    for j in range(n_loops):
        for k in range(n_rand):
            if verbose > 0:
                str = "Loop %d/%d, random vector %d/%d (forward action)" % (
                    j + 1,
                    n_loops,
                    k + 1,
                    n_rand,
                )
                petscprint(L.get_comm(), str)
            x.zeroEntries()
            Qfwd_hat_lst[k] = _action(
                L,
                L.apply,
                tsim,
                tstore,
                omegas,
                x,
                Qadj_hat_lst[k],
                Qfwd_hat_lst[k],
                Qfwd,
                tol,
                verbose,
            )
        Qfwd_hat_lst2 = _reorder_list(Qfwd_hat_lst, Qfwd_hat_lst2)
        for i in range(len(Qfwd_hat_lst2)):
            Qfwd_hat_lst2[i].orthogonalize(None)
        Qfwd_hat_lst = _reorder_list(Qfwd_hat_lst2, Qfwd_hat_lst)

        for k in range(n_rand):
            if verbose > 0:
                str = "Loop %d/%d, random vector %d/%d (adjoint action)" % (
                    j + 1,
                    n_loops,
                    k + 1,
                    n_rand,
                )
                petscprint(L.get_comm(), str)
            x.zeroEntries()
            Qadj_hat_lst[k] = _action(
                L,
                L.apply_hermitian_transpose,
                tsim,
                tstore,
                omegas,
                x,
                Qfwd_hat_lst[k],
                Qadj_hat_lst[k],
                Qadj,
                tol,
                verbose,
            )
        Qadj_hat_lst2 = _reorder_list(Qadj_hat_lst, Qadj_hat_lst2)
        Rlst = []
        R = create_dense_matrix(PETSc.COMM_SELF, (n_rand, n_rand))
        for i in range(len(Qadj_hat_lst2)):
            Qadj_hat_lst2[i].orthogonalize(R)
            Rlst.append(R.copy())
        R.destroy()
        Qadj_hat_lst = _reorder_list(Qadj_hat_lst2, Qadj_hat_lst)
        if j < n_loops - 1:
            for obj in Rlst:
                obj.destroy()

    x.destroy()
    # Compute low-rank SVD
    Slst = []
    for j, R in enumerate(Rlst):
        u, s, v = sp.linalg.svd(R.getDenseArray())
        v = v.conj().T
        s = s[:n_svals]
        u = u[:, :n_svals]
        v = v[:, :n_svals]
        u = PETSc.Mat().createDense(
            (n_rand, n_svals), None, u, comm=PETSc.COMM_SELF
        )
        v = PETSc.Mat().createDense(
            (n_rand, n_svals), None, v, comm=PETSc.COMM_SELF
        )
        Qfwd_hat_lst2[j].multInPlace(v, 0, n_svals)
        Qfwd_hat_lst2[j].setActiveColumns(0, n_svals)
        Qfwd_hat_lst2[j].resize(n_svals, copy=True)
        Qadj_hat_lst2[j].multInPlace(u, 0, n_svals)
        Qadj_hat_lst2[j].setActiveColumns(0, n_svals)
        Qadj_hat_lst2[j].resize(n_svals, copy=True)
        Slst.append(np.diag(s))
        u.destroy()
        v.destroy()

    lists = [Rlst, Qfwd_hat_lst, Qadj_hat_lst]
    for lst in lists:
        for obj in lst:
            obj.destroy()

    return Qfwd_hat_lst2, Slst, Qadj_hat_lst2
