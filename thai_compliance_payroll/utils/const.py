MONTHS = [
    ("1", "January"),
    ("2", "February"),
    ("3", "March"),
    ("4", "April"),
    ("5", "May"),
    ("6", "June"),
    ("7", "July"),
    ("8", "August"),
    ("9", "September"),
    ("10", "October"),
    ("11", "November"),
    ("12", "December"),
]

PND1_LINES = [
    (
        "1",
        "1. Income under Section 40(1): salaries, wages, etc. (In general cases.)",
    ),
    (
        "2",
        "2. Income under Section 40(1): salaries, wages, etc. (In the case where the Revenue Department has given approval to apply 3% withholding tax.)",
    ),
    (
        "3",
        "3. Income under Section 40(1)(2) (In case of single payment made by employer by reason of termination of employment.)",
    ),
    (
        "4",
        "4. Income under Section 40(2) where a recipient is a resident of Thailand.",
    ),
    (
        "5",
        "5. Income under Section 40(2) where a recipient is a non-resident of Thailand.",
    ),
]

WTC_LINES = [
    ("a", "1. Salary, wage, pension, etc. under Section 40(1)"),
    ("b", "2. Commissions etc. under Section 40(2)"),
    ("c", "3. Royalties etc. under Section 40(3)"),
    ("d", "4.a. Interest, etc. under Section 40(4)(a)"),
    ("e", "4.b.1.1. 30 percent of net profit."),
    ("f", "4.b.1.2. 25 percent of net profit."),
    ("g", "4.b.1.3. 20 percent of net profit."),
    ("h", "4.b.1.4. Other rate (specify)"),
    ("i", "4.b.2.1. Net profit of business that is exempted from income tax."),
    (
        "j",
        "4.b.2.2. Dividend on share of profit which is exempted from income tax",
    ),
    (
        "k",
        "4.b.2.3. The portion of net profit after deduction of net loss carried forward for five years up to the present accounting period.",
    ),
    ("l", "4.b.2.4. Recognition of profits using the equity method."),
    ("m", "4.b.2.5. Other (specify)"),
    (
        "n",
        """
        5.  Payment of income subject to withholding tax according to the Revenue
            Department\’s Instruction issued under Section 3 Tredecim, such as prizes, any
            reductions or benefits due to sales promotions, prices received from contests,
            competitions or lucky draws, public entertainers\’ income, income derived from
            performance of work, advertisement fees, rents, transportation fees, services fees,
            insurance premiums against loss, etc.""",
    ),
    ("o", "6. Others (Please specify)..."),
]

MODELS_WITH_CUSTOM_FIELDS = [
    {
        "name": "thailand.pnd1.attachment.line",
        "views": ["pnd1.month.employees.form"],
        "place_holder": "line_place_holder",
        "prefix": "",
    },
    {
        "name": "thailand.pnd1.year.company",
        "views": ["pnd1.year.company.form"],
        "place_holder": "tot_company_place_holder",
        "prefix": "total_company_",
    },
    {
        "name": "thailand.pnd1.month",
        "views": [
            "pnd1.month.employees.form",
            "pnd1.year.company.form",
        ],
        "place_holder": "tot_place_holder",
        "prefix": "total_",
    },
    {
        "name": "thailand.pnd1.year.attachment.line",
        "views": ["pnd1.year.company.form"],
        "place_holder": "line_place_holder",
        "prefix": "",
    },
]
