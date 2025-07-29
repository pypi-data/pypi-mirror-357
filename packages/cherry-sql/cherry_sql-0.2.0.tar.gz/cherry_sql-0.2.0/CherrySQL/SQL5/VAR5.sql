CREATE TABLE Material_type_import (
    ID INT PRIMARY KEY,
    [Тип материала] NVARCHAR(100) NOT NULL,
    [Процент потерь сырья] FLOAT NOT NULL
);

CREATE TABLE Materials_import (
    ID INT PRIMARY KEY,
    [Наименование материала] NVARCHAR(255) NOT NULL,
    [Тип материала] INT NOT NULL,
    [Цена единицы материала] FLOAT NOT NULL,
    [Количество на складе] INT NOT NULL,
    [Минимальное количество] INT NOT NULL,
    [Количество в упаковке] FLOAT NOT NULL,
    [Единица измерения] NVARCHAR(50),
    FOREIGN KEY ([Тип материала]) REFERENCES Material_type_import(ID)
);

CREATE TABLE Product_type_import (
    ID INT PRIMARY KEY,
    [Тип продукции] NVARCHAR(100) NOT NULL,
    [Коэффициент типа продукции] FLOAT NOT NULL
);

CREATE TABLE Products_import (
    ID INT PRIMARY KEY,
    [Тип продукции] INT NOT NULL,
    [Наименование продукции] NVARCHAR(255) NOT NULL,
    [Артикул] NVARCHAR(50),
    [Минимальная стоимость для партнера] FLOAT NOT NULL,
    FOREIGN KEY ([Тип продукции]) REFERENCES Product_type_import(ID)
);

CREATE TABLE Material_products__import (
    ID INT PRIMARY KEY,
    [Наименование материала] INT NOT NULL,
    [Продукция] INT NOT NULL,
    [Необходимое количество материала] FLOAT NOT NULL,
    FOREIGN KEY ([Наименование материала]) REFERENCES Materials_import(ID),
    FOREIGN KEY ([Продукция]) REFERENCES Products_import(ID)
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
    Password NVARCHAR(255) NOT NULL,
    Email NVARCHAR(255),
    RoleID INT NOT NULL FOREIGN KEY REFERENCES Roles(RoleID)
);