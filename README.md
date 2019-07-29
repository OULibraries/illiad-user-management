# illiad-user-management
_Helper Scripts for ILLiad User Management_
---

This module updates/imports users into ILLiad

**Actual ILLiad Database updates still need to be implemented, but this module will generate the framework of what actions need to be taken.**

---
This is accomplished by:

* Parsing two XML files containing user metadata
* Combining the resultant files into a single Python List
* Moving the existing module-specific users database table
    - NOTE: This is is an internal SQLite3 database table for user
      comparison and in no way alters the ILLiad database
* Creating a database table containing the new users
  from the generated Python List
    - NOTE: This is is an internal SQLite3 database table for user
      comparison and in no way alters the ILLiad database
* Creating three tables with ILLiad user states
    - Users to be added
    - Users to be removed
    - Users to be updated


The following files are expected to exist in the directory
from which this module is executed:

* lib_emp.txt
    - A XML document containing employee (Faculty/Staff) metadata
* lib_stu.txt
    - A XML document containing student metadata
* cat2s
    - A text file containing departmental pipe-delimeted metadata
* cat3s
    - A text file containing degree/major pipe-delimeted metadata
