FROM ubuntu:latest

# Set environment variables
ENV ANDROID_HOME=/opt/asdk \
    EMU_NUM=1 \
    PATH=$PATH:/opt/asdk/tools:/opt/asdk/platform-tools:/opt/asdk/build-tools/25.0.3

# Set build variables
ARG SDKFILE=sdk-tools-linux-3859397.zip
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG VNCPASS=password

# Update and install everything necessary
RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y install --no-install-recommends software-properties-common && \
    add-apt-repository ppa:webupd8team/java && \
    echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | debconf-set-selections && \
    apt-get -y update && \
    apt-get install -y --no-install-recommends vnc4server \
    oracle-java8-installer unzip lib32stdc++6 xfonts-base file \
    libgtk-3-dev python-gobject-dev python-gi-dev python-pip xmacro \
    fonts-font-awesome net-tools libpulse0 python-setuptools python-wheel && \
    pip install uiautomator && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir /opt/asdk && \
    cd /opt/asdk && \
    wget -q https://dl.google.com/android/repository/$SDKFILE && \
    unzip $SDKFILE && \
    rm -rf $SDKFILE && \
    echo "y" | tools/bin/sdkmanager --update && \
    echo "y" | tools/bin/sdkmanager "platform-tools" "emulator" \
    "build-tools;25.0.3" "platforms;android-19" \
    "system-images;android-19;google_apis;x86" && \
    groupadd -f -g $GROUP_ID ub && \
    useradd -o -u $USER_ID -g $GROUP_ID -ms /bin/bash ub && \
    mkdir /tests && chown -R $USER_ID:$GROUP_ID /tests /opt/asdk

# Set a new user
USER ub

# Set up everything
RUN echo "$VNCPASS\n$VNCPASS\n\n" | vncpasswd && \
    /opt/asdk/tools/bin/avdmanager create avd -k \
    "system-images;android-19;google_apis;x86" \
    -n "vm" -d "Nexus S" -c 256M -g "google_apis" && \
    echo "hw.camera.back=none" >> ~/.android/avd/vm.avd/config.ini && \
    echo "hw.camera.front=none" >> ~/.android/avd/vm.avd/config.ini && \
    echo "hw.ramSize=1024" >> ~/.android/avd/vm.avd/config.ini && \
    echo "vm.heapSize=256" >> ~/.android/avd/vm.avd/config.ini && \
    echo "skin.dynamic=no" >> ~/.android/avd/vm.avd/config.ini && \
    echo "skin.name=480x800" >> ~/.android/avd/vm.avd/config.ini && \
    echo "skin.path=480x800" >> ~/.android/avd/vm.avd/config.ini && \
    sed -i 's/hw.keyboard=no/hw.keyboard=yes/' ~/.android/avd/vm.avd/config.ini && \
    echo "window.x = 5\nwindow.y = 5" > ~/.android/avd/vm.avd/emulator-user.ini

# Copy required files
ADD ./xstartup /home/ub/.vnc/xstartup
ADD ./uscr /home/ub/uscr

# Execute the file
CMD "/home/ub/uscr/start.sh" $EMU_NUM