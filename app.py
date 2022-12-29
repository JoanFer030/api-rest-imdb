from flask import Flask, jsonify, render_template, request, redirect, url_for
from decouple import config
import data_func
import tools

app = Flask(__name__, template_folder='templates', static_folder="static")
email = tools.Email()
api_keys = tools.ApiKey()
app.config['JSON_SORT_KEYS'] = False

# Inicio
@app.route("/", methods=["GET", "POST"])
def index():
    rutas_gen = {
        "titulos/":data_func.titulos,
        "titulos/peliculas/":data_func.peliculas,
        "titulos/series/":data_func.series,
        "personas/":data_func.personas,
        "generos/":data_func.generos,
    }
    rutas_ind = {
        "titulos/":data_func.titulo,
        "personas/":data_func.persona,
        "generos/":data_func.genero,
    }
    if request.method == "POST":
        api_key = request.form.get("api-key")
        valid, auth = api_keys.is_valid(api_key)
        if api_key is None:
            data = {"estado":400, "mensaje": "Por favor introduce un clave API"}
        elif valid:
            ruta = request.form.get("ruta-api")
            if ruta in rutas_gen:
                data, status = rutas_gen[ruta](request.url_root)
                clave = api_key
            else:
                if ruta.count("/") == 2:
                    ruta_l = ruta.split("/")
                    ruta_ind = f"{ruta_l[0]}/"
                    if ruta_ind in rutas_ind:
                        data, status = rutas_ind[ruta_ind](ruta_l[1], request.url_root)
                        clave = api_key
                    else:
                        data = {"ruta":"no válida"}
                        ruta = "titulos/T00001"
                        clave = api_key
                else:
                    data = {"ruta":"no válida"}
                    ruta = "titulos/T00001"
                    clave = api_key
        else:
            data = {"estado":403, "mensaje": "La clave API no es válida"}
            ruta = "titulos/T00001"
            clave = "SbKUVxbHLyv1aRveBboelaoq8XkHfG3IE9l8LYHUtcgXWYinCHQfF6iy7AfFJXKZ"
    else:
        ruta = "titulos/T00001/"
        clave = "SbKUVxbHLyv1aRveBboelaoq8XkHfG3IE9l8LYHUtcgXWYinCHQfF6iy7AfFJXKZ"
        data, status = rutas_ind["titulos/"]("T00001", request.url_root)
    return render_template("index.html", data=tools.formato_dicc(data), ruta=ruta, clave=clave)

# Obtener api_key
@app.route("/api_key/", methods=["GET", "POST"])
def api_key():
    if request.method == "POST":
        to_mail = request.form.get("email")
        if len(to_mail) != 0 and "." in to_mail and "@" in to_mail:
            if email.is_valid(to_mail):
                key = api_keys.create_apikey(to_mail)
                email.send_email(to_mail, key, request.url_root)
                return redirect(url_for("api_key")+"?ok")
            else:
                return redirect(url_for("api_key")+"?fail-send")
        else:
            return redirect(url_for("api_key")+"?fail-mail")
    return render_template("api_key.html")

# Ejemplos
@app.route("/examples/", methods=["GET"])
def examples():
    return render_template("examples.html")

# Documentación
@app.route("/documentation/", methods=["GET"])
def documentation():
    return render_template("documentation.html")

