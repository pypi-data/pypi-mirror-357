CREATE TABLE Material_type_import (
    ID INT PRIMARY KEY,
    "Тип материала" TEXT NOT NULL,
    "Процент потерь сырья" DECIMAL(4,2) NOT NULL
);

CREATE TABLE Product_type_import (
    ID INT PRIMARY KEY,
    "Тип продукции" TEXT NOT NULL,
    "Коэффициент типа продукции" DECIMAL(4,2) NOT NULL
);

CREATE TABLE Workshops_import (
    ID INT PRIMARY KEY,
    "Название цеха" TEXT NOT NULL,
    "Тип цеха" TEXT NOT NULL,
    "Количество человек для производства" INT NOT NULL
);

CREATE TABLE Products_import (
    ID INT PRIMARY KEY,
    "Тип продукции" INT NOT NULL,
    "Наименование продукции" TEXT NOT NULL,
    Артикул INT NOT NULL,
    "Минимальная стоимость для партнера" DECIMAL(10,2) NOT NULL,
    "Основной материал" INT NOT NULL,
    FOREIGN KEY ("Тип продукции") REFERENCES Product_type_import(ID),
    FOREIGN KEY ("Основной материал") REFERENCES Material_type_import(ID)
);

CREATE TABLE Product_workshops_import (
    ID INT PRIMARY KEY,
    "Наименование продукции" INT NOT NULL,
    "Название цеха" INT NOT NULL,
    "Время изготовления, ч" DECIMAL(4,2) NOT NULL,
    FOREIGN KEY ("Наименование продукции") REFERENCES Products_import(ID),
    FOREIGN KEY ("Название цеха") REFERENCES Workshops_import(ID)
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