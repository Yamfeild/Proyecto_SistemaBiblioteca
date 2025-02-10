CREATE DATABASE Biblioteca;
USE Biblioteca;

CREATE TABLE Usuario (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nombres VARCHAR(25) NOT NULL,
    apellidos VARCHAR(25) NOT NULL,
    direccion VARCHAR(50) NOT NULL
);

CREATE TABLE Bibliotecario (
    idBibliotecario INT PRIMARY KEY AUTO_INCREMENT,
    nombres VARCHAR(25) NOT NULL,
    apellidos VARCHAR(25) NOT NULL,
    usuario VARCHAR(30) UNIQUE NOT NULL,
    contrasena VARCHAR(30) NOT NULL
);

CREATE TABLE Libro (
    isbn VARCHAR(17) PRIMARY KEY, 
    titulo VARCHAR(40) NOT NULL,
    autor VARCHAR(35) NOT NULL,
    editorial VARCHAR(30),
    anio_publicacion DATE,
    genero VARCHAR(30),
    disponibilidad BOOLEAN DEFAULT TRUE,
    estado VARCHAR(25),
    categoria VARCHAR(30)
);

CREATE TABLE Prestamo (
    idPrestamo INT PRIMARY KEY AUTO_INCREMENT,
    fecha_Prestamo DATE NOT NULL,
    fecha_Devolucion DATE NOT NULL,
    estado VARCHAR(25) NOT NULL,
    idBibliotecario INT,
    id_usuario INT,
    FOREIGN KEY (idBibliotecario) REFERENCES Bibliotecario(idBibliotecario),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
);

CREATE TABLE Prestamo_Libro (
    idPrestamo_Libro INT PRIMARY KEY AUTO_INCREMENT,
    idPrestamo INT,
    isbn VARCHAR(17),
    cantidad INT NOT NULL,
    FOREIGN KEY (idPrestamo) REFERENCES Prestamo(idPrestamo),
    FOREIGN KEY (isbn) REFERENCES Libro(isbn)
);

CREATE TABLE Multa (
    idMulta INT PRIMARY KEY AUTO_INCREMENT,
    fechaEmision DATE NOT NULL,
    monto DOUBLE NOT NULL,
    estado VARCHAR(30) NOT NULL,
    id_usuario INT,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
);

CREATE TABLE Notificacion (
    idNotificacion INT PRIMARY KEY AUTO_INCREMENT,
    fechaEnviado DATE NOT NULL,
    mensaje TEXT NOT NULL,
    idMulta INT,
    FOREIGN KEY (idMulta) REFERENCES Multa(idMulta)
);

INSERT INTO Usuario (nombres, apellidos, direccion) VALUES
('Juan', 'Perez', 'Av. Siempre Viva 123'),
('Maria', 'Gomez', 'Calle Falsa 456'),
('Carlos', 'Lopez', 'Av. Principal 789');

INSERT INTO Bibliotecario (nombres, apellidos, usuario, contrasena) VALUES
('Ana', 'Ramirez', 'ana_admin', 'admin123'),
('Luis', 'Gonzalez', 'luis_biblio', 'biblio456');

INSERT INTO Libro (isbn, titulo, autor, editorial, anio_publicacion, genero, disponibilidad, estado, categoria) VALUES
('978-1234567890', 'Cien Años de Soledad', 'Gabriel García Márquez', 'Editorial Sudamericana', '1967-01-01', 'Novela', 1, 'Nuevo', 'Literatura'),
('978-0987654321', 'El Principito', 'Antoine de Saint-Exupéry', 'Reynal & Hitchcock', '1943-01-01', 'Fábula', 1, 'Usado', 'Infantil');

INSERT INTO Prestamo (fecha_Prestamo, fecha_Devolucion, estado, idBibliotecario, id_usuario) VALUES
('2024-01-15', '2024-02-15', 'activo', 1, 1),
('2024-01-20', '2024-02-20', 'activo', 2, 2);

INSERT INTO Prestamo_Libro (idPrestamo, isbn, cantidad) VALUES
(1, '978-1234567890', 1),
(2, '978-0987654321', 1);

