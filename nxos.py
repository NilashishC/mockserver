#!/usr/bin/python
#

import sys
import MockSSH

from twisted.python import log

def conf_output_error(instance):
    instance.writeln("MockSSH: supported usage: conf t")


def conf_output_success(instance):
    instance.writeln("Enter configuration commands, one per line. End "
                     "with CNTL/Z")


def conf_change_protocol_prompt(instance):
    instance.protocol.prompt = "\rNexus9000v(config)#"


command_conf = MockSSH.ArgumentValidatingCommand(
    'conf', [conf_output_success, conf_change_protocol_prompt],
    [conf_output_error], *["t"])


def exit_command_success(instance):
    if 'config' in instance.protocol.prompt:
        instance.protocol.prompt = "\rNexus9000v(config)#"
    else:
        instance.protocol.call_command(instance.protocol.commands['_exit'])


def exit_command_failure(instance):
    instance.writeln("MockSSH: supported usage: exit")


command_exit = MockSSH.ArgumentValidatingCommand('exit', [exit_command_success],
                                                 [exit_command_failure], *[])


class command_username(MockSSH.SSHCommand):
    name = 'username'

    def start(self):
        if 'config' not in self.protocol.prompt:
            self.writeln("MockSSH: Please run the username command in `conf t'")

        if (not len(self.args) == 3 or not self.args[1] == 'password'):
            self.writeln("MockSSH: Supported usage: username "
                         "<username> password <password>")

        self.exit()

class command_show(MockSSH.SSHCommand):
    name = 'show'

    def start(self):
        if 'config' in self.protocol.prompt:
            self.writeln("MockSSH: Please run the show commands in # prompt'")
        
        if len(self.args) < 1:
            self.writeln("\n% Incomplete command at '^' marker.")
        
        else:
            # this part only works with vlans now
            if self.args[0] == "running-config":
                self.writeln(open("runcfg_vlan", "r").read())
            else:
                self.writeln(open("show_{0}".format(self.args[0]), "r").read())

        self.exit()

class command_terminal(MockSSH.SSHCommand):
    name = 'terminal'

    def start(self):
        self.exit()


commands = [
    command_conf, command_username, command_exit, command_show, command_terminal,
]


def main():
    users = {'ansible': 'ansible'}

    log.startLogging(sys.stderr)

    MockSSH.runServer(
        commands, prompt="\rNexus9000v# ", interface='127.0.0.1', port=9999, **users)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("User interrupted")
        sys.exit(1)
