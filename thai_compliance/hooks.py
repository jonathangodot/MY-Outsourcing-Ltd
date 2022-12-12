from odoo import _
from odoo.exceptions import UserError
from .utils.const import *
import os
import shutil
import logging

_logger = logging.getLogger(__name__)


def test_post_init_hook(cr, registry):
    """Create forlders and move templates in."""
    os.makedirs(PATH_TMP, exist_ok=True)
    os.makedirs(PATH_TEMPLATE, exist_ok=True)

    for key, file_name in FILE_NAMES_PNG.items():
        try:
            shutil.copyfile(
                os.path.join(BASE_SRC_PATH_PNG, file_name),
                os.path.join(PATH_TEMPLATE, file_name),
            )
        except Exception as e:
            raise UserError(_(f"{e}"))


def test_uninstall_hook(cr, registy):
    """Remove folders."""
    shutil.rmtree(PATH_TMP)
    shutil.rmtree(PATH_TEMPLATE)
