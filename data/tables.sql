drop table history;
create table history (
	idHistory bigint not null auto_increment, 
	account_id int(11) not null, 
	product varchar(30) not null, 
	timestamp datetime not null, 
	device varchar(50) not null, 
	item varchar(30) not null, 
	description varchar(255) not null,
	value varchar(30) not null,
	timestampMonitor timestamp DEFAULT CURRENT_TIMESTAMP not null,
	foreign key (account_id) references customer_accounts(account_id), 
	primary key(idHistory) );
	
--alter table history add timestampMonitor timestamp DEFAULT CURRENT_TIMESTAMP;
--alter table history modify column timestampMonitor timestamp default current_timestamp not null;
	
-- insert into history (account_id, product, timestamp, device, item, description, value) values (18, 'JP-PROD', '2016-05-04 14:41', 'JP-DEV', 'JP-ITEM', 'JP-DESC', 'down');
-- insert into lastStatus (account_id, product, device, item, description, timestamp, value) values (12, 'Vyatta', 'xyz.icc', 'VPN', '{"LocalID": "1.1.1.1", "Tunnel": "10", "Description": "VPN with XYZ", "PeerID": "0.0.0.0"}', '2016-05-04 14:41', 'up');
-- insert into lastStatus (account_id, product, device, item, description, timestamp, value) values (18, 'VPX', 'xyz.icc', 'UpDown', 'UpDown', '2016-05-04 14:41', 'down');
	
drop table lastStatus;
create table lastStatus (
	idLastStatus bigint not null auto_increment, 
	account_id int(11) not null, 
	product varchar(30) not null, 
	device varchar(50) not null, 
	item varchar(30) not null, 
	description varchar(255) not null,
	timestamp datetime not null,
	value varchar(30) not null,
	timestampMonitor timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP not null,
	foreign key (account_id) references customer_accounts(account_id),
	primary key(idLastStatus),
	CONSTRAINT uc_lastStatus UNIQUE (account_id, product, device, item, description));
	
--alter table lastStatus add timestampMonitor timestamp DEFAULT CURRENT_TIMESTAMP;
--alter table lastStatus modify column timestampMonitor timestamp default current_timestamp not null;
--alter table lastStatus add timestampMonitor timestamp ON UPDATE CURRENT_TIMESTAMP;
	
DROP TRIGGER trigger_setLastStatus;
DELIMITER //
CREATE TRIGGER trigger_setLastStatus
AFTER INSERT
   ON history FOR EACH ROW
BEGIN
   INSERT INTO lastStatus (account_id,
	     product,
	     device,
	     item,
	     description,
	     timestamp,
	     value)
	VALUES (NEW.account_id,
	     NEW.product,
	     NEW.device,
	     NEW.item,
	     NEW.description,
	     NEW.timestamp,
	     NEW.value)
	ON DUPLICATE KEY UPDATE
	     timestamp=NEW.timestamp,
	     value=NEW.value;
END; //
DELIMITER ;

DROP VIEW viewDashboardMain;
CREATE VIEW viewDashboardMain AS 
	SELECT lastStatus.account_id, customer_accounts.account_label, product, 
	(select count(*) from lastStatus as statusDown where lastStatus.account_id=statusDown.account_id and lastStatus.product=statusDown.product and statusDown.value='down' and not statusDown.description like "%[NO TV WARNING]%" and date_add(timestampMonitor, interval 5 minute)>now()) as down,
	(select count(*) from lastStatus as statusUp where lastStatus.account_id=statusUp.account_id and lastStatus.product=statusUp.product and (statusUp.value<>'down' or statusUp.description like "%[NO TV WARNING]%") and date_add(timestampMonitor, interval 5 minute)>now()) as up
	from lastStatus
	inner join customer_accounts on customer_accounts.account_id = lastStatus.account_id
	group by lastStatus.account_id, customer_accounts.account_label, product
	order by down desc, customer_accounts.account_label, product;
-- select * from viewDashboardMain;

-- select count(*) from lastStatus as statusUp where statusUp.account_id=18 and statusUp.product="Vyatta" and statusUp.value<>'down' and date_add(timestampMonitor, interval 5 minute)>now();

DROP VIEW viewDashboardMarquee;	
CREATE VIEW viewDashboardMarquee AS
	SELECT customer_accounts.account_label, lastStatus.device, lastStatus.item, lastStatus.description, lastStatus.value 
	from lastStatus
	inner join customer_accounts on customer_accounts.account_id = lastStatus.account_id
	where lastStatus.value='down' and not lastStatus.description like "%[NO TV WARNING]%" and date_add(timestampMonitor, interval 5 minute)>now();
-- select * from viewDashboardMarquee;

DROP VIEW viewLastUpdateByCustomer;
CREATE VIEW viewLastUpdateByCustomer AS
	select account_id, max(timestamp) as lastUpdate from lastStatus group by account_id; 
	