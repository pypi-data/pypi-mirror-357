import hylife.geometry.mappings_3d as map3d
import hylife.geometry.mappings_3d_fast as mapping_fast
import hylife.linear_algebra.core as linalg
import hylife.utilitis_FEEC.basics.spline_evaluation_3d as eva
import hylife.utilitis_FEEC.bsplines_kernels as bsp
import input_run.equilibrium_PIC as equ_PIC
from pyccel.decorators import types


@types(
    "int[:]",
    "double[:,:,:]",
    "int",
    "double[:]",
    "double[:]",
    "double[:]",
    "double[:]",
    "int[:]",
    "int[:]",
    "int[:]",
    "double[:,:,:]",
    "double[:,:,:]",
    "double[:,:,:]",
)
def grid_density(Nel, gather_grid, kind_map, params_map, tf1, tf2, tf3, pf, nelf, nbasef, cx, cy, cz):
    # =======================================================================
    # -- removed omp: #$ omp parallel
    # -- removed omp: #$ omp do private (ie1, ie2, ie3, x1, x2, x3)
    for ie1 in range(Nel[0]):
        for ie2 in range(Nel[1]):
            for ie3 in range(Nel[2]):
                # ========= physical domain =============
                x1 = map3d.f(
                    ie1 / Nel[0],
                    ie2 / Nel[2],
                    ie3 / Nel[2],
                    1,
                    kind_map,
                    params_map,
                    tf1,
                    tf2,
                    tf3,
                    pf,
                    nbasef,
                    cx,
                    cy,
                    cz,
                )
                x2 = map3d.f(
                    ie1 / Nel[0],
                    ie2 / Nel[2],
                    ie3 / Nel[2],
                    2,
                    kind_map,
                    params_map,
                    tf1,
                    tf2,
                    tf3,
                    pf,
                    nbasef,
                    cx,
                    cy,
                    cz,
                )
                x3 = map3d.f(
                    ie1 / Nel[0],
                    ie2 / Nel[2],
                    ie3 / Nel[2],
                    3,
                    kind_map,
                    params_map,
                    tf1,
                    tf2,
                    tf3,
                    pf,
                    nbasef,
                    cx,
                    cy,
                    cz,
                )

                gather_grid[ie1, ie2, ie3] += equ_PIC.nh_eq_phys(x1, x2, x3)
    # -- removed omp: #$ omp end do
    # -- removed omp: #$ omp end parallel
    ierr = 0


