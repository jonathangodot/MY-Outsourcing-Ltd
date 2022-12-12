## Requirements
This module has been developped in order to work with the module Payroll.</br>
It also requires the module Mail in order to track some actions on the needs and the schedules.</br>
(All requrements are automatically installed by the overtime module.)</br>
In the model `need`, a `PercentField` is display. This field nees a specific module nammed [`vendor_ks_percent_field](https://apps.odoo.com/apps/modules/15.0/vendor_ks_percent_field/).

## Purpose
The purpose of this module is to create an enviroment to manage the overtimes for a company. And to make a link with the Payroll module, in order to create the work entries related to the overtime.

## Workflow
### Without need
From the `Schedule` menu, the user can create schedules of OTs. One schedule is linked to an employee, and is composed of several OTs.</br>
Once the schedule created, the user can create OTs. Important to know :
- It is impossible to save a schedule empty.
- It is impossible to create overlapping OT's for a same employee, even if the overlapping OT is in an othe schedule.
- Once the schedule is completed, the user can accept it.
- A document needs to be uploaded in order to validate it.
- A schedule in an other state than draft can not be updated.
- At any time, the user can set the schedule as draft in order to update it.
- For more convinience, a user can repeat an OT the next day or the next week.
- A schedule is considered over when his date is before the current day.
- Once accepted, the OTs can be published as work entries. The work entries will then be created.
- At any time, an OT can be cancelled, wich will be bubstracted from the number of hours allocated to the schedule.

### With need
- A `need` object is a need the company has that will be filled by some overtime.
- A description can be written to explain the need, the date from and the date to are not mendatory.
- On the form view of this object, the user can monitor how the filling of this need is going. To do so, the field `Tot. Hours` must be correctly filled. As new schedules are created from the need's view, the number of hours field will progress (note that the schedules in draft state won't be considered).
- Once the allocated field reaches 100%, the user can validate the need.
- From this view, the user can publish the work entries for each schedule, or all of them if none of them are in a draft state, and if the need is not in draft state either.

### Uploading the document
- At the bottom of the view for `Schedule` objects, there is a paperclip icon. When the user will click on it, he will be able to upload any file supported by Odoo.
- The name of the file will be modified by the following structure : %SCHEDULE_NAME% - %DATE_START% - %DATE_STOP%
- Once uploaded, the state can be set to validated.
- If deleted, the state will be reset to accepted.

## Important to know
- After uploading the document, the user might need to refresh the page in order to see the `Validate` button
- Some other updats need the page to be refreshed to be displayed