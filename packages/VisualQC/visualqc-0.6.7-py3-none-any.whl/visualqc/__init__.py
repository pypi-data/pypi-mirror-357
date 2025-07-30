# -*- coding: utf-8 -*-

"""Top-level package for visualqc."""

__all__ = ['outlier_advisory',
           'gather_freesurfer_data',
           'read_aparc_stats_in_hemi',
           'read_aseg_stats',
           'read_aparc_stats_wholebrain',
           ]

__author__ = """Pradeep Reddy Raamana"""
__email__ = 'raamana@gmail.com'


try:
    from ._version import __version__
except ImportError:
    __version__ = "0+unknown"

from sys import version_info

if version_info.major > 2:
    from visualqc.readers import (gather_freesurfer_data, read_aparc_stats_in_hemi,
                                  read_aseg_stats, read_aparc_stats_wholebrain)
    from visualqc.outliers import outlier_advisory
else:
    raise NotImplementedError('Python 3 or higher is required to run VisualQC.'
                              'Please upgrade.')
del version_info
