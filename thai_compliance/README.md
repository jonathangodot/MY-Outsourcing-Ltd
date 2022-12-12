This is the base for all futur thai compliance modules.
It provides the structure of the modules, required fields on several models, and an abstract model that the document should inherit from.
Provides the write PDF workflow.
The PDF templates are also provided by this module. When installing, template folder, and temp folder will be created so that odoo can later use them in order to duplicate and fill them.

### Fields added :
- Detail the address to fit the official documents fields (for example, include District, Soi...) on the partner, company and employee models
- Adds the TIN field on employee
- The social security rate is editable by the user

### PDF creation workflow
- The coordinates of every field of every document have been recorded in a python dictionary.
- When the user exports the PDF document, the serialized dictionary containing the data is matched with the coordinate dictionary, and the data is written on the PDF.
- Some logic exists in order to format the PDF, such as the font size, the alignment, etc.