#!/bin/bash

export LC_ALL=C
IFS='
'

# function that makes copies of uscr directory
mdirs() {

    for ((i=1;i<$(($1+1));i++)); do

        echo "Creating uscr$i contents..."

        # make a directory
        rm -rf uscr$i;
        mkdir uscr$i;

        # link required files
        for j in 'apk' 'conf' 'misc' 'atest.py' 'misc.py' 'pyadb.py' 'ui.py'; do
            ln -s  ../uscr/$j uscr$i/$j
        done

        # change emulator port in main.json
        ep="$((5554+($i-1)*2))"
        cat uscr/main.json | sed -re "s/tor-5554/tor-$ep/" > uscr$i/main.json

        # copy Android VM
        echo "Copying Android VM$i..."
        rm -rf .android/avd/vm$i.avd .android/avd/vm$i.ini
        cp -R .android/avd/vm.avd .android/avd/vm$i.avd
        cat .android/avd/vm.ini | sed -e "s/vm\.avd/vm$i.avd/" > .android/avd/vm$i.ini

    done
}

# function that check if emulators are alive
emu_check() {

    # get VNC and emulator status
    emu=`/opt/asdk/platform-tools/adb devices | grep emul`
    vm=`netstat -an`

    for ((i=1;i<$(($1+1));i++)); do

        # extract the status of current emulator
        ivm=`echo $vm | grep :::600$i`
        iemu=`echo $emu | grep $((5554+($i-1)*2))`

        # if VNC or emulator are dead, restart
        if ([ -z $ivm ] || [ -z $iemu ]); then

            echo "VNC or emulator #$i is dead, restarting..."
            vnc4server -kill :10$i
            vnc4server -geometry 540x920 :10$i

            sleep 5

            # get VNC and emulator status again
            vm=`netstat -an`
            emu=`/opt/asdk/platform-tools/adb devices | grep emul`
        fi

    done

}

# make sure that parameter is not empty
if [ -n $1 ]; then

    # kill ADB
    /opt/asdk/platform-tools/adb kill-server

    # go to the home directory
    cd /home/ub/

    # create directories
    mdirs $1

    # start monitoring
    echo "Starting monitoring..."
    while sleep 3; do

        emu_check $1

    done
fi