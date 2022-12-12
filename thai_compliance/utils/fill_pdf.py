# """Odoo uses PyPDF2(v1.26.0) to fill pdf forms.
# The methodes used in the v2 are not available here. The methodes syntaxe are different."""
# from PyPDF2 import PdfFileWriter, PdfFileReader
from .PyPDF2 import PdfReader, PdfWriter
from .PyPDF2.generic._base import NameObject
from .PyPDF2.generic import create_string_object
from .const import *
import os
import logging

_logger = logging.getLogger(__name__)


def fill_pdf(data, file_type, out_file_name, detail_type=None, nb_pages=0):
    """Build a new document, if details pages are required, add them to the new document
    and change the field name in order to distinguish one from an other."""
    reader = PdfReader(os.path.join(PATH_TEMPLATE, FILE_NAMES_PDF[file_type]))
    writer = PdfWriter()
    page = reader.pages[0]
    writer.add_page(page)

    if detail_type:
        detail_pages(detail_type, nb_pages, writer)
    fill_form(data, writer)
    out_file = export_file(out_file_name, writer)

    return out_file


def export_file(out_file_name, writer):
    """Write the pdf to the file system"""
    out_file = os.path.join(PATH_TMP, out_file_name)
    with open(out_file, "wb") as f:
        writer.write(f)
    return out_file


def fill_form(data, writer):
    """Fill the PDF form with the serialized values stored in data"""
    for page in writer.pages:
        for field, value in data.items():
            writer.update_page_form_field_values(page, {field: value})


def detail_pages(detail_type, nb_pages, writer):
    """Add the detail pages to the new document and change the field name
    in order to distinguish one from an other."""
    for i in range(1, nb_pages + 1):
        reader_detail = PdfReader(
            os.path.join(PATH_TEMPLATE, FILE_NAMES_PDF[detail_type])
        )
        page_detail = reader_detail.pages[0]
        for field_in_file in page_detail["/Annots"].getObject():
            if "/T" in field_in_file.getObject():
                for field in (
                    SPS1_10_detail_fields
                    if "sps1_10" in detail_type
                    else PND1_month_attachment_fields
                    if "pnd1" in detail_type
                    else []
                ):
                    if field in field_in_file.getObject()["/T"]:
                        change_field_name(field_in_file, f"_{i}")
                        break

        writer.add_page(page_detail)


def change_field_name(field, suffix):
    """Change the field name in order to distinguish one from an other."""
    field.getObject().update(
        {NameObject("/T"): create_string_object(field.getObject()["/T"] + suffix)}
    )
