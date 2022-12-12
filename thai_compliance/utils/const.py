import os


FILE_NAMES_PDF = {
    "pnd1_en": "pnd1_en.pdf",
    "pnd1_th": "pnd1_th.pdf",
    "pnd1_attachment_en": "pnd1_attachment_en.pdf",
    "pnd1_attachment_th": "pnd1_attachment_th.pdf",
    #
    "pnd1_kor_th": "pnd1_kor_th.pdf",
    "pnd1_kor_attachment_th": "pnd1_kor_attachment_th.pdf",
    #
    "withholding_tax_certificate_en": "wtc_en.pdf",
    "withholding_tax_certificate_th": "wtc_th.pdf",
    #
    "sps1_10_main_en": "sps1_10_main_en.pdf",
    "sps1_10_main_th": "sps1_10_main_th.pdf",
    "sps1_10_detail_en": "sps1_10_detail_en.pdf",
    "sps1_10_detail_th": "sps1_10_detail_th.pdf",
}
FILE_NAMES_PNG = {
    "pnd1_en": "pnd1_en.png",
    "pnd1_th": "pnd1_th.png",
    "pnd1_attachment_en": "pnd1_attachment_en.png",
    "pnd1_attachment_th": "pnd1_attachment_th.png",
    #
    "pnd1_kor_th": "pnd1_kor_th.png",
    "pnd1_kor_attachment_th": "pnd1_kor_attachment_th.png",
    #
    "withholding_tax_certificate_en": "wtc_en.png",
    "withholding_tax_certificate_th": "wtc_th.png",
    #
    "sps1_10_main_en": "sps1_10_main_en.png",
    "sps1_10_main_th": "sps1_10_main_th.png",
    "sps1_10_detail_en": "sps1_10_detail_en.png",
    "sps1_10_detail_th": "sps1_10_detail_th.png",
}
BASE_PATH = os.path.join(
    os.path.abspath("./var/lib/odoo")
    if "var" in os.listdir(".")
    else os.path.abspath("./data/filestore/")
)

PATH_TEMPLATE = os.path.join(os.path.abspath(BASE_PATH), "templates/")
PATH_TMP = os.path.join(os.path.abspath(BASE_PATH), "tmp/")
EXTRA_ADDON = (
    os.path.abspath("./mnt/extra-addons/")
    if "mnt" in os.listdir(".")
    else os.path.abspath("./src/user/")
)
BASE_SRC_PATH_PDF = os.path.join(
    EXTRA_ADDON,
    "thai_compliance/static/src/pdf/templates/",
)
BASE_SRC_PATH_PNG = os.path.join(
    EXTRA_ADDON,
    "thai_compliance/static/src/png/templates/",
)

FONTS_PATH = os.path.join(
    EXTRA_ADDON,
    "thai_compliance/static/src/fonts/",
)

DIFFERENT_FIELDS = {
    "pnd1_attachment": [
        "page_no",
        "recipient_pin",
        "recipient_tin",
        "recipient_name",
        "recipient_surname",
        "recipient_address",
        "payment_date",
        "condition",
        "amount_paid",
        "tax_withheld",
        "number",
        "income_type",
    ],
    "pnd1_kor_attachment": [
        "page_no",
        "recipient_pin",
        "recipient_name",
        "recipient_surname",
        "recipient_address",
        "payment_date",
        "condition",
        "amount_paid",
        "tax_withheld",
        "number",
        "income_type",
    ],
    "sps1_10_detail": [
        "number",
        "id_nb",
        "employee_name",
        "wage_",
        "contribution",
        "sheet_no",
    ],
}

PADDING = 10

FIELD_SPACING = [
    "company_pid",
    "company_tin",
    "branch_no",
    "branch_nb",
    "address_post_code",
    "employee_pid",
    "employee_tin",
    "id_nb",
    "account_nb",
]
FIELD_SPACING += [f"recipient_pin_{i}" for i in range(0, 9)]
FIELD_SPACING += [f"id_nb_{i}" for i in range(0, 11)]
