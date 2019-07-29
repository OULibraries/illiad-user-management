import sqlite3

"""
This object contains functions to perform user updates/imports into ILLiad
Actual ILLiad Database updates still need to be implemented,
but this module will generate the framework of what actions need to be taken.

The following functions exist:

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

"""


class illiad_manager:
    def __init__(self):
        self.cnxn = sqlite3.connect("sqlite.db")
        self.cursor = self.cnxn.cursor()

    def gen_user_adds(self):
        """This function creates a table containg entries to be added in ILLiad
        These entries are calculated by finding entries present in users_new
        that are not present in users_old.

        Parameters:
        None

        Returns:
        None
        """

        self.cursor.execute(
            """create table if not exists
                           ill_add (user_id, alt_id, user_name_full,
                                      first_name, middle_name, last_name,
                                      user_profile, user_cat1,
                                      user_cat2, major, user_cat3,
                                      department, phone1, main_street,
                                      main_city, main_state, main_zip,
                                      email1, userdata)"""
        )
        self.cursor.execute("""delete from ill_add""")
        user_list = self.cursor.execute(
            """select * from (SELECT DISTINCT user_id
                                                     FROM USERS_NEW
                                                     WHERE user_id Not IN
                                                    (SELECT DISTINCT user_id
                                                    FROM USERS_OLD)) f
                                    join USERS_NEW using(USER_ID)"""
        ).fetchall()
        for single_user in user_list:
            self.cursor.execute(
                """insert into ill_add values(?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?,
                      ?, ?, ?, ?, ?, ?, ?, ?)""",
                single_user,
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

        self.cursor.execute(
            """create table if not exists
                           ill_remove (user_id, alt_id, user_name_full,
                                      first_name, middle_name, last_name,
                                      user_profile, user_cat1,
                                      user_cat2, major, user_cat3,
                                      department, phone1, main_street,
                                      main_city, main_state, main_zip,
                                      email1, userdata)"""
        )
        self.cursor.execute("""delete from ill_remove""")
        user_list = self.cursor.execute(
            """select * from (SELECT DISTINCT user_id
                                                     FROM USERS_OLD
                                                     WHERE user_id Not IN
                                                    (SELECT DISTINCT user_id
                                                    FROM USERS_NEW)) f
                                    join USERS_OLD using(USER_ID)"""
        ).fetchall()
        for single_user in user_list:
            self.cursor.execute(
                """insert into ill_remove values(?, ?, ?, ?, ?, ?, ?, ?, ?,?,
                      ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                single_user,
            )

    def gen_user_updates(self):
        """This function creates a table containg metadata updates
        for existing users in ILLiad

        Parameters:
        None

        Returns:
        None
        """

        self.cursor.execute(
            """create table if not exists
                           ill_update (user_id, alt_id, user_name_full,
                                      first_name, middle_name, last_name,
                                      user_profile, user_cat1,
                                      user_cat2, major, user_cat3,
                                      department, phone1, main_street,
                                      main_city, main_state, main_zip,
                                      email1, userdata)"""
        )
        self.cursor.execute("""delete from ill_update""")
        user_list = self.cursor.execute(
            """SELECT distinct f.*
                                      FROM USERS_OLD as a
                                      join (select * from users_new) f
                                      on a.user_id = f.user_id
                                      where f.userdata != a.userdata"""
        ).fetchall()
        for single_user in user_list:
            self.cursor.execute(
                """insert into ill_update values(?, ?, ?, ?, ?, ?, ?, ?, ?,?,
                      ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                single_user,
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
        self.cursor.execute(
            """create table if not exists
                           users_new (user_id, alt_id, user_name_full,
                                      first_name, middle_name, last_name,
                                      user_profile, user_cat1,
                                      user_cat2, major, user_cat3,
                                      department, phone1, main_street,
                                      main_city, main_state, main_zip,
                                      email1, userdata)"""
        )
        # users_new becomes users_old,
        # so users_old is dropped and remade from users_new
        self.cursor.execute("""drop table if exists users_old""")
        self.cursor.execute("""create table users_old as select *
                            from users_new""")

        # Clear out users_new and import new users from user_list
        self.cursor.execute("""DELETE from users_new""")

        for single_user in user_list:
            self.cursor.execute(
                """insert into users_new values(?, ?, ?, ?, ?, ?, ?, ?, ?,?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?)""",
                single_user,
            )

    def close_cnxn(self):
        """Commit transactions and close database
        """
        self.cnxn.commit()
        self.cnxn.close()
