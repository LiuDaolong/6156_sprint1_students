use students6156DB;

insert into `Students` 
values ('dl3515', 'Daolong', 'Liu', 'dl3515@columbia.edu', '1234567890', 'Computer Science', 'cloud computing, data analysis');
insert into `Students` 
values ('yt2777', 'Yuming', 'Tian', 'yt2777@columbia.edu', '1234567890', 'Computer Science', 'cloud computing, natural language processing');

insert into `EnrollCourse`
values ('dl3515', '11038');
insert into `EnrollCourse`
values ('yt2777', '11038');

insert into `SelectProject`
values ('dl3515', '11038', 'aws_lions');
insert into `SelectProject`
values ('yt2777', '11038', 'aws_lions');