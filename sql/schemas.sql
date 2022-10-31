use students6156DB;

drop table if exists `EnrollCourse`;
drop table if exists `SelectProject`;
drop table if exists `Projects`;
drop table if exists `Course`;
drop table if exists `Students`;

create table `Students` (
    `studentID` varchar(10) not null,
    `FirstName` varchar(50),
    `LastName` varchar(50),
    `email` varchar(100),
    `phone` varchar(20),
    `major` varchar(50),
    `interests` varchar(255),
    primary key (`studentID`)
);

create table `EnrollCourse` (
    `studentID` varchar(10) not null,
    `CRN` varchar(20) not null,
    primary key (`studentID`, `CRN`),
    foreign key (`studentID`) references `Students`(`studentID`)
);

create table `SelectProject` (
    `studentID` varchar(10) not null,
    `CRN` varchar(20) not null,
    `projectID` varchar(20) not null,
    primary key (`studentID`, `projectID`),
    foreign key (`studentID`, `CRN`) references `EnrollCourse`(`studentID`, `CRN`)
);