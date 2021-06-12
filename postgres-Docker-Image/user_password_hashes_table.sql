/c hmda_data_app_db;
CREATE TABLE user_password_hashes (
	username VARCHAR(200) NOT NULL PRIMARY KEY,
	hash VARCHAR(200) NOT NULL
);

INSERT INTO user_password_hashes (username, hash) 
VALUES 
('defaultUsername', '$argon2id$v=19$m=102400,t=2,p=8$OHpiH/W99Dfzv62YK4nWxQ$rfQIy222V9AzWMeg30Fc8A');