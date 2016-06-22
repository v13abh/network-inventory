#network_inventory.py - Connect to a network device and pull serial number for inventory count

import paramiko 
import time
import re
import getpass

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # Not a secure implementation. Check you destination IP addresses!

username = input('Username: ')

# Function to hide password entry on the screen 
def enterPassword(): 
  while True: 
    password = getpass.getpass('Enter password:')
    passwordConfirm = getpass.getpass('Confirm password:')
    if password != passwordConfirm:
      print ('Passwords do not match. Please try again.')
    else:
      return password

password = enterPassword()

infile = input('IP Address Filename: ')
outfile = input('Output Filename: ')

# Open specified IP address file, import addresses into list, close file when complete
with open(infile, encoding='utf-8') as f: 
    ip = [x.strip('\n') for x in f.readlines()]
    print('\nImporting IP Address List from %s.\n' % infile)
    switchCount = len(ip)
    print('%d IP Addresses imported.\n' % switchCount)

# Create a file with user provided name, write required data, close when complete
# And for each IP address in list, connect and pull hostname and serial numbers of each switch in stack and place in output file
with open(outfile, 'w', encoding='utf-8') as f: 
    for i in range(switchCount): 
        ssh.connect(ip[i], username=username, password=password)
        print('Connecting to ' + ip[i] + '...')

        shell = ssh.invoke_shell()

        shell.send('\n')
        output = repr(shell.recv(50))
        hostname = re.findall(r'(?<=^).*?(?=#)', output)
        f.write('\n' + hostname[0] + ' ')
        
        shell.send('show version | include System Serial\n')

        time.sleep(5)

        output = repr(shell.recv(500))
        serial = re.findall(r'(?<=: ).*?(?=\W)', output)

        serialCount = len(serial)

        for i in range(serialCount):
            f.write(serial[i] + ' ')

        print(serial)

        
print('Complete!')

ssh.close()
