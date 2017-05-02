--
-- Licensed to the Apache Software Foundation (ASF) under one
-- or more contributor license agreements.  See the NOTICE file
-- distributed with this work for additional information
-- regarding copyright ownership.  The ASF licenses this file
-- to you under the Apache License, Version 2.0 (the
-- "License"); you may not use this file except in compliance
-- with the License.  You may obtain a copy of the License at
--
--   http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing,
-- software distributed under the License is distributed on an
-- "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
-- KIND, either express or implied.  See the License for the
-- specific language governing permissions and limitations
-- under the License.
--
CREATE EXTENSION pgcrypto;

DO $$
DECLARE
    ADMSALT bytea;
    EMUSALT bytea;
    EMUUSER integer;
    EMUCON  integer;
BEGIN
 ADMSALT = digest(concat(cast(current_timestamp as text), random()::text), 'sha256');
 EMUSALT = digest(concat(cast(current_timestamp as text), random()::text), 'sha256');

-- Create default user "guadmin" with password "guadmin"
--            digest(concat('guadmin', encode(ADMSALT, 'hex')), 'sha256'),
--            ADMSALT,

INSERT INTO guacamole_user (username, password_hash, password_salt, password_date)
    VALUES ('guadmin',
            E'\\x7d41bccc21c9d572c530f06493f99f5c480946046a749de9231441ceb803b94b',
            E'\\x84208edb3c77753b3fb156ca3c6951ec510f41f35f9e85d5c4ed1f0b817662db',
            CURRENT_TIMESTAMP);

INSERT INTO guacamole_user (username, password_hash, password_salt, password_date)
    VALUES ('emu',
            E'\\x63c5f1ba7e2223d185221b13e94e10b0653218bc499f5d1b89ce23e1cd7396d6',
            E'\\x8ac60127e99ee3ee70ee5ca594de81fc44ecdd9c2735b47e2e18be443dc760a2',
            CURRENT_TIMESTAMP);


EMUUSER = lastval();

INSERT INTO guacamole_connection (connection_name, protocol, max_connections, max_connections_per_user)
    VALUES ('vm',
            'vnc',
            1,
            1);

EMUCON = lastval();

-- Grant emu user permission to read vm connection properties
INSERT INTO guacamole_connection_permission (user_id, connection_id, permission)
    VALUES (EMUUSER, 
            EMUCON, 
            'READ'::guacamole_object_permission_type);

INSERT INTO guacamole_connection_parameter VALUES (EMUCON, 'hostname', 'vm');
INSERT INTO guacamole_connection_parameter VALUES (EMUCON, 'port', '6001');
INSERT INTO guacamole_connection_parameter VALUES (EMUCON, 'password', 's3cr3t99');

END $$;


-- Grant this user all system permissions
INSERT INTO guacamole_system_permission
SELECT user_id, permission::guacamole_system_permission_type
FROM (
    VALUES
        ('guadmin', 'CREATE_CONNECTION'),
        ('guadmin', 'CREATE_CONNECTION_GROUP'),
        ('guadmin', 'CREATE_SHARING_PROFILE'),
        ('guadmin', 'CREATE_USER'),
        ('guadmin', 'ADMINISTER')
) permissions (username, permission)
JOIN guacamole_user ON permissions.username = guacamole_user.username;

-- Grant admin permission to read/update/administer self
INSERT INTO guacamole_user_permission
SELECT guacamole_user.user_id, affected.user_id, permission::guacamole_object_permission_type
FROM (
    VALUES
        ('guadmin', 'guadmin', 'READ'),
        ('guadmin', 'guadmin', 'UPDATE'),
        ('guadmin', 'guadmin', 'ADMINISTER')
) permissions (username, affected_username, permission)
JOIN guacamole_user          ON permissions.username = guacamole_user.username
JOIN guacamole_user affected ON permissions.affected_username = affected.username;

