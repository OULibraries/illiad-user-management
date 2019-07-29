import sqlite3
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


def illiad_add_user():
    """This function creates a table containg entries to be added in ILLiad
    These entries are calculated by finding entries present in users_new
    that are not present in users_old.

    Parameters:
    None

    Returns:
    None
    """

    cnxn = sqlite3.connect("sqlite.db")
    cursor = cnxn.cursor()
    cursor.execute('''create table if not exists
                       ill_add (user_id, alt_id, user_name_full,
                                  first_name, middle_name, last_name,
                                  user_profile, user_cat1,
                                  user_cat2, major, user_cat3,
                                  department, phone1, main_street,
                                  main_city, main_state, main_zip,
                                  email1, userdata)''')
    cursor.execute('''delete from ill_add''')
    user_list = cursor.execute('''select * from (SELECT DISTINCT user_id
                                                 FROM USERS_NEW
                                                 WHERE user_id Not IN
                                                (SELECT DISTINCT user_id
                                                FROM USERS_OLD)) f
                                join USERS_NEW using(USER_ID)''').fetchall()
    for single_user in user_list:
        cursor.execute(
                 '''insert into ill_add values(?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?,
                  ?, ?, ?, ?, ?, ?, ?, ?)''', single_user)
    cnxn.commit()
    cnxn.close()


def illiad_remove_user():
    """This function creates a table containg entries to be removed in ILLiad
    These entries are calculated by finding entries present in users_old
    that are not present in users_new.

    Parameters:
    None

    Returns:
    None
    """

    cnxn = sqlite3.connect("sqlite.db")
    cursor = cnxn.cursor()
    cursor.execute('''create table if not exists
                       ill_remove (user_id, alt_id, user_name_full,
                                  first_name, middle_name, last_name,
                                  user_profile, user_cat1,
                                  user_cat2, major, user_cat3,
                                  department, phone1, main_street,
                                  main_city, main_state, main_zip,
                                  email1, userdata)''')
    cursor.execute('''delete from ill_remove''')
    user_list = cursor.execute('''select * from (SELECT DISTINCT user_id
                                                 FROM USERS_OLD
                                                 WHERE user_id Not IN
                                                (SELECT DISTINCT user_id
                                                FROM USERS_NEW)) f
                                join USERS_OLD using(USER_ID)''').fetchall()
    for single_user in user_list:
        cursor.execute(
                 '''insert into ill_remove values(?, ?, ?, ?, ?, ?, ?, ?, ?,?,
                  ?, ?, ?, ?, ?, ?, ?, ?, ?)''', single_user)
    cnxn.commit()
    cnxn.close()


def illiad_update_user():
    """This function creates a table containg metadata updates
    for existing users in ILLiad

    Parameters:
    None

    Returns:
    None
    """

    cnxn = sqlite3.connect("sqlite.db")
    cursor = cnxn.cursor()
    cursor.execute('''create table if not exists
                       ill_update (user_id, alt_id, user_name_full,
                                  first_name, middle_name, last_name,
                                  user_profile, user_cat1,
                                  user_cat2, major, user_cat3,
                                  department, phone1, main_street,
                                  main_city, main_state, main_zip,
                                  email1, userdata)''')
    cursor.execute('''delete from ill_update''')
    user_list = cursor.execute('''SELECT distinct f.*
                                  FROM USERS_OLD as a
                                  join (select * from users_new) f
                                  on a.user_id = f.user_id
                                  where f.userdata != a.userdata''').fetchall()
    for single_user in user_list:
        cursor.execute(
                 '''insert into ill_update values(?, ?, ?, ?, ?, ?, ?, ?, ?,?,
                  ?, ?, ?, ?, ?, ?, ?, ?, ?)''', single_user)
    cnxn.commit()
    cnxn.close()


def update_tables(user_list):
    """This function updates two user management update_tables,
    users_old contains the imported users from the previous
    users_new contains the new users that are being imported

    Parameters:
    user_list: List containing parsed user data to be passed into SQLite3 table

    Returns:
    None
    """

    cnxn = sqlite3.connect("sqlite.db")
    cursor = cnxn.cursor()
    # Create users_new table if it doesn't exist, typically during first run
    cursor.execute('''create table if not exists
                       users_new (user_id, alt_id, user_name_full,
                                  first_name, middle_name, last_name,
                                  user_profile, user_cat1,
                                  user_cat2, major, user_cat3,
                                  department, phone1, main_street,
                                  main_city, main_state, main_zip,
                                  email1, userdata)''')
    # users_new becomes users_old,
    # so users_old is dropped and remade from users_new
    cursor.execute('''drop table if exists users_old''')
    cursor.execute('''create table users_old as select * from users_new''')

    # Clear out users_new and import new users from user_list
    cursor.execute('''DELETE from users_new''')

    for single_user in user_list:
        cursor.execute(
             '''insert into users_new values(?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?,
              ?, ?, ?, ?, ?, ?, ?)''', single_user)
    cnxn.commit()
    cnxn.close()


