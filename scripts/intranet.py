import os
import subprocess


DEFAULT_ADDRESS = "10.0.10.1/24"

class output_elements:
    ROW="---------------------------------------------------\n"

class color:
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    ORANGE='\033[0;33m'
    BLUE='\033[94m'
    LGREEN='\033[1;32m'



def runCommand(command_in):
    cmd_run = command_in
    proccess =  subprocess.Popen(cmd_run, shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cmd_out, cmd_err = proccess.communicate()

    cmd_out = cmd_out.decode('ascii')
    cmd_err = cmd_err.decode('ascii')

    return cmd_out, cmd_err


def sudoCheck():
    cmd_su = "echo 'root test' > /etc/__rootAccess__"
    su_out, su_err = runCommand(cmd_su)

    if(su_err !=""):
        print(f"{color.RED} RUN WITH SUPERUSER PERMISSIONS ! ")
        exit(0)
    else:
        cmd_su = "rm /etc/__rootAccess__"
        runCommand(cmd_su)

def showInterfaces(interfaces):
    index=0
    for interface in interfaces:
        cmd_ip = " ip -f inet addr show "+ interface +" | awk '/inet / {print $2}'"
        ip_out, ip_err = runCommand(cmd_ip)

        address = ip_out

        if(ip_out == ""):
            address = f"{color.RED} UNDEFINED"
        
        if(ip_err !=""):
            address = f"{color.RED} {ip_err}"
    
        print(f"{color.LGREEN}[{index}] {interface}\n\n IP ADDRESS: {color.BLUE}{address}")
        index +=1



sudoCheck()

file_name = "intranet.yaml"
cmd_delete = f"rm {file_name}"
runCommand(cmd_delete)

print(color.RED + output_elements.ROW + color.BLUE + "\t\tLSI - CEFET-MG")
print(color.RED + output_elements.ROW + color.BLUE + "\tCONFIGURING NETWORKING INTERFACE\n" + color.RED + output_elements.ROW )



print(color.LGREEN + "\tIDENTIFYING PHYSICAL INTERFACES\n")


cmd_LAN='''ls -l /sys/class/net/ | grep -v virtual | awk -F " " '{print $9}' > interfaces'''
runCommand(cmd_LAN)

interfaces = []

with open("interfaces") as file:
    interfaces = file.readlines()

interfaces = list(interfaces)

#Remove empty interfaces
for interface in interfaces:
    if(interface == "\n"):
        interfaces.remove(interface)

#Remove \n from lines
index = 0
for interface in interfaces:
    interfaces[index] = interfaces[index].replace("\n", "")
    index +=1


## SHOW INTERFACES
showInterfaces(interfaces)

print("\tSELECT INTERFACE TO CONFIGURE INTRANET\n")
index = int(input())
if(index < 0 or index > len(interfaces)):
    print(f"{color.RED} Interface inválida")
    exit(0)

router = interfaces[index]

print(color.BLUE + "\tGENERATING FILE CONFIGUARTION\n")
file = open(file_name, "w")
file.write("ethernets:\n")

## GERA O ARQUIVO DE CONFIGURAÇÃO
index = 0
for interface in interfaces:
    
    if(interface == router):
        file.write(f"### WAN INTERFACE {interface} STATIC\n")
        file.write("\t"+interface+":\n")
        file.write("\t\taddresses:\n")
        file.write(f"\t\t\t- {DEFAULT_ADDRESS}\n")
    else:
        file.write(f"### WAN INTERFACE {interface} DHCP\n")
        file.write("\t"+interface+":\n")
        file.write("\t\tdhcp4: yes\n")


## COPIA O ARQUIVO PARA A PATA DETINO
cmd_cp = f"cp {file_name} /etc/netplan/ "
cp_out, cp_err = runCommand(cmd_cp)

if(cp_err !=""):
    print(f"{color.RED} Failed to copy file. ERROR: {cp_err}")
    exit(0)

print(color.BLUE + "\t\nAPPLY CONFIGURATION AND RESTARTING SERVICES")

done = os.path.exists("/etc/netplan/"+file_name)

if(not done):
     print(f"{color.RED} ERROR: Unable to check /etc/netplan/"+file_name)
     exit(0)


cmd_np = f"netplay apply "
np_out, np_err = runCommand(cmd_np)


if(np_err !=""):
     print(f"{color.RED} Failed to run {cmd_np}\n\t ERROR: {np_err}")
     exit(0)

showInterfaces(interfaces)

print(f"{color.GREEN}\tIS RIGHT? [0] NO [1] YES\n")
response = int(input())

if(not response):
    print(f"{color.RED} failed do apply changes")
    exit(0)










