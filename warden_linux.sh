#! /bin/bash

#remove log files if present
find . -name \*.log -exec mv {} warden.log_old \;

#check for arguments to pass
ARG=$1

#execute the main python module, pass the arguments
python2 main $ARG

#after execution, remove compiled .pyc files
find . -name \*.pyc -exec rm {} \;
