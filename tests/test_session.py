"""
This module contains items that pertain to the entire test session.
"""

import os
import shutil

import pytest

from tests import clean_up, outdir

STARTUP = True

@pytest.fixture(scope="session",autouse=True)
def manage_outdir(request):
    """
    At the beginning of the session, creates the test outdir. If tests.clean_up,
    deletes this folder after the tests have finished running.

    Arguments
    - request contains the pytest session, including collected tests
    """
    global STARTUP
    if STARTUP and os.path.exists(outdir):
        # create clean space for running tests
        shutil.rmtree(outdir)
        STARTUP = False
        os.mkdir(outdir)
    def finalize_outdir():
        if os.path.exists(outdir) and clean_up:
            shutil.rmtree(outdir)
    request.addfinalizer(finalize_outdir)
