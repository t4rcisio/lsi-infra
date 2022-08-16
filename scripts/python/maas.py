import subprocess
import os
from time import sleep



url = "https://github.com/Work-From-Home-Tech/maas.git"


class output_elements:
    ROW="---------------------------------------------------\n"

class color:
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    ORANGE='\033[0;33m'
    BLUE='\033[94m'
    LGREEN='\033[1;32m'


def errorMessage(command, getOut):
    print(f"{color.BLUE} FAIL TO RUN : {command}" )

    if(getOut):
        exit()

def runCommand(command_in):
    cmd_run = command_in
    print(f"DEBUG:\n Running <{command_in}>")
    sleep(2)
    proccess =  subprocess.Popen(cmd_run, shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE,)
    cmd_out, cmd_err = proccess.communicate()

    if(command_in != "yes Y | apt-get upgrade"):
        cmd_out = cmd_out.decode('ascii')
        cmd_err = cmd_err.decode('ascii')
    return cmd_out, cmd_err


def createUser():
    print(f"{color.GREEN}CREATE USER\n")

    print(f"{color.BLUE}USER: ")
    user = input()
    print(f"{color.BLUE}PASSWORD: ")
    pass_0 = input()

    print(f"{color.BLUE}REPEAT PASSWORD: ")
    pass_1 = input()

    print(f"{color.BLUE}MAIL (OPTIONAL): ")
    mail = input()

    return user, pass_0, pass_1, mail


def salveUser(user, password, mail):
    cmd_user = f"yes {user} {password} {password} {mail} | maas createadmin"
    user_done, user_err = runCommand(cmd_user)

def loadInterfaces():
    interface = []
    with open("interfaces") as file:
        interface = file.readlines()

    interface = list(interface)
    
    file.close()
    name = interface[0]
    address = interface[1]
    
    return name, address


def cloneRepo():
    print(f"{color.GREEN}CLONE PLAYBOOK")
    cmd_clone = f"git clone {url}"
    clone_done, clone_err = runCommand(cmd_clone)



def installAnsible():

    print(f"{color.GREEN}INSTALL ANSIBLE")
    cmd_ansible = f"yes 'yes' | apt-get install ansible"
    ansible_done, ansible_err = runCommand(cmd_ansible)


def generatePlaybook():

    print(f"{color.GREEN} REPLACE PLAYBOOK FILE")
    name, address = loadInterfaces()
    file_in = open("./maas/maas-setup.yml", "rt")
    file_ot = open("./maas/maas-lsi.yml", "wt")

    for line in file_in:
        line_st = line.replace('"{{ ansible_default_ipv4.interface  }}"', f'"{name}"')
        line_st = line_st.replace('"{{ ansible_default_ipv4.address }}"', f'"{address}"')
        file_ot.write(line_st)
    
    file_in.close()
    file_ot.close()


def runPlaybook():
    print(f"{color.GREEN}RUN PLAYBOOK")
    cmd_playbook = f"ansible /maas/maas-lsi.yml"
    os.system(cmd_playbook)


print(f"{output_elements.ROW} {color.BLUE}INSTALL AND CONFIGURE MAAS\n {output_elements.ROW}")

cloneRepo()
installAnsible()
generatePlaybook()



verify = True
while verify:

    check_pass = False
    user, pass_0, pass_1, mail = createUser()
    user = user.replace(" ", "")
    if(user == ""):
        print(f"{color.RED} INVALID USER, TRY AGAIN")
    else:
        check_pass = True
    
    if(check_pass):
        pass_0 = pass_0.replace(" ", "")
        pass_1 = pass_1.replace(" ", "")

        if(pass_0 == pass_1):
            verify = False
            print(f"{color.BLUE}{output_elements.ROW}USER: {user}\nPASSWORD: {pass_0}{output_elements.ROW}")
            salveUser(user, pass_0, mail)
            print(f"{color.LGREEN} ALL DONE") 

        else:
            print(f"{color.RED} PASSWORD DOESN'T MATCH, TRY AGAIN")   





