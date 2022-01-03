import illiad_manager
import json
import xml.etree.ElementTree as ElementTree

"""
This module updates/imports users into ILLiad
Actual ILLiad Database updates still need to be implemented,
but this module will generate the framework of what actions need to be taken.

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

lib_emp.txt
    - A XML document containing employee (Faculty/Staff) metadata
lib_stu.txt
    - A XML document containing student metadata
cat2s
    - A text file containing departmental pipe-delimeted metadata
cat3s
    - A text file containing degree/major pipe-delimeted metadata

"""


def main():
    """
    This function does initial loading of files,
    it steps line-by-line through two XML files to generate SQLite3 Tables

    Parameters:
    None

    Returns:
    None
    """
    cat2dict = {}
    cat3dict = {}
    with open("cat2s", "r") as cat2file:
        for cat2 in cat2file:
            cat2data = cat2.split("|")
            cat2dict[cat2data[2]] = cat2data[3]

    with open("cat3s", "r") as cat3file:
        for cat3 in cat3file:
            cat3data = cat3.split("|")
            cat3dict[cat3data[2]] = cat3data[3]

    empdoc = ElementTree.parse("lib_emp.txt")
    studoc = ElementTree.parse("lib_stu.txt")
    emproot = empdoc.getroot()
    sturoot = studoc.getroot()
    user_list = []
    im = illiad_manager.illiad_manager()
    for i in emproot.findall("user"):
        user_list.append(im.getuser(i, cat2dict, cat3dict))

    for i in sturoot.findall("user"):
        user_list.append(im.getuser(i, cat2dict, cat3dict))
    try:
        print('Updating Tables')
        im.update_tables(user_list)
        print('Generating User Adds')
        im.gen_user_adds()
        # print('Generating User Removes')
        # im.gen_user_removals()
        print('Generating User Updates')
        im.gen_user_updates()
        # print('Removing Users')
        # im.remove_users()
        print('Adding Users')
        im.add_users()
        print('Updating Users')
        im.update_users()
        print('Closing Connection')
        im.close_cnxn()
    except Exception as e:
        print("FAILURE: ", e)


if __name__ == "__main__":
    main()