# =============================================================================================================================================================================
@types(
    "double",
    "double[:,:]",
    "double[:]",
    "double[:,:,:]",
    "double[:,:,:]",
    "double[:,:,:]",
    "double[:,:,:]",
    "int",
    "int[:]",
    "int[:]",
    "int[:]",
    "int[:]",
    "double[:]",
    "double[:]",
    "double[:]",
    "double[:,:]",
    "int",
    "double[:]",
    "double[:]",
    "double[:]",
    "double[:]",
    "int[:]",
    "int[:]",
    "int[:]",
    "double[:,:,:]",
    "double[:,:,:]",
    "double[:,:,:]",
)
def vv(
    tol,
    out_vector,
    Jeq,
    bb1,
    bb2,
    bb3,
    n,
    Np_loc,
    NbaseN,
    NbaseD,
    Nel,
    p,
    t1,
    t2,
    t3,
    particles,
    kind_map,
    params_map,
    tf1,
    tf2,
    tf3,
    pf,
    nelf,
    nbasef,
    cx,
    cy,
    cz,
):
    from numpy import empty, zeros

    pn1 = p[0]
    pn2 = p[1]
    pn3 = p[2]

    pd1 = pn1 - 1
    pd2 = pn2 - 1
    pd3 = pn3 - 1

    # p + 1 non-vanishing basis functions up tp degree p
    b1 = empty((pn1 + 1, pn1 + 1), dtype=float)
    b2 = empty((pn2 + 1, pn2 + 1), dtype=float)
    b3 = empty((pn3 + 1, pn3 + 1), dtype=float)

    l1 = empty(pn1, dtype=float)
    l2 = empty(pn2, dtype=float)
    l3 = empty(pn3, dtype=float)

    r1 = empty(pn1, dtype=float)
    r2 = empty(pn2, dtype=float)
    r3 = empty(pn3, dtype=float)

    # scaling arrays for M-splines
    d1 = empty(pn1, dtype=float)
    d2 = empty(pn2, dtype=float)
    d3 = empty(pn3, dtype=float)
    # non-vanishing N-splines
    bn1 = empty(pn1 + 1, dtype=float)
    bn2 = empty(pn2 + 1, dtype=float)
    bn3 = empty(pn3 + 1, dtype=float)

    # non-vanishing D-splines
    bd1 = empty(pd1 + 1, dtype=float)
    bd2 = empty(pd2 + 1, dtype=float)
    bd3 = empty(pd3 + 1, dtype=float)

    vel2 = zeros(3, dtype=float)
    vel = zeros(3, dtype=float)
    dfinv = zeros((3, 3), dtype=float)
    out_vector[:, :] = 0.0

    # ================ for mapping evaluation ==================
    # spline degrees
    pf1 = pf[0]
    pf2 = pf[1]
    pf3 = pf[2]

    # pf + 1 non-vanishing basis functions up tp degree pf
    b1f = empty((pf1 + 1, pf1 + 1), dtype=float)
    b2f = empty((pf2 + 1, pf2 + 1), dtype=float)
    b3f = empty((pf3 + 1, pf3 + 1), dtype=float)

    # left and right values for spline evaluation
    l1f = empty(pf1, dtype=float)
    l2f = empty(pf2, dtype=float)
    l3f = empty(pf3, dtype=float)

    r1f = empty(pf1, dtype=float)
    r2f = empty(pf2, dtype=float)
    r3f = empty(pf3, dtype=float)

    # scaling arrays for M-splines
    d1f = empty(pf1, dtype=float)
    d2f = empty(pf2, dtype=float)
    d3f = empty(pf3, dtype=float)

    # pf + 1 derivatives
    der1f = empty(pf1 + 1, dtype=float)
    der2f = empty(pf2 + 1, dtype=float)
    der3f = empty(pf3 + 1, dtype=float)

    # needed mapping quantities
    df = empty((3, 3), dtype=float)
    fx = empty(3, dtype=float)

    # -- removed omp: #$ omp parallel
    # -- removed omp: #$ omp do private (tt, eta1, eta2, eta3, span1, span2, span3, ip, l1, l2, l3, r1, r2, r3, b1, b2, b3, d1, d2, d3, bn1, bn2, bn3, bd1, bd2, bd3, vel, vel2, dfinv, U_value, span1f, span2f, span3f, l1f, l2f, l3f, r1f, r2f, r3f, b1f, b2f, b3f, d1f, d2f, d3f, der1f, der2f, der3f, df, fx, x1, x2, x3, Jeq)
    for ip in range(Np_loc):
        vel[:] = 0.0

        eta1 = particles[0, ip]
        eta2 = particles[1, ip]
        eta3 = particles[2, ip]
        span1 = int(eta1 * Nel[0]) + pn1
        span2 = int(eta2 * Nel[1]) + pn2
        span3 = int(eta3 * Nel[2]) + pn3

        bsp.basis_funs_all(t1, pn1, eta1, span1, l1, r1, b1, d1)
        bsp.basis_funs_all(t2, pn2, eta2, span2, l2, r2, b2, d2)
        bsp.basis_funs_all(t3, pn3, eta3, span3, l3, r3, b3, d3)
        bn1[:] = b1[pn1, :]
        bd1[:] = b1[pd1, :pn1] * d1[:]
        bn2[:] = b2[pn2, :]
        bd2[:] = b2[pd2, :pn2] * d2[:]
        bn3[:] = b3[pn3, :]
        bd3[:] = b3[pd3, :pn3] * d3[:]

        vel[0] = eva.evaluation_kernel(
            pd1, pn2, pn3, bd1, bn2, bn3, span1 - 1, span2, span3, NbaseD[0], NbaseN[1], NbaseN[2], bb1
        )
        vel[1] = eva.evaluation_kernel(
            pn1, pd2, pn3, bn1, bd2, bn3, span1, span2 - 1, span3, NbaseN[0], NbaseD[1], NbaseN[2], bb2
        )
        vel[2] = eva.evaluation_kernel(
            pn1, pn2, pd3, bn1, bn2, bd3, span1, span2, span3 - 1, NbaseN[0], NbaseN[1], NbaseD[2], bb3
        )

        tt = eva.evaluation_kernel(
            pn1, pn2, pn3, bn1, bn2, bn3, span1, span2, span3, NbaseN[0], NbaseN[1], NbaseN[2], n
        )
        if abs(tt) > tol:
            U_value = 1.0 / tt
        else:
            U_value = 0.0
        # ========= mapping evaluation =============
        span1f = int(eta1 * nelf[0]) + pf1
        span2f = int(eta2 * nelf[1]) + pf2
        span3f = int(eta3 * nelf[2]) + pf3

        # evaluate Jacobian matrix
        mapping_fast.df_all(
            kind_map,
            params_map,
            tf1,
            tf2,
            tf3,
            pf,
            nbasef,
            span1f,
            span2f,
            span3f,
            cx,
            cy,
            cz,
            l1f,
            l2f,
            l3f,
            r1f,
            r2f,
            r3f,
            b1f,
            b2f,
            b3f,
            d1f,
            d2f,
            d3f,
            der1f,
            der2f,
            der3f,
            eta1,
            eta2,
            eta3,
            df,
            fx,
            0,
        )

        # evaluate inverse Jacobian matrix
        mapping_fast.df_inv_all(df, dfinv)
        # =========================================

        linalg.matrix_vector(dfinv, vel, vel2)

        x1 = map3d.f(eta1, eta2, eta3, 1, kind_map, params_map, tf1, tf2, tf3, pf, nbasef, cx, cy, cz)
        x2 = map3d.f(eta1, eta2, eta3, 2, kind_map, params_map, tf1, tf2, tf3, pf, nbasef, cx, cy, cz)
        x3 = map3d.f(eta1, eta2, eta3, 3, kind_map, params_map, tf1, tf2, tf3, pf, nbasef, cx, cy, cz)

        Jeq[0] = equ_PIC.jhx_eq(x1, x2, x3)
        Jeq[1] = equ_PIC.jhy_eq(x1, x2, x3)
        Jeq[2] = equ_PIC.jhz_eq(x1, x2, x3)

        vel[0] = vel2[1] * Jeq[2] - vel2[2] * Jeq[1]
        vel[1] = vel2[2] * Jeq[0] - vel2[0] * Jeq[2]
        vel[2] = vel2[0] * Jeq[1] - vel2[1] * Jeq[0]
        out_vector[0, ip] -= U_value * vel[0]
        out_vector[1, ip] -= U_value * vel[1]
        out_vector[2, ip] -= U_value * vel[2]
    # -- removed omp: #$ omp end do
    # -- removed omp: #$ omp end parallel

    ierr = 0


