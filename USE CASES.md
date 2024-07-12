											
											USE CASES
											---------

USE CASE - LOGIN & REGISTRATION

1. Entry points for login and registration are product landing page, employer landing page, or job application page.
2. User login can happen via email and password only.
3. A candidate can login or register via a social account as well. (but not an employer)
4. A candidate should be allowed to login without email verification.
5. An employer should not be allowed to login without email verification.
6. When logging/registering from a job application page, remember the job being applied to and redirect the candidate back on the appropriate page and initiate aplication.
7. When registering a new candidate from social media
  a. Extract all information into the new profile
  b. If another account exists with the same email, add suthentication method to the account and merge the newly fetched data.


USE CASE - APPLYING TO A JOB

1. If a user is not logged in he should be allowed to apply with resume or with product profile.
2. Candidates which are already logged in, have only one option to apply, directly proceed to 3c and continue.
3. On choosing to apply with resume
  a. Show a popup to request an attachment. 
  b. On submission, redirect to a confirmation page where data parsed from his resume are shown. The user also has option to modify name(required), email(required) (prefilled from parsed data).
  c. If for the given email a product profile exists, prompt user to login and use full profile for application.
  d. If user chooses to continue anyway, use the current details and make a copy of the profile to be attached with the application.
  e. If user chooses to login, change the flow to 3.
4. On choosing to apply with product
  a. Login/Register as candidate.
  b. The user is redirected to the job application page and the process is initiated.
  c. The user is taken to an intermediary confirmation page where his current profile is shown in a mini resume along with any attachments available (with date of upload).
  d. If there are any conflicts to be resolved they are shown there as well.
  e. Every block of conflict is shown separately and for 10 or more conflicts always show 10+ Pending Actions
  f. User has the option to apply anyway disregarding any conflicts that exist.
  g. Clicking on the mini resume opens up a profile preview where all the data is listed.
  h. Clicking on a conflict block will open editing and conflict resolution for that block.
  i. Editing any block in profile preview will open editing for that block. If conflicts exist in the block, the resolution has to be offered there as well.
  j. Social fabs will allow him to link more social media profiles or refetch details from existing. Adding in more conflict blocks if required.
  k. Candidates redirected from 2 should see the new attachment and details filled in the conflict section.
5. Users application will not be accepted without atleast name and email.
6. On proceeding from 2 or 3 the user will be prompted with the option to add cover letter and Employer's custom application form (if available).
7. Submitting the form completes his application procedure.

USE CASE - CANDIDATE PROFILE

1. A candidate profile can have multiple versions. Only the latest version is visible to a candidate on site. Previous versions are maintained to track record of data used to apply.
2. A candidate profile is editable on a block by block basis. Every block's editing also includes any resolutions to be performed.
3. Social fabs will allow him to link more social media profiles or refetch details from existing. Adding in more conflict blocks if required.

USE CASE - CONFLICT MANAGEMENT - IDENTIFICATION

1. Triggers for conflict management are both candidate profile and login/registration.
2. For every single chunk identified as conflicting the entire block is marked as conflicted.
3. Conflicts are shown during the editing of the block.
4. Every block's label contains the Pending Actions tag.
5. Conflicts and their resolutions are both recorded for future reference (Do not prompt a user for conflict that he has already resolved).

USE CASE - CONFLICT MANGEMENT - RESOLUTION