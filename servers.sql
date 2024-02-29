BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "servers" (
	"id"	INTEGER,
	"session_id"	TEXT NOT NULL,
	"query"	TEXT NOT NULL,
	"address"	TEXT NOT NULL,
	"username"	TEXT NOT NULL,
	"password"	TEXT NOT NULL,
	"timestamp"	REAL NOT NULL UNIQUE,
	"config_description"	TEXT NOT NULL,
	"commands"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO "servers" VALUES (1,'4928e4cb-05ae-474a-a2aa-ede3f3dbef02','need to do this for 16 addresses!! also /24','','','',1708728785.38119,'Note that the subnet mask `/24` means that the last byte of the IP address can be any value from 0 to 255.','nv set interface swp1s0 ip address 10.1.1.1/24
nv set interface swp1s1 ip address 10.1.1.2/24
nv set interface swp1s2 ip address 10.1.1.3/24
nv set interface swp1s3 ip address 10.1.1.4/24
nv set interface swp1s4 ip address 10.1.1.5/24
nv set interface swp1s5 ip address 10.1.1.6/24
nv set interface swp1s6 ip address 10.1.1.7/24
nv set interface swp1s7 ip address 10.1.1.8/24
nv set interface swp2s0 ip address 10.1.1.9/24
nv set interface swp2s1 ip address 10.1.1.10/24
nv set interface swp2s2 ip address 10.1.1.11/24
nv set interface swp2s3 ip address 10.1.1.12/24
nv set interface swp2s4 ip address 10.1.1.13/24
nv set interface swp2s5 ip address 10.1.1.14/24
nv set interface swp2s6 ip address 10.1.1.15/24');
INSERT INTO "servers" VALUES (2,'4928e4cb-05ae-474a-a2aa-ede3f3dbef02','we need to configure the switch ports from 192.0.0.1/24 .. All 16 of them','','','',1708728853.20023,'Note that the above commands assume that the switch ports are named `swp1s0` through `swp1s14`. If your switch ports have different names, you will need to adjust the commands accordingly.','nv set interface swp1s0 ip address 192.0.0.1/24
nv set interface swp1s1 ip address 192.0.0.2/24
nv set interface swp1s2 ip address 192.0.0.3/24
nv set interface swp1s3 ip address 192.0.0.4/24
nv set interface swp1s4 ip address 192.0.0.5/24
nv set interface swp1s5 ip address 192.0.0.6/24
nv set interface swp1s6 ip address 192.0.0.7/24
nv set interface swp1s7 ip address 192.0.0.8/24
nv set interface swp1s8 ip address 192.0.0.9/24
nv set interface swp1s9 ip address 192.0.0.10/24
nv set interface swp1s10 ip address 192.0.0.11/24
nv set interface swp1s11 ip address 192.0.0.12/24
nv set interface swp1s12 ip address 192.0.0.13/24
nv set interface swp1s13 ip address 192.0.0.14/24
nv set interface swp1s14 ip address 192.0.0.15/24');
INSERT INTO "servers" VALUES (3,'6ab7fa3f-b8dc-4440-9e51-1c8e1cf7db56','How do I configure an invidia switch for 16 ports','','','',1708884177.5384,'Note that the above commands assume that the NVIDIA switch has 16 ports and that the IP addresses are assigned in a CIDR notation with a subnet mask of 255.255.255.255 (i.e., a subnet mask of 255.255.255.255). If the subnet mask is different, you will need to adjust the CIDR notation accordingly.','nv set interface swp1s0 ip address 10.1.1.1/31
nv set interface swp1s1 ip address 10.1.1.2/31
nv set interface swp1s2 ip address 10.1.1.3/31
nv set interface swp1s3 ip address 10.1.1.4/31
nv set interface swp1s4 ip address 10.1.1.5/31
nv set interface swp1s5 ip address 10.1.1.6/31
nv set interface swp1s6 ip address 10.1.1.7/31
nv set interface swp1s7 ip address 10.1.1.8/31
nv set interface swp1s8 ip address 10.1.1.9/31
nv set interface swp1s9 ip address 10.1.1.10/31
nv set interface swp1s10 ip address 10.1.1.11/31
nv set interface swp1s11 ip address 10.1.1.12/31
nv set interface swp1s12 ip address 10.1.1.13/31
nv set interface swp1s13 ip address 10.1.1.14/31
nv set interface swp1s14 ip address 10.1.1.15/31');
COMMIT;
