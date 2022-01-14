use sys;
drop database if exists DatabaseProcess;
create database DatabaseProcess;
use DatabaseProcess;

create table ManageTime
(
	ID int,
    StartTime time,
    EndTime time,
    StartTimeAgain time,

    constraint PK_ManageTime primary key (ID)
);

insert ManageTime
values(1, '6:00', '19:00', '20:00');
select ID, Time_format(StartTime, '%H:%i') , Time_format(EndTime, '%H:%i'), Time_format(StartTimeAgain, '%H:%i') from ManageTime;

update ManageTime set EndTime = '6:30' where ID = 1