# Administrador
@app.route("/admin/", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        api_key = request.form.get("api-key")
        valid, auth = api_keys.is_valid(api_key)
        if valid and auth == "a":
            to_mail = request.form.get("email")
            if len(to_mail) != 0 and "." in to_mail and "@" in to_mail:
                if email.is_valid(to_mail):
                    key = api_keys.create_apikey(to_mail, "a")
                    email.send_email(to_mail, key, request.url_root)
                    return redirect(url_for("admin")+"?ok")
                else:
                    return redirect(url_for("admin")+"?fail-send")
            else:
                return redirect(url_for("admin")+"?fail-mail")
        else:
            return redirect(url_for("admin")+"?fail-key")
    return render_template("admin.html")

# api - rutas
@app.route("/api/")
def rutas():
    url_root = request.url_root
    rutas_api = {
        "obtener clave" : f"{url_root}api_key/",
        "eliminar clave" : f"{url_root}eliminar_clave/?api_key=<clave>",
        "titulos":f"{url_root}titulos/?api_key=<clave>",
        "peliculas":f"{url_root}titulos/peliculas/?api_key=<clave>",
        "series":f"{url_root}titulos/series/?api_key=<clave>",
        "titulo":f"{url_root}titulos/<cod>/?api_key=<clave>",
        "personas":f"{url_root}personas/?api_key=<clave>",
        "persona":f"{url_root}personas/<cod>/?api_key=<clave>",
        "generos":f"{url_root}generos/?api_key=<clave>",
        "genero":f"{url_root}generos/<cod>/?api_key=<clave>",
    }
    return jsonify(rutas_api), 200

# api - eliminar clave
@app.route("/api/eliminar_clave/", methods=["GET"])
def eliminar_clave():
    api_key = request.args.get("api_key")
    valid, auth = api_keys.is_valid(api_key)
    if api_key is None:
        return jsonify({"estado":400, "mensaje": "Por favor introduce un clave API"}), 400
    elif valid:
        data, status = api_keys.delete(api_key)
        return jsonify(data), status
    else:
        return jsonify({"estado":403, "mensaje": "La clave API no es válida"}), 403

# api - titulos
@app.route("/api/titulos/", methods=["GET", "POST"])
def titulos():
    api_key = request.args.get("api_key")
    valid, auth = api_keys.is_valid(api_key)
    if api_key is None:
        return jsonify({"estado":400, "mensaje": "Por favor introduce un clave API"}), 400
    elif valid:
        if request.method == "POST" and auth == "a":
            data, status = data_func.crear_titulo(request.get_json(force=True), request.url_root)
            return jsonify(data), status
        elif request.method == "POST" and auth != "a":
            return jsonify({"estado":401, "mensaje": "La clave API no es válida para este procedimiento"}), 401
        elif request.method == "GET":
            data, status = data_func.titulos(request.url_root)
            return jsonify(data), status
    else:
        return jsonify({"estado":403, "mensaje": "La clave API no es válida"}), 403

# api - peliculas
@app.route("/api/titulos/peliculas/", methods=["GET"])
def peliculas():
    api_key = request.args.get("api_key")
    valid, auth = api_keys.is_valid(api_key)
    if api_key is None:
        return jsonify({"estado":400, "mensaje": "Por favor introduce un clave API"}), 400
    elif valid:
        data, status = data_func.peliculas(request.url_root)
        return jsonify(data), status
    else:
        return jsonify({"estado":403, "mensaje": "La clave API no es válida"}), 403

# api - series
@app.route("/api/titulos/series/", methods=["GET"])
def series():
    api_key = request.args.get("api_key")
    valid, auth = api_keys.is_valid(api_key)
    if api_key is None:
        return jsonify({"estado":400, "mensaje": "Por favor introduce un clave API"}), 400
    elif valid:
        data, status = data_func.series(request.url_root)
        return jsonify(data), status
    else:
        return jsonify({"estado":403, "mensaje": "La clave API no es válida"}), 403

# api - un titulo
@app.route("/api/titulos/<string:cod>/", methods=["GET", "DELETE", "PATCH"])
def titulo(cod):
    api_key = request.args.get("api_key")
    valid, auth = api_keys.is_valid(api_key)
    if api_key is None:
        return jsonify({"estado":400, "mensaje": "Por favor introduce un clave API"}), 400
    elif valid:
        if request.method == "DELETE" and auth == "a":
            data, status = data_func.eliminar_titulo(cod)
            return jsonify(data), status
        elif request.method == "PATCH" and auth == "a":
            data, status = data_func.actualizar_titulo(cod, request.get_json(force=True), request.url_root)
            return jsonify(data), status
        elif request.method in ["PATCH", "DELETE"] and auth != "a":
            return jsonify({"estado":401, "mensaje": "La clave API no es válida para este procedimiento"}), 401
        elif request.method == "GET":
            data, status = data_func.titulo(cod, request.url_root)
            return jsonify(data), status
    else:
        return jsonify({"estado":403, "mensaje": "La clave API no es válida"}), 403

# api - personas
@app.route("/api/personas/", methods=["GET", "POST"])
def personas():
    api_key = request.args.get("api_key")
    valid, auth = api_keys.is_valid(api_key)
    if api_key is None:
        return jsonify({"estado":400, "mensaje": "Por favor introduce un clave API"}), 400
    elif valid:
        if request.method == "POST" and auth == "a":
            data, status = data_func.crear_persona(request.get_json(force=True), request.url_root)
            return jsonify(data), status
        elif request.method == "POST" and auth != "a":
            return jsonify({"estado":401, "mensaje": "La clave API no es válida para este procedimiento"}), 401
        elif request.method == "GET":
            data, status = data_func.personas(request.url_root)
            return jsonify(data), status
    else:
        return jsonify({"estado":403, "mensaje": "La clave API no es válida"}), 403

# api - persona
@app.route("/api/personas/<string:cod>/", methods=["GET", "DELETE", "PATCH"])
def persona(cod):
    api_key = request.args.get("api_key")
    valid, auth = api_keys.is_valid(api_key)
    if api_key is None:
        return jsonify({"estado":400, "mensaje": "Por favor introduce un clave API"}), 400
    elif valid:
        if request.method == "DELETE" and auth == "a":
            data, status = data_func.eliminar_persona(cod)
            return jsonify(data), status
        elif request.method == "PATCH" and auth == "a":
            data, status = data_func.actualizar_persona(cod, request.get_json(force=True), request.url_root)
            return jsonify(data), status
        elif request.method in ["PATCH", "DELETE"] and auth != "a":
            return jsonify({"estado":401, "mensaje": "La clave API no es válida para este procedimiento"}), 401
        elif request.method == "GET":
            data, status = data_func.persona(cod, request.url_root)
            return jsonify(data), status
    else:
        return jsonify({"estado":403, "mensaje": "La clave API no es válida"}), 403

# api - generos
@app.route("/api/generos/", methods=["GET", "POST"])
def generos():
    api_key = request.args.get("api_key")
    valid, auth = api_keys.is_valid(api_key)
    if api_key is None:
        return jsonify({"estado":400, "mensaje": "Por favor introduce un clave API"}), 400
    elif valid:
        if request.method == "POST" and auth == "a":
            data, status = data_func.crear_genero(request.get_json(force=True), request.url_root)
            return jsonify(data), status
        elif request.method == "POST" and auth != "a":
            return jsonify({"estado":401, "mensaje": "La clave API no es válida para este procedimiento"}), 401
        elif request.method == "GET":
            data, status = data_func.generos(request.url_root)
            return jsonify(data), status
    else:
        return jsonify({"estado":403, "mensaje": "La clave API no es válida"}), 403

# api - genero
@app.route("/api/generos/<string:cod>/", methods=["GET", "DELETE", "PATCH"])
def genero(cod):
    api_key = request.args.get("api_key")
    valid, auth = api_keys.is_valid(api_key)
    if api_key is None:
        return jsonify({"estado":400, "mensaje": "Por favor introduce un clave API"}), 400
    elif valid:
        if request.method == "DELETE" and auth == "a":
            data, status = data_func.eliminar_genero(cod)
            return jsonify(data), status
        elif request.method == "PATCH" and auth == "a":
            data, status = data_func.actualizar_genero(cod, request.get_json(force=True), request.url_root)
            return jsonify(data), status
        elif request.method in ["PATCH", "DELETE"] and auth != "a":
            return jsonify({"estado":401, "mensaje": "La clave API no es válida para este procedimiento"}), 401
        elif request.method == "GET":
            data, status = data_func.genero(cod, request.url_root)
            return jsonify(data), status
    else:
        return jsonify({"estado":403, "mensaje": "La clave API no es válida"}), 403


if __name__ == "__main__":
    app.run(debug=config("DEBUG", cast=bool))