# Copyright 2015 47Lining LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from nucleator.cli.utils import ValidateCustomerAction
from nucleator.cli.command import Command
from nucleator.cli import properties
from nucleator.cli import ansible
import re, string, argparse


def validate_instance_type(instance_type_name):
    # TODO - would be nice to validate & catch errs in instance type vocabulay here
    return None if True else "Instance Type Error Message"


class ValidateInstanceTypeAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        error_msg = validate_instance_type(values)
        if error_msg:
            parser.error(error_msg)
        else:
            setattr(namespace, self.dest, values)


class Openvpn(Command):

    name = "openvpn"
    default_openvpn_instance_type = "t2.micro"

    def parser_init(self, subparsers):
        """
        Initialize parsers for this command.
        """
        # add parser for openvpn command
        openvpn_parser = subparsers.add_parser('openvpn')
        openvpn_subparsers = openvpn_parser.add_subparsers(dest="subcommand")

        # provision subcommand
        openvpn_provision = openvpn_subparsers.add_parser('provision', help="Provision a new nucleator openvpn stackset")
        openvpn_provision.add_argument("--customer", required=True, action=ValidateCustomerAction, help="Name of customer from nucleator config")
        openvpn_provision.add_argument("--cage", required=True, help="Name of cage from nucleator config")
        openvpn_provision.add_argument("--instance-type", required=False, default=self.default_openvpn_instance_type, action=ValidateInstanceTypeAction, help="ec2 instance type, (default: '{0}')".format(self.default_openvpn_instance_type))
        openvpn_provision.add_argument("--name", required=True, help="Instance name of openvpn stackset to provision")

        # configure subcommand
        openvpn_configure = openvpn_subparsers.add_parser('configure', help="Configure a new nucleator openvpn stackset")
        openvpn_configure.add_argument("--customer", required=True, action=ValidateCustomerAction, help="Name of customer from nucleator config")
        openvpn_configure.add_argument("--cage", required=True, help="Name of cage from nucleator config")
        openvpn_configure.add_argument("--name", required=True, help="Instance name of openvpn stackset to configure")

        # delete subcommand
        openvpn_delete = openvpn_subparsers.add_parser('delete', help="delete specified nucleator openvpn stackset")
        openvpn_delete.add_argument("--customer", action=ValidateCustomerAction, required=True, help="Name of customer from nucleator config")
        openvpn_delete.add_argument("--cage", required=True, help="Name of cage from nucleator config")
        openvpn_delete.add_argument("--name", required=True, help="Instance name of openvpn stackset to delete")

    def provision(self, **kwargs):
        """
        This command provisions a new openvpn compute instance in the indicated Customer Cage.
        """
        cli = Command.get_cli(kwargs)
        cage = kwargs.get("cage", None)
        customer = kwargs.get("customer", None)
        if cage is None or customer is None:
            raise ValueError("cage and customer must be specified")
        extra_vars = {
            "cage_name": cage,
            "customer_name": customer,
            "verbosity": kwargs.get("verbosity", None),
            "debug_credentials": kwargs.get("debug_credentials", None),
        }

        extra_vars["openvpn_deleting"] = kwargs.get("openvpn_deleting", False)

        name = kwargs.get("name", None)
        if name is None:
            raise ValueError("name must be specified")
        self.validate_name(name)
        extra_vars["name"] = name

        extra_vars["cli_stackset_name"] = "openvpn"
        extra_vars["cli_stackset_instance_name"] = name

        instance_type = kwargs.get("instance_type", None)
        extra_vars["openvpn_instance_type"] = instance_type

        command_list = []
        command_list.append("account")
        command_list.append("cage")
        command_list.append("openvpn")

        cli.obtain_credentials(commands=command_list, cage=cage, customer=customer, verbosity=kwargs.get("verbosity", None), debug_credentials=kwargs.get("debug_credentials", None))

        return cli.safe_playbook(self.get_command_playbook("openvpn_provision.yml"),
                                 is_static=True,  # dynamic inventory not required
                                 **extra_vars
                                 )

    def configure(self, **kwargs):
        """
        This command configures the specified openvpn stackset in the indicated Customer Cage.
        """
        cli = Command.get_cli(kwargs)
        cage = kwargs.get("cage", None)
        customer = kwargs.get("customer", None)
        if cage is None or customer is None:
            raise ValueError("cage and customer must be specified")
        extra_vars = {
            "cage_name": cage,
            "customer_name": customer,
            "verbosity": kwargs.get("verbosity", None),
            "debug_credentials": kwargs.get("debug_credentials", None),
        }

        name = kwargs.get("name", None)
        if name is None:
            raise ValueError("name must be specified")
        self.validate_name(name)
        extra_vars["name"] = name

        extra_vars["cli_stackset_name"] = "openvpn"
        extra_vars["cli_stackset_instance_name"] = name

        # Used by the openvpn-2fa role
        extra_vars["EASYRSA_REQ_ORG"] = kwargs.get("rsa_org", customer)
        extra_vars["EASYRSA_REQ_EMAIL"] = kwargs.get("rsa_email", "{0}@{1}".format(cage, customer))
        extra_vars["EASYRSA_REQ_OU"] = kwargs.get("rsa_ou", "{0} {0} cage".format(customer, cage))

        command_list = []
        command_list.append("account")
        command_list.append("cage")
        command_list.append("openvpn")

        inventory_manager_rolename = "NucleatorOpenvpnInventoryManager"

        cli.obtain_credentials(commands=command_list, cage=cage, customer=customer, verbosity=kwargs.get("verbosity", None), debug_credentials=kwargs.get("debug_credentials", None))

        return cli.safe_playbook(
            self.get_command_playbook("openvpn_configure.yml"),
            inventory_manager_rolename,
            **extra_vars
        )

    def validate_name(self, value):
        alphanum = re.compile("^[a-z0-9]*$")
        if alphanum.match(value) is None:
            raise ValueError("Invalid stackset instance name - only lowercase alphanumeric characters are allowed")
        if len(value) < 1 or len(value) > 63:
            raise ValueError("Invalid stackset instance name - must be from 1 to 63 characters")
        if not value[0] in string.ascii_lowercase:
            raise ValueError("Invalid stackset instance name - must begin with a lowercase letter")
        if value.find("--") > -1:
            raise ValueError("Invalid stackset instance name - cannot contain consecutive dashes")
        if value[-1] == '-':
            raise ValueError("Invalid stackset instance name - cannot end with a dash")

    def delete(self, **kwargs):
        """
        This command deletes a previously provisioned Openvpn from the indicated Customer Cage.
        """

        kwargs["openvpn_deleting"] = True

        return self.provision(**kwargs)


# Create the singleton for auto-discovery
command = Openvpn()
