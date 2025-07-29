# -*- coding: utf-8 -*-
"""
Components that require PyWake.

@author: ricriv
"""

# %% Import.


import numpy as np
import xarray as xr
from py_wake.flow_map import Points
from py_wake.utils import gradients
from py_wake.wind_farm_models.engineering_models import (
    All2AllIterative,
    PropagateDownwind,
    PropagateUpDownIterative,
)

from wind_farm_loads.tool_agnostic import (
    SmoothPotFunctions,
    _get_sensor_names,
    _preallocate_ilktn,
    _predict_loads_pod,
    _predict_loads_sector_average,
    rotate_grid,
)

# %% Classes to avoid self wake and self blockage.


class PropagateDownwindNoSelfInduction(PropagateDownwind):
    """Same as `PropagateDownwind`, but the wake, added turbulence and blockage are set to 0 in a sphere that surrounds each rotor.

    The objective of this class is to obtain a flow map that does not measure
    the induction of the current turbine, while keeping the same wind farm power.
    """

    def __init__(self, *args, pot=SmoothPotFunctions.pot_sharp, **kwargs):
        PropagateDownwind.__init__(self, *args, **kwargs)
        self.pot = pot

    def _calc_deficit(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        deficit, blockage = PropagateDownwind._calc_deficit(
            self, dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, np.newaxis, :, np.newaxis])
        deficit = deficit * weight
        if blockage is not None:
            blockage = blockage * weight
        return deficit, blockage

    def _calc_deficit_convection(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        deficit, uc, sigma_sqr = self.wake_deficitModel.calc_deficit_convection(
            dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        deficit, blockage = self._add_blockage(deficit, dw_ijlk, **kwargs)
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, np.newaxis, :, np.newaxis])
        deficit = deficit * weight
        if blockage is not None:
            blockage = blockage * weight
        return deficit, uc, sigma_sqr, blockage

    def _calc_added_turbulence(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        added_ti = self.turbulenceModel.calc_added_turbulence(
            dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, np.newaxis, :, np.newaxis])
        added_ti = added_ti * weight
        return added_ti


class PropagateUpDownIterativeNoSelfInduction(PropagateUpDownIterative):
    """Same as `PropagateUpDownIterative`, but the wake, added turbulence and blockage are set to 0 in a sphere that surrounds each rotor.

    The objective of this class is to obtain a flow map that does not measure
    the induction of the current turbine, while keeping the same wind farm power.
    """

    def __init__(self, *args, pot=SmoothPotFunctions.pot_sharp, **kwargs):
        PropagateUpDownIterative.__init__(self, *args, **kwargs)
        self.pot = pot

    def _calc_deficit(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        deficit, blockage = PropagateUpDownIterative._calc_deficit(
            self, dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, np.newaxis, :, np.newaxis])
        deficit = deficit * weight
        if blockage is not None:
            blockage = blockage * weight

        return deficit, blockage

    def _calc_deficit_convection(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        deficit, uc, sigma_sqr = self.wake_deficitModel.calc_deficit_convection(
            dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        deficit, blockage = self._add_blockage(deficit, dw_ijlk, **kwargs)
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, np.newaxis, :, np.newaxis])
        deficit = deficit * weight
        if blockage is not None:
            blockage = blockage * weight
        return deficit, uc, sigma_sqr, blockage

    def _calc_added_turbulence(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        added_ti = self.turbulenceModel.calc_added_turbulence(
            dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, np.newaxis, :, np.newaxis])
        added_ti = added_ti * weight
        return added_ti


