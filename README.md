Nucleator OpenVPN
=================

This Stackset is currently under development.

Nucleator OpenVPN is a Nucleator stackset that provisions and configures an OpenVPN Server within the specified Nucleator Cage.  The OpenVPN Server is configued to use two factor authentication using Google Authenticator.

You can use nucleator openvpn to enable communication into a Nucleator Cage from external hosts that are running a free gui-based OpenVPN client such as TunnelBlick, OpenVPN (gui for Windows PCs) or OpenVPN Connect (gui for iOs and Android devices).

OpenVPN setup is based on Mike Jones' excellent post: http://www.mikejonesey.co.uk/security/2fa/openvpn-with-2fa.  His mikejonesey.openvpn-2fa ansible role is downloaded as a dependency via ansible galaxy.  

To see the full list of supported options, use the command:

> nucleator openvpn --help
