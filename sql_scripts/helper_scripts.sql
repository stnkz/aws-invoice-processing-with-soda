truncate table invoices
-- drop table  invoices

create table if not exists invoices(invoice_key varchar(100), invoice_desc varchar(100), due_date varchar(20), name varchar(100), amount numeric(6, 2))

insert into invoices (invoice_key, invoice_desc, due_date, name, amount)
values ('Test', 'Account Number: 1234 567 8901 ', '2020-06-08T00:00:00', 'Test', 150.42)

select * from invoices