class All2AllIterativeNoSelfInduction(All2AllIterative):
    """Same as `All2AllIterative`, but the wake, added turbulence and blockage are set to 0 in a sphere that surrounds each rotor.

    The objective of this class is to obtain a flow map that does not measure
    the induction of the current turbine, while keeping the same wind farm power.
    """

    def __init__(self, *args, pot=SmoothPotFunctions.pot_sharp, **kwargs):
        All2AllIterative.__init__(self, *args, **kwargs)
        self.pot = pot

    def _calc_deficit(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        deficit, blockage = All2AllIterative._calc_deficit(
            self, dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, np.newaxis, :, np.newaxis])
        deficit = deficit * weight
        if blockage is not None:
            blockage = blockage * weight
        return deficit, blockage

    def _calc_deficit_convection(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        deficit, uc, sigma_sqr = self.wake_deficitModel.calc_deficit_convection(
            dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        deficit, blockage = self._add_blockage(deficit, dw_ijlk, **kwargs)
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, np.newaxis, :, np.newaxis])
        deficit = deficit * weight
        if blockage is not None:
            blockage = blockage * weight
        return deficit, uc, sigma_sqr, blockage

    def _calc_added_turbulence(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        added_ti = self.turbulenceModel.calc_added_turbulence(
            dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, np.newaxis, :, np.newaxis])
        added_ti = added_ti * weight
        return added_ti


# %% Functions to extract the inflow.


def _arg2ilk(v, I, L, K=None):
    """
    Convert a variable to shape `(I, L, K)` or `(I, L)` if `K` is not provided.

    Similar to `py_wake.utils.functions.arg2ilk`, with the difference that
    the variable is broadcasted to the specified shape and that a 2D output is allowed.
    The variable may be:

        - Constant.
        - Dependent on wind turbine `(I)`.
        - Dependent on wind turbine and wind direction or wind turbine and time `(IL)`.
        - Dependent on wind turbine, wind direction and wind speed `(ILK)`.


    Parameters
    ----------
    v : float, array_like
        Input variable that needs to be converted to `(I, L, K)` or `(I, L)` shape.
    I : int
        Number of turbines.
    L : int
        Number of wind directions or time.
    K : int, optional
        Number of wind speeds. When provided, `L` is the wind direction. The default is `None` which means that `L` is time.

    Returns
    -------
    r : (I, L, K) or (I, L) ndarray
        Input variable converted to `(I, L, K)` shape.

    """
    # Adapted from py_wake.utils.functions.arg2ilk
    if v is None:
        return v
    v_ = np.asarray(v)
    if v_.shape == ():
        #       wt          time                             wt          wd          ws
        v_ = v_[np.newaxis, np.newaxis] if K is None else v_[np.newaxis, np.newaxis, np.newaxis]  # fmt: skip

    elif v.shape in [(I,), (1,)]:
        #       wt time                             wt wd          ws
        v_ = v_[:, np.newaxis] if K is None else v_[:, np.newaxis, np.newaxis]

    elif v.shape in [(I, L), (1, L), (I, 1), (1, 1)]:
        #                            wt wd ws
        v_ = v_ if K is None else v_[:, :, np.newaxis]

    elif v.shape in {
        (I, L, K),
        (1, L, K),
        (I, 1, K),
        (I, L, 1),
        (1, 1, K),
        (1, L, 1),
        (I, 1, 1),
        (1, 1, 1),
    }:
        pass

    elif v.shape == (L,):
        #       wt          time                    wt          wd ws
        v_ = v_[np.newaxis, :] if K is None else v_[np.newaxis, :, np.newaxis]

    elif v.shape in [(L, K), (L, 1), (1, K)]:
        #       wt          time                    wt          wd ws
        v_ = v_[np.newaxis, :] if K is None else v_[np.newaxis, :, :]

    elif v.shape == (K,):
        #       wt          wd or time
        v_ = v_[np.newaxis, np.newaxis]

    else:
        valid_shapes = f"(), ({I}), ({I},{L}), ({I},{L},{K}), ({L},), ({L}, {K})"
        raise ValueError(
            f"Argument has shape {v.shape}, which is not supported. Valid shapes are {valid_shapes} (interpreted in this order)"
        )

    if K is None:
        return np.broadcast_to(v_, (I, L))
    else:
        return np.broadcast_to(v_, (I, L, K))


def get_rotor_averaged_wind_speed(sim_res):
    """
    Get rotor-averaged wind speed.

    Parameters
    ----------
    sim_res : py_wake SimulationResult
        A simulation result from PyWake. Must follow a call to the wind farm model.

    Returns
    -------
    WS_eff : xarray DataArray
        Effective wind speed as a function of: ambient wind speed, ambient wind direction, turbine number and type.

    """
    return sim_res["WS_eff"]


