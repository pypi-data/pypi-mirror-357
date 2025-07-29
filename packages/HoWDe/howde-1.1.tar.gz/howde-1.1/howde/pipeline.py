import itertools
import pyspark.sql.functions as F

from .utils import (
    validate_input_columns,
    check_and_convert,
)

from .core import (
    get_hourly_trajectories,
    find_home,
    find_work,
    get_stop_level,
    get_change_level,
    pre_process_stops,
)

from .config import default_config, REQUIRED_COLUMNS, REQUIRED_COLUMNS_WITH_TZ


def HoWDe_compute(df_stops, config, output_format="stop"):
    """
    Core pipeline: Detect home and work locations and format output.

    Parameters
    ----------
    df_stops : pyspark.sql.DataFrame
        Preprocessed stop-level input data.
    config : dict
        Configuration with detection parameters.
    output_format : str, default="stop"
        Can be "stop" (detailed, same as stops) or "change" (compact, one row per day with home/work loc change).

    Returns
    -------
    pyspark.sql.DataFrame
        Labelled stops with home/work assignments.
    """
    df_traj = get_hourly_trajectories(df_stops, config)
    df_traj = find_home(df_traj, config)
    df_labeled = find_work(df_traj, config)

    if output_format == "stop":
        return get_stop_level(df_stops, df_labeled)
    elif output_format == "change":
        return get_change_level(df_labeled)
    else:
        raise ValueError(
            f"Unknown output_format: {output_format} (only stop or change allowed)"
        )


def HoWDe_labelling(
    input_data,
    edit_config_default=None,
    range_window_home=28,
    range_window_work=42,
    dhn=3,
    dn_H=0.7,
    dn_W=0.5,
    hf_H=0.7,
    hf_W=0.4,
    df_W=0.6,
    output_format="stop",
    verbose=False,
):
    """
    Run the full HoWDe labelling pipeline over one or multiple parameter configurations.
    
    This function detects home and work locations based on patterns in stop data.
    Users can specify a single parameter configuration or provide lists of values to 
    run multiple configurations in parallel.
    
    Parameters
    ----------
    input_data : pyspark.sql.DataFrame
        Input dataset containing stop information with the following columns:
            - useruuid (str or int): unique user identifier
            - loc (str or int): stop location ID (unique by useruuid). Avoid using "-1" as location labels, as these will be dropped.
            - start (long): Unix timestamp indicating the start of the stop
            - end (long): Unix timestamp indicating the end of the stop
            - tz_hour_start, tz_minute_start (optional): timezone offsets for local time
            - country (optional): country code; if not provided, 'GL0B' will be used
            
    edit_config_default : dict, optional
        Dictionary to override default preprocessing and detection configurations 
        (e.g., stop duration thresholds, valid hours for home/work detection).

    range_window_home : float or list, default=28
        Size of the sliding window (in days) used to detect home locations. Can be a list to test multiple values.

    range_window_work : float or list, default=42
        Size of the sliding window (in days) used to detect work locations. Can be a list.

    dhn : float or list, default=3
        Minimum number of night-/work-hour bins required in a day for that day to be considered valid.

    dn_H : float or list, default=0.7
        Maximum fraction of missing days allowed in the home detection window.

    dn_W : float or list, default=0.5
        Maximum fraction of missing days allowed in the work detection window.

    hf_H : float or list, default=0.7
        Minimum average fraction of night-hour bins per day for a location to qualify as ‘Home’.

    hf_W : float or list, default=0.4
        Minimum average fraction of work-hour bins per day for a location to qualify as ‘Work’.

    df_W : float or list, default=0.6
        Minimum fraction of days within the work detection window that a location must be visited to qualify as ‘Work’.

    output_format : str, default="stop"
        Format of the output:
            - "stop": stop-level data with inferred home/work labels
            - "change": compact format with one row per day per user, indicating changes in home/work locations

    verbose : bool, default=False
        If True, prints processing status and configuration details.

    Returns
    -------
    pyspark.sql.DataFrame or list of dict
        If a single configuration is specified, returns a PySpark DataFrame with labeled stops.
        If multiple configurations are explored, returns a list of dicts:
            - 'configs': the parameter settings used
            - 'res': the resulting labeled DataFrame for each configuration

    Notes
    -----
    (*) Parameters that accept a list will trigger multiple detection runs, one per configuration.

    """

    # 1. Load config
    config = default_config()
    if edit_config_default is not None:
        config.update(edit_config_default)

    # 2. Validate input data
    REQUIRED_COLUMNS = ["useruuid", "loc", "start", "end"]
    REQUIRED_COLUMNS_WITH_TZ = REQUIRED_COLUMNS + ["tz_hour_start", "tz_minute_start"]
    required_cols = (
        REQUIRED_COLUMNS_WITH_TZ if not config["is_time_local"] else REQUIRED_COLUMNS
    )
    validate_input_columns(input_data, required_cols, label="stop data")

    # 3. Validate selected output format
    if output_format not in {"stop", "change"}:
        raise ValueError(
            f"Invalid output_format: {output_format}. Must be 'stop' or 'change'."
        )

    # 4. Convert parameters to lists
    (
        dhn,
        dn_H,
        dn_W,
        range_window_home,
        range_window_work,
        hf_H,
        hf_W,
        df_W,
    ) = check_and_convert(
        [
            dhn,
            dn_H,
            dn_W,
            range_window_home,
            range_window_work,
            hf_H,
            hf_W,
            df_W,
        ]
    )

    # 5. Pre-process stops
    df_stops = pre_process_stops(input_data, config)
    df_stops = df_stops.cache()
    
    if verbose:
        print("[HowDe] Stops pre-processed")

    # 6. Loop over parameter combinations
    output = []
    param_grid = itertools.product(
        range_window_home,
        range_window_work,
        dhn,
        dn_H,
        hf_H,
        dn_W,
        hf_W,
        df_W,
    )

    for rW_H, rW_W, noneD, noneH, freqH, noneW, freqWh, freqWd in param_grid:
        config_ = config.copy()
        config_.update(
            {
                "range_window_home": rW_H,
                "range_window_work": rW_W,
                "dhn": F.lit(noneD),
                "dn_H": F.lit(noneH),
                "hf_H": F.lit(freqH),
                "dn_W": F.lit(noneW),
                "hf_W": F.lit(freqWh),
                "df_W": F.lit(freqWd),
            }
        )

        if verbose:
            print(
                f"[HoWDe] Running config: "
                f"rw_H={rW_H}, rw_W={rW_W}, dn_H={noneH}, hf_H={freqH}, "
                f"dn_W={noneW}, hf_W={freqWh}, df_W={freqWd}"
            )

        df_labeled = HoWDe_compute(df_stops, config_, output_format=output_format)
        output.append({"configs": config_, "res": df_labeled})

    if verbose:
        print("[HoWDe] All computations registered (lazy)")

    if len(output) == 1:
        return output[0]["res"]

    return output
