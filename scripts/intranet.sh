#!/bin/bash



printf "\n${BLUE}${ROW}\n\t${ORANGE} CONFIG INTERFACE TO START INTRANET\n${BLUE}${ROW}\n"

printf "\n\t${LGREEN} IDENTIFYING PHYSICAL INTERFACES\n"
ls -l /sys/class/net/ | grep -v virtual | awk -F " " '{print $9}' > interfaces.txt



printf "\n${BLUE} [0] ${RED}${net1}"
printf "\n${BLUE} [1] ${RED}${net2}"

printf "\n\n\t${LGREEN} SELECT INTERFACE TO CONFIGURE INTRANET\n"



echo \n
