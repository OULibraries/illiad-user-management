#!/bin/sh


source conf.sh

cd "${INSTAL_PATH}"
rsync -avP "${DATA_SRC}/lib_emp.txt" "${INSTALL_PATH}/lib_emp.txt"
rsync -avP "${DATA_SRC}/lib_stu.txt" "${INSTALL_PATH}/lib_stu.txt"
python3 im_import.py > im_output.txt
wait
python3 sendemail.py
