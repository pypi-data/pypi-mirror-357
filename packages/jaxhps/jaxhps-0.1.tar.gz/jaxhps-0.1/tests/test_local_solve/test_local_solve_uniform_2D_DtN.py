import numpy as np
import jax.numpy as jnp
import jax
import logging
from jaxhps.local_solve._uniform_2D_DtN import (
    local_solve_stage_uniform_2D_DtN,
    _gather_coeffs_2D,
    assemble_diff_operator,
    get_DtN,
)
from jaxhps._precompute_operators_2D import precompute_diff_operators_2D
from jaxhps._discretization_tree import DiscretizationNode2D
from jaxhps._domain import Domain
from jaxhps._pdeproblem import PDEProblem


class Test_gather_coeffs_2D:
    def test_0(self) -> None:
        """Tests things return correct shape."""
        n_leaf_nodes = 30
        p_squared = 17

        xx_coeffs = np.random.normal(size=(n_leaf_nodes, p_squared))
        yy_coeffs = np.random.normal(size=(n_leaf_nodes, p_squared))

        out_coeffs, out_bools = _gather_coeffs_2D(
            D_xx_coeffs=xx_coeffs, D_yy_coeffs=yy_coeffs
        )
        assert out_coeffs.shape == (2, n_leaf_nodes, p_squared)
        assert out_bools.shape == (6,)
        assert out_bools[0].item() is True
        assert out_bools[1].item() is False
        assert out_bools[2].item() is True
        assert out_bools[3].item() is False
        assert out_bools[4].item() is False
        assert out_bools[5].item() is False

    def test_2(self) -> None:
        """Tests things return correct shape."""
        n_leaf_nodes = 30
        p_squared = 17

        xx_coeffs = np.ones((n_leaf_nodes, p_squared))
        yy_coeffs = np.zeros((n_leaf_nodes, p_squared))

        out_coeffs, out_bools = _gather_coeffs_2D(
            D_xx_coeffs=xx_coeffs, D_yy_coeffs=yy_coeffs
        )
        assert jnp.all(out_coeffs[0] == 1)
        assert jnp.all(out_coeffs[1] == 0)
        jax.clear_caches()


class Test_assemble_diff_operator:
    def test_0(self) -> None:
        p = 8
        half_side_len = 0.25

        d_x, d_y, d_xx, d_yy, d_xy = precompute_diff_operators_2D(
            p, half_side_len
        )

        stacked_diff_operators = jnp.stack(
            [d_xx, d_xy, d_yy, d_x, d_y, jnp.eye(p**2)]
        )
        coeffs_arr = jnp.ones((3, p**2))
        which_coeffs = jnp.array([True, True, True, False, False, False])
        out = assemble_diff_operator(
            coeffs_arr, which_coeffs, stacked_diff_operators
        )
        assert out.shape == (p**2, p**2)
        jax.clear_caches()


class Test__local_solve_stage_2D:
    def test_0(self, caplog) -> None:
        """Tests the solve_stage function returns without error and returns the correct shape
        when boundary data are not passed to the function.
        """
        caplog.set_level(logging.DEBUG)
        p = 8
        q = 6
        l = 2
        n_leaves = 4**l

        root = DiscretizationNode2D(xmin=0.0, xmax=1.0, ymin=0.0, ymax=1.0)
        domain = Domain(p=p, q=q, root=root, L=l)

        # This could be np.random.normal(size=(n_leaves, p**2))
        d_xx_coeffs = jnp.array(np.random.normal(size=(n_leaves, p**2)))
        d_yy_coeffs = jnp.array(np.random.normal(size=(n_leaves, p**2)))
        source_term = jnp.array(np.random.normal(size=(n_leaves, p**2)))

        t = PDEProblem(
            domain=domain,
            source=source_term,
            D_xx_coefficients=d_xx_coeffs,
            D_yy_coefficients=d_yy_coeffs,
        )

        print("test_0: n_leaves = ", n_leaves)
        print("test_0: n_gauss_bdry = ", 4 * q)

        (
            Y_arr,
            T_arr,
            v_arr,
            h_arr,
        ) = local_solve_stage_uniform_2D_DtN(pde_problem=t)

        assert Y_arr.shape == (n_leaves, p**2, 4 * q)
        assert T_arr.shape == (n_leaves, 4 * q, 4 * q)
        assert v_arr.shape == (n_leaves, p**2)
        assert h_arr.shape == (n_leaves, 4 * q)
        jax.clear_caches()


class Test_get_DtN:
    def test_0(self) -> None:
        """Asserts that the get_DtN function returns without error and returns the correct shape."""
        p = 16
        q = 14
        n_cheby_bdry = 4 * (p - 1)
        n_src = 3

        diff_operator = np.random.normal(size=(p**2, p**2)).astype(np.float64)
        I_P = np.random.normal(size=(n_cheby_bdry, 4 * q)).astype(np.float64)
        Q_D = np.random.normal(size=(4 * q, p**2)).astype(np.float64)
        source_term = np.random.normal(size=(p**2, n_src)).astype(np.float64)

        Y, DtN, v, v_prime = get_DtN(
            source_term=source_term,
            diff_operator=diff_operator,
            Q=Q_D,
            P=I_P,
        )

        assert Y.shape == (p**2, 4 * q)
        assert DtN.shape == (4 * q, 4 * q)
        assert v.shape == (p**2, n_src)
        assert v_prime.shape == (4 * q, n_src)
        jax.clear_caches()
