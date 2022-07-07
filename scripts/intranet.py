import os
import subprocess
from time import sleep
import yaml
import time


DEFAULT_ADDRESS = "10.10.10.1/24"

class output_elements:
    ROW="---------------------------------------------------\n"

class color:
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    ORANGE='\033[0;33m'
    BLUE='\033[94m'
    LGREEN='\033[1;32m'

yaml_Static = '''
### WAN INTERFACE {interface} STATIC
 {interface}:
  addresses:
   - {DEFAULT_ADDRESS}

'''

yaml_DHCP= '''
### WAN INTERFACE {interface} DHCP
 {interface}:
  dhcp4: yes
'''

process_status = 0

def animation():
    animation = "|/-\\"
    idx = 0
    while  not process_status:
        print(animation[idx % len(animation)], end="\r")
        idx += 1
        time.sleep(0.1)



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

def updateSys():
    runCommand("yes Y | apt-get update")
    runCommand("yes Y | apt-get upgrade")

sudoCheck()

file_name = "intranet.yaml"
cmd_delete = f"rm {file_name}"
runCommand(cmd_delete)

updateSys()



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

nodes = {}

## GERA O ARQUIVO DE CONFIGURAÇÃO
index = 0
for interface in interfaces:
    
    if(interface == router):
       config = {'addresses': [DEFAULT_ADDRESS]}
       nodes[interface] = config
    else:
        config = {'dhcp4': '''yes'''}
        nodes[interface] = config


yaml_config = {'network':{'version': 2,'renderer': 'networkd', 'ethernets': nodes}}
yaml_file = yaml.safe_dump(yaml_config, file)


file.close()

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


cmd_np = f"netplan apply "
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


print(color.BLUE + "\tTESTING CONNECTION\n")
cmd_dns = "ping 8.8.8.8 -c 5"
dns_out, dns_err = runCommand(cmd_dns)

print(dns_out)

print(color.BLUE + "\tENABLE IPV4 FORWARDING\n")
cmd_ip4="echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf"
runCommand(cmd_ip4)

cmd_ip4_appy = "sysctl -p"
runCommand(cmd_ip4_appy)


cmd_ip4_check = "tail -n 1 /etc/sysctl.conf"
check_out, check_err = runCommand(cmd_ip4_check)

if(check_out != "net.ipv4.ip_forward=1\n"):
    print(color.RED+ "\tFAIL TO CHANGE IPV4 FORWARDING, TRY : add net.ipv4.ip_forward=1 on /etc/sysctl.conf\n")
    exit(0)


cmd_i_iptables = "yes Y | apt-get install iptables-persistent -y"
ipt_done, ipt_err = runCommand(cmd_i_iptables)

if(ipt_err !=""):
    updateSys()
    ipt_done, ipt_err = runCommand(cmd_i_iptables)


if(ipt_err !=""):
    print(color.RED + "\tFAIL TO INSTALL "+color.RED+"iptables-persistent\n")
    exit(0)


print(color.BLUE + "\tCONFIGURE IPTABLES\n")
cmd_ipt_0 = "iptables -t nat -A POSTROUTING -j MASQUERADE"
ipt_done, ipt_err = runCommand(cmd_ipt_0)

if(ipt_err !=""):
    print(color.RED + f"\tFAIL TO CONFIGURE IPTABLE: $ {cmd_ipt_0}\n")
    exit(0)

print(color.BLUE + "\tSAVE IPTABLES\n")
cmd_ipt_save = "iptables-save > /etc/iptables/rules.v4"
ipt_done, ipt_err = runCommand(cmd_ipt_save)

if(ipt_err !=""):
    print(color.RED + f"\tFAIL TO CONFIGURE IPTABLE: $ {cmd_ipt_save}\n")
    exit(0)


cmd_dns_0 =  'rm -f /etc/resolv.conf'
runCommand(cmd_dns_0)
sleep(3)
cmd_dns_1 = 'ln -s /run/systemd/resolve/resolv.conf /etc/resolv.conf'
runCommand(cmd_dns_1)


print(color.BLUE + "\tTESTING CONNECTION\n")
cmd_dns = "ping google.com -c 5"
dns_out, dns_err = runCommand(cmd_dns)
print(dns_out)

print(color.BLUE + f"\tALL DONE!\n")

print(color.RED + f"\tRESTARTING...!\n")

runCommand("reboot")