# ===================== bv substep =======================


# ==========================================================================================
@types(
    "double",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "double[:,:,:,:,:,:]",
    "double[:,:,:]",
    "double[:,:,:,:]",
    "double[:,:,:,:]",
    "double[:,:,:,:]",
    "int[:,:]",
    "int[:,:]",
    "int[:,:]",
)
def bvpre(tol, nel1, nel2, nel3, nq1, nq2, nq3, p1, p2, p3, uvalue, n, bn1, bn2, bn3, idnx, idny, idnz):
    # -- removed omp: #$ omp parallel
    # -- removed omp: #$ omp do private (ie1, ie2, ie3, q1, q2, q3, il1, il2, il3, value)

    for ie1 in range(nel1):
        for ie2 in range(nel2):
            for ie3 in range(nel3):
                for q1 in range(nq1):
                    for q2 in range(nq2):
                        for q3 in range(nq3):
                            value = 0.0
                            for il1 in range(p1 + 1):
                                for il2 in range(p2 + 1):
                                    for il3 in range(p3 + 1):
                                        value += (
                                            bn1[ie1, il1, 0, q1]
                                            * bn2[ie2, il2, 0, q2]
                                            * bn3[ie3, il3, 0, q3]
                                            * n[idnx[ie1, il1], idny[ie2, il2], idnz[ie3, il3]]
                                        )
                            if abs(value) > tol:
                                uvalue[ie1, ie2, ie3, q1, q2, q3] = 1.0 / value
                            else:
                                uvalue[ie1, ie2, ie3, q1, q2, q3] = 0.0

    # -- removed omp: #$ omp end do
    # -- removed omp: #$ omp end parallel

    ierr = 0


