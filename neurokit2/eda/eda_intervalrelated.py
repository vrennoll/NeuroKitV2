# -*- coding: utf-8 -*-
from warnings import warn

import numpy as np
import pandas as pd

from ..misc import NeuroKitWarning
from .eda_sympathetic import eda_sympathetic


def eda_intervalrelated(data, sampling_rate=1000):
    """**EDA Analysis on Interval-Related Data**

    Performs EDA analysis on longer periods of data (typically > 10 seconds), such as resting-state data.

    Parameters
    ----------
    data : Union[dict, pd.DataFrame]
        A DataFrame containing the different processed signal(s) as
        different columns, typically generated by :func:`eda_process` or
        :func:`bio_process()`. Can also take a dict containing sets of
        separately processed DataFrames.

    Returns
    -------
    DataFrame
        A dataframe containing the analyzed EDA features. The analyzed
        features consist of the following:
        * ``"SCR_Peaks_N"``: the number of occurrences of Skin Conductance Response (SCR).
        * ``"SCR_Peaks_Amplitude_Mean"``: the mean amplitude of the SCR peak occurrences.
        * ``"EDA_Tonic_SD"``: the mean amplitude of the SCR peak occurrences.
        * ``"EDA_Sympathetic"``: see :func:`eda_sympathetic`.

    See Also
    --------
    .bio_process, eda_eventrelated

    Examples
    ----------
    .. ipython:: python

      import neurokit2 as nk

      # Download data
      data = nk.data("bio_resting_8min_100hz")

      # Process the data
      df, info = nk.eda_process(data["EDA"], sampling_rate=100)

      # Single dataframe is passed
      nk.eda_intervalrelated(df, sampling_rate=100)

      epochs = nk.epochs_create(df, events=[0, 25300], sampling_rate=100, epochs_end=20)
      nk.eda_intervalrelated(epochs, sampling_rate=100)

    """

    # Format input
    if isinstance(data, pd.DataFrame):
        results = _eda_intervalrelated(data, sampling_rate=sampling_rate)
        results = pd.DataFrame.from_dict(results, orient="index").T
    elif isinstance(data, dict):
        results = {}
        for index in data:
            results[index] = {}  # Initialize empty container

            # Add label info
            results[index]["Label"] = data[index]["Label"].iloc[0]

            results[index] = _eda_intervalrelated(
                data[index], results[index], sampling_rate=sampling_rate
            )

        results = pd.DataFrame.from_dict(results, orient="index")

    return results


# =============================================================================
# Internals
# =============================================================================


def _eda_intervalrelated(data, output={}, sampling_rate=1000):
    """Format input for dictionary."""
    # Sanitize input
    colnames = data.columns.values

    # SCR Peaks
    if "SCR_Peaks" not in colnames:
        warn(
            "We couldn't find an `SCR_Peaks` column. Returning NaN for N peaks.",
            category=NeuroKitWarning,
        )
        output["SCR_Peaks_N"] = np.nan
    else:
        output["SCR_Peaks_N"] = np.nansum(data["SCR_Peaks"].values)

    # Peak amplitude
    if "SCR_Amplitude" not in colnames:
        warn(
            "We couldn't find an `SCR_Amplitude` column. Returning NaN for peak amplitude.",
            category=NeuroKitWarning,
        )
        output["SCR_Peaks_Amplitude_Mean"] = np.nan
    else:
        output["SCR_Peaks_Amplitude_Mean"] = np.nanmean(data["SCR_Amplitude"].values)

    # Get variability of tonic
    if "EDA_Tonic" in colnames:
        output["EDA_Tonic_SD"] = np.nanstd(data["EDA_Tonic"].values)

    # EDA Sympathetic
    if "EDA_Clean" in colnames:
        output.update(eda_sympathetic(data["EDA_Clean"], sampling_rate=sampling_rate))
    elif "EDA_Raw" in colnames:
        # If not clean signal, use raw
        output.update(eda_sympathetic(data["EDA_Raw"], sampling_rate=sampling_rate))

    return output