def get_rotor_averaged_turbulence_intensity(sim_res):
    """
    Get rotor-averaged turbulence intensity.

    Parameters
    ----------
    sim_res : py_wake SimulationResult
        A simulation result from PyWake. Must follow a call to the wind farm model.

    Returns
    -------
    TI_eff : xarray DataArray
        Effective turbulence intensity as a function of: ambient wind speed, ambient wind direction, turbine number and type.

    """
    return sim_res["TI_eff"]


def compute_flow_map(
    sim_res,
    x_grid,
    y_grid,
    z_grid,
    align_in_yaw=True,
    align_in_tilt=True,
    axial_wind=False,
    wt=None,
    wd=None,
    ws=None,
    time=None,
    dtype=np.float32,
    save_grid=False,
):
    r"""
    Compute the effective wind speed and Turbulence Intensity over a rotor.

    This function receives a grid, and then rotates it by the wind direction. Optionally,
    the grid is also rotated by the yaw and tilt of each turbine to align it with the rotor plane.
    Finally, the grid is translated to each rotor center and the flow map is computed.

    Parameters
    ----------
    sim_res : py_wake SimulationResult
        Simulation result computed by PyWake. Must follow a call to the wind farm model.
    x_grid : (N, M) or (N, M, Type) ndarray
        x coordinate (downwind) of the grid points, before rotation by yaw and tilt. Should be 0.
        Typically generated by `make_rectangular_grid` or `make_polar_grid`.
        The first 2 dimensions cover the rotor, while the last is over the turbine types.
        If the user passes a 2D array, the grid is assumed to be the same for all turbine types.
    y_grid : (N, M) or (N, M, Type) ndarray
        List of y coordinate (crosswind) of the grid points, before rotation by yaw and tilt.
        Typically generated by `make_rectangular_grid` or `make_polar_grid`.
        If the user passes a 2D array, the grid is assumed to be the same for all turbine types.
    z_grid : (N, M) or (N, M, Type) ndarray
        List of z coordinate (up) of the grid points, before rotation by yaw and tilt.
        Typically generated by `make_rectangular_grid` or `make_polar_grid`.
        If the user passes a 2D array, the grid is assumed to be the same for all turbine types.
    align_in_yaw : bool, optional
        If `True` (default) the grid is aligned in yaw with the rotor plane.
    align_in_tilt : bool, optional
        If `True` (default) the grid is aligned in tilt with the rotor plane.
    axial_wind : bool, optional
        If `True` the axial wind speed and TI are returned. That is, the downstream wind speed computed by PyWake
        is multiplied by :math:`\cos(\mathrm{yaw}) \cos(\mathrm{tilt})`. The default is `False`.
    wt : int, (I) array_like, optional
        Wind turbines. Must be a subset of the one contained in `sim_res`.
        The default is `None`, which means to use all available wind turbines.
    wd : float, (L) array_like, optional
        Wind direction, in deg. Must be a subset of the one contained in `sim_res`.
        The default is `None`, which means to use all available wind directions.
    ws : float, (K) array_like, optional
        Wind speed. Must be a subset of the one contained in `sim_res`.
        The default is `None`, which means to use all available wind speeds.
    time : float, (Time) array_like, optional
        Time. Must be a subset of the one contained in `sim_res`.
        The default is `None`, which means to use all available time instants.
    dtype : data-type, optional
        The desired data-type for the result. The default is single precision,
        which should be enough for all outputs. The properties of each type can
        be checked with `np.finfo(np.float32(1.0))`.
    save_grid : bool, optional
        If `True` the grid will be saved for all inflow conditions. Since this comes at a significant
        memory cost, it is recommended to switch it on only for debug purposes.
        The default is `False`.

    Returns
    -------
    flow_map : xarray DataSet
        Effective wind speed, effective turbulence intensity and corresponding grid points
        for each turbine and flow case.

    """
    # Get the number of turbine types.
    n_types = len(sim_res.windFarmModel.windTurbines._names)

    # The grid must be a numpy array with 3 dimensions.
    # The first 2 cover the rotor, while the last is over the types.
    # This implies that all turbine types must have the same number of grid points.
    # If the user passes a 2D array, the grid is assumed to be the same for all types.
    if x_grid.ndim == 2 and y_grid.ndim == 2 and z_grid.ndim == 2:
        x_grid_t = np.broadcast_to(
            x_grid[:, :, np.newaxis], (x_grid.shape[0], x_grid.shape[1], n_types)
        )
        y_grid_t = np.broadcast_to(
            y_grid[:, :, np.newaxis], (y_grid.shape[0], y_grid.shape[1], n_types)
        )
        z_grid_t = np.broadcast_to(
            z_grid[:, :, np.newaxis], (z_grid.shape[0], z_grid.shape[1], n_types)
        )

    elif x_grid.ndim == 3 and y_grid.ndim == 3 and z_grid.ndim == 3:
        x_grid_t = x_grid
        y_grid_t = y_grid
        z_grid_t = z_grid
        # Check that there is 1 grid per turbine type.
        if x_grid_t.shape[2] != n_types:
            raise ValueError(
                f"{x_grid_t.shape[2]} grid types provided, but {n_types} were expected."
            )
    else:
        raise ValueError("The grid must be a 2D or 3D array.")

    # The default value of wt, wd, ws and time is the one in sim_res.
    wt_ = sim_res["wt"].values if wt is None else np.atleast_1d(wt)
    wd_ = sim_res["wd"].values if wd is None else np.atleast_1d(wd)
    ws_ = sim_res["ws"].values if ws is None else np.atleast_1d(ws)
    if "time" in sim_res.dims:
        time_ = sim_res["time"].values if time is None else np.atleast_1d(time)

    # Convert yaw and tilt to arrays.
    # If time is not present the result has shape (I, L, K), i.e. (turbines, wind directions, wind speeds).
    # Instead, if time is present, the result has shape (I, Time), i.e. (turbines, time).
    # These arrays are contained in sim_res, therefore all turbines, directions and speeds and times must be used.
    I = sim_res.sizes["wt"]
    if "time" in sim_res.dims:
        Time = sim_res.sizes["time"]
        if align_in_yaw:
            yaw_turbines_ = _arg2ilk(sim_res["yaw"].values, I, Time)
        else:
            yaw_turbines_ = _arg2ilk(0.0, I, Time)
        if align_in_tilt:
            tilt_turbines_ = _arg2ilk(sim_res["tilt"].values, I, Time)
        else:
            tilt_turbines_ = _arg2ilk(0.0, I, Time)
    else:
        L = sim_res.sizes["wd"]
        K = sim_res.sizes["ws"]
        if align_in_yaw:
            yaw_turbines_ = _arg2ilk(sim_res["yaw"].values, I, L, K)
        else:
            yaw_turbines_ = _arg2ilk(0.0, I, L, K)
        if align_in_tilt:
            tilt_turbines_ = _arg2ilk(sim_res["tilt"].values, I, L, K)
        else:
            tilt_turbines_ = _arg2ilk(0.0, I, L, K)

    # Conveniently access turbine position.
    x_turbines_ = sim_res["x"].values
    y_turbines_ = sim_res["y"].values
    z_turbines_ = np.atleast_1d(sim_res["h"].values)

    # Preallocate DataSet for effective wind speed, turbulence intensity and grid points.
    # In the flow map computed by PyWake the order of dimensions is: points (1D), wd, ws, or points (1D), time.
    # In the flow map returned by this function wt, wd and ws, or time, are placed first, followed by the quantity and grid dimensions.
    # This order enables vectorization in predict_loads_pod().
    # Each turbine type is allowed to have a different grid, but all grids must have the same number of points.
    # The grid dimensions are labeled q0 and q1 because they might either be y and z or radius and azimuth.
    xr_dict = {}
    if "time" in sim_res.dims:
        # Set the independent coordinates: turbine, time and quantity.
        coords_flow = {
            "wt": wt_,
            "time": time_,
            "quantity": ["WS_eff", "TI_eff"],
        }
        dims_flow = list(coords_flow) + ["q0", "q1"]
        # Set the dependent coordinates: wind direction and wind speed.
        time_index = np.searchsorted(sim_res["time"].values, time_)
        coords_flow["wd"] = (["time"], wd_[time_index])
        coords_flow["ws"] = (["time"], ws_[time_index])

        xr_dict["flow"] = xr.DataArray(
            data=np.full(
                (
                    wt_.size,
                    time_.size,
                    2,  # Effective wind speed and TI.
                    x_grid_t.shape[0],
                    x_grid_t.shape[1],
                ),
                np.nan,
                dtype=dtype,
            ),
            coords=coords_flow,
            dims=dims_flow,
        )

        if save_grid:
            xr_dict["grid"] = xr.DataArray(
                data=np.full(
                    (
                        wt_.size,
                        time_.size,
                        3,  # x, y, z
                        x_grid_t.shape[0],
                        x_grid_t.shape[1],
                    ),
                    np.nan,
                    dtype=dtype,
                ),
                coords={
                    "wt": wt_,
                    "time": time_,
                    "axis": ["x", "y", "z"],
                },
                dims=["wt", "time", "axis", "q0", "q1"],
            )

    else:  # "time" not in sim_res.dims
        xr_dict["flow"] = xr.DataArray(
            data=np.full(
                (
                    wt_.size,
                    wd_.size,
                    ws_.size,
                    2,  # Effective wind speed and TI.
                    x_grid_t.shape[0],
                    x_grid_t.shape[1],
                ),
                np.nan,
                dtype=dtype,
            ),
            coords={
                "wt": wt_,
                "wd": wd_,
                "ws": ws_,
                "quantity": ["WS_eff", "TI_eff"],
            },
            dims=["wt", "wd", "ws", "quantity", "q0", "q1"],
        )

        if save_grid:
            xr_dict["grid"] = xr.DataArray(
                data=np.full(
                    (
                        wt_.size,
                        wd_.size,
                        ws_.size,
                        3,  # x, y, z
                        x_grid_t.shape[0],
                        x_grid_t.shape[1],
                    ),
                    np.nan,
                    dtype=dtype,
                ),
                coords={
                    "wt": wt_,
                    "wd": wd_,
                    "ws": ws_,
                    "axis": ["x", "y", "z"],
                },
                dims=["wt", "wd", "ws", "axis", "q0", "q1"],
            )
    ds = xr.Dataset(xr_dict)

    # Convert all angles from deg to rad.
    wd_rad = np.deg2rad(wd_)
    yaw_turbines_ = np.deg2rad(yaw_turbines_)
    tilt_turbines_ = np.deg2rad(tilt_turbines_)

    cos_yaw_cos_tilt = np.cos(yaw_turbines_) * np.cos(tilt_turbines_)

    angle_ref = np.deg2rad(90.0)

    if "time" in sim_res.dims:
        # Loop over the turbines.
        for i in wt_:
            # Get type of current turbine.
            i_type = int(sim_res["type"][i])
            # Loop over time.
            for t in range(time_.size):
                # Convert grid from downwind-crosswind-z to east-north-z.
                # While doing that, also rotate by yaw and tilt.
                # This can be done because the order of rotations is first yaw and then tilt.
                # It will NOT work for a floating turbine.
                # We rely on this function to create new arrays, so that the following
                # translation will not affect the original ones.
                # The formula for the yaw is taken from py_wake.wind_turbines._wind_turbines.WindTurbines.plot_xy()
                x_grid_, y_grid_, z_grid_ = rotate_grid(
                    x_grid_t[:, :, i_type],
                    y_grid_t[:, :, i_type],
                    z_grid_t[:, :, i_type],
                    yaw=angle_ref - wd_rad[t] + yaw_turbines_[i, t],  # [rad]
                    tilt=-tilt_turbines_[i, t],  # [rad]
                    degrees=False,
                )
                # Move grid to rotor center. The turbine position is in east-north-z coordinates.
                x_grid_ += x_turbines_[i]
                y_grid_ += y_turbines_[i]
                z_grid_ += z_turbines_[i]
                it = {"wt": wt_[i], "time": time_[t]}
                if save_grid:
                    ds["grid"].loc[{**it, "axis": "x"}] = x_grid_
                    ds["grid"].loc[{**it, "axis": "y"}] = y_grid_
                    ds["grid"].loc[{**it, "axis": "z"}] = z_grid_
                # Compute flow map.
                flow_map = sim_res.flow_map(
                    grid=Points(x_grid_.ravel(), y_grid_.ravel(), z_grid_.ravel()),
                    time=[time_[t]],
                )
                ds["flow"].loc[{**it, "quantity": "WS_eff"}] = flow_map[
                    "WS_eff"
                ].values.reshape(x_grid_.shape)
                ds["flow"].loc[{**it, "quantity": "TI_eff"}] = flow_map[
                    "TI_eff"
                ].values.reshape(x_grid_.shape)

        # Project wind speed.
        if axial_wind:
            ds["flow"] *= cos_yaw_cos_tilt[:, :, np.newaxis, np.newaxis, np.newaxis]

    else:  # "time" not in sim_res.dims
        # Loop over the turbines.
        for i in wt_:
            # Get type of current turbine.
            i_type = int(sim_res["type"][i])
            # Loop over wind directions.
            for l in range(wd_.size):
                # Loop over wind speeds.
                for k in range(ws_.size):
                    # Convert grid from downwind-crosswind-z to east-north-z.
                    # While doing that, also rotate by yaw and tilt.
                    # This can be done because the order of rotations is first yaw and then tilt.
                    # It will NOT work for a floating turbine.
                    # We rely on this function to create new arrays, so that the following
                    # translation will not affect the original ones.
                    # The formula for the yaw is taken from py_wake.wind_turbines._wind_turbines.WindTurbines.plot_xy()
                    x_grid_, y_grid_, z_grid_ = rotate_grid(
                        x_grid_t[:, :, i_type],
                        y_grid_t[:, :, i_type],
                        z_grid_t[:, :, i_type],
                        yaw=angle_ref - wd_rad[l] + yaw_turbines_[i, l, k],  # [rad]
                        tilt=-tilt_turbines_[i, l, k],  # [rad]
                        degrees=False,
                    )
                    # Move grid to rotor center. The turbine position is in east-north-z coordinates.
                    x_grid_ += x_turbines_[i]
                    y_grid_ += y_turbines_[i]
                    z_grid_ += z_turbines_[i]
                    ilk = {"wt": wt_[i], "wd": wd_[l], "ws": ws_[k]}
                    if save_grid:
                        ds["grid"].loc[{**ilk, "axis": "x"}] = x_grid_
                        ds["grid"].loc[{**ilk, "axis": "y"}] = y_grid_
                        ds["grid"].loc[{**ilk, "axis": "z"}] = z_grid_
                    # Compute flow map.
                    flow_map = sim_res.flow_map(
                        grid=Points(x_grid_.ravel(), y_grid_.ravel(), z_grid_.ravel()),
                        wd=wd_[l],
                        ws=ws_[k],
                    )
                    ds["flow"].loc[{**ilk, "quantity": "WS_eff"}] = flow_map[
                        "WS_eff"
                    ].values.reshape(x_grid_.shape)
                    ds["flow"].loc[{**ilk, "quantity": "TI_eff"}] = flow_map[
                        "TI_eff"
                    ].values.reshape(x_grid_.shape)

        # Project wind speed.
        if axial_wind:
            ds["flow"] *= cos_yaw_cos_tilt[:, :, :, np.newaxis, np.newaxis, np.newaxis]

    return ds


