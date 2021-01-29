import mysql.connector, tkinter as tk, webbrowser
from tabulate import tabulate
from tkinter import ttk

DB_NAME = "Restaurant_Management"
USER = "root"
PASSWD = ""
ORIG_USER = "root"
ORIG_PASSWD = ""
option = None
roles = ["Admin", "Customer", "Restaurant Manager", "Shop Manager"]
db_users = ["database_admin", "database_customer", "database_restaurant_manager", "database_shop_manager"]
passwords = ["Admin", "1234", "1234", "1234"]
event_args = None


class Restaurant:
    def __init__(self, dbname, username, password, orig_username, orig_password):
        self.dbname = dbname
        self.username = username
        self.password = password
        self.orig_username = orig_username
        self.orig_password = orig_password
        self.db = self.init_db()


    def init_db(self):
        db = mysql.connector.connect(
            host="localhost",
            user=self.orig_username,
            passwd=self.orig_password
        )
        cur = db.cursor()
        statement = "SHOW DATABASES LIKE '{}'".format(DB_NAME);
        cur.execute(statement)
        # checking if our DB already exists
        exists = cur.fetchone()
        # if db doesn't exist, create it
        if not exists:
            statement = "CREATE DATABASE {}".format(DB_NAME)
            cur.execute(statement)
            print("Database {} didn't exist and was created successfully\n".format(DB_NAME))
            db.close()
            db = mysql.connector.connect(
                host="localhost",
                user=self.orig_username,
                passwd=self.orig_password,
                database=self.dbname
            )
            self.build_tables(db)
            self.insert_initial_data(db)
            self.create_triggers(db)
            self.create_procedures(db)
            self.create_roles(db)

        # if db exists, connect to it
        else:
            print("Database {} already exists and was opened successfully\n".format(DB_NAME))
            db.close()
            db = mysql.connector.connect(
                host="localhost",
                user=self.username,
                passwd=self.password,
                database=self.dbname
            )
        db.commit()
        return db



    def build_tables(self, db):
        cur = db.cursor()

        # need a for loop so that cursor runs all of the statements! Without
        # the loop it simply will not execute anything!
        for result in cur.execute('''
        -- Entities
        CREATE table if not exists Menu ( foodName varchar(50)
                          , price decimal(10, 2) not null
                          , start DATE not null
                          , end date not null
                          , primary key (foodName, start)
                          , key (foodName, price));
        
        
        create table if not exists customer ( CID INT primary key auto_increment
                              , FName varchar(20) not null
                              , LName varchar(20) not null
                              , NID decimal(10,0) not null
                              , cphone decimal(11,0) not null
                              , age INT(2) not null
                              , credit decimal(10,2) default 0
                              );
        
        create table if not exists address ( AID INT auto_increment primary key
                             , CID INT not null
                             , name varchar(20) not null
                             , address varchar(255) not null
                             , fphone decimal(11,0)
                             , foreign key (CID) references customer(CID));
        
        create table if not exists courier ( CNID decimal(10,0) primary key
                             , CID INT auto_increment
                             , CFName varchar(20) not null
                             , CLName varchar(20) not null
                             , cphone decimal(11,0) not null
                             , key (CID));
        
        
        create table if not exists orders ( orderID INT primary key auto_increment
                            , orderDate datetime not null
                            , customerID INT
                            , AID INT
                            , courierID INT
                            , foreign key (customerID) references customer(CID)
                            , foreign key (AID) references address(AID)
                            , foreign key (courierID) references courier(CID));
        
        create table if not exists shop ( SID INT primary key auto_increment
                          , SName varchar(255) not null
                          , status ENUM('active', 'inactive'));
        
        create table if not exists shopItem( SID INT
                             , IID INT
                             , IName varchar(50) not null
                             , Iprice decimal(10,2)
                             , start date not null
                             , end date not null
                             , primary key (SID, IID, Iprice)
                             , foreign key (SID) references shop(SID));
        
        create table if not exists shopOrder( orderID INT primary key auto_increment
                              , SID INT not null
                              , orderDate date not null
                              , foreign key (SID) references shop(SID));
        
        
        
        -- Relations
        
        create table if not exists order_menu ( orderID INT
                                , foodName varchar(50)
                                , price decimal(10, 2)
                                , unit int default 1
                                , primary key (orderID, foodName, price)
                                , foreign key (orderID) references orders(orderID)
                                , foreign key (foodName, price) references menu(foodName, price));
        
        
        create table if not exists shopOrder_Items ( orderID INT
                                     , SID INT
                                     , IID INT
                                     , Iprice decimal(10,2)
                                     , unit int default 1
                                     , primary key (orderID, SID, IID, Iprice)
                                     , foreign key (orderID) references shopOrder(orderID)
                                     , foreign key (SID, IID, Iprice) references shopItem(SID, IID, Iprice));
        
        
        
        -- Log tables
        
        -- Entities
        
        CREATE table if not exists Menu_log (
                            logTime datetime
                          , logTable varchar(20)
                          , logOperation enum('insert', 'delete', 'update')
                          , foodName varchar(50)
                          , price decimal(10, 2) not null
                          , start DATE not null
                          , end date not null);
        
        
        create table if not exists customer_log (
                                logTime datetime
                              , logTable varchar(20)
                              , logOperation enum('insert', 'delete', 'update')
                              , CID INT
                              , FName varchar(20) not null
                              , LName varchar(20) not null
                              , NID decimal(10,0) not null
                              , cphone decimal(11,0) not null
                              , age INT(2) not null
                              , credit decimal(10,2) default 0
                              );
        
        create table if not exists address_log (
                                logTime datetime
                              , logTable varchar(20)
                              , logOperation enum('insert', 'delete', 'update')
                             , AID INT
                             , CID INT not null
                             , name varchar(20) not null
                             , address varchar(255) not null
                             , fphone decimal(11,0));
        
        create table if not exists courier_log (
                                logTime datetime
                              , logTable varchar(20)
                              , logOperation enum('insert', 'delete', 'update')
                            , CNID decimal(10,0)
                             , CID INT
                             , CFName varchar(20) not null
                             , CLName varchar(20) not null
                             , cphone decimal(11,0) not null);
        
        
        create table if not exists orders_log (
                                logTime datetime
                              , logTable varchar(20)
                              , logOperation enum('insert', 'delete', 'update')
                            , orderID INT
                            , orderDate datetime not null
                            , customerID INT
                            , AID INT
                            , courierID INT);
        
        create table if not exists shop_log (
                                logTime datetime
                              , logTable varchar(20)
                              , logOperation enum('insert', 'delete', 'update')
                            , SID INT
                          , SName varchar(255) not null
                          , status ENUM('active', 'inactive'));
        
        create table if not exists shopItem_log (
                                logTime datetime
                              , logTable varchar(20)
                              , logOperation enum('insert', 'delete', 'update')
                             , SID INT
                             , IID INT
                             , IName varchar(50) not null
                             , Iprice decimal(10,2)
                             , start date not null
                             , end date not null);
        
        create table if not exists shopOrder_log (
                                logTime datetime
                              , logTable varchar(20)
                              , logOperation enum('insert', 'delete', 'update')
                              , orderID INT
                              , SID INT not null
                              , orderDate date);
        
        
        
        -- Relations
        
        create table if not exists order_menu_log (
                                    logTime datetime
                              , logTable varchar(20)
                              , logOperation enum('insert', 'delete', 'update')
                                , orderID INT
                                , foodName varchar(50)
                                , price decimal(10, 2)
                                , unit int default 1);
        
        
        create table if not exists shopOrder_Items_log (
                                        logTime datetime
                                 , logTable varchar(20)
                                 , logOperation enum('insert', 'delete', 'update')
                                    , orderID INT
                                     , SID INT
                                     , IID INT
                                     , Iprice decimal(10,2)
                                     , unit int default 1);
        
        ''', multi=True):
            pass


    # inserting initial data to the database tables
    def insert_initial_data(self, db):
        cur = db.cursor()

        # need a for loop so that cursor runs all of the statements! Without
        # the loop it simply will not execute anything!
        for result in cur.execute(''' 
        -- data for table `menu`
        INSERT INTO `menu` (`foodName`, `price`, `start`, `end`) VALUES
        ('a', '25.50', '2020-01-31', '2020-02-02'),
        ('a', '30.00', '2020-02-03', '2020-02-10'),
        ('b', '33.00', '2020-01-15', '2020-01-31'),
        ('c', '30.50', '2020-01-25', '2020-01-31'),
        ('d', '40.00', '2020-01-24', '2020-01-31');   
        -- data for table `customer`     
        INSERT INTO `customer` (`CID`, `FName`, `LName`, `NID`, `cphone`, `age`, `credit`) VALUES
        (1, 'Arash', 'Haji', '102244567', '912845633', 22, 20),
        (2, 'Babak', 'Emami', '124325', '9128468635', 20, 10),
        (3, 'Abbas', 'Najafi', '1294234619', '99999999999', 19, 50),
        (13, 'Sahand', 'Najafi2', '1294234619', '99999999999', 19, 4.50),
        (14, 'Babak', 'Najafi2', '1294234619', '99999999999', 19, 0),
        (15, 'Reza', 'Rezvani', '23', '91284682550', 33, 50),
        (16, 'Zahra', 'Najafi2', '1294234619', '29424123451', 19, 0),
        (17, 'Sara', 'Sedighi', '1294234619', '294241234', 19, 0),
        (20, 'asd', 'asd', '1234567891', '12341234123', 21, 60),
        (21, 'Abbas', 'Mousavi', '385492174', '12345123451', 31, 0),
        (22, 'Amir', 'Javan', '1234123469', '97412345601', 28, 0),
        (45, 'Akj', 'kls', '1395321852', '12312321', 43, 12),
        (46, 'sdaf', 'hgdf', '1239540348', '9128468255', 45, 10);
        
        -- data for table `address`
        INSERT INTO `address` (`AID`, `CID`, `name`, `address`, `fphone`) VALUES
        (8, 1, 'haha', 'asdjas dfh', '12123'),
        (569, 1, 't1', 'dsaf', NULL),
        (570, 1, 't2', 'des', '1234561789'),
        (571, 1, 't3', 'dsaf', '144121004'),
        (572, 1, 't4', 'dsa', '1441210088'),
        (573, 1, 't6', 'hj', '1441261006'),
        (574, 1, 't7', '523', '1234567891'),
        (575, 1, 't8', '46', '1234567891'),
        (578, 1, 't', '324', '9128468255'),
        (579, 1, 't', '342', '1234561234'),
        (581, 1, 'tre', '432', '9125674322');
        
        -- data for table `courier`
        INSERT INTO `courier` (`CNID`, `CID`, `CFName`, `CLName`, `cphone`) VALUES
        ('35165', 2, 'Amir', 'Naseri', '9216588464'),
        ('213123', 3, 'Amir', 'Abbasi', '9325345644'),
        ('5846879159', 1, 'Ali', 'Amiri', '9124563456');
        
        -- data for table `orders`
        INSERT INTO `orders` (`orderID`, `orderDate`, `customerID`, `AID`, `courierID`) VALUES
        (1, '2020-01-31 17:25:05', 3, NULL, NULL),
        (2, '2020-01-31 17:25:15', 1, 8, 1),
        (3, '2020-01-30 17:26:22', 2, NULL, NULL),
        (4, '2020-01-31 20:38:09', 3, 573, NULL),
        (7, '2020-01-31 20:38:09', 46, NULL, 3),
        (30, '2020-01-30 17:26:22', NULL, NULL, NULL);
        
        -- data for table `order_menu`
        INSERT INTO `order_menu` (`orderID`, `foodName`, `price`, `unit`) VALUES
        (1, 'a', '25.50', 1),
        (1, 'b', '33.00', 3),
        (1, 'd', '40.00', 1),
        (2, 'a', '25.50', 1),
        (2, 'a', '30.00', 2),
        (3, 'a', '30.00', 4),
        (3, 'b', '33.00', 1),
        (4, 'd', '40.00', 3);
        
        -- data for table `shop`
        INSERT INTO `shop` (`SID`, `SName`, `status`) VALUES
        (1, 'Shop_One', 'active'),
        (2, 'Shop_Two', 'active'),
        (3, 'Shop_Three', 'inactive');
        
        -- data for table `shopitem`
        INSERT INTO `shopitem` (`SID`, `IID`, `IName`, `Iprice`, `start`, `end`) VALUES
        (1, 1, 'item1', '20.00', '2020-01-24', '2020-01-27'),
        (1, 1, 'item1', '30.00', '2020-01-30', '2020-02-02'),
        (1, 2, 'item2', '15.00', '2020-01-31', '2020-02-04'),
        (1, 3, 'item3', '10.50', '2020-01-30', '2020-01-31'),
        (2, 1, 'item1', '10.00', '2020-01-31', '2020-02-03'),
        (2, 2, 'item2', '25.50', '2020-01-03', '2020-01-31'),
        (3, 1, 'item1', '17.00', '2020-01-16', '2020-01-31');
        
        -- data for table `shoporder`
        INSERT INTO `shoporder` (`orderID`, `SID`, `orderDate`) VALUES
        (1, 1, '2020-01-31'),
        (2, 1, '2020-01-30'),
        (3, 2, '2020-01-31');
        
        -- data for table `shoporder_items`
        INSERT INTO `shoporder_items` (`orderID`, `SID`, `IID`, `Iprice`, `unit`) VALUES
        (1, 1, 1, '20.00', 1),
        (1, 1, 2, '15.00', 3),
        (1, 1, 3, '10.50', 1),
        (2, 1, 3, '10.50', 1),
        (3, 1, 1, '20.00', 3);
        ''', multi=True):
            pass


    # creating the triggers for the first time
    def create_triggers(self, db):
        cur = db.cursor()

        # need a for loop so that cursor runs all of the statements! Without
        # the loop it simply will not execute anything!
        for result in cur.execute(''' 
        -- Checking phone numbers

        CREATE TRIGGER check_address_phone
        BEFORE INSERT
        ON address
        FOR EACH ROW
        BEGIN
          IF (length(NEW.fphone) <> 10) THEN -- Abort when trying to insert this record
                CALL phone_number_not_valid; -- raise an error to prevent insertion to the table
          END IF;
        END;


        CREATE TRIGGER check_courier_phone
        BEFORE INSERT
        ON courier
        FOR EACH ROW
        BEGIN
          IF ((length(NEW.cphone) <> 10) OR not(CAST(NEW.cphone AS CHAR(10)) like '9%')) THEN -- Abort when trying to insert this record
                CALL phone_number_not_valid; -- raise an error to prevent insertion to the table
          END IF;
        END;


        CREATE TRIGGER check_customer_phone
        BEFORE INSERT
        ON customer
        FOR EACH ROW
        BEGIN
          IF ((length(NEW.cphone) <> 10) OR not(CAST(NEW.cphone AS CHAR(10)) like '9%')) THEN -- Abort when trying to insert this record
                CALL phone_number_not_valid; -- raise an error to prevent insertion to the table
          END IF;
        END;


        -- Triggers for logs

        -- menu logs


        CREATE TRIGGER ins_menuLog
        AFTER insert
        ON menu
        FOR EACH ROW
        BEGIN
            INSERT INTO menu_log VALUES(Now(), 'menu', 'insert', NEW.foodName, NEW.price, new.start, new.end);
        END;



        CREATE TRIGGER update_menuLog
        before update
        ON menu
        FOR EACH ROW
        BEGIN
            INSERT INTO menu_log VALUES(Now(), 'menu', 'update', OLD.foodName, OLD.price, OLD.start, OLD.end);
        END;

        

        CREATE TRIGGER del_menuLog
        before delete
        ON menu
        FOR EACH ROW
        BEGIN
            INSERT INTO menu_log VALUES(Now(), 'menu', 'delete', OLD.foodName, OLD.price, OLD.start, OLD.end);
        END;

        
        -- customer logs
        

        CREATE TRIGGER ins_customerLog
        AFTER insert
        ON customer
        FOR EACH ROW
        BEGIN
            INSERT INTO customer_log VALUES(Now(), 'customer', 'insert', NEW.CID, NEW.FName, NEW.LName, NEW.NID, NEW.cphone, NEW.age, NEW.credit);
        END;

        

        CREATE TRIGGER update_customerLog
        before update
        ON customer
        FOR EACH ROW
        BEGIN
            INSERT INTO customer_log VALUES(Now(), 'customer', 'update', OLD.CID, OLD.FName, OLD.LName, OLD.NID, OLD.cphone, OLD.age, OLD.credit);
        END;

        

        CREATE TRIGGER del_customerLog
        before delete
        ON customer
        FOR EACH ROW
        BEGIN
            INSERT INTO customer_log VALUES(Now(), 'customer', 'delete', OLD.CID, OLD.FName, OLD.LName, OLD.NID, OLD.cphone, OLD.age, OLD.credit);
        END;

        
        -- address logs
        

        CREATE TRIGGER ins_adressLog
        AFTER insert
        ON address
        FOR EACH ROW
        BEGIN
            INSERT INTO address_log VALUES(Now(), 'address', 'insert', NEW.AID, NEW.CID, NEW.name, NEW.address, NEW.fphone);
        END;

        

        CREATE TRIGGER update_addressLog
        before update
        ON address
        FOR EACH ROW
        BEGIN
            INSERT INTO address_log VALUES(Now(), 'address', 'update', OLD.AID, OLD.CID, OLD.name, OLD.address, OLD.fphone);
        END;

        

        CREATE TRIGGER del_addressLog
        before delete
        ON address
        FOR EACH ROW
        BEGIN
            INSERT INTO address_log VALUES(Now(), 'address', 'delete', OLD.AID, OLD.CID, OLD.name, OLD.address, OLD.fphone);
        END;

        
        -- courier logs
        

        CREATE TRIGGER ins_courierLog
        AFTER insert
        ON courier
        FOR EACH ROW
        BEGIN
            INSERT INTO courier_log VALUES(Now(), 'courier', 'insert', NEW.CNID, NEW.CID, NEW.CFName, NEW.CLName, NEW.cphone);
        END;

        

        CREATE TRIGGER update_courierLog
        before update
        ON courier
        FOR EACH ROW
        BEGIN
            INSERT INTO courier_log VALUES(Now(), 'courier', 'update', OLD.CNID, OLD.CID, OLD.CFName, OLD.CLName, OLD.cphone);
        END;

        

        CREATE TRIGGER del_courierLog
        before delete
        ON courier
        FOR EACH ROW
        BEGIN
            INSERT INTO courier_log VALUES(Now(), 'courier', 'delete', OLD.CNID, OLD.CID, OLD.CFName, OLD.CLName, OLD.cphone);
        END;

        
        -- orders logs
        

        CREATE TRIGGER ins_ordersLog
        AFTER insert
        ON orders
        FOR EACH ROW
        BEGIN
            INSERT INTO orders_log VALUES(Now(), 'orders', 'insert', NEW.orderID, NEW.orderDate, NEW.customerID, NEW.AID, NEW.courierID);
        END;

        

        CREATE TRIGGER update_ordersLog
        before update
        ON orders
        FOR EACH ROW
        BEGIN
            INSERT INTO orders_log VALUES(Now(), 'orders', 'update', OLD.orderID, OLD.orderDate, OLD.customerID, OLD.AID, OLD.courierID);
        END;

        

        CREATE TRIGGER del_ordersLog
        before delete
        ON orders
        FOR EACH ROW
        BEGIN
            INSERT INTO orders_log VALUES(Now(), 'orders', 'delete', OLD.orderID, OLD.orderDate, OLD.customerID, OLD.AID, OLD.courierID);
        END;

        
        -- shop logs
        

        CREATE TRIGGER ins_shopLog
        AFTER insert
        ON shop
        FOR EACH ROW
        BEGIN
            INSERT INTO shop_log VALUES(Now(), 'shop', 'insert', NEW.SID, NEW.SName, NEW.status);
        END;

        

        CREATE TRIGGER update_shopLog
        before update
        ON shop
        FOR EACH ROW
        BEGIN
            INSERT INTO shop_log VALUES(Now(), 'shop', 'update', OLD.SID, OLD.SName, OLD.status);
        END;

        

        CREATE TRIGGER del_shopLog
        before delete
        ON shop
        FOR EACH ROW
        BEGIN
            INSERT INTO shop_log VALUES(Now(), 'shop', 'delete', OLD.SID, OLD.SName, OLD.status);
        END;

        
        -- shopItem logs
        

        CREATE TRIGGER ins_shopItemLog
        AFTER insert
        ON shopItem
        FOR EACH ROW
        BEGIN
            INSERT INTO shopItem_log VALUES(Now(), 'shopItem', 'insert', NEW.SID, NEW.IID, NEW.IName, NEW.Iprice, NEW.start, NEW.end);
        END;

        

        CREATE TRIGGER update_shopItemLog
        before update
        ON shopItem
        FOR EACH ROW
        BEGIN
            INSERT INTO shopItem_log VALUES(Now(), 'shopItem', 'update', OLD.SID, OLD.IID, OLD.IName, OLD.Iprice, OLD.start, OLD.end);
        END;

        

        CREATE TRIGGER del_shopItemLog
        before delete
        ON shopItem
        FOR EACH ROW
        BEGIN
            INSERT INTO shopItem_log VALUES(Now(), 'shopItem', 'delete', OLD.SID, OLD.IID, OLD.IName, OLD.Iprice, OLD.start, OLD.end);
        END;


        
        -- shopOrder logs
        

        CREATE TRIGGER ins_shopOrderLog
        AFTER insert
        ON shopOrder
        FOR EACH ROW
        BEGIN
            INSERT INTO shopOrder_log VALUES(Now(), 'shopOrder', 'insert', NEW.orderID, new.SID, new.orderDate);
        END;

        

        CREATE TRIGGER update_shopOrderLog
        before update
        ON shopOrder
        FOR EACH ROW
        BEGIN
            INSERT INTO shopOrder_log VALUES(Now(), 'shopOrder', 'update', OLD.orderID, OLD.SID, OLD.orderDate);
        END;

        

        CREATE TRIGGER del_shopOrderLog
        before delete
        ON shopOrder
        FOR EACH ROW
        BEGIN
            INSERT INTO shopOrder_log VALUES(Now(), 'shopOrder', 'delete', OLD.orderID, OLD.SID, OLD.orderDate);
        END;

        
        -- order_menu logs
        

        CREATE TRIGGER ins_order_menuLog
        AFTER insert
        ON order_menu
        FOR EACH ROW
        BEGIN
            INSERT INTO order_menu_log VALUES(Now(), 'order_menu', 'insert', NEW.orderID, NEW.foodName, NEW.price, NEW.unit);
        END;

        

        CREATE TRIGGER update_order_menuLog
        before update
        ON order_menu
        FOR EACH ROW
        BEGIN
            INSERT INTO order_menu_log VALUES(Now(), 'order_menu', 'update', OLD.orderID, OLD.foodName, OLD.price, OLD.unit);
        END;

        

        CREATE TRIGGER del_order_menuLog
        before delete
        ON order_menu
        FOR EACH ROW
        BEGIN
            INSERT INTO order_menu_log VALUES(Now(), 'order_menu', 'delete', OLD.orderID, OLD.foodName, OLD.price, OLD.unit);
        END;

        
        -- shoporder_items logs
        

        CREATE TRIGGER ins_shoporder_itemsLog
        AFTER insert
        ON shoporder_items
        FOR EACH ROW
        BEGIN
            INSERT INTO shoporder_items_log VALUES(Now(), 'shoporder_items', 'insert', NEW.orderID, NEW.SID, NEW.IID, NEW.Iprice, NEW.unit);
        END;

        

        CREATE TRIGGER update_shoporder_itemsLog
        before update
        ON shoporder_items
        FOR EACH ROW
        BEGIN
            INSERT INTO shoporder_items_log VALUES(Now(), 'shoporder_items', 'update', OLD.orderID, OLD.SID, OLD.IID, OLD.Iprice, OLD.unit);
        END;

        

        CREATE TRIGGER del_shoporder_itemsLog
        before delete
        ON shoporder_items
        FOR EACH ROW
        BEGIN
            INSERT INTO shoporder_items_log VALUES(Now(), 'shoporder_items', 'delete', OLD.orderID, OLD.SID, OLD.IID, OLD.Iprice, OLD.unit);
        END;

        ''', multi=True):
            pass


    # creating the procedures and functions for our database
    def create_procedures(self, db):
        cur = db.cursor()

        # need a for loop so that cursor runs all of the statements! Without
        # the loop it simply will not execute anything!
        for result in cur.execute(''' 
        -- refreshing logs, deleting logs older than 3 days
        CREATE PROCEDURE if not exists refresh_logs()
        BEGIN
            delete from address_log
                where date (now()) - date (logTime) > 3;
            delete from courier_log
                where date (now()) - date (logTime) > 3;
            delete from customer_log
                where date (now()) - date (logTime) > 3;
            delete from menu_log
                where date (now()) - date (logTime) > 3;
            delete from order_menu_log
                where date (now()) - date (logTime) > 3;
            delete from orders_log
                where date (now()) - date (logTime) > 3;
            delete from shop_log
                where date (now()) - date (logTime) > 3;
            delete from shoporder_items_log
                where date (now()) - date (logTime) > 3;
            delete from shoporder_log
                where date (now()) - date (logTime) > 3;
            delete from shoporder_items_log
                where date (now()) - date (logTime) > 3;
        END;
            
        -- transfering credit between users
        CREATE PROCEDURE transfer_money(IN senderID int, IN receiverID int, IN amount int)
        BEGIN
            IF (select credit from customer where CID = senderID) >= amount THEN
            update customer
            set credit = credit - amount
            where CID = senderID;
        
            update customer
            set credit = credit + amount
            where CID = receiverID;
        
            END IF;
        END;
        
        -- adding a new food to the menu            
        CREATE PROCEDURE add_new_food(IN food_name varchar(50), IN new_price decimal(10, 2), IN start_date date, IN end_date date)
        BEGIN
            INSERT INTO `Menu` (`foodName`, `price`, `start`, `end`) VALUES
            (food_name, new_price, start_date, end_date);
            
        END;
        
        -- add a bonus credit to every customer
        CREATE PROCEDURE credit_giveaway(IN amount decimal(10, 2))
        BEGIN
            UPDATE customer
            SET customer.credit = customer.credit + amount;
        
        END;
        
        -- function to return the number of addresses for each person
        CREATE FUNCTION customer_addresses (
            customer_id int
        )
        RETURNS int
        DETERMINISTIC
        BEGIN
            DECLARE num_addresses int;
            set num_addresses = (select count(*) from address where CID = customer_id);
            RETURN num_addresses;
        END;
        
        -- getting total menu price
        CREATE FUNCTION total_menu_price (
        )
        RETURNS decimal(10, 2)
        DETERMINISTIC
        BEGIN
            DECLARE total_price decimal(10, 2);
            set total_price= (select sum(price) from menu);
            RETURN total_price;
        END;
        
        -- gettint total number of menu items
        CREATE FUNCTION menu_items_num (
        )
        RETURNS int
        DETERMINISTIC
        BEGIN
            DECLARE total_num int;
            set total_num = (select count(*) from menu);
            RETURN total_num;
        END;
        ''', multi=True):
            pass


    # creating the roles for our database
    def create_roles(self, db):
        cur = db.cursor()

        # need a for loop so that cursor runs all of the statements! Without
        # the loop it simply will not execute anything!
        for result in cur.execute(''' 
        CREATE USER if not exists 'database_admin'@'localhost' IDENTIFIED BY 'Admin';
        CREATE USER if not exists 'database_customer'@'localhost' IDENTIFIED BY '1234';
        CREATE USER if not exists 'database_restaurant_manager'@'localhost' IDENTIFIED BY '1234';
        CREATE USER if not exists 'database_shop_manager'@'localhost' IDENTIFIED BY '1234';
        
        -- granting permissions to the roles
        flush privileges;
        -- db_admin perssions
        GRANT ALL PRIVILEGES ON restaurant_management.* TO 'database_admin'@'localhost' IDENTIFIED BY 'Admin';
        
        -- customer perssions
        GRANT SELECT ON restaurant_management.menu to 'database_customer'@'localhost' IDENTIFIED BY '1234';
        GRANT SELECT ON restaurant_management.courier to 'database_customer'@'localhost' IDENTIFIED BY '1234';
        GRANT SELECT ON restaurant_management.order_menu to 'database_customer'@'localhost' IDENTIFIED BY '1234';
        GRANT SELECT ON restaurant_management.orders to 'database_customer'@'localhost' IDENTIFIED BY '1234';
        
        -- restaurant_manager permissions
        GRANT  SELECT, INSERT, UPDATE, DELETE ON restaurant_management.address TO 'database_restaurant_manager'@'localhost' IDENTIFIED BY '1234';
        GRANT  SELECT, INSERT, UPDATE, DELETE ON restaurant_management.address_log TO 'database_restaurant_manager'@'localhost' IDENTIFIED BY '1234';
        GRANT  SELECT, INSERT, UPDATE, DELETE ON restaurant_management.courier TO 'database_restaurant_manager'@'localhost' IDENTIFIED BY '1234';
        GRANT  SELECT, INSERT, UPDATE, DELETE ON restaurant_management.courier_log TO 'database_restaurant_manager'@'localhost' IDENTIFIED BY '1234';
        GRANT  SELECT, INSERT, UPDATE, DELETE ON restaurant_management.customer TO 'database_restaurant_manager'@'localhost' IDENTIFIED BY '1234';
        GRANT  SELECT, INSERT, UPDATE, DELETE ON restaurant_management.customer_log TO 'database_restaurant_manager'@'localhost' IDENTIFIED BY '1234';
        GRANT  SELECT, INSERT, UPDATE, DELETE ON restaurant_management.menu TO 'database_restaurant_manager'@'localhost' IDENTIFIED BY '1234';
        GRANT  SELECT, INSERT, UPDATE, DELETE ON restaurant_management.menu_log TO 'database_restaurant_manager'@'localhost' IDENTIFIED BY '1234';
        GRANT  SELECT, INSERT, UPDATE, DELETE ON restaurant_management.order_menu TO 'database_restaurant_manager'@'localhost' IDENTIFIED BY '1234';
        GRANT  SELECT, INSERT, UPDATE, DELETE ON restaurant_management.order_menu_log TO 'database_restaurant_manager'@'localhost' IDENTIFIED BY '1234';
        GRANT  SELECT, INSERT, UPDATE, DELETE ON restaurant_management.orders TO 'database_restaurant_manager'@'localhost' IDENTIFIED BY '1234';
        GRANT  SELECT, INSERT, UPDATE, DELETE ON restaurant_management.orders_log TO 'database_restaurant_manager'@'localhost' IDENTIFIED BY '1234';
        
        -- shop_manager permissions
        GRANT  SELECT, INSERT, UPDATE, DELETE ON restaurant_management.shop TO 'database_shop_manager'@'localhost' IDENTIFIED BY '1234';
        GRANT  SELECT, INSERT, UPDATE, DELETE ON restaurant_management.shop_log TO 'database_shop_manager'@'localhost' IDENTIFIED BY '1234';
        GRANT  SELECT, INSERT, UPDATE, DELETE ON restaurant_management.shopitem TO 'database_shop_manager'@'localhost' IDENTIFIED BY '1234';
        GRANT  SELECT, INSERT, UPDATE, DELETE ON restaurant_management.shopitem_log TO 'database_shop_manager'@'localhost' IDENTIFIED BY '1234';
        GRANT  SELECT, INSERT, UPDATE, DELETE ON restaurant_management.shoporder TO 'database_shop_manager'@'localhost' IDENTIFIED BY '1234';
        GRANT  SELECT, INSERT, UPDATE, DELETE ON restaurant_management.shoporder_log TO 'database_shop_manager'@'localhost' IDENTIFIED BY '1234';
        GRANT  SELECT, INSERT, UPDATE, DELETE ON restaurant_management.shoporder_items TO 'database_shop_manager'@'localhost' IDENTIFIED BY '1234';
        GRANT  SELECT, INSERT, UPDATE, DELETE ON restaurant_management.shoporder_items_log TO 'database_shop_manager'@'localhost' IDENTIFIED BY '1234';

        ''', multi=True):
            pass
        


    # showing database tables
    def show_tables(self):

        db = self.db
        cursor = self.db.cursor()
        cursor.execute("show tables;", multi=False)

        tables = [item[0] for item in cursor.fetchall()]
        print("Select a table:")

        for i in range(len(tables)):
            print(i, tables[i])

        tab = combo_box(tables, "Choose a table", "Select a table")
        stmt = "describe " + tables[tab]
        print(stmt)
        cursor.execute(stmt)
        headers = [item[0] for item in cursor.fetchall()]

        print(headers)
        stmt = "select * from " + tables[tab]
        cursor.execute(stmt)
        result = [item for item in cursor.fetchall()]
        for i in range(len(result)):
            print(result[i])

        def show():
            listBox.delete(*listBox.get_children())
            stmt = "select * from " + tables[tab]
            cursor.execute(stmt)
            result = [item for item in cursor.fetchall()]
            tempList = result
            for i in range(len(tempList)):
                listBox.insert("", "end", values=result[i])

        def insert():
            stmt = "Insert into " + tables[tab] + " values("
            tmpres = ''
            for i in range(len(headers)):
                tmpres = entries[i].get()
                if isSelectable(i):
                    cp = entries[i].current()
                    tmpres = str(blist1[getProperBlist(i)][cp])
                if isSelectable2(i):
                    cp = entries[i].current()
                    tmpres = str(blist2[cp])
                if tmpres == '' or tmpres == 'None':
                    tmpres = 'null'
                else:
                    tmpres = "'" + tmpres + "'"
                stmt += tmpres
                stmt += ", "
            stmt = stmt[:-2]
            stmt += ")"
            print(stmt)
            cursor.execute(stmt)
            db.commit()
            show()

        backupRow = []

        def update():
            stmt = "update " + tables[tab] + " set "
            tmpres = ''
            for i in range(len(headers)):
                tmpres = entries[i].get()
                if isSelectable(i):
                    cp = entries[i].current()
                    tmpres = str(blist1[getProperBlist(i)][cp])
                if isSelectable2(i):
                    cp = entries[i].current()
                    tmpres = str(blist2[cp])
                if tmpres == '' or tmpres == 'None':
                    tmpres = 'null'
                else:
                    tmpres = "'" + tmpres + "'"
                stmt += headers[i] + "=" + tmpres + ", "
            stmt = stmt[:-2]
            stmt += " Where "
            print(backupRow)
            for i in range(len(headers)):
                tmpres = backupRow[i]
                if tmpres == '' or tmpres == 'None':
                    tmpres = 'null'
                else:
                    tmpres = "'" + tmpres + "'"
                if tmpres == 'null':
                    stmt += headers[i] + " is null and "
                    continue
                stmt += headers[i] + "=" + tmpres + " and "
            stmt = stmt[:-4]
            print(stmt)
            cursor.execute(stmt)
            db.commit()
            show()

        def delete():
            stmt = "delete from " + tables[tab] + " where "
            print(backupRow)
            tmpres = ''
            for i in range(len(headers)):
                tmpres = backupRow[i]
                if tmpres == '' or tmpres == 'None':
                    tmpres = 'null'
                else:
                    tmpres = "'" + tmpres + "'"
                if tmpres == 'null':
                    stmt += headers[i] + " is null and "
                    continue
                stmt += headers[i] + "='" + backupRow[i] + "' and "
            stmt = stmt[:-4]
            print(stmt)
            cursor.execute(stmt)
            db.commit()
            show()

        def onClick(event):
            backupRow.clear()
            item = listBox.identify("item", event.x, event.y)
            print(listBox.item(item, 'values'))
            ins = listBox.item(item, 'values')
            for i in range(len(ins)):
                print(ins[i])
                backupRow.append(ins[i])
                entries[i].delete(0, tk.END)
                entries[i].insert(0, ins[i])

        def isSelectable(i):
            '''if tables[tab] == 'orders' and (
                    headers[i] == 'AID' or headers[i] == 'customerID' or headers[i] == 'courierID'):
                return True'''
            return False

        def getProperBlist(i):
            if headers[i] == 'AID':
                return 0
            elif headers[i] == 'courierID':
                return 1
            elif headers[i] == 'customerID':
                return 2

        def isSelectable2(i):
            '''if (tables[tab] == 'shoporder' or tables[tab] == 'shoporder_items') and (headers[i] == 'SID'):
                return True'''
            return False

        root = tk.Tk()
        tree = ttk.Treeview()
        #  Entry(self.root, textvariable=mystring).grid(row=0, column=1, sticky=E)  # entry textbox
        showTable = root
        showTable.title("9631019 - Arash Hajisafi")
        label = tk.Label(showTable, text=tables[tab], font=("Arial", 30)).grid(row=0, columnspan=len(headers))
        label2 = tk.Label(showTable, text="                      ").grid(row=4, columnspan=len(headers))
        label3 = tk.Label(showTable, text="                      ").grid(row=6, columnspan=len(headers))
        # create Treeview with 3 columns
        cols = headers
        tree = ttk.Treeview(showTable, columns=headers, show='headings')
        listBox = tree
        # set column headings
        for col in cols:
            listBox.heading(col, text=col)
        listBox.grid(row=10, column=0, columnspan=len(headers))
        show()
        entries = []

        blist1 = [[], [], []]
        blist2 = []
        for i in range(len(headers)):
            if isSelectable(i):
                if headers[i] == 'AID':
                    stmt = "select * from address"
                    cursor.execute(stmt)
                    resultset = [item for item in cursor.fetchall()]
                    resultset.insert(0, "None")
                    blist1[0] = [item[0] for item in resultset]
                    blist1[0][0] = "None"
                    print(resultset)
                    entries.append(ttk.Combobox(showTable, values=resultset))
                    entries[i].grid(row=5, column=i)
                    continue
                elif headers[i] == 'courierID':
                    stmt = "select * from courier"
                    cursor.execute(stmt)
                    resultset = [item for item in cursor.fetchall()]
                    resultset.insert(0, "None")
                    blist1[1] = [item[1] for item in resultset]
                    blist1[1][0] = "None"
                    print(resultset)
                    entries.append(ttk.Combobox(showTable, values=resultset))
                    entries[i].grid(row=5, column=i)
                    continue
                elif headers[i] == 'customerID':
                    stmt = "select * from customer"
                    cursor.execute(stmt)
                    resultset = [item for item in cursor.fetchall()]
                    resultset.insert(0, "None")
                    blist1[2] = [item[0] for item in resultset]
                    blist1[2][0] = "None"
                    print(resultset)
                    entries.append(ttk.Combobox(showTable, values=resultset))
                    entries[i].grid(row=5, column=i)
                    continue
            elif isSelectable2(i):
                stmt = "select * from shop"
                cursor.execute(stmt)
                resultset = [item for item in cursor.fetchall()]
                k = 0
                lim = len(resultset)
                while k < lim:
                    if resultset[k][2] == 'inactive':
                        del resultset[k]
                        lim -= 1
                        k -= 1
                    k += 1
                resultset.insert(0, "None")
                blist2 = [item[0] for item in resultset]
                blist2[0] = 'None'
                print(resultset)
                print(blist2)
                entries.append(ttk.Combobox(showTable, values=resultset))
                entries[i].grid(row=5, column=i)
                continue

            entries.append(ttk.Entry(root))
            entries[i].grid(row=5, column=i)

        updateButton = tk.Button(showTable, text="Update", width=15, command=update).grid(row=1, column=0)
        closeButton = tk.Button(showTable, text="Close", width=15, command=exit).grid(row=3, column=len(headers) - 1)
        deleteButton = tk.Button(showTable, text="Delete", width=15, command=delete).grid(row=1,
                                                                                          column=len(headers) - 1)
        insertButton = tk.Button(showTable, text="Insert", width=15, command=insert).grid(row=3, column=0)

        listBox.bind("<ButtonRelease-1>", onClick)
        root.mainloop()
        db.close()


    # generating reports from queries
    def generate_reports(self):
        db = self.db
        cursor = db.cursor()

        f = open("report.txt", "w")

        # Customers ordered on which days + how many addresses they have
        cursor.execute("""select customer.CID, customer.FName, customer.LName, customer.credit, customer_addresses(customer.CID) as num_of_addresses, orderDate
        from customer, orders
        where orders.customerID = customer.CID;""")

        printReportBeautifully(cursor, "Customers ordered on which days + how many addresses they have", ['Customer ID', 'First Name', 'Last Name', 'Credits', '# Addresses', 'on date'], f)

        # food menu along with max, min, and average menu price as well as the total number of available food
        cursor.execute("""select foodName, price, average_price, max_price, min_price,
       total_menu_price, food_num
        from menu, (select avg(price) as average_price, max(price) as max_price, min(price) as min_price,
       total_menu_price() as total_menu_price, menu_items_num() as food_num from menu) as agg_clause;
       """)

        printReportBeautifully(cursor, "food menu along with max, min, and average menu price as well as the total number of available food", ['foodName', 'price', 'average_price', 'max_price', 'min_price', 'total_menu_price', '# available food'], f)

        # Total Sales
        cursor.execute("""select om.foodName, sum(om.unit) as total_sold, avg(om.price) as unit_price, date (o.orderDate) as on_date
        from order_menu om, orders o
        where om.orderID = o.orderID
        group by om.foodName, date(o.orderDate)
        order by on_date;""")

        printReportBeautifully(cursor, "Total Sales", ['foodName', 'total_sold', 'unit_price', 'on_date'], f)

        # Income for each menu-order
        cursor.execute(
            """select o.orderID, sum(om.unit * om.price) as total_price, date(orderDate) as on_Date from order_menu om, orders o where om.orderID = o.orderID group by o.orderID""")

        printReportBeautifully(cursor, "Income for each menu-order", ['orderID', 'total_price', 'on_date'], f)

        # Total income for each day
        cursor.execute("""select on_date, sum(total_price) as total_income from
        (select o.orderID, sum(om.unit * om.price) as total_price, date(orderDate) as on_Date from order_menu om, orders o where om.orderID = o.orderID group by o.orderID) as day_order
        group by on_date""")

        printReportBeautifully(cursor, 'Total income for each day', ['on_date', 'total_income'], f)

        # Order cost for each order from shop
        cursor.execute("""select so.orderID, sum(soi.unit * soi.Iprice) as order_cost, date(orderDate) as on_Date
        from shoporder so, shopOrder_Items soi
        where so.orderID = soi.orderID
        group by so.orderID""")

        printReportBeautifully(cursor, 'Order cost for each order from shop', ['orderID', 'order_cost', 'on_date'], f)

        # Total spendings on each day for shop orders
        cursor.execute("""select on_date, sum(total_price) as total_spent from
        (
        select so.orderID, sum(soi.unit * soi.Iprice) as total_price, date(orderDate) as on_Date
        from shoporder so, shopOrder_Items soi
        where so.orderID = soi.orderID
        group by so.orderID ) as day_spent
        group by on_date""")

        printReportBeautifully(cursor, 'Total spent on each day for shop orders', ['on_date', 'total_spent'], f)

        # Profit for each day
        cursor.execute("""select spent.on_Date, total_income, total_spent, (total_income - total_spent) as profit
        from (select on_date, sum(total_price) as total_income from
        (select o.orderID, sum(om.unit * om.price) as total_price, date(orderDate) as on_Date from order_menu om, orders o where om.orderID = o.orderID group by o.orderID) as day_order
        group by on_date) as incomes
        , (select on_date, sum(total_price) as total_spent from
        (
        select so.orderID, sum(soi.unit * soi.Iprice) as total_price, date(orderDate) as on_Date
        from shoporder so, shopOrder_Items soi
        where so.orderID = soi.orderID
        group by so.orderID ) as day_spent
        group by on_date) as spent
        where incomes.on_Date = spent.on_Date""")

        printReportBeautifully(cursor, 'Profit for each day', ['on_date', 'total_income', 'total_spent', 'profit'], f)


        # Ordered food for each customer
        cursor.execute("""select c.CID, c.FName, c.LName, om.foodName, sum(om.unit) as times_ordered from order_menu om, orders o, customer c
        where om.orderID = o.orderID and o.customerID = c.CID
        group by cid, foodName;""")

        printReportBeautifully(cursor, 'Ordered food for each customer',
                               ['customerID', 'First_name', 'Last_name', 'foodName', 'times_ordered'], f)


        # Food most ordered by each user
        cursor.execute("""select  user_orders.CID, FName, LName, foodName as most_ordered_food, times_ordered
        from (
            select max(times_ordered) as max_ordered_times, CID
            from (
                select c.CID, c.FName, c.LName, om.foodName, sum(om.unit) as times_ordered from order_menu om, orders o, customer c
                where om.orderID = o.orderID and o.customerID = c.CID
                group by cid, foodName) as user_orders
                group by CID
            ) as user_orders,
             (
            select c.CID, c.FName, c.LName, om.foodName, sum(om.unit) as times_ordered from order_menu om, orders o, customer c
            where om.orderID = o.orderID and o.customerID = c.CID
            group by cid, foodName
                 ) as ordered
        where ordered.times_ordered = max_ordered_times and ordered.CID = user_orders.CID;""")

        printReportBeautifully(cursor, 'Food most ordered by each user',
                               ['customerID', 'First_name', 'Last_name', 'most_oredered_food', 'times_ordered'], f)

        db.close()
        f.close()
        webbrowser.open("report.txt")

    def remove_tables(self):
        db = self.db
        cursor = db.cursor()

        cursor.execute("show tables")

        tables = [item[0] for item in cursor.fetchall()]
        print("Select a table to remove:")

        for i in range(len(tables)):
            print(i, tables[i])

        tab = combo_box(tables, "Select table to remove", "Select table to remove")
        stmt = "drop table " + tables[tab]
        print(stmt)
        cursor.execute(stmt)
        db.commit()
        print("Table", tables[tab], "removed")
        db.close()

    def create_tables(self):
        db = self.db
        cursor = db.cursor()

        fields = 'Table name', 'Attributes', 'Constraints'

        def mktable():
            stmt = ""
            stmt += "create table "
            stmt += ents[0].get()
            stmt += "(" + ents[1].get()
            if ents[2].get() != "":
                stmt += ", "
            stmt += ents[2].get() + ")"
            print(stmt)
            cursor.execute(stmt)
            db.commit()
            root.destroy()

        def makeform(root, fields):
            entries = []
            for field in fields:
                row = tk.Frame(root)
                lab = tk.Label(row, width=15, text=field, anchor='w')
                ent = tk.Entry(row)
                row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
                lab.pack(side=tk.LEFT)
                ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
                entries.append(ent)
            return entries

        root = tk.Tk()
        ents = makeform(root, fields)

        b1 = tk.Button(root, text='Create Table', command=mktable)
        b1.pack(side=tk.LEFT, padx=5, pady=5)
        b2 = tk.Button(root, text='Quit', command=root.destroy)
        b2.pack(side=tk.LEFT, padx=5, pady=5)
        root.mainloop()

        db.close()

    def close_connection(self):
        self.db.commit()
        self.db.close()


    # calling the refresh_logs() procedure
    def refresh_logs(self):
        db = self.db
        cursor = db.cursor()

        cursor.callproc('refresh_logs')
        db.commit()


    # calling the transfer_money() procedure
    def transfer_money(self):
        global event_args
        db = self.db
        cursor = db.cursor()
        money_transfer_window()
        event_args[0] = int(event_args[0])
        event_args[1] = int(event_args[1])
        event_args[2] = float(event_args[2])

        cursor.callproc('transfer_money', (event_args[0], event_args[1], event_args[2]))
        db.commit()


    # calling the add_new_food() procedure
    def credit_giveaway(self):
        global event_args
        db = self.db
        cursor = db.cursor()

        credit_giveaway_window()
        cursor.callproc('credit_giveaway', (float(event_args),  ))
        db.commit()
        print("Every customer's credit increased by {}".format(float(event_args)))




