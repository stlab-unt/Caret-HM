# Caret-HM
*Capture/Replay And Heatmap Generation Framework for Android*

*Version 1.0*

## Prerequisites
- `Ubuntu` 16.04 or later
- Access to `/dev/kvm`:
  `chmod 777 /dev/kvm`
- `docker` 17.03 or later
- `docker-compose` 1.12.0 or later

## Getting Started
1. Copy contents of docker-compose project in the desired folder
2. Modify `.env`:
  - Set `USER_ID`, `GROUP_ID` to your user and group id
  - Set `EMU_NUM` to a number of desired emulators (usually, number of cores - 2)
  - Set `TEST_DIR` and `SQL_DATA` to the desired directories
3. Set permissions of `TEST_DIR` and `SQL_DATA` to `777`:

     `chmod 777 (YOUR_TEST_DIR) (YOUR_SQL_DATA)`
4. If VNC password needs to be modified, change it in .env and conf/pgsql/002-create-admin-user.sql

    Alternatively, you can change VNC password only in `.env` and change it in the [Guacamole](http://guacamole.incubator.apache.org/) web interface later.
5. Start `dockerd`, if necessary:

    `sudo dockerd`
5. In the folder, execute:

    `docker-compose build`
6. Verify that /dev/kvm is accessible, otherwise give permissions:

    `chmod 777 /dev/kvm`
7. Start containers:

    `docker-compose up`
8. Once all containers are up, you should be able to access the framework at:

    http://localhost/ - for emulator access
    
    http://localhost/jsac - for heatmap generation
9. If your `EMU_NUM` is larger than `1`, you will need to add additional virtual machines to [Guacamole](http://guacamole.incubator.apache.org/).
    To do so, login as `guadmin` to [Guacamole](http://guacamole.incubator.apache.org/) and add additional virtual machines. The ports start from `6001` to `6000+EMU_NUM`
10. Additional configuration options available in `conf` and the corresponding `-docker` folders.

## Default Credentials
 - VNC Password: `s3cr3t99`
    - Where to change
      - `.env`, and
      - `conf/pgsql/002-create-admin-user.sql`
 - Access to emulator:
     - Username: `emu`
     - Password: `android`
     - Where to change
       - Encrypted in `conf/pgsql/002-create-admin-user.sql` using SHA256, more information is at [Guacamole website](https://guacamole.incubator.apache.org/doc/gug/jdbc-auth.html), or
       - Guacamole admin inteface
  - Guacamole adminstration login
      - Username: `guadmin`
      - Password: `guadmin`
      - Where to change
        - Encrypted in `conf/pgsql/002-create-admin-user.sql` using SHA256, more information is at [Guacamole website](https://guacamole.incubator.apache.org/doc/gug/jdbc-auth.html), or
       - Guacamole user settings inteface (administrator cannot change its password from Guacamole admin inteface)

## Adding your own app
1. Add your apk to `uscr-docker/uscr/apk`
2. Copy and modify one of the configuration files at `uscr-docker/uscr/conf`

## Frequently asked questions

#### Docker requires sudo, everytime I run it, what should I do?
Make sure that your user in docker group, the detailed answer is available [here](https://askubuntu.com/questions/477551/how-can-i-use-docker-without-sudo).


#### My tests are not saved, why?
Make sure that permissions for `TEST_DIR` and `SQL_DATA` are set to `777`.

#### Something does not work, what should I do?
- The first place to start is always to check permissions.
- Verify that your `USER_ID` and `GROUP_ID` are corresponding to your user and group ids.
- If nothing helps, please [submit a new issue](https://github.com/stlab-unt/Caret-HM/issues/new).