INSERT INTO Multa (fechaEmision, monto, estado, id_usuario) VALUES
('2024-02-16', 5.00, 'pendiente', 1),
('2024-02-20', 3.50, 'pagado', 2);

--Libros Prestados Actualmente
--π (Libro.isbn, Libro.titulo, Libro.autor, Prestamo.fecha_Prestamo, Prestamo.fecha_Devolucion)
--(σ (Prestamo.estado = 'activo') (Prestamo ⨝ Prestamo_Libro ⨝ Libro))
SELECT Libro.isbn, Libro.titulo, Libro.autor, Prestamo.fecha_Prestamo, Prestamo.fecha_Devolucion
FROM Prestamo
JOIN Prestamo_Libro ON Prestamo.idPrestamo = Prestamo_Libro.idPrestamo
JOIN Libro ON Prestamo_Libro.isbn = Libro.isbn
WHERE Prestamo.estado = 'activo';

CREATE VIEW LibrosPrestadosActuales AS
SELECT Libro.isbn, Libro.titulo, Libro.autor, Prestamo.fecha_Prestamo, Prestamo.fecha_Devolucion
FROM Prestamo
JOIN Prestamo_Libro ON Prestamo.idPrestamo = Prestamo_Libro.idPrestamo
JOIN Libro ON Prestamo_Libro.isbn = Libro.isbn
WHERE Prestamo.estado = 'activo';

--Usuarios con Multas Pendientes
--π (Usuario.id_usuario, Usuario.nombres, Usuario.apellidos, Multa.monto)
--(σ (Multa.estado = 'pendiente') (Usuario ⨝ Multa))
SELECT Usuario.id_usuario, Usuario.nombres, Usuario.apellidos, Multa.monto
FROM Usuario
JOIN Multa ON Usuario.id_usuario = Multa.id_usuario
WHERE Multa.estado = 'pendiente';

CREATE VIEW UsuariosConMultasPendientes AS
SELECT Usuario.id_usuario, Usuario.nombres, Usuario.apellidos, Multa.monto
FROM Usuario
JOIN Multa ON Usuario.id_usuario = Multa.id_usuario
WHERE Multa.estado = 'pendiente';

--Libros Más Solicitados
--γ (Libro.isbn, Libro.titulo, COUNT(Prestamo_Libro.idPrestamo) AS total_prestamos)
--(π (Libro.isbn, Libro.titulo, Prestamo_Libro.idPrestamo) (Libro ⨝ Prestamo_Libro))
SELECT Libro.isbn, Libro.titulo, COUNT(Prestamo_Libro.idPrestamo) AS total_prestamos
FROM Libro
JOIN Prestamo_Libro ON Libro.isbn = Prestamo_Libro.isbn
GROUP BY Libro.isbn, Libro.titulo
ORDER BY total_prestamos DESC;

CREATE VIEW LibrosMasSolicitados AS
SELECT Libro.isbn, Libro.titulo, COUNT(Prestamo_Libro.idPrestamo) AS total_prestamos
FROM Libro
JOIN Prestamo_Libro ON Libro.isbn = Prestamo_Libro.isbn
GROUP BY Libro.isbn, Libro.titulo
ORDER BY total_prestamos DESC;

--Préstamos Vencidos
--π (Prestamo.idPrestamo, Usuario.nombres, Usuario.apellidos, Prestamo.fecha_Prestamo, Prestamo.fecha_Devolucion)
--(σ (Prestamo.fecha_Devolucion < CURDATE()) (Prestamo ⨝ Usuario))
SELECT Prestamo.idPrestamo, Usuario.nombres, Usuario.apellidos, Prestamo.fecha_Prestamo, Prestamo.fecha_Devolucion
FROM Prestamo
JOIN Usuario ON Prestamo.id_usuario = Usuario.id_usuario
WHERE Prestamo.fecha_Devolucion < CURDATE();

CREATE VIEW PrestamosVencidos AS
SELECT Prestamo.idPrestamo, Usuario.nombres, Usuario.apellidos, Prestamo.fecha_Prestamo, Prestamo.fecha_Devolucion
FROM Prestamo
JOIN Usuario ON Prestamo.id_usuario = Usuario.id_usuario
WHERE Prestamo.fecha_Devolucion < CURDATE();
