# written by Dary

import os, sys, StringIO , subprocess

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

adb = '/Applications/Android-SDK/platform-tools/adb'

def format(fg=None, bg=None, bright=False, bold=False, dim=False, reset=False):
    # manually derived from http://en.wikipedia.org/wiki/ANSI_escape_code#Codes
    codes = []
    if reset: codes.append("0")
    else:
        if not fg is None: codes.append("3%d" % (fg))
        #if not fg is None: codes.append("38;5;100")
        if not bg is None:
            if not bright: codes.append("4%d" % (bg))
            else: codes.append("10%d" % (bg))
        if bold: codes.append("1")
        elif dim: codes.append("2")
        else: codes.append("22")
    return "\033[%sm" % (";".join(codes))


#linebuf.write("%s%s%s " % (format(fg=YELLOW,bg=RED, bright=True), "Test", format(reset=True)))
#line = linebuf.getvalue()
#print line

def multiCmd(runCmd):
    cmd = adb + ' ' + ' '.join(sys.argv[1:])
    devices = os.popen(adb + " devices | sed '1,1d' | sed '$d' | cut -f 1 | sort").read().splitlines()
    #print devices
    devices_number = len(devices);

    if devices_number == 0:
        print 'No emulators or devices detected - nothing to do.'
    elif devices_number == 1 and runCmd:
        subprocess.call(cmd.split())
    else:
        devices_model_name=[]
        devices_versions=[]
        for device in devices:
            model_name_cmd = adb + ' devices | grep ' + device + r' | cut -f 1 | xargs -I $ ' + adb + ' -s $ shell cat /system/build.prop | grep "ro.product.model" | cut -d "=" -f 2 | tr -d '+r'" \r\t\n"'
            platform_versions_cmd = adb + ' devices | grep ' + device + r' | cut -f 1 | xargs -I $ ' + adb + ' -s $ shell cat /system/build.prop | grep "ro.build.version.release" | cut -d "=" -f 2 | tr -d ' + r'"\r\t\n"'
            devices_model_name.append(os.popen(model_name_cmd).read())
            devices_versions.append(os.popen(platform_versions_cmd).read())
        #print devices_model_name
        #print devices_versions
        if runCmd:
            print 'Multiple devices detected, please select one'
        else:
            print 'List of devices attached'
        num = 1
        for device in devices:
            linebuf = StringIO.StringIO()
            linebuf.write("%s%s%s " % (format(fg=BLACK,bg=BLACK,bright=True), str(num).strip().center(3), format(reset=True)))
            linebuf.write("%s%s%s " % (format(fg=YELLOW,bright=True), device.strip()[:16].ljust(16), format(reset=True)))
            linebuf.write("%s%s%s " % (format(fg=CYAN,bright=True), devices_versions[num-1].strip().center(7), format(reset=True)))
            linebuf.write("%s%s%s " % (format(fg=MAGENTA,bright=True), devices_model_name[num-1].strip().ljust(20), format(reset=True)))
            line = linebuf.getvalue()
            print line
            #print str(num)+": " + device + "\t\t" + devices_versions[num-1] + "\t\t"+ devices_model_name[num-1]
            num = num + 1
        if runCmd:
            user_input = raw_input("> ")
            #print user_input
            if user_input.isdigit() and 0< int(user_input) <= len(devices):
                print "executing following command:"
                cmd = adb + " -s " + devices[int(user_input)-1] +' '+ ' '.join(sys.argv[1:])
                print "    "+cmd+"\n"
                subprocess.call(cmd.split())
            else:
                print 'You must enter a vaild number'


cmd =  adb + ' ' +' '.join(sys.argv[1:])

NO_MULTI_COMMAND=['start-server','kill-server','forward','connect','disconnect','help','version','ppp']
try:
    first_args = sys.argv[1]
    if first_args == 'devices':
        multiCmd(False)
    else:
        if NO_MULTI_COMMAND.count(first_args) == 1:
            subprocess.call(cmd.split())
        else:
            multiCmd(True)
except:
    #print 'No args'
    multiCmd(False)
