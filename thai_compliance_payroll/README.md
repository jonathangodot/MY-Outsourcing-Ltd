The purpose of this module is to automatically generate official documents required by the revenue department and the social security department.</br>
The documents have been integreted in Odoo. All the fields that the user can usually input on the official document are now in a more user friendly, editable and automated interface within odoo.

### Required fields added
- 3 percent tax on the structure. As this field is not supposed to change, and it would be dangerous to do so, it is only accessible in developer mode. It should be set once and for all at the creating of a structure object.
- thai_compliance_income_type on the salary rule object for technical purpose
- Code config in order to let the user choose which code is associated with which line on the payslips.

### User Worflow
The documents are separated into 2 distinct menus : 
- Revenu Department, that lists the PND1, PND1 kor and the withholding tax certificate
- Social Security, that lists the SPS1-10</br>

The user can access all of his reports from these menus, and create new ones. Odoo will make sure there is no duplicates when creating a new report.</br>
When creating a new report, the user only need to fill the name of the company, the year, and the month (only in case of monthly report), and click on generate report. Odoo will analyse the contracts and the payslips in order to generate all the data. The user can then review what has been computed, and update it if needed.</br>
Then, the user can export the documents into official documents that will be accepted by the diferent department.

- Depending how the salary rules have been configured, the codes coresponding to the gross salary, the withholding tax, or the social security contribution might change. The user can update these codes in the Configuration -> Settings menu. (note : settings need to be saved after first installation, otherwise, the amounts will remain empty when generating reports) By default, the codes are the following : 
    - Gross salary : GROSS
    - Withholding tax : PT
    - Social security contribution : SS</br>
- The user might want to display more than these kind of revenues/deductions. In the menu Configurations -> Income types, the user can add new income/deduction field to analyse from the payslips and display on the PND1 and the PND1 kor Odoo objetcs. They won't appear on the official documents. When creating a new field the user must give him a name, a code, and the different salary rules it is supposed to cover (several rules might cover the same revenue/deduction for different salary structures).
- The withholding tax certificates are computed from the PND1 kor object. One withholding tax certifacate will be generated per employee appearing on the PND1 kor.
- All the documents are generatable in english or in thai, except for the PND1 kor, which is only available in thai.
- Odoo will fill this document with all the data at his disposal, but it is the responsibility of the employee to make sure the informations are correct, and to correct them if they are not.

### Under the hood
#### PND1
- Odoo will search all the payslips of the given month and year, of the selected company that are either done or paid. It will then iterate through them, and create a new attachment line per employee that has at least one payslip for the month (an employee can be paid on a weekly or bi-monthly basis).
- The totals will be automatically computed as they are computed fields.
- The income type lines will also be automatically computed, one line will be created per income type, then, for each payslip, Odoo will check if there is a government authorisation to apply a 3% tax. If yes, the amounts of the correspondig payslip will be counted in the 2nd type of income, othewise, they will be counted in the 1st type of income. The 3rd, 4th and 5th types of income have not been implemented.

#### PND1 kor
- The management of the PND1 kor is quite similar than the PND1, except that instead of iteration through payslips, Odoo will iterate through PND1 in order to sum them up.

#### Withholding Tax Certificate
- The withholding tax certificate is computed from the PND1 kor. One withholding tax certificate will be generated per employee appearing on the PND1 kor.
- Odoo will iterate through each line (one line correspondig to one employee) en create the WTC for this employee. Odoo will fetch all the relevant data from the employee sheet and his payslips in order to fill as best as possible this document.

#### SPS1-10
- Odoo will first get all the employees of the company, and iterate through the ones who have a running contract. For each employee, Odoo will create a new line, and fill it with the relevant data.
- The totals are, as always, computed fields and are therefor automatically computed.