def finder(tree, elmkey):
    """A XML helper function that returns the text of an Element if it exists
    If it is not set it retuns an empty string

    Parameters:
    tree: ElementTree object from which to lookup key
    elmkey: Element object to lookup the text value of from tree

    Returns:
    ret: A string object containing the text value of the ElementTree Loookup
         contains "" if lookup is fails
    """

    tmp = tree.find(elmkey)
    if tmp is not None:
        ret = tmp.text
    else:
        ret = ""
    return ret


def getuser(user, cat2dict={}, cat3dict={}):
    """Parse a XML User entry and output a list
    containing formatted user entries

    Parameters:
    cat2dict: A dictionary containing departmental categories
    cat3dict: A dictionary containing major/degree categories

    Returns:
    user: A list containing parsed users fields
    """
    line1 = ""
    city = ""
    state = ""
    postalCode = ""
    email = ""
    phone = ""
    barcode = ""
    usercat1 = ""
    usercat2 = ""
    usercat3 = ""
    usercat2der = ""
    usercat3der = ""
    ouNetID = ""
    firstName = ""
    middleName = ""
    lastName = ""
    userGroup = ""
    ouNetID = finder(user, "primary_id")
    firstName = finder(user, "first_name")
    middleName = finder(user, "middle_name")
    lastName = finder(user, "last_name")
    userGroup = finder(user, "user_group")
    contact_info = user.findall("./contact_info/addresses/*")
    email_info = user.findall("./contact_info/emails/*")
    phone_info = user.findall("./contact_info/phones/*")
    id_type = finder(user, "./user_identifiers/user_identifier/id_type")
    id_val = finder(user, "./user_identifiers/user_identifier/value")
    stats_info = user.findall("./user_statistics/user_statistic")
    cats = {}
    for i in contact_info:
        if i.attrib['preferred'] == "true":
            city = finder(i, "city")
            line1 = finder(i, "line1")
            state = finder(i, "state_province")
            postalCode = finder(i, "postal_code")

    for i in email_info:
        if i.attrib['preferred'] == "true":
            email = finder(i, "email_address")

    for i in phone_info:
        if i.attrib['preferred'] == "true":
            phone = finder(i, "phone_number")

    for i in stats_info:
        tmparr = finder(i, "statistic_category").split(':')
        cats[tmparr[0]] = tmparr[1]

    if id_type == "BARCODE":
        barcode = id_val

    usercat1 = cats.get('CAT1')
    usercat2 = cats.get('CAT2')
    usercat3 = cats.get('CAT3')
    usercat2der = cat2dict.get(usercat2)
    usercat3der = cat3dict.get(usercat3)
    longline = '|'
    fullName = " "
    fullName = fullName.join([firstName, middleName, lastName])
    new_user = [barcode, ouNetID, fullName, firstName, middleName, lastName,
                userGroup, usercat1, usercat2, usercat2der, usercat3,
                usercat3der, phone, line1, city, state, postalCode, email]

    for i, j in enumerate(new_user):
        if j is None:
            new_user[i] = ""

    new_user.append(longline.join(new_user))
    return new_user


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
            cat2data = cat2.split('|')
            cat2dict[cat2data[2]] = cat2data[3]

    with open("cat3s", "r") as cat3file:
        for cat3 in cat3file:
            cat3data = cat3.split('|')
            cat3dict[cat3data[2]] = cat3data[3]

    empdoc = ElementTree.parse("lib_emp.txt")
    studoc = ElementTree.parse("lib_stu.txt")
    emproot = empdoc.getroot()
    sturoot = studoc.getroot()
    user_list = []
    for i in emproot.findall("user"):
        user_list.append(getuser(i, cat2dict, cat3dict))

    for i in sturoot.findall("user"):
        user_list.append(getuser(i, cat2dict, cat3dict))

    update_tables(user_list)
    illiad_add_user()
    illiad_remove_user()
    illiad_update_user()