def printReportBeautifully(cursor, title, headersnames, f):
    f.write(title)
    f.write("\n")
    print(title)
    myresult = cursor.fetchall()
    finalres = tabulate(myresult, headers=headersnames, tablefmt='psql')
    print(finalres)
    f.write(finalres)
    f.write("\n\n\n")
    print("\n")


# reading combo_box's value to global variables
def get_combo_value(combo_display, app):
    global option, USER, db_users
    option = combo_display.current()
    app.destroy()


# reading combo_box's value + password to global variables
def get_combo_value_wpass(combo_display, pass_entry, app):
    global option, USER, PASSWD, db_users
    option = combo_display.current()
    USER = db_users[option]
    PASSWD = pass_entry.get()
    print("Selected User: {}\nEntered Password: {}".format(USER, PASSWD))
    app.destroy()


# Making and displaying a little window to select an option from the given options
def combo_box(optionset, title, top_label):
    global option
    app = tk.Tk()
    app.geometry('300x100')
    label_top = tk.Label(app, text=top_label)
    label_top.grid(column=0, row=0)
    combo_display = ttk.Combobox(app, values=optionset)
    combo_display.grid(column=0, row=1)
    combo_display.current(0)
    option_button = tk.Button(app, text="OK", width=15, command=lambda: get_combo_value(combo_display, app)).grid(row=2, column=0)
    exit_button = tk.Button(app, text="Exit", width=15, command=exit).grid(row=3, column=0)
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)
    app.title(title)
    app.mainloop()
    return option


