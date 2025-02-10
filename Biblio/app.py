from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Configuración de la base de datos
db_config = {
    "host": "localhost",
    "user": "David",
    "password": "123456",
    "database": "Biblioteca"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Usuario")
    usuarios = cursor.fetchall()
    conn.close()
    return render_template("listar_usuarios.html", usuarios=usuarios)

@app.route("/usuarios/crear", methods=["GET", "POST"])
def crear_usuario():
    if request.method == "POST":
        nombres = request.form["nombres"]
        apellidos = request.form["apellidos"]
        direccion = request.form["direccion"]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Usuario (nombres, apellidos, direccion) VALUES (%s, %s, %s)",
            (nombres, apellidos, direccion),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("listar_usuarios"))
    return render_template("crear_usuario.html")

@app.route("/usuarios/editar/<int:id>", methods=["GET", "POST"])
def editar_usuario(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        nombres = request.form["nombres"]
        apellidos = request.form["apellidos"]
        direccion = request.form["direccion"]
        cursor.execute(
            "UPDATE Usuario SET nombres = %s, apellidos = %s, direccion = %s WHERE id_usuario = %s",
            (nombres, apellidos, direccion, id),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("listar_usuarios"))
    cursor.execute("SELECT * FROM Usuario WHERE id_usuario = %s", (id,))
    usuario = cursor.fetchone()
    conn.close()
    return render_template("editar_usuario.html", usuario=usuario)

@app.route("/usuarios/eliminar/<int:id>", methods=["POST"])
def eliminar_usuario(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Usuario WHERE id_usuario = %s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("listar_usuarios"))

@app.route("/libros")
def listar_libros():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Libro")
    libros = cursor.fetchall()
    conn.close()
    return render_template("listar_libros.html", libros=libros)

@app.route("/libros/crear", methods=["GET", "POST"])
def crear_libro():
    if request.method == "POST":
        isbn = request.form["isbn"]
        titulo = request.form["titulo"]
        autor = request.form["autor"]
        editorial = request.form["editorial"]
        anio_publicacion = request.form["anio_publicacion"]
        genero = request.form["genero"]
        estado = request.form["estado"]
        categoria = request.form["categoria"]
        cantidad_disponible = request.form["cantidad_disponible"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Libro (isbn, titulo, autor, editorial, anio_publicacion, genero, estado, categoria, cantidad_disponible) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (isbn, titulo, autor, editorial, anio_publicacion, genero, estado, categoria, cantidad_disponible),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("listar_libros"))
    return render_template("crear_libro.html")

@app.route("/libros/editar/<string:isbn>", methods=["GET", "POST"])
def editar_libro(isbn):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        titulo = request.form["titulo"]
        autor = request.form["autor"]
        editorial = request.form["editorial"]
        anio_publicacion = request.form["anio_publicacion"]
        genero = request.form["genero"]
        estado = request.form["estado"]
        categoria = request.form["categoria"]
        cantidad_disponible = request.form["cantidad_disponible"]

        cursor.execute(
            "UPDATE Libro SET titulo = %s, autor = %s, editorial = %s, anio_publicacion = %s, genero = %s, estado = %s, categoria = %s, cantidad_disponible = %s WHERE isbn = %s",
            (titulo, autor, editorial, anio_publicacion, genero, estado, categoria, cantidad_disponible, isbn),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("listar_libros"))
    cursor.execute("SELECT * FROM Libro WHERE isbn = %s", (isbn,))
    libro = cursor.fetchone()
    conn.close()
    return render_template("editar_libro.html", libro=libro)

@app.route("/libros/eliminar/<string:isbn>", methods=["POST"])
def eliminar_libro(isbn):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Libro WHERE isbn = %s", (isbn,))
    conn.commit()
    conn.close()
    return redirect(url_for("listar_libros"))
@app.route("/prestamos")
def listar_prestamos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT Prestamo.idPrestamo, Prestamo.fecha_Prestamo, Prestamo.fecha_Devolucion, Prestamo.estado,
               Usuario.nombres AS usuario_nombres, Usuario.apellidos AS usuario_apellidos,
               Bibliotecario.nombres AS bibliotecario_nombres, Bibliotecario.apellidos AS bibliotecario_apellidos,
               Libro.titulo, Prestamo_Libro.cantidad
        FROM Prestamo
        JOIN Usuario ON Prestamo.id_usuario = Usuario.id_usuario
        JOIN Bibliotecario ON Prestamo.idBibliotecario = Bibliotecario.idBibliotecario
        JOIN Prestamo_Libro ON Prestamo.idPrestamo = Prestamo_Libro.idPrestamo
        JOIN Libro ON Prestamo_Libro.isbn = Libro.isbn
    """)
    prestamos = cursor.fetchall()
    conn.close()
    return render_template("listar_prestamos.html", prestamos=prestamos)


@app.route("/prestamos/crear", methods=["GET", "POST"])
def crear_prestamo():
    if request.method == "POST":
        # Datos del préstamo
        fecha_prestamo = request.form["fecha_prestamo"]
        fecha_devolucion = request.form["fecha_devolucion"]
        estado = request.form["estado"]
        id_bibliotecario = request.form["id_bibliotecario"]
        id_usuario = request.form["id_usuario"]

        # Datos del libro y cantidad
        isbn = request.form["isbn"]
        cantidad = int(request.form["cantidad"])

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Verificar si hay suficiente cantidad disponible
            cursor.execute("SELECT cantidad_disponible FROM Libro WHERE isbn = %s", (isbn,))
            libro = cursor.fetchone()
            if libro and libro[0] >= cantidad:  # Cambiar a índice entero
                # Insertar el préstamo
                cursor.execute(
                    "INSERT INTO Prestamo (fecha_Prestamo, fecha_Devolucion, estado, idBibliotecario, id_usuario) VALUES (%s, %s, %s, %s, %s)",
                    (fecha_prestamo, fecha_devolucion, estado, id_bibliotecario, id_usuario),
                )
                id_prestamo = cursor.lastrowid  # Obtener el ID del préstamo recién creado

                # Insertar el libro asociado al préstamo
                cursor.execute(
                    "INSERT INTO Prestamo_Libro (idPrestamo, isbn, cantidad) VALUES (%s, %s, %s)",
                    (id_prestamo, isbn, cantidad),
                )

                # Actualizar la cantidad disponible del libro
                cursor.execute(
                    "UPDATE Libro SET cantidad_disponible = cantidad_disponible - %s WHERE isbn = %s",
                    (cantidad, isbn),
                )

                conn.commit()
                conn.close()
                return redirect(url_for("listar_prestamos"))
            else:
                conn.close()
                return "No hay suficiente cantidad disponible del libro."
        except mysql.connector.Error as err:
            conn.rollback()
            conn.close()
            return f"Error: {err}"

    # Si es GET, mostrar el formulario
    return render_template("crear_prestamo.html")


@app.route("/prestamos/editar/<int:id>", methods=["GET", "POST"])
def editar_prestamo(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        fecha_prestamo = request.form["fecha_prestamo"]
        fecha_devolucion = request.form["fecha_devolucion"]
        estado = request.form["estado"]
        id_bibliotecario = request.form["id_bibliotecario"]
        id_usuario = request.form["id_usuario"]
        cursor.execute(
            "UPDATE Prestamo SET fecha_Prestamo = %s, fecha_Devolucion = %s, estado = %s, idBibliotecario = %s, id_usuario = %s WHERE idPrestamo = %s",
            (fecha_prestamo, fecha_devolucion, estado, id_bibliotecario, id_usuario, id),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("listar_prestamos"))
    cursor.execute("SELECT * FROM Prestamo WHERE idPrestamo = %s", (id,))
    prestamo = cursor.fetchone()
    conn.close()
    return render_template("editar_prestamo.html", prestamo=prestamo)

@app.route("/prestamos/eliminar/<int:id>", methods=["POST"])
def eliminar_prestamo(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Eliminar las filas correspondientes en la tabla Prestamo_Libro
        cursor.execute("DELETE FROM Prestamo_Libro WHERE idPrestamo = %s", (id,))
        # Luego eliminar la fila en la tabla Prestamo
        cursor.execute("DELETE FROM Prestamo WHERE idPrestamo = %s", (id,))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        return f"Error: {err}"
    finally:
        conn.close()
    return redirect(url_for("listar_prestamos"))

@app.route("/prestamos/devolver/<int:id>", methods=["POST"])
def devolver_prestamo(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Obtener el libro y la cantidad del préstamo
        cursor.execute("SELECT isbn, cantidad FROM Prestamo_Libro WHERE idPrestamo = %s", (id,))
        prestamo_libro = cursor.fetchone()

        if prestamo_libro:
            isbn = prestamo_libro[0]  # Acceder por índice
            cantidad = prestamo_libro[1]  # Acceder por índice

            # Actualizar la cantidad disponible del libro
            cursor.execute(
                "UPDATE Libro SET cantidad_disponible = cantidad_disponible + %s WHERE isbn = %s",
                (cantidad, isbn),
            )

            # Cambiar el estado del préstamo a "devuelto"
            cursor.execute(
                "UPDATE Prestamo SET estado = 'devuelto' WHERE idPrestamo = %s",
                (id,),
            )

            conn.commit()
            conn.close()
            return redirect(url_for("listar_prestamos"))
        else:
            conn.close()
            return "Préstamo no encontrado."
    except mysql.connector.Error as err:
        conn.rollback()
        conn.close()
        return f"Error: {err}"
@app.route("/multas", methods=["GET"])
def listar_multas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Multa")
    multas = cursor.fetchall()
    conn.close()
    return render_template("listar_multas.html", multas=multas)

@app.route("/multas/crear", methods=["GET", "POST"])
def crear_multa():
    if request.method == "POST":
        fecha_emision = request.form["fecha_emision"]
        monto = request.form["monto"]
        estado = request.form["estado"]
        id_usuario = request.form["id_usuario"]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Multa (fechaEmision, monto, estado, id_usuario) VALUES (%s, %s, %s, %s)",
            (fecha_emision, monto, estado, id_usuario),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("listar_multas"))
    return render_template("crear_multa.html")

@app.route("/multas/editar/<int:id>", methods=["GET", "POST"])
def editar_multa(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        fecha_emision = request.form["fecha_emision"]
        monto = request.form["monto"]
        estado = request.form["estado"]
        id_usuario = request.form["id_usuario"]
        cursor.execute(
            "UPDATE Multa SET fechaEmision = %s, monto = %s, estado = %s, id_usuario = %s WHERE idMulta = %s",
            (fecha_emision, monto, estado, id_usuario, id),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("listar_multas"))
    cursor.execute("SELECT * FROM Multa WHERE idMulta = %s", (id,))
    multa = cursor.fetchone()
    conn.close()
    return render_template("editar_multa.html", multa=multa)

@app.route("/multas/eliminar/<int:id>", methods=["POST"])
def eliminar_multa(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Multa WHERE idMulta = %s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("listar_multas"))

@app.route("/prestamo_libro", methods=["GET"])
def listar_prestamo_libro():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Prestamo_Libro")
    prestamo_libros = cursor.fetchall()
    conn.close()
    return render_template("listar_prestamo_libro.html", prestamo_libros=prestamo_libros)

@app.route("/prestamo_libro/crear", methods=["GET", "POST"])
def crear_prestamo_libro():
    if request.method == "POST":
        id_prestamo = request.form["id_prestamo"]
        isbn = request.form["isbn"]
        cantidad = request.form["cantidad"]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Prestamo_Libro (idPrestamo, isbn, cantidad) VALUES (%s, %s, %s)",
            (id_prestamo, isbn, cantidad),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("listar_prestamo_libro"))
    return render_template("crear_prestamo_libro.html")

@app.route("/prestamo_libro/eliminar/<int:id>", methods=["POST"])
def eliminar_prestamo_libro(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Prestamo_Libro WHERE idPrestamo_Libro = %s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("listar_prestamo_libro"))

@app.route("/consultas")
def consultas():
    return render_template("consultas.html")

@app.route("/consultas/libros_prestados_actuales")
def libros_prestados_actuales():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM View_LibrosPrestadosActuales")
    libros = cursor.fetchall()
    conn.close()
    return render_template("libros_prestados_actuales.html", libros=libros)

@app.route("/consultas/usuarios_multas_pendientes")
def usuarios_multas_pendientes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM View_UsuariosConMultasPendientes")
    usuarios = cursor.fetchall()
    conn.close()
    return render_template("usuarios_multas_pendientes.html", usuarios=usuarios)

@app.route("/consultas/libros_mas_solicitados")
def libros_mas_solicitados():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM View_LibrosMasSolicitados")
    libros = cursor.fetchall()
    conn.close()
    return render_template("libros_mas_solicitados.html", libros=libros)

@app.route("/consultas/prestamos_vencidos")
def prestamos_vencidos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM View_PrestamosVencido")
    prestamos = cursor.fetchall()
    conn.close()
    return render_template("prestamos_vencidos.html", prestamos=prestamos)

@app.route("/consultas/bibliotecario_con_Prestamos")
def bibliotecario_con_Prestamos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM view_bibliotecario_con_prestamos")
    bibliotecario = cursor.fetchall()
    conn.close()
    return render_template("bibliotecario_con_Prestamos.html", bibliotecario=bibliotecario)

@app.route("/consultas/librosEditorial_con_Autor")
def librosEditorial_con_Autor():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM View_LibrosEditorial_Autor")
    editorial = cursor.fetchall()
    conn.close()
    return render_template("librosEditorial_Autor.html", editorial=editorial)

@app.route("/consultas/usuariosConLibrosPrestados")
def usuariosConLibrosPrestados():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM View_UsuariosConLibrosPrestados")
    prestado = cursor.fetchall()
    conn.close()
    return render_template("usuariosConLibrosPrestados.html", prestado=prestado)

@app.route("/consultas/detallesMultasPendientes")
def detallesMultasPendientes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM View_DetallesMultasPendientes")
    pendiente = cursor.fetchall()
    conn.close()
    return render_template("detallesMultasPendientes.html", pendiente=pendiente)



if __name__ == "__main__":
    app.run(debug=True)