# %% Functions to evaluate the loads.


def predict_loads_rotor_average(
    surrogates, sim_res, *additional_inputs, dtype=np.float32, ti_in_percent=True
):
    r"""
    Evaluate the load surrogate models based on rotor-averaged wind speed and turbulence intensity. Additional (control) inputs are supported as well.

    Each load surrogate is evaluated as

    .. math::
      y = f(\mathrm{WS}, \mathrm{TI}, \boldsymbol{\theta})

    where :math:`\mathrm{WS}` is the rotor-averaged wind speed, :math:`\mathrm{TI}` is the rotor-averaged turbulence intensity and
    :math:`\boldsymbol{\theta}` are the additional inputs (typically, control parameters). The surrogates are evaluated
    for all turbines and ambient inflow conditions.

    The load database has been described in
    `Guilloré, A., Campagnolo, F. & Bottasso, C. L. (2024). A control-oriented load surrogate model based on sector-averaged inflow quantities: capturing damage for unwaked, waked, wake-steering and curtailed wind turbines <https://doi.org/10.1088/1742-6596/2767/3/032019>`_
    where it was proposed to include the controller set point by adding the yaw, pitch and rotor speed.
    This function has been developed using the surrogate models trained by Hari, which are based on the database provided by TUM.

    Parameters
    ----------
    surrogates : dict of surrogates_interface.surrogates.SurrogateModel
        Dictionary containing surrogate models. The keys will be used as sensor names.
    sim_res : py_wake SimulationResult
        Simulation result computed by PyWake. Must follow a call to the wind farm model.
    additional_inputs : list of ndarray
        Additional inputs to evaluate the load surrogate models.
        Must be coherent with the simulation result. PyWake rules are applied to broadcast each additional
        input to shape `(wt, wd, ws)` or `(wt, time)`. Typical additional inputs are:

            - Yaw, pitch and rotor speed.
            - Yaw and curtailment level.

        It is the user responsibility to pass the inputs in the order required by the surrogates, and to use the correct units.
    dtype : data-type, optional
        The desired data-type for the result. The default is single precision,
        which should be enough for all outputs. The properties of each type can
        be checked with `np.finfo(np.float32(1.0))`.
    ti_in_percent : bool
        If `True` (default) the turbulence intensity is multiplied by 100 before evaluating the surrogates.

    Returns
    -------
    loads : xarray.DataArray
        Loads for each turbine, ambient inflow condition and sensor.

    """
    # Preallocate a DataArray for the results.
    loads = _preallocate_ilktn(
        wt=sim_res["wt"].values,
        wd=sim_res["wd"].values,
        ws=sim_res["ws"].values,
        time=sim_res["time"].values if "time" in sim_res.dims else None,
        name=_get_sensor_names(surrogates),
        dtype=dtype,
    )

    # Multiply the turbulence intensity by 100?
    if ti_in_percent:
        ti = sim_res["TI_eff"].values.ravel() * 100.0
    else:
        ti = sim_res["TI_eff"].values.ravel()

    # Ensure that the additional inputs have shape [wt, wd, ws] or [wt, time].
    if "time" in sim_res.dims:
        theta = [
            _arg2ilk(th, sim_res["wt"].size, sim_res["time"].size).ravel().astype(dtype)
            for th in additional_inputs
        ]
    else:
        theta = [
            _arg2ilk(
                th,
                sim_res["wt"].size,
                sim_res["wd"].size,
                sim_res["ws"].size,
            )
            .ravel()
            .astype(dtype)
            for th in additional_inputs
        ]

    # Compose input for load surrogate.
    x = np.column_stack(
        (
            sim_res["WS_eff"].values.astype(dtype).ravel(),  # [m/s]
            ti.astype(dtype),
            *theta,
        )
    )

    # Loop over the surrogate models and evaluate them.
    for sensor in surrogates.keys():
        loads.loc[{"name": sensor}] = (
            surrogates[sensor].predict_output(x).reshape(sim_res["WS_eff"].shape)
        )
    return loads


