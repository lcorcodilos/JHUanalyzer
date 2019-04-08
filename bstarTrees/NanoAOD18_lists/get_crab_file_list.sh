#!/bin/bash
#set -x 

list_files()
{
    local files=`xrdfs root://cmseos.fnal.gov ls  $1`
    for file in $files
    do
        if [[ $file == *.root ]];
        then
            echo root://cmseos.fnal.gov/$file
        elif [[ $file != *log* ]] && [[ $file != *fail* ]] ; 
        then
            list_files $file
        fi
    done
}
        

        
list_files $1