# ==========================================================================================
@types(
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "int[:,:]",
    "int[:,:]",
    "int[:,:]",
    "int[:,:]",
    "int[:,:]",
    "int[:,:]",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:]",
    "double[:,:,:]",
    "double[:,:,:]",
    "double[:,:]",
    "double[:]",
    "double[:]",
    "double[:]",
    "double[:,:,:,:]",
    "double[:,:,:,:]",
    "double[:,:,:,:]",
    "double[:,:,:,:]",
    "double[:,:,:,:]",
    "double[:,:,:,:]",
)
def bvright1(
    G_inv_11,
    G_inv_12,
    G_inv_13,
    G_inv_22,
    G_inv_23,
    G_inv_33,
    idnx,
    idny,
    idnz,
    iddx,
    iddy,
    iddz,
    nel1,
    nel2,
    nel3,
    nq1,
    nq2,
    nq3,
    p1,
    p2,
    p3,
    d1,
    d2,
    d3,
    b1value,
    b2value,
    b3value,
    b1,
    b2,
    b3,
    dft,
    generate_weight1,
    generate_weight3,
    Jeq,
    bn1,
    bn2,
    bn3,
    bd1,
    bd2,
    bd3,
):
    # ======================================================================================

    # -- removed omp: #$ omp parallel
    # -- removed omp: #$ omp do private (ie1, ie2, ie3, q1, q2, q3, il1, il2, il3, value)

    for ie1 in range(nel1):
        for ie2 in range(nel2):
            for ie3 in range(nel3):
                for q1 in range(nq1):
                    for q2 in range(nq2):
                        for q3 in range(nq3):
                            value = 0.0
                            for il1 in range(d1 + 1):
                                for il2 in range(p2 + 1):
                                    for il3 in range(p3 + 1):
                                        value += (
                                            bd1[ie1, il1, 0, q1]
                                            * bn2[ie2, il2, 0, q2]
                                            * bn3[ie3, il3, 0, q3]
                                            * b1[iddx[ie1, il1], idny[ie2, il2], idnz[ie3, il3]]
                                        )

                            b1value[ie1, ie2, ie3, q1, q2, q3] = value

    # -- removed omp: #$ omp end do
    # -- removed omp: #$ omp end parallel

    # -- removed omp: #$ omp parallel
    # -- removed omp: #$ omp do private (ie1, ie2, ie3, q1, q2, q3, il1, il2, il3, value)

    for ie1 in range(nel1):
        for ie2 in range(nel2):
            for ie3 in range(nel3):
                for q1 in range(nq1):
                    for q2 in range(nq2):
                        for q3 in range(nq3):
                            value = 0.0
                            for il1 in range(p1 + 1):
                                for il2 in range(d2 + 1):
                                    for il3 in range(p3 + 1):
                                        value += (
                                            bn1[ie1, il1, 0, q1]
                                            * bd2[ie2, il2, 0, q2]
                                            * bn3[ie3, il3, 0, q3]
                                            * b2[idnx[ie1, il1], iddy[ie2, il2], idnz[ie3, il3]]
                                        )

                            b2value[ie1, ie2, ie3, q1, q2, q3] = value
    # -- removed omp: #$ omp end do
    # -- removed omp: #$ omp end parallel

    # -- removed omp: #$ omp parallel
    # -- removed omp: #$ omp do private (ie1, ie2, ie3, q1, q2, q3, il1, il2, il3, value)

    for ie1 in range(nel1):
        for ie2 in range(nel2):
            for ie3 in range(nel3):
                for q1 in range(nq1):
                    for q2 in range(nq2):
                        for q3 in range(nq3):
                            value = 0.0
                            for il1 in range(p1 + 1):
                                for il2 in range(p2 + 1):
                                    for il3 in range(d3 + 1):
                                        value += (
                                            bn1[ie1, il1, 0, q1]
                                            * bn2[ie2, il2, 0, q2]
                                            * bd3[ie3, il3, 0, q3]
                                            * b3[idnx[ie1, il1], idny[ie2, il2], iddz[ie3, il3]]
                                        )

                            b3value[ie1, ie2, ie3, q1, q2, q3] = value
    # -- removed omp: #$ omp end do
    # -- removed omp: #$ omp end parallel

    # -- removed omp: #$ omp parallel
    # -- removed omp: #$ omp do private (ie1, ie2, ie3, q1, q2, q3, dft, generate_weight1, generate_weight3)
    for ie1 in range(nel1):
        for ie2 in range(nel2):
            for ie3 in range(nel3):
                for q1 in range(nq1):
                    for q2 in range(nq2):
                        for q3 in range(nq3):
                            dft[0, 0] = G_inv_11[ie1, ie2, ie3, q1, q2, q3]
                            dft[0, 1] = G_inv_12[ie1, ie2, ie3, q1, q2, q3]
                            dft[0, 2] = G_inv_13[ie1, ie2, ie3, q1, q2, q3]
                            dft[1, 0] = G_inv_12[ie1, ie2, ie3, q1, q2, q3]
                            dft[1, 1] = G_inv_22[ie1, ie2, ie3, q1, q2, q3]
                            dft[1, 2] = G_inv_23[ie1, ie2, ie3, q1, q2, q3]
                            dft[2, 0] = G_inv_13[ie1, ie2, ie3, q1, q2, q3]
                            dft[2, 1] = G_inv_23[ie1, ie2, ie3, q1, q2, q3]
                            dft[2, 2] = G_inv_33[ie1, ie2, ie3, q1, q2, q3]
                            generate_weight3[0] = b1value[ie1, ie2, ie3, q1, q2, q3]
                            generate_weight3[1] = b2value[ie1, ie2, ie3, q1, q2, q3]
                            generate_weight3[2] = b3value[ie1, ie2, ie3, q1, q2, q3]
                            linalg.matrix_vector(dft, generate_weight3, generate_weight1)
                            b1value[ie1, ie2, ie3, q1, q2, q3] = generate_weight1[0]
                            b2value[ie1, ie2, ie3, q1, q2, q3] = generate_weight1[1]
                            b3value[ie1, ie2, ie3, q1, q2, q3] = generate_weight1[2]

    # -- removed omp: #$ omp end do
    # -- removed omp: #$ omp end parallel

    ierr = 0


