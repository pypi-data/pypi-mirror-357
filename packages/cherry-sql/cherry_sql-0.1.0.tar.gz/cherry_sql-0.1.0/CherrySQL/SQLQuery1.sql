CREATE TABLE Material_type_import (
    ID INT PRIMARY KEY,
    Тип_материала NVARCHAR(255) NOT NULL,
    Процент_брака_материала FLOAT NOT NULL
);

CREATE TABLE Product_type_import (
    ID INT PRIMARY KEY,
    Тип_продукции NVARCHAR(255) NOT NULL,
    Коэффициент_типа_продукции FLOAT NOT NULL
);

CREATE TABLE Products_import (
    ID INT PRIMARY KEY,
    Тип_продукции INT NOT NULL FOREIGN KEY REFERENCES Product_type_import(ID),
    Наименование_продукции NVARCHAR(255) NOT NULL,
    Артикул NVARCHAR(50) NOT NULL,
    Минимальная_стоимость_для_партнера FLOAT NOT NULL
);

CREATE TABLE Partners_import (
    ID INT PRIMARY KEY,
    Тип_партнера NVARCHAR(50) NOT NULL,
    Наименование_партнера NVARCHAR(255) NOT NULL,
    Директор NVARCHAR(255),
    Электронная_почта_партнера NVARCHAR(100),
    Телефон_партнера NVARCHAR(50),
    Юридический_адрес_партнера NVARCHAR(500),
    ИНН VARCHAR(12),
    Рейтинг INT
);

CREATE TABLE Partner_products_request_import (
    ID INT PRIMARY KEY,
    Продукция INT NOT NULL FOREIGN KEY REFERENCES Products_import(ID),
    Наименование_партнера INT NOT NULL FOREIGN KEY REFERENCES Partners_import(ID),
    Количество_продукции INT NOT NULL
);



CREATE TABLE Roles (
    RoleID INT PRIMARY KEY,
    RoleName NVARCHAR(50) NOT NULL
);

-- Добавим роли
INSERT INTO Roles (RoleID, RoleName) VALUES
(1, 'Пользователь'),
(2, 'Менеджер'),
(3, 'Администратор');


CREATE TABLE Users (
    UserID INT PRIMARY KEY IDENTITY(1,1),
    Username NVARCHAR(100) NOT NULL UNIQUE,
    PasswordHash NVARCHAR(255) NOT NULL,
    Email NVARCHAR(255),
    RoleID INT NOT NULL FOREIGN KEY REFERENCES Roles(RoleID)
);
