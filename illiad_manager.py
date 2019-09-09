import sqlite3
import pyodbc
import secrets


"""
This object contains functions to perform user updates/imports into ILLiad
Actual ILLiad Database updates still need to be implemented,
but this module will generate the framework of what actions need to be taken.

The following functions exist:

finder:
    - XML Lookup tool
get_user:
    - Process XML entry and return formatted user entry
gen_user_adds:
    - Compares users_old with users_new to generate table
      containing user additions
gen_user_removals:
    - Compares users_new with users_old to generate table
      containing user removals
gen_user_updates:
    - Compares users_new with users_old to generate table
      containing user updates
update_tables:
    - Takes a list containing parsed user data to be passed into SQLite3,
      this will shift users_new to users_old and generate a fresh users_new
      from parsed user data
add_users:
    - Add users in ILLiad database from SQLite3 user addition table
update_users()
    - Update users in ILLiad database from SQLite3 user update table

remove_users()
    - Remove users in ILLiad database from SQLite3 user remove table

"""


class illiad_manager:
    def __init__(self):
        """Object defintions:
              illcnxn:
                - ILLiad Database Connection
              sqlite3cnxn:
                - Local SQLite3 Database Connection
              ill_cursor:
                - Cursor object for ILLiad Database,
                  performs operations using illcnxn
                - Connection String is stored in a secrets file, secrets.py,
                  this will need to be created/modified.
              sqlite3_cursor:
                - Cursor object for local SQLite3 Database,
                  performs operations using sqlite3cnxn
        """

        self.illcnxn = pyodbc.connect(secrets.illiad_cnxn)
        self.sqlite3cnxn = sqlite3.connect("sqlite.db")
        self.ill_cursor = self.illcnxn.cursor()
        self.ill_cursor.fast_executemany = True
        self.sqlite3_cursor = self.sqlite3cnxn.cursor()

    def gen_user_adds(self):
        """This function creates a table containg entries to be added in ILLiad
        These entries are calculated by finding entries present in users_new
        that are not present in users_old.

        Parameters:
        None

        Returns:
        None
        """

        self.sqlite3_cursor.execute(
            """create table if not exists
                           ill_add (user_id, alt_id, user_name_full,
                                      first_name, middle_name, last_name,
                                      user_profile, user_cat1,
                                      user_cat2, major, user_cat3,
                                      department, phone1, main_street,
                                      main_city, main_state, main_zip,
                                      email1, userdata)"""
        )
        print('\tClearing ill_add')
        self.sqlite3_cursor.execute("""delete from ill_add""")
        print('\tGetting New Users')
        user_list = self.sqlite3_cursor.execute(
            """select * from (SELECT DISTINCT user_id
                                                     FROM USERS_NEW
                                                     WHERE user_id Not IN
                                                    (SELECT DISTINCT user_id
                                                    FROM USERS_OLD)) f
                                    join USERS_NEW using(USER_ID)"""
        ).fetchall()
        print('\tMarking ' + str(len(user_list)) + ' users to be added')
        self.sqlite3_cursor.executemany(
                """insert into ill_add values(?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?,
                      ?, ?, ?, ?, ?, ?, ?, ?)""", user_list
            )

    def gen_user_removals(self):
        """This creates a table containg entries to be removed in ILLiad
        These entries are calculated by finding entries present in users_old
        that are not present in users_new.

        Parameters:
        None

        Returns:
        None
        """

        self.sqlite3_cursor.execute(
            """create table if not exists
                           ill_remove (user_id, alt_id, user_name_full,
                                      first_name, middle_name, last_name,
                                      user_profile, user_cat1,
                                      user_cat2, major, user_cat3,
                                      department, phone1, main_street,
                                      main_city, main_state, main_zip,
                                      email1, userdata)"""
        )
        print('\tClearing ill_remove')
        self.sqlite3_cursor.execute("""delete from ill_remove""")
        print('\tGetting Users to be Removed')
        user_list = self.sqlite3_cursor.execute(
            """select * from (SELECT DISTINCT user_id
                                                     FROM USERS_OLD
                                                     WHERE user_id Not IN
                                                    (SELECT DISTINCT user_id
                                                    FROM USERS_NEW)) f
                                    join USERS_OLD using(USER_ID)"""
        ).fetchall()
        print('\tMarking ' + str(len(user_list)) + ' users to be Removed')
        self.sqlite3_cursor.executemany(
                """insert into ill_remove values(?, ?, ?, ?, ?, ?, ?, ?, ?,?,
                      ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                user_list,
            )

    def gen_user_updates(self):
        """This function creates a table containg metadata updates
        for existing users in ILLiad

        Parameters:
        None

        Returns:
        None
        """

        self.sqlite3_cursor.execute(
            """create table if not exists
                           ill_update (user_id, alt_id, user_name_full,
                                      first_name, middle_name, last_name,
                                      user_profile, user_cat1,
                                      user_cat2, major, user_cat3,
                                      department, phone1, main_street,
                                      main_city, main_state, main_zip,
                                      email1, userdata)"""
        )
        print('\tClearing ill_update')
        self.sqlite3_cursor.execute("""delete from ill_update""")
        print('\tGetting users to Update')
        user_list = self.sqlite3_cursor.execute(
            """
            select f.alt_id, f.last_name, f.first_name,
            f.user_id, f.user_profile, f.email1, f.phone1, f.department,
            f.main_street, f.main_city, f.main_state, f.main_zip,
            f.user_cat1 from (select alt_id, last_name, first_name,
            user_id, user_profile, email1, phone1, department,
            SUBSTR(main_street,1,39) as main_street,
            SUBSTR(main_city, 1, 29) as main_city,
            SUBSTR(main_state,1,2) as main_state,
            main_zip, user_cat1,  alt_id|| last_name
            || first_name|| user_id || user_profile || email1 ||
            phone1|| department||SUBSTR(main_street,1,39)||
            SUBSTR(main_city, 1, 29) || SUBSTR(main_state,1,2)
            || main_zip || user_cat1
                as hash from users_old) as a
                join (select user_id, last_name, first_name,
                user_id, user_profile, email1, phone1, department,
                SUBSTR(main_street,1,39) as main_street,
            SUBSTR(main_city, 1, 29) as main_city,
            SUBSTR(main_state,1,2) as main_state,
            main_zip, user_cat1, alt_id, alt_id|| last_name
                || first_name|| user_id || user_profile || email1 ||
                phone1|| department|| SUBSTR(main_street,1,39)||
            SUBSTR(main_city, 1, 29) || SUBSTR(main_state,1,2)
            || main_zip || user_cat1
                as hash
                from users_new) f
                using(alt_id)
                where f.hash != a.hash"""
        ).fetchall()
        print('\tMarking ' + str(len(user_list)) + ' users to be Updated')
        self.sqlite3_cursor.executemany(
                """insert into ill_update(alt_id, last_name, first_name,
                user_id, user_profile, email1, phone1, department, main_street,
                main_city, main_state, main_zip, user_cat1)
                values(?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?, ?, ?)""",
                user_list,
            )

    def update_tables(self, user_list):
        """This function updates two user management update_tables,
        users_old contains the imported users from the previous
        users_new contains the new users that are being imported

        Parameters:
        user_list: List containing parsed user data to be passed into SQLite3

        Returns:
        None
        """

        # Create users_new table if it doesn't exist,
        # typically during first run
        self.sqlite3_cursor.execute(
            """create table if not exists
                           users_new (user_id, alt_id, user_name_full,
                                      first_name, middle_name, last_name,
                                      user_profile, user_cat1,
                                      user_cat2, major, user_cat3,
                                      department, phone1, main_street,
                                      main_city, main_state, main_zip,
                                      email1, userdata)"""
        )

        print("\tClearing users_old")
        self.sqlite3_cursor.execute("""delete from users_old""").fetchall()

        print("\tGetting current ILLiad Users")
        ill_users = self.ill_cursor.execute("""SELECT UserName, LastName, FirstName, SSN,
                Status, EMailAddress, Phone, Department, Address, City, State,
                Zip, Site from Users""").fetchall()

        print("\tInserting " + str(len(ill_users)) + " users into users_old")
        self.sqlite3_cursor.executemany("""insert into users_old
        (alt_id, last_name, first_name, user_id,
            user_profile, email1, phone1, department,
            main_street, main_city, main_state,
            main_zip, user_cat1)
            values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", ill_users)

        # # Clear out users_new and import new users from user_list
        print("\tClearing users_new")
        self.sqlite3_cursor.execute("""DELETE from users_new""")
        print("\tInserting " + str(len(user_list)) + " users into users_new")
        self.sqlite3_cursor.executemany(
                        """insert into users_new values(?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?,
                        ?, ?, ?, ?, ?, ?, ?, ?)""",
                        user_list,
                    )

    def add_users(self):
        """This function performs user additions to the ILLiad database
           by querying the local SQLite3 ill_add table

        Parameters:
        None

        Returns:
        None
        """

        user_adds = self.sqlite3_cursor.execute(
            """select alt_id, last_name, first_name, user_id, user_profile,
            email1, phone1, department, SUBSTR(main_street,1,39),
            SUBSTR(main_city, 1, 29), SUBSTR(main_state,1,2),
            main_zip, user_cat1 from ill_add"""
        ).fetchall()

        ill_users = self.ill_cursor.execute("""select distinct
                                            UserName from users""").fetchall()
        ill_list = []
        for i in ill_users:
            ill_list.append(i[0])

        add_list = []
        add_id = []
        for i in user_adds:
            if i[0] not in ill_list:
                add_list.append(i)
                add_id.append(i[0])

        print('\tAdding ' + str(len(add_list)) + ' users')
        if len(add_list) > 0:
            self.ill_cursor.executemany(
                    """insert into users (UserName, LastName, FirstName, SSN,
                    Status, EMailAddress, Phone, Department, Address, City,
                    State, Zip, Site) values
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", add_list
                )
            for user in add_id:
                self.ill_cursor.execute("""update users
            set LastChangedDate=GETDATE(), NVTGC='ILL', Cleared='Yes',
            Web='Yes',NotificationMethod='Electronic' where UserName = ?
        """, user)

    def remove_users(self):
        """This function performs user removals to the ILLiad database
           by querying the local SQLite3 ill_remove table

        Parameters:
        None

        Returns:
        None
        """

        user_removals = self.sqlite3_cursor.execute(
            """select alt_id from ill_remove"""
        ).fetchall()
        print('\tRemoving ' + str(len(user_removals)) + ' users')
        if len(user_removals) > 0:
            self.ill_cursor.executemany(
                """delete from users where UserName=?""", user_removals)

    def update_users(self):
        """This function performs updates to the ILLiad database by querying
           the local SQLite3 ill_update table

        Parameters:
        None

        Returns:
        None
        """

        user_updates = self.sqlite3_cursor.execute(
            """select last_name, first_name, user_id, user_profile,
            email1, phone1, department, SUBSTR(main_street,1,39),
            SUBSTR(main_city, 1, 29), SUBSTR(main_state,1,2),
            main_zip, user_cat1, alt_id from ill_update"""
        ).fetchall()

        print('\tUpdating ' + str(len(user_updates)) + ' users')
        if len(user_updates) > 0:
            self.ill_cursor.executemany(
                    """update users
                    set LastName=?, FirstName=?, SSN=?, Status=?,
                    EMailAddress=?, Phone=?, Department=?, Address=?, City=?,
                    State=?, Zip=?, Site=? where UserName = ?""",
                    user_updates)

    def finder(self, tree, elmkey):
        """A XML helper function that returns the text of an Element if it exists
        If it is not set it retuns an empty string

        Parameters:
        tree: ElementTree object from which to lookup key
        elmkey: Element object to lookup the text value of from tree

        Returns:
        ret: A string object containing the text value of the ElementTree
            contains "" if lookup is fails
        """

        tmp = tree.find(elmkey)
        if tmp is not None:
            ret = tmp.text
        else:
            ret = ""
        return ret

    def getuser(self, user, cat2dict={}, cat3dict={}):
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
        ouNetID = self.finder(user, "primary_id")
        firstName = self.finder(user, "first_name")
        middleName = self.finder(user, "middle_name")
        lastName = self.finder(user, "last_name")
        userGroup = self.finder(user, "user_group")
        contact_info = user.findall("./contact_info/addresses/*")
        email_info = user.findall("./contact_info/emails/*")
        phone_info = user.findall("./contact_info/phones/*")
        id_prefix = "./user_identifiers/user_identifier"
        id_type = self.finder(user, id_prefix + "/id_type")
        id_val = self.finder(user, id_prefix + "/value")
        stats_info = user.findall("./user_statistics/user_statistic")
        cats = {}
        for i in contact_info:
            if i.attrib["preferred"] == "true":
                city = self.finder(i, "city")
                line1 = self.finder(i, "line1")
                state = self.finder(i, "state_province")
                postalCode = self.finder(i, "postal_code")

        for i in email_info:
            if i.attrib["preferred"] == "true":
                email = self.finder(i, "email_address")

        for i in phone_info:
            if i.attrib["preferred"] == "true":
                phone = self.finder(i, "phone_number")

        for i in stats_info:
            tmparr = self.finder(i, "statistic_category").split(":")
            cats[tmparr[0]] = tmparr[1]

        if id_type == "BARCODE":
            barcode = id_val

        usercat1 = cats.get("CAT1")
        usercat2 = cats.get("CAT2")
        usercat3 = cats.get("CAT3")
        usercat2der = cat2dict.get(usercat2)
        usercat3der = cat3dict.get(usercat3)
        longline = "|"
        fullName = " "
        fullName = fullName.join([firstName, middleName, lastName])
        new_user = [
            barcode,
            ouNetID,
            fullName,
            firstName,
            middleName,
            lastName,
            userGroup,
            usercat1,
            usercat2,
            usercat2der,
            usercat3,
            usercat3der,
            phone,
            line1,
            city,
            state,
            postalCode,
            email,
        ]

        for i, j in enumerate(new_user):
            if j is None:
                new_user[i] = ""

        new_user.append(longline.join(new_user))
        return new_user

    def close_cnxn(self):
        """Commit transactions and close database
        """
        self.illcnxn.commit()
        self.sqlite3cnxn.commit()
        self.sqlite3cnxn.close()
        self.illcnxn.close()
