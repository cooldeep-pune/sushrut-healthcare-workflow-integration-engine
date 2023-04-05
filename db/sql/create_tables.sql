create table healthcare_channels(channel_id varchar(50) NOT NULL PRIMARY KEY,channel_name VARCHAR(50) NOT NULL,content json NOT NULL);
 ALTER TABLE healthcare_channels ADD CONSTRAINT unique_name UNIQUE (channel_name);
create table channels_deployed(deployed_channel_id varchar(50) NOT NULL PRIMARY KEY);