# written by Lucas

import os, sys, StringIO, subprocess
from termcolor import colored, cprint
# import shlex

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

adb = '/Applications/Android-SDK/platform-tools/adb'

FAILURE_STATUS = ['offline', 'unauthorized']

NO_MULTI_COMMAND = ['start-server', 'kill-server', 'connect', 'disconnect', 'help', 'version', 'ppp', 'root', 'unroot', 'usb', 'tcpip']

def format(fg=None, bg=None, bright=False, bold=False, dim=False, reset=False):
    # manually derived from http://en.wikipedia.org/wiki/ANSI_escape_code#Codes
    codes = []
    if reset:
        codes.append("0")
    else:
        if not fg is None: codes.append("3%d" % (fg))
        # if not fg is None: codes.append("38;5;100")
        if not bg is None:
            if not bright:
                codes.append("4%d" % (bg))
            else:
                codes.append("10%d" % (bg))
        if bold:
            codes.append("1")
        elif dim:
            codes.append("2")
        else:
            codes.append("22")
    return "\033[%sm" % (";".join(codes))

def multi_cmd(run_cmd):
    # adb get serial no
    devices = os.popen(adb + " devices | sed '1,1d' | sed '$d' | cut -f 1").read().splitlines()
    # print devices
    for device in devices[:]:
        if device.startswith('*') and device.endswith('*'):
            print device
            devices.remove(device)
    # adb get-state
    devices_status = os.popen(adb + " devices | sed '1,1d' | sed '$d' | cut -f 2").read().splitlines()

    # print devices
    # print devices_status
    devices_number = len(devices);

    if devices_number == 0:
        print 'No emulators or devices detected - nothing to do.'
    elif devices_number == 1 and run_cmd:
        subprocess.call(cmd)
    else:
        devices_model_name = []
        devices_versions = []
        fornum = 0
        for device in devices:
            if FAILURE_STATUS.count(devices_status[fornum]) == 0:
                # model_name_cmd = adb + ' devices | grep ' + device + r' | cut -f 1 | xargs -I $ ' + adb + ' -s $ shell cat /system/build.prop | grep "ro.product.model" | cut -d "=" -f 2 | tr -d ' + r'" \r\t\n"'
                model_name_cmd = adb + ' devices | grep ' + device + r' | cut -f 1 | xargs -I $ ' + adb + ' -s $ shell getprop ro.product.model'
                # platform_versions_cmd = adb + ' devices | grep ' + device + r' | cut -f 1 | xargs -I $ ' + adb + ' -s $ shell cat /system/build.prop | grep "ro.build.version.release" | cut -d "=" -f 2 | tr -d ' + r'"\r\t\n"'
                platform_versions_cmd = adb + ' devices | grep ' + device + r' | cut -f 1 | xargs -I $ ' + adb + ' -s $ shell getprop ro.build.version.release'
                devices_model_name.append(os.popen(model_name_cmd).read())
                devices_versions.append(os.popen(platform_versions_cmd).read())
            else:
                devices_model_name.append(devices_status[fornum])
                devices_versions.append(devices_status[fornum])
            fornum += 1
        # print devices_model_name
        # print devices_versions
        if run_cmd:
            print 'Multiple devices detected, please select one'
        else:
            print 'List of devices attached'
        num = 1
        for device in devices:
            linebuf = StringIO.StringIO()
            linebuf.write(
                "%s%s%s " % (format(fg=BLACK, bg=BLACK, bright=True), str(num).strip().center(3), format(reset=True)))
            linebuf.write(
                "%s%s%s " % (format(fg=YELLOW, bright=True), device.strip()[:20].ljust(20), format(reset=True)))
            linebuf.write("%s%s%s " % (
                format(fg=CYAN, bright=True), devices_versions[num - 1].strip().center(16), format(reset=True)))
            linebuf.write("%s%s%s " % (
                format(fg=MAGENTA, bright=True), devices_model_name[num - 1].strip().ljust(20), format(reset=True)))
            line = linebuf.getvalue()
            print line
            # print str(num)+": " + device + "\t\t" + devices_versions[num-1] + "\t\t"+ devices_model_name[num-1]
            num += 1
        sys.stdout.flush()
        if run_cmd:
            user_input = raw_input("> ")
            # print user_input
            if user_input.isdigit() and 0 < int(user_input) <= len(devices):
                print "executing following command:"
                linebuf = StringIO.StringIO()
                cmd = adb + " -s " + devices[int(user_input) - 1] + ' ' + ' '.join(sys.argv[1:])
                # print cmd + "\n"
                # linebuf.write(adb)
                linebuf.write("%s%s%s " % (format(fg=BLACK, bg=BLACK, bright=True), adb, format(reset=True)))
                linebuf.write("%s%s%s " % (format(fg=YELLOW), "-s " + devices[int(user_input) - 1], format(reset=True)))
                linebuf.write("%s%s%s " % (format(fg=GREEN), ' '.join(sys.argv[1:]), format(reset=True)))
                line = linebuf.getvalue()
                print line
                print
                subprocess.call(cmd.split())
            else:
                print 'You must enter a valid number'

cmd = [adb] + sys.argv[1:]

try:
    first_args = sys.argv[1]
    if first_args == 'devices':
        multi_cmd(False)
    else:
        if NO_MULTI_COMMAND.count(first_args) == 1 or first_args == '-s':
            subprocess.call(cmd)
        else:
            multi_cmd(True)
except KeyboardInterrupt:
    pass
except:
    # multi_cmd(False)
    subprocess.call(cmd)