def predict_loads_pod(
    surrogates,
    flow_map,
    *additional_inputs,
    dtype=np.float32,
    ti_in_percent=True,
):
    r"""
    Evaluate the load surrogate models based on Proper Orthogonal Decomposition of wind speed and turbulence intensity. Additional (control) inputs are supported as well.

    Each load surrogate is evaluated as

    .. math::
      y = f(\mathrm{WS}, \mathrm{TI}, \boldsymbol{\theta})

    where :math:`\mathrm{WS}` is the wind speed over the grid used to generated the POD basis, :math:`\mathrm{TI}` is
    the turbulence intensity over the grid used to generated the POD basis and :math:`\boldsymbol{\theta}` are the
    additional inputs (typically, control parameters). The surrogates are evaluated for all turbines and ambient inflow conditions.

    The load database has been described in
    `Guilloré, A., Campagnolo, F. & Bottasso, C. L. (2024). A control-oriented load surrogate model based on sector-averaged inflow quantities: capturing damage for unwaked, waked, wake-steering and curtailed wind turbines <https://doi.org/10.1088/1742-6596/2767/3/032019>`_
    where it was proposed to include the controller set point by adding the yaw, pitch and rotor speed.
    This function has been developed using the surrogate models trained by Hari, which are based on the database provided by TUM.

    Parameters
    ----------
    surrogates : dict of surrogates_interface.surrogates.SurrogateModel
        Dictionary containing surrogate models. The keys will be used as sensor names.
    flow_map : xarray DataSet
        Effective wind speed, effective turbulence intensity and corresponding grid points
        for each turbine and flow case. Generated by `compute_flow_map()`.
    additional_inputs : list of ndarray
        Additional inputs to evaluate the load surrogate models.
        Must be coherent with the flow map. PyWake rules are applied to broadcast each additional
        input to shape `(wt, wd, ws)` or `(wt, time)`. Typical additional inputs are:

            - Yaw, pitch and rotor speed.
            - Yaw and curtailment level.

        It is the user responsibility to pass the inputs in the order required by the surrogates, and to use the correct units.
    dtype : data-type, optional
        The desired data-type for the result. The default is single precision,
        which should be enough for all outputs. The properties of each type can
        be checked with `np.finfo(np.float32(1.0))`.
    ti_in_percent : bool
        If `True` (default) the turbulence intensity is multiplied by 100 before evaluating the surrogates.

    Returns
    -------
    loads : xarray.DataArray
        Loads for each turbine, ambient inflow condition and sensor.

    """
    return _predict_loads_pod(
        surrogates,
        flow_map,
        _arg2ilk,
        *additional_inputs,
        dtype=np.float32,
        ti_in_percent=True,
    )


