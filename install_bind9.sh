#!/bin/sh

# Exit when any command fails
set -e

# Check if domain and IP were passed as parameters, otherwise prompt
if [ $# -eq 0 ]; then
	read -p 'Domain: ' DOMAIN
	IP=$(ifconfig | awk 'sub(/inet addr:/,""){print $1; exit;}')
elif [ $# -eq 1 ]; then
	DOMAIN=$1
	IP=$(ifconfig | awk 'sub(/inet addr:/,""){print $1; exit;}')
elif [ $# -eq 2 ]; then
	DOMAIN=$1
	IP=$2
fi

# Get up to date
apt-get update && apt-get -y upgrade

# Install Bind
apt-get -y install bind9

# Create a zone for your domain
cat > /etc/bind/named.conf.local << EOT
//
// Do any local configuration here
//

// Consider adding the 1918 zones here, if they are not used in your
// organization
//include "/etc/bind/zones.rfc1918";

zone "$DOMAIN" {
    type master;
    file "/etc/bind/zones/$DOMAIN.zone"; # zone file path
};
EOT

# Create a directory to store zone configs
mkdir /etc/bind/zones

# Create zone file for your domain
cat > /etc/bind/zones/$DOMAIN.zone << EOT
\$TTL    604800
@       IN      SOA     ns1.$DOMAIN. $DOMAIN. (
                  3       ; Serial
             604800     ; Refresh
              86400     ; Retry
            2419200     ; Expire
             604800 )   ; Negative Cache TTL
;
; name servers - NS records
     IN      NS      ns1.$DOMAIN.

; name servers - A records
ns1.$DOMAIN.          IN      A       $IP

; TXT records
test IN TXT "This is a test"
EOT

# Edit configuration to disable forwarders (prevent abuse)
# and bind to the IP address specified
cat > /etc/bind/named.conf.options << EOT
options {
	directory "/var/cache/bind";

	// If there is a firewall between you and nameservers you want
	// to talk to, you may need to fix the firewall to allow multiple
	// ports to talk.  See http://www.kb.cert.org/vuls/id/800113

	// If your ISP provided one or more IP addresses for stable 
	// nameservers, you probably want to use them as forwarders.  
	// Uncomment the following block, and insert the addresses replacing 
	// the all-0's placeholder.

	//forwarders {
	//	8.8.8.8;
	//	8.8.4.4;
	//};

	//========================================================================
	// If BIND logs error messages about the root key being expired,
	// you will need to update your keys.  See https://www.isc.org/bind-keys
	//========================================================================
	//dnssec-validation auto;

	auth-nxdomain no;    # conform to RFC1035
	//listen-on-v6 { any; };
	listen-on { $IP; };
	allow-transfer { none; };
};
EOT

# Restart the service
service bind9 restart