# Making and displaying a little window to select an option from the given options + entering the password
def combo_box_wpassword(optionset, title, top_label):
    global option
    app = tk.Tk()
    app.geometry('300x150')
    label_top = tk.Label(app, text=top_label)
    label_top.grid(column=0, row=0)
    combo_display = ttk.Combobox(app, values=optionset)
    combo_display.grid(column=0, row=1)
    pass_label = tk.Label(app, text="Enter password:")
    pass_label.grid(column=0, row=2)
    pass_entry = ttk.Entry(app, show="*", width=15)
    pass_entry.grid(column=0, row=3)
    combo_display.current(0)
    option_button = tk.Button(app, text="OK", width=15, command=lambda: get_combo_value_wpass(combo_display, pass_entry, app)).grid(row=4, column=0)
    exit_button = tk.Button(app, text="Exit", width=15, command=exit).grid(row=5, column=0)
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)
    app.title(title)
    app.mainloop()
    return option


# Making and displaying a little window for money transferring
def money_transfer_window():
    global event_args
    app = tk.Tk()
    app.geometry('300x200')
    label_top = tk.Label(app, text="Enter details")
    det1 = tk.Label(app, text="From (User ID):")
    det2 = tk.Label(app, text="To (User ID):")
    det3 = tk.Label(app, text="Amount (Number):")
    label_top.grid(column=0, row=0)
    det1.grid(column=0, row=1)
    det2.grid(column=0, row=2)
    det3.grid(column=0, row=3)
    entry1 = ttk.Entry(app, width=7)
    entry2 = ttk.Entry(app, width=7)
    entry3 = ttk.Entry(app, width=7)
    entry1.grid(column=1, row=1)
    entry2.grid(column=1, row=2)
    entry3.grid(column=1, row=3)
    option_button = tk.Button(app, text="OK", width=15, command=lambda: get_transfer_details(app, entry1, entry2, entry3)).grid(row=4, column=0)
    exit_button = tk.Button(app, text="Exit", width=15, command=exit).grid(row=5, column=0)
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)
    app.title("Money Transfer")
    app.mainloop()
    return event_args


