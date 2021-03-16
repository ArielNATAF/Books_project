CREATE TABLE tt_user (
    user_id int IDENTITY(1,1) PRIMARY KEY,
	first_name nvarchar(255) not null,
    last_name nvarchar(255) not null,
	birth_year int,
	age AS YEAR(GETDATE())-birth_year, -----computed column
	gender varchar(50),
    city nvarchar(255),
	state nvarchar(255),
    country nvarchar(255),
	email_id varchar(256),
	is_active bit,
	data_source varchar(50)
);


);
-- drop table tt_user_detail
create table tt_master_book(
	book_id  int IDENTITY(1000,1) PRIMARY KEY,
	book_title nvarchar(500) not null,
	book_author nvarchar(500),
	isbn varchar(20),
	isbn_13 bigint,
	year_of_publication int,
	book_language nvarchar(50),
	average_rating float,
	number_of_pages int,
	awards nvarchar(max),
	book_description nvarchar(max),
	books_in_series varchar(500),
	author_genres varchar(256),
	issue_flag bit,
	is_active bit,
	data_source varchar(50)
);

create table tt_tag(
	tag_id int IDENTITY(1,1) PRIMARY KEY,
	tag_name varchar(50)
	is_active bit
);
-- drop table tt_tag

create table tt_rating(
	rating_id int IDENTITY(1,1) PRIMARY KEY,
	book_id int,
	user_id int,
	rating int
	CONSTRAINT FK_bookrating FOREIGN KEY (book_id)
    REFERENCES tt_master_book(book_id),
	CONSTRAINT FK_userrating FOREIGN KEY (user_id)
    REFERENCES tt_user(user_id),
	is_active bit,
	data_source varchar(50)
);

create table tt_book_tag(
	book_tag_id int IDENTITY(1,1) PRIMARY KEY,
	book_id int,
	tag_id int
	CONSTRAINT FK_book_tag FOREIGN KEY (book_id)
    REFERENCES tt_master_book(book_id),
	CONSTRAINT FK_booktag FOREIGN KEY (tag_id)
    REFERENCES tt_tag(tag_id),
	is_active bit,
	data_source varchar(50)
);

