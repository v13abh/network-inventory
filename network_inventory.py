#network_inventory.py - Connect to a network device and pull serial number for inventory count

import paramiko
import time
import re
from getpass import getpass

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # Not a secure implementation. Check you destination IP addresses!

username = input('Username: ')


# Function to hide password entry on the screen
def enterPassword():
    while True:
        password = getpass('Enter password:')
        if password == getpass('Confirm password:'):
            return password
        print('Passwords do not match. Please try again.')

password = enterPassword()

infile = input('IP Address Filename: ')
outfile = input('Output Filename: ')

# Open specified IP address file, import addresses into list, close file when complete
with open(infile, 'r', encoding='utf-8') as f:
    ipAddresses = [line for line in f.read().splitlines()]
    print('\nImporting IP Address List from %s.\n' % infile)
    print('%d IP Addresses imported.\n' % len(ipAddresses))

# Create a file with user provided name, write required data, close when complete
# And for each IP address in list, connect and pull hostname and serial numbers of each switch in stack and place in output file
with open(outfile, 'w', encoding='utf-8') as f:
    for ipAddress in ipAddresses:
        ssh.connect(ipAddress, username=username, password=password)
        print('Connecting to %s...' % ipAddress)

        shell = ssh.invoke_shell()

        shell.send('\n')
        output = repr(shell.recv(50))
        hostname = re.findall(r'(?<=^).*?(?=#)', output)
        f.write('\n%s ' % hostname[0])

        shell.send('show version | include System Serial\n')

        time.sleep(5)

        output = repr(shell.recv(500))
        serials = re.findall(r'(?<=: ).*?(?=\W)', output)

        for serial in serials:
            f.write('%s ' % serial)

        print(serials)

print('Complete!')

ssh.close()