# Making and displaying a little window to select an option from the given options + entering the password
def credit_giveaway_window():
    global option
    app = tk.Tk()
    app.geometry('400x100')
    label_top = tk.Label(app, text="Enter the amount you want to increase to customers' credits")
    label_top.grid(column=0, row=0)
    credit_display = ttk.Entry(app, width=7)
    credit_display.grid(column=0, row=1)
    option_button = tk.Button(app, text="OK", width=15, command=lambda: get_credit_value(credit_display, app)).grid(row=2, column=0)
    exit_button = tk.Button(app, text="Exit", width=15, command=exit).grid(row=3, column=0)
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)
    app.title("Credit Giveaway")
    app.mainloop()
    return option


# getting money transfer details
def get_transfer_details(app, entry1, entry2, entry3):
    global event_args
    event_args = []
    event_args.append(entry1.get())
    event_args.append(entry2.get())
    event_args.append(entry3.get())
    print("Payment Entries:\tFrom: {}\tTo: {}\tAmount: {}".format(event_args[0], event_args[1], event_args[2]))
    app.destroy()



# reading credit's value to global variables
def get_credit_value (credit_display, app):
    global event_args
    event_args = None
    event_args = credit_display.get()
    app.destroy()



def main():
    global USER, PASSWD, ORIG_USER, ORIG_PASSWD, option, roles
    global option
    db = Restaurant(DB_NAME, USER, PASSWD, ORIG_USER, ORIG_PASSWD)
    db.close_connection()
    while True:

        first_option = roles
        combo_box_wpassword(first_option, "Select an option", "Select user type:")
        print(option)

        db = None

        try:
            db = Restaurant(DB_NAME, USER, PASSWD, ORIG_USER, ORIG_PASSWD)
        except:
            print("Wrong Password!")
            continue

        if option == 0:
            second_option = ["Show and Edit tables", "Get reports", "Remove tables", "Create tables", "Refresh logs", "Transfer Money", "Credit Giveaway Procedure"]
            combo_box(second_option, "Select an option", "Select action:")
            print(option)
            if option == 0:
                db.show_tables()
            elif option == 1:
                db.generate_reports()
            elif option == 2:
                print("remove table")
                db.remove_tables()
            elif option == 3:
                print("create table")
                db.create_tables()
            elif option == 4:
                db.refresh_logs()
            elif option == 5:
                db.transfer_money()
            elif option == 6:
                db.credit_giveaway()


        else:
            second_option = ["Show and Edit tables"]
            combo_box(second_option, "Select an option", "Select action:")
            print(option)
            if option == 0:
                db.show_tables()


if __name__ == "__main__":
    main()