def predict_loads_sector_average(
    surrogates,
    sector_average,
    *additional_inputs,
    dtype=np.float32,
    ti_in_percent=True,
):
    r"""
    Evaluate the load surrogate models based on sector average of wind speed and turbulence intensity. Additional (control) inputs are supported as well.

    Each load surrogate is evaluated as

    .. math::
      y = f(\mathrm{WS}, \mathrm{TI}, \boldsymbol{\theta})

    where :math:`\mathrm{WS}` is the sector-averaged wind speed, :math:`\mathrm{TI}` is the sector-averaged
    turbulence intensity and :math:`\boldsymbol{\theta}` are the additional inputs (typically, control parameters).
    The surrogates are evaluated for all turbines and ambient inflow conditions.

    The load database has been described in
    `Guilloré, A., Campagnolo, F. & Bottasso, C. L. (2024). A control-oriented load surrogate model based on sector-averaged inflow quantities: capturing damage for unwaked, waked, wake-steering and curtailed wind turbines <https://doi.org/10.1088/1742-6596/2767/3/032019>`_
    where it was proposed to include the controller set point by adding the yaw, pitch and rotor speed.
    This function has been developed using the surrogate models trained by Hari, which are based on the database provided by TUM.

    Parameters
    ----------
    surrogates : dict of surrogates_interface.surrogates.SurrogateModel
        Dictionary containing surrogate models. The keys will be used as sensor names.
    sector_average : xarray DataArray
        Sector average of effective wind speed and effective turbulence intensity
        for each turbine and flow case. Generated by `compute_sector_average()`.
    additional_inputs : list of ndarray
        Additional inputs to evaluate the load surrogate models.
        Must be coherent with the sector average. PyWake rules are applied to broadcast each additional
        input to shape `(wt, wd, ws)` or `(wt, time)`. Typical additional inputs are:

            - Yaw, pitch and rotor speed.
            - Yaw and curtailment level.

        It is the user responsibility to pass the inputs in the order required by the surrogates, and to use the correct units.
    dtype : data-type, optional
        The desired data-type for the result. The default is single precision,
        which should be enough for all outputs. The properties of each type can
        be checked with `np.finfo(np.float32(1.0))`.
    ti_in_percent : bool
        If `True` (default) the turbulence intensity is multiplied by 100 before evaluating the surrogates.

    Returns
    -------
    loads : xarray.DataArray
        Loads for each turbine, ambient inflow condition and sensor.

    """
    return _predict_loads_sector_average(
        surrogates,
        sector_average,
        _arg2ilk,
        *additional_inputs,
        dtype=np.float32,
        ti_in_percent=True,
    )