# ==========================================================================================
@types(
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:]",
    "double[:]",
    "double[:]",
    "double[:]",
    "double[:,:]",
    "double[:,:]",
    "double[:,:]",
    "double[:,:]",
    "double[:,:]",
    "double[:,:]",
)
def bvright2(
    DFI_11,
    DFI_12,
    DFI_13,
    DFI_21,
    DFI_22,
    DFI_23,
    DFI_31,
    DFI_32,
    DFI_33,
    df_det,
    Jeqx,
    Jeqy,
    Jeqz,
    nel1,
    nel2,
    nel3,
    nq1,
    nq2,
    nq3,
    p1,
    p2,
    p3,
    d1,
    d2,
    d3,
    b1value,
    b2value,
    b3value,
    uvalue,
    dft,
    generate_weight1,
    generate_weight3,
    Jeq,
    pts1,
    pts2,
    pts3,
    wts1,
    wts2,
    wts3,
):
    # ======================================================================================

    # -- removed omp: #$ omp parallel
    # -- removed omp: #$ omp do private (ie1, ie2, ie3, q1, q2, q3, dft, detdet, generate_weight1, generate_weight3, Jeq)
    for ie1 in range(nel1):
        for ie2 in range(nel2):
            for ie3 in range(nel3):
                for q1 in range(nq1):
                    for q2 in range(nq2):
                        for q3 in range(nq3):
                            generate_weight1[0] = b1value[ie1, ie2, ie3, q1, q2, q3]
                            generate_weight1[1] = b2value[ie1, ie2, ie3, q1, q2, q3]
                            generate_weight1[2] = b3value[ie1, ie2, ie3, q1, q2, q3]

                            dft[0, 0] = DFI_11[ie1, ie2, ie3, q1, q2, q3]
                            dft[0, 1] = DFI_12[ie1, ie2, ie3, q1, q2, q3]
                            dft[0, 2] = DFI_13[ie1, ie2, ie3, q1, q2, q3]
                            dft[1, 0] = DFI_21[ie1, ie2, ie3, q1, q2, q3]
                            dft[1, 1] = DFI_22[ie1, ie2, ie3, q1, q2, q3]
                            dft[1, 2] = DFI_23[ie1, ie2, ie3, q1, q2, q3]
                            dft[2, 0] = DFI_31[ie1, ie2, ie3, q1, q2, q3]
                            dft[2, 1] = DFI_32[ie1, ie2, ie3, q1, q2, q3]
                            dft[2, 2] = DFI_33[ie1, ie2, ie3, q1, q2, q3]
                            detdet = df_det[ie1, ie2, ie3, q1, q2, q3] * wts1[ie1, q1] * wts2[ie2, q2] * wts3[ie3, q3]
                            Jeq[0] = Jeqx[ie1, ie2, ie3, q1, q2, q3]
                            Jeq[1] = Jeqy[ie1, ie2, ie3, q1, q2, q3]
                            Jeq[2] = Jeqz[ie1, ie2, ie3, q1, q2, q3]
                            linalg.matrix_vector(dft, Jeq, generate_weight3)

                            b1value[ie1, ie2, ie3, q1, q2, q3] = (
                                detdet
                                * uvalue[ie1, ie2, ie3, q1, q2, q3]
                                * (
                                    generate_weight3[1] * generate_weight1[2]
                                    - generate_weight3[2] * generate_weight1[1]
                                )
                            )
                            b2value[ie1, ie2, ie3, q1, q2, q3] = (
                                detdet
                                * uvalue[ie1, ie2, ie3, q1, q2, q3]
                                * (
                                    generate_weight3[2] * generate_weight1[0]
                                    - generate_weight3[0] * generate_weight1[2]
                                )
                            )
                            b3value[ie1, ie2, ie3, q1, q2, q3] = (
                                detdet
                                * uvalue[ie1, ie2, ie3, q1, q2, q3]
                                * (
                                    generate_weight3[0] * generate_weight1[1]
                                    - generate_weight3[1] * generate_weight1[0]
                                )
                            )

    # -- removed omp: #$ omp end do
    # -- removed omp: #$ omp end parallel

    ierr = 0


