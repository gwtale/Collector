drop table history;
create table history (
	idHistory mediumint not null auto_increment, 
	account_id int(11) not null, 
	product varchar(30) not null, 
	time datetime not null, 
	device varchar(50) not null, 
	item varchar(30) not null, 
	description varchar(255) not null,
	value varchar(30) not null,
	foreign key (account_id) references customer_accounts(account_id), 
	primary key(idHistory) );