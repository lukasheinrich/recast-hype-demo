#!/bin/zsh

#fail on any error
set -e 

#check for valid kerberos ticket
klist -s
if [ $? -eq 0 ];then
  echo "we have a valid kerberos ticket. continue."
else
  echo "no valid kerberos ticket. exit."
  exit 1
fi

svn co svn+ssh://svn.cern.ch/reps/atlas-dgillber/dgillber/HiggsPlusJets/Hype_Project/hype implementation/hype
(cd implementation/hype && make)

