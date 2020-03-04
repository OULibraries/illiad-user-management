# illiad-user-management
_Helper Scripts for ILLiad User Management_
---

This module synchronizes ILLiad database with a supplied XML document

A optional email module has also been added which will send an email containing the output of the management script (if directed to a file), to defined email recipients 

---
**Requires:**

Database Access to ILLiad
* SELECT, INSERT, and DELETE Permissions required 

Python 3.6+

pip

Python Packages
* [pyodbc](https://github.com/mkleehammer/pyodbc)

  - _"pyodbc is an open source Python module that makes accessing ODBC databases simple. It implements the DB API 2.0 specification but is packed with even more Pythonic convenience."_


* [sqlite3](https://docs.python.org/3/library/sqlite3.html) (Included in standard library)

  - _"SQLite is a C library that provides a lightweight disk-based database that doesn’t require a separate server process and allows accessing the database using a nonstandard variant of the SQL query language"_

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
* secrets.py  
    - Connection String is stored here this will need to be created/modified.

---

Example Usage:
```
  import illiad_manager

  # Make new illiad_manager object
  im = illiad_manager.illiad_manager()

  # Parse employee XML data
  employee_doc = ElementTree.parse("lib_emp.txt")
  employee_xmlroot = empdoc.getroot()

  # Create user list and parse XML tree into user list,
    utilize two dictionary files containing department and degree mappings
  user_list = []
  for user in employee_xmlroot.findall("user"):
      user_list.append(im.getuser(user, department_dict, degree_dict))

  # Update local SQLite3 tables with new data
  im.update_tables(user_list)

  # Generate user addition table
  im.gen_user_adds()

  # Generate user removal table
  im.gen_user_removals()

  # Generate user update table
  im.gen_user_updates()

  # Add users in ILLiad database from SQLite3 user addition table
  im.add_users()

  # Update users in ILLiad database from SQLite3 user update table
  im.update_users()

  # Remove users in ILLiad database from SQLite3 user remove table
  im.remove_users()

  # Close illiad_manager connection (commits and closes connection to both ILLiad database and local SQLite3 database)
  im.close_cnxn()
```
