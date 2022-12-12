from PIL import Image, ImageFont, ImageDraw
import os
from contextlib import suppress
from .const import *
from .img_coordinates import *
import logging

_logger = logging.getLogger(__name__)


def fill_pdf(data, file_type, out_file_name, detail_type=None, nb_pages=0):
    Image._initialized = 0
    Image.init()
    out_file = os.path.join(PATH_TMP, out_file_name)

    main_page = write_img(data, file_type)
    detail_pages = []
    for p in range(0, nb_pages):
        detail_pages.append(write_img(data, detail_type, p))

    main_page.save(
        out_file,
        format="pdf",
        save_all=True,
        append_images=detail_pages,
        resolution=300,
    )
    return out_file


def write_img(data, file_type, p=0):
    with Image.open(os.path.join(PATH_TEMPLATE, FILE_NAMES_PNG[file_type])) as image:
        draw = ImageDraw.Draw(image)

        for field, value in data.items():
            with suppress(KeyError):
                font_name = (
                    "NotoSansJP-Medium.otf"
                    if value == "✓"
                    else "NotoSerifThai-VariableFont_wdth,wght.ttf"
                )
                font_path = os.path.join(FONTS_PATH, font_name)
                if field in coordinates[file_type]:
                    write_value(file_type, draw, font_path, field, value)
                else:
                    """Writing detail (for fields that are different on every detail pages)"""
                    for detail_field in DIFFERENT_FIELDS[
                        file_type.replace("_en", "").replace("_th", "")
                    ]:
                        if detail_field in field:
                            splited_field_name = field.split("_")
                            if p + 1 == int(splited_field_name[-1]):
                                del splited_field_name[-1]
                                field_name = "_".join(splited_field_name)
                                write_value(
                                    file_type, draw, font_path, field_name, value
                                )

        img = image.convert("RGB")
    return img


def write_value(file_type, draw, font_path, field, value):
    value = value
    color = "blue"
    _logger.info(f"Field : {field} Font adj : {adjust_font(file_type, field)}")
    font = ImageFont.truetype(
        font_path,
        int(
            font_size(
                len(value),
                address=True if "address" in field and "pnd1" in file_type else False,
                field=field,
            )
            * adjust_font(file_type, field)
        ),
    )
    y = coordinates[file_type][field][1] - (PADDING - 3)
    if (
        "th" == file_type[-2:]
        or "withholding_tax_certificate" in file_type
        or "sps1_10" in file_type
    ) and ("baht" in field or "satang" in field):
        x = coordinates[file_type][field][0] - PADDING
        draw.text(
            (x, y),
            value,
            font=font,
            fill=color,
            allign="right",
            anchor="rs",
        )
    else:
        x = coordinates[file_type][field][0] + PADDING
        draw_text_psd_style(
            draw,
            (x, y),
            value,
            font,
            tracking=adjust_tracking(file_type, field),
            fill=color,
            allign="left",
            anchor="ls",
        )


def adjust_tracking(file_type, field):
    if field in FIELD_SPACING:
        if file_type == "withholding_tax_certificate_th":
            return 540
        if "withholding_tax_certificate" in file_type and "tin" in field:
            return 460
        if file_type == "sps1_10_main_en" or file_type == "sps1_10_detail_en":
            return 40
        if "sps1_10" in file_type and "th" in file_type:
            if "post_code" in field:
                return 0
            if "main" in file_type:
                return 440
            return 630
        return 420
    return 0


def adjust_font(file_type, field):
    if (
        "tot_withholding_tax_in_letter" in field
        and "withholding_tax_certificate" in file_type
    ):
        return 1.65
    if (
        "address" in field
        and "post_code" not in field
        and "withholding_tax_certificate" in file_type
    ):
        return 2
    if (
        "pid" in field
        or "branch_no" in field
        or "post_code" in field
        or "pin" in field
        or "tin" in field
        or "account" in field
        or "id_nb" in field
    ):
        if file_type == "pnd1_th":
            return 1.55
        if (
            file_type == "withholding_tax_certificate_en"
            or file_type == "withholding_tax_certificate_th"
        ):
            return 1.435
        if file_type == "pnd1_kor_th":
            return 1.45
        if file_type == "pnd1_attachment_th" or file_type == "pnd1_kor_attachment_th":
            return 1.6
        if file_type == "sps1_10_detail_th" or file_type == "sps1_10_main_th":
            return 1.6
    if file_type == "sps1_10_detail_en":
        return 0.8
    return 1


def font_size(len, address=False, field=""):
    if address:
        if "building" in field:
            if len < 15:
                return 25
            elif len < 25:
                return 20
            else:
                return 15
        if (
            "room_no" in field
            or "floor_no" in field
            or "address_no" in field
            or "moo" in field
        ):
            if len < 5:
                return 25
            elif len < 7:
                return 20
            else:
                return 15
        if (
            "street" in field
            or "road" in field
            or "district" in field
            or "province" in field
        ):
            if len < 35:
                return 25
            elif len < 55:
                return 20
            else:
                return 15
    if len < 35:
        return 30
    elif len < 50:
        return 25
    elif len < 70:
        return 20
    else:
        return 15


def draw_text_psd_style(draw, xy, text, font, tracking=0, leading=None, **kwargs):
    """
    usage: draw_text_psd_style(draw, (0, 0), "Test",
                tracking=-0.1, leading=32, fill="Blue")

    Leading is measured from the baseline of one line of text to the
    baseline of the line above it. Baseline is the invisible line on which most
    letters—that is, those without descenders—sit. The default auto-leading
    option sets the leading at 120% of the type size (for example, 12‑point
    leading for 10‑point type).

    Tracking is measured in 1/1000 em, a unit of measure that is relative to
    the current type size. In a 6 point font, 1 em equals 6 points;
    in a 10 point font, 1 em equals 10 points. Tracking
    is strictly proportional to the current type size.
    """

    def stutter_chunk(lst, size, overlap=0, default=None):
        for i in range(0, len(lst), size - overlap):
            r = list(lst[i : i + size])
            while len(r) < size:
                r.append(default)
            yield r

    x, y = xy
    font_size = font.size
    lines = text.splitlines()
    if leading is None:
        leading = font.size * 1.2
    for line in lines:
        for a, b in stutter_chunk(line, 2, 1, " "):
            w = font.getlength(a + b) - font.getlength(b)

            draw.text((x, y), a, font=font, **kwargs)
            x += w + (tracking / 1000) * font_size
        y += leading
        x = xy[0]
