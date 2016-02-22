Nucleator OpenVPN
=================

Nucleator OpenVPN is a Nucleator stackset that provisions and configures an OpenVPN Server within the specified Nucleator Cage.  The OpenVPN Server is configured to use two factor authentication using Google Authenticator.

You can use nucleator openvpn to enable communication into a Nucleator Cage from external hosts that are running a free gui-based OpenVPN client such as Tunnelblick, OpenVPN (gui for Windows PCs) or OpenVPN Connect (gui for iOS and Android devices).

OpenVPN setup is based on [Mike Jones' excellent post](http://www.mikejonesey.co.uk/security/2fa/openvpn-with-2fa).  His mikejonesey.openvpn-2fa ansible role is downloaded as a dependency via ansible galaxy.

To see the full list of supported options, use the command:

> nucleator openvpn --help

The most common usages are:

`nucleator openvpn provision` \  
	`--customer` *customername* \  
    `--cage` *cagename* \  
    `--name` *vpn_server_name*

`nucleator openvpn configure` \  
	`--customer` *customername* \    
    `--cage` *cagename* \  
    `--name` *vpn_server_name*

`nucleator openvpn delete` \  
	`--customer` *customername* \    
    `--cage` *cagename* \  
    `--name` *vpn_server_name*

Once the configure step has run sufficiently, you will find a client.tar.gz in the Downloads folder of your home directory.  Unpack that file to get the VPN configuration files you will need for an application such as Tunnelblick.