# ==========================================================================================
@types(
    "int[:,:]",
    "int[:,:]",
    "int[:,:]",
    "int[:,:]",
    "int[:,:]",
    "int[:,:]",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "int",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:,:,:]",
    "double[:,:,:,:]",
    "double[:,:,:,:]",
    "double[:,:,:,:]",
    "double[:,:,:,:]",
    "double[:,:,:,:]",
    "double[:,:,:,:]",
    "double[:,:,:]",
    "double[:,:,:]",
    "double[:,:,:]",
)
def bvfinal(
    idnx,
    idny,
    idnz,
    iddx,
    iddy,
    iddz,
    nel1,
    nel2,
    nel3,
    nq1,
    nq2,
    nq3,
    p1,
    p2,
    p3,
    d1,
    d2,
    d3,
    b1value,
    b2value,
    b3value,
    uvalue,
    bn1,
    bn2,
    bn3,
    bd1,
    bd2,
    bd3,
    temp_final_1,
    temp_final_2,
    temp_final_3,
):
    temp_final_1[:, :, :] = 0.0
    temp_final_2[:, :, :] = 0.0
    temp_final_3[:, :, :] = 0.0
    # ======================================================================================
    # -- removed omp: #$ omp parallel
    # -- removed omp: #$ omp do reduction ( + : temp_final_1) private (ie1, ie2, ie3, q1, q2, q3, il1, il2, il3, value)
    for ie1 in range(nel1):
        for ie2 in range(nel2):
            for ie3 in range(nel3):
                for il1 in range(p1 + 1):
                    for il2 in range(d2 + 1):
                        for il3 in range(d3 + 1):
                            value = 0.0
                            for q1 in range(nq1):
                                for q2 in range(nq2):
                                    for q3 in range(nq3):
                                        value += (
                                            b1value[ie1, ie2, ie3, q1, q2, q3]
                                            * bn1[ie1, il1, 0, q1]
                                            * bd2[ie2, il2, 0, q2]
                                            * bd3[ie3, il3, 0, q3]
                                        )

                            temp_final_1[idnx[ie1, il1], iddy[ie2, il2], iddz[ie3, il3]] += value

    # -- removed omp: #$ omp end do
    # -- removed omp: #$ omp end parallel

    # -- removed omp: #$ omp parallel
    # -- removed omp: #$ omp do reduction ( + : temp_final_2) private (ie1, ie2, ie3, q1, q2, q3, il1, il2, il3, value)

    for ie1 in range(nel1):
        for ie2 in range(nel2):
            for ie3 in range(nel3):
                for il1 in range(d1 + 1):
                    for il2 in range(p2 + 1):
                        for il3 in range(d3 + 1):
                            value = 0.0
                            for q1 in range(nq1):
                                for q2 in range(nq2):
                                    for q3 in range(nq3):
                                        value += (
                                            b2value[ie1, ie2, ie3, q1, q2, q3]
                                            * bd1[ie1, il1, 0, q1]
                                            * bn2[ie2, il2, 0, q2]
                                            * bd3[ie3, il3, 0, q3]
                                        )

                            temp_final_2[iddx[ie1, il1], idny[ie2, il2], iddz[ie3, il3]] += value

    # -- removed omp: #$ omp end do
    # -- removed omp: #$ omp end parallel

    # -- removed omp: #$ omp parallel
    # -- removed omp: #$ omp do reduction ( + : temp_final_3) private (ie1, ie2, ie3, q1, q2, q3, il1, il2, il3, value)
    for ie1 in range(nel1):
        for ie2 in range(nel2):
            for ie3 in range(nel3):
                for il1 in range(d1 + 1):
                    for il2 in range(d2 + 1):
                        for il3 in range(p3 + 1):
                            value = 0.0
                            for q1 in range(nq1):
                                for q2 in range(nq2):
                                    for q3 in range(nq3):
                                        value += (
                                            b3value[ie1, ie2, ie3, q1, q2, q3]
                                            * bd1[ie1, il1, 0, q1]
                                            * bd2[ie2, il2, 0, q2]
                                            * bn3[ie3, il3, 0, q3]
                                        )

                            temp_final_3[iddx[ie1, il1], iddy[ie2, il2], idnz[ie3, il3]] += value

    # -- removed omp: #$ omp end do
    # -- removed omp: #$ omp end parallel

    ierr = 0
