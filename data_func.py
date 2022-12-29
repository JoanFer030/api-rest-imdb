import database
from datetime import datetime

db = database.DB()

def date_to_str(date):
    return f"{date.day:02}-{date.month:02}-{date.year:04}"

def time_to_str(time):
    if time.hour > 0:
        return f"{time.hour}h {time.minute}min"
    return f"{time.minute} min"

def comprobar_hora(hora):
    try:
        datetime.strptime(hora, "%H:%M")
        return True
    except:
        return False

def comprobar_fecha(fecha):
    try:
        datetime.strptime(fecha, "%d-%m-%Y")
        return True
    except:
        return False

def titulos(url_root):
    d_pelis, status = peliculas(url_root)
    d_series, status = series(url_root)
    resul = []
    for i in d_pelis:
        resul.append(i)
        resul[-1]["tipo"] = "pelicula"
    for i in d_series:
        resul.append(i)
        resul[-1]["tipo"] = "serie"
    return resul, 200

def peliculas(url_root):
    cols_pelis = ("codigo", "titulo", "anyo", "valoracion", "director", "nominaciones", "premios", "duracion", "ranking_peli", "cod_pers", "cod_gen")
    query ="""
        SELECT  t.{}, t.{}, t.{}, t.{}, t.{}, t.{}, t.{}, p.{}, p.{}, a.{}, c.{}
        FROM titulos t JOIN peliculas p 
            ON t.codigo=p.codigo LEFT JOIN actua a
                ON p.codigo=a.cod_titu LEFT JOIN clasificado c
                    ON p.codigo=c.cod_titu
        ORDER BY t.codigo
    """.format(*cols_pelis)
    pelis = db.select(query)
    resul = []
    act = {}
    for peli in pelis:
        if peli[0]in act:
            dict = resul[-1]
            if peli[9] not in act[peli[0]][0]:
                url = url_root + f"api/personas/{peli[9]}/"
                dict["actores"].append(url)
                act[peli[0]][0].add(peli[9])
            if peli[10] not in act[peli[0]][1]:
                url = url_root + f"api/generos/{peli[10]}/"
                dict["generos"].append(url)
                act[peli[0]][1].add(peli[10])
        else:
            dict = {}
            for i, etiq in enumerate(cols_pelis):
                value = peli[i]
                if i == 7:
                    dict[etiq] = time_to_str(value)
                elif i == 9:
                    dict["actores"] = []
                    if value is not None:
                        url = url_root + f"api/personas/{value}/"
                        dict["actores"].append(url)
                elif i == 10:
                    dict["generos"] = []
                    if value is not None:
                        url = url_root + f"api/generos/{value}/"
                        dict["generos"].append(url)
                elif i == 4:
                    if value is not None:
                        dict["director"] = url_root + f"api/personas/{value}/"
                    else:
                        dict["director"] = ""
                else:
                    dict[etiq] = value
            resul.append(dict)
            act[peli[0]] = (set(), set())
            act[peli[0]][0].add(peli[9])
            act[peli[0]][1].add(peli[10])
    return resul, 200

def series(url_root):
    cols_series = ("codigo", "titulo", "anyo", "valoracion", "director", "nominaciones", "premios", "duracion_cap", "ranking_series", "episodios", "cod_pers", "cod_gen")
    query ="""
        SELECT t.{}, t.{}, t.{}, t.{}, t.{}, t.{}, t.{}, s.{}, s.{}, s.{}, a.{}, c.{}
        FROM titulos t JOIN series s 
            ON t.codigo=s.codigo LEFT JOIN actua a
                ON s.codigo=a.cod_titu LEFT JOIN clasificado c
                    ON s.codigo=c.cod_titu
        ORDER BY t.codigo
    """.format(*cols_series)
    series = db.select(query)
    resul = []
    act = {}
    for serie in series:
        if serie[0]in act:
            dict = resul[-1]
            if serie[10] not in act[serie[0]][0]:
                url = url_root + f"api/personas/{serie[10]}/"
                dict["actores"].append(url)
                act[serie[0]][0].add(serie[10])
            if serie[11] not in act[serie[0]][1]:
                url = url_root + f"api/generos/{serie[11]}/"
                dict["generos"].append(url)
                act[serie[0]][1].add(serie[11])
        else:
            dict = {}
            for i, etiq in enumerate(cols_series):
                value = serie[i]
                if i == 7:
                    dict[etiq] = time_to_str(value)
                elif i == 10:
                    dict["actores"] = []
                    if value is not None:
                        url = url_root + f"api/personas/{value}/"
                        dict["actores"].append(url)
                elif i == 11:
                    dict["generos"] = []
                    if value is not None:
                        url = url_root + f"api/generos/{value}/"
                        dict["generos"].append(url)
                elif i == 4:
                    if value is not None:
                        dict["director"] = url_root + f"api/personas/{value}/"
                    else:
                        dict["director"] = ""
                else:
                    dict[etiq] = value
            resul.append(dict)
            act[serie[0]] = (set(), set())
            act[serie[0]][0].add(serie[10])
            act[serie[0]][1].add(serie[11])
    return resul, 200

def titulo(cod, url_root):
    es_peli = len(db.select(f"SELECT * FROM peliculas WHERE codigo='{cod}'")) > 0
    if es_peli:
        cols = ("codigo", "titulo", "anyo", "valoracion", "director", "nominaciones", "premios", "duracion", "ranking_peli", "cod_pers", "cod_gen")
        query ="""
            SELECT t.{}, t.{}, t.{}, t.{}, t.{}, t.{}, t.{}, p.{}, p.{}, a.{}, c.{}
            FROM titulos t JOIN peliculas p 
            ON t.codigo=p.codigo JOIN actua a
                ON p.codigo=a.cod_titu JOIN clasificado c
                    ON p.codigo=c.cod_titu
            WHERE t.codigo='{}'
        """.format(*cols, cod)
        titulo = db.select(query)
        info = {"tipo":"pelicula", "acts":9, "gens":10}
    else:
        cols = ("codigo", "titulo", "anyo", "valoracion", "director", "nominaciones", "premios", "duracion_cap", "ranking_series", "episodios", "cod_pers", "cod_gen")
        query = """
            SELECT t.{}, t.{}, t.{}, t.{}, t.{}, t.{}, t.{}, s.{}, s.{}, s.{}, a.{}, c.{}
            FROM titulos t JOIN series s 
            ON t.codigo=s.codigo JOIN actua a
                ON s.codigo=a.cod_titu JOIN clasificado c
                    ON s.codigo=c.cod_titu
            WHERE s.codigo='{}'
        """.format(*cols, cod)
        titulo = db.select(query)
        info = {"tipo":"serie", "acts":10, "gens":11}
    if len(titulo) == 0:
            return {"estado":404, "mensaje": "El título introducido no existe"}, 404
    acts = set()
    gens = set()
    dict = {}
    titulo_0 = titulo[0]
    for i, etiq in enumerate(cols):
        value = titulo_0[i]
        if i == 7:
            dict[etiq] = time_to_str(value)
        elif i == info["acts"]:
            url = url_root + f"api/personas/{value}/"
            dict["actores"] = [url]
        elif i == info["gens"]:
            url = url_root + f"api/generos/{value}/"
            dict["generos"] = [url]
        elif i == 4:
            if value is not None:
                        dict["director"] = url_root + f"api/personas/{value}/"
            else:
                dict["director"] = ""
        else:
            dict[etiq] = value
    acts.add(titulo_0[info["acts"]])
    gens.add(titulo_0[info["gens"]])
    for i in titulo[1:]:
        act, gen = i[info["acts"]], i[info["gens"]]
        if act not in acts:
            url = url_root + f"api/personas/{act}/"
            dict["actores"].append(url)
            acts.add(act)
        if gen not in gens:
            url = url_root + f"api/generos/{gen}/"
            dict["generos"].append(url)
            gens.add(gen)
    dict["tipo"] = info["tipo"]
    return dict, 200

def crear_titulo(json, url_root):
    query = f"""
        SELECT codigo
        FROM titulos
        ORDER BY codigo DESC
    """
    cods = db.select(query)
    if len(cods) < 1:
        cod = 1
    else:
        cod = cods[0][0]
        cod = int(cod[1:])+1
    n_cod = f"T{cod:05}"
    personas = [i[0] for i in db.select("SELECT codigo FROM personas")]
    generos = [i[0] for i in db.select("SELECT codigo FROM generos")]
    cols = ("titulo", "anyo", "valoracion", "nominaciones", "premios", "director", "tipo", "duracion", "ranking", "episodios", "actores", "generos")
    valores = []
    for i in cols:
        valor = json.get(i, None)
        if type(valor) == str:
            if "'" in valor:
                valor = valor.replace("'", " ")
        valores.append(valor)
    if None in valores[:9]:
        return {"estado":400, "mensaje":f"Son necesarios los siguientes datos: {', '.join(cols)}"}, 400
    elif valores[6] == "s" and valores[9] is None:
        return {"estado":400, "mensaje":f"Son necesarios los siguientes datos: {', '.join(cols)}"}, 400
    elif type(valores[0]) != str:
        return {"estado":400, "mensaje":"El titulo ha de ser una cadena de texto (ej. 'Cadena Perpetua')"}, 400
    elif type(valores[1]) != int:
        return {"estado":400, "mensaje":"El año ha de ser un entero (ej. 2023)"}, 400
    elif type(valores[2]) != float:
        return {"estado":400, "mensaje":"La valoración ha de ser un numero decimal (ej. 7.9)"}, 400
    elif type(valores[3]) != int:
        return {"estado":400, "mensaje":"El nº de nominaciones ha de ser un entero (ej. 45)"}, 400
    elif type(valores[4]) != int:
        return {"estado":400, "mensaje":"El nº de premios ha de ser un entero (ej. 23)"}, 400
    elif valores[5] not in personas:
        return {"estado":400, "mensaje":"El codigo del director introducido no existe"}, 400
    elif valores[6] not in ["s", "p"]:
        return {"estado":400, "mensaje":"El campo tipo no tiene un valor válido (s-serie, p-película)"}, 400
    elif not comprobar_hora(valores[7]):
        return {"estado":400, "mensaje":"El formato de duración no es correcto ('hh:mm')"}, 400
    elif type(valores[8]) != int:
        return {"estado":400, "mensaje":"El nº de ranking ha de ser un entero (ej. 12)"}, 400
    elif valores[10] is not None:
        if all(act not in personas for act in valores[10]):
            return {"estado":400, "mensaje":"El codigo de algún actor no existe"}, 400
    elif valores[11] is not None:
        if all(gen not in generos for gen in valores[11]):
            return {"estado":400, "mensaje":"El codigo de algún género no existe"}, 400
    if valores[6] == "s":
        ranks = [i[0] for i in db.select("SELECT ranking_series FROM series")]
        if valores[8] in ranks:
            return {"estado":400, "mensaje":f"El top {valores[8]} ya está usado"}, 400
        if type(valores[9]) != int:
            return {"estado":400, "mensaje":"El nº de capítulos ha de ser un entero (ej. 21)"}, 400
        vals_titu = [n_cod]
        vals_serie = []
        for i in valores[:6]:
            vals_titu.append(i)
        for i in valores[7:10]:
            vals_serie.append(i)
        vals_serie.append(n_cod)
        db.insert("titulos", vals_titu)
        db.insert("series", vals_serie)
        for actor in valores[10]:
            db.insert("actua", (n_cod, actor))
        for genero in valores[11]:
            db.insert("clasificado", (n_cod, genero))
    else:
        ranks = [i[0] for i in db.select("SELECT ranking_peli FROM peliculas")]
        if valores[8] in ranks:
            return {"estado":400, "mensaje":f"El top {valores[8]} ya está usado"}, 400
        vals_titu = [n_cod]
        vals_peli = []
        for i in valores[:6]:
            vals_titu.append(i)
        for i in valores[7:9]:
            vals_peli.append(i)
        vals_peli.append(n_cod)
        db.insert("titulos", vals_titu)
        db.insert("peliculas", vals_peli)
        for actor in valores[10]:
            db.insert("actua", (n_cod, actor))
        for genero in valores[11]:
            db.insert("clasificado", (n_cod, genero))
    url = url_root + f"titulos/{n_cod}/"
    return {"estado":201, "mensaje":"Titulo creado de forma correcta", "url":url}, 201

def actualizar_titulo(cod, json, url_root):
    cols = ("titulo", "anyo", "valoracion", "nominaciones", "premios", "director", "duracion", "episodios")
    if len(json) != 1:
        return {"estado":400, "mensaje":"Solo se puede actualizar un campo"}, 400
    query = """
        SELECT codigo
        FROM titulos
        WHERE codigo='{}'
    """.format(cod)
    titulo = db.select(query)
    if len(titulo) == 0:
        return {"estado":404, "mensaje": "El título introducido no existe"}, 404
    if list(json.keys())[0] not in cols:
        return {"estado":400, "mensaje":f"Solo se puede actualizar uno de los siguientes campos: {', '.join(cols)}"}, 400
    col = list(json.keys())[0]
    val = json[col]
    if val is None:
        return {"estado":400, "mensaje":f"El campo {col} debe tener algun valor"}, 400
    elif col == cols[0] and type(val) != str:
        return {"estado":400, "mensaje":"El título ha de ser una cadena de texto (ej. 'Cadena Perpetua')"}, 400
    elif col == cols[1] and type(val) != int:
        return {"estado":400, "mensaje":"El año ha de ser un entero (ej. 2023)"}, 400
    elif col == cols[2] and type(val) != float:
        return {"estado":400, "mensaje":"La valoración ha de ser un numero decimal (ej. 7.9)"}, 400
    elif col == cols[3] and type(val) != int:
        return {"estado":400, "mensaje":"El nº de nominaciones ha de ser un entero (ej. 45)"}, 400
    elif col == cols[4] and type(val) != int:
        return {"estado":400, "mensaje":"El nº de premios ha de ser un entero (ej. 23)"}, 400
    elif col == cols[5]:
        personas = [i[0] for i in db.select("SELECT codigo FROM personas")]
        if val not in personas:
            return {"estado":400, "mensaje":"El codigo del director introducido no existe"}, 400
    elif col == cols[6] and not comprobar_hora(val):
        return {"estado":400, "mensaje":"El formato de duración no es correcto ('hh:mm')"}, 400
    else:
        if type(val) == str:
            val = val.replace("'", " ")
        if col in cols[:6]:
            db.update("titulos", {col:val}, cod)
        else:
            es_serie = len(db.select(f"SELECT * FROM series WHERE codigo='{cod}'")) > 0
            if es_serie:
                if col == cols[7] and type(val) != int:
                    return {"estado":400, "mensaje":"El nº de capítulos ha de ser un entero (ej. 21)"}, 400
                nombres = {"duracion":"duracion_cap", "episodios":"episodios"}
                tabla = "series"
            else:
                if col == cols[7]:
                    return {"estado":400, "mensaje":"El nº de capítulos no se puede actualizar en una pelicula"}, 400
                nombres = {"duracion":"duracion"}
                tabla = "peliculas"
            db.update(tabla, {nombres[col]:val}, cod)
        url = url_root + f"titulos/{cod}/"   
        return {"estado":202, "mensaje":"Titulo actualizado de forma correcta", "url":url}, 202

def eliminar_titulo(cod):
    query = """
        SELECT codigo
        FROM titulos
        WHERE codigo='{}'
    """.format(cod)
    titulo = db.select(query)
    if len(titulo) == 0:
        return {"estado":404, "mensaje": "El título introducida no existe"}, 404
    else:
        db.delete("personas", cod)
        return {"estado":202, "mensaje":"Título eliminado de forma correcta"}, 202

def personas(url_root):
    cols_pers = ("codigo", "nombre", "fecha_nac", "pais", "nominaciones", "premios", "cod_titu", "codigo")
    query ="""
        SELECT p.{}, p.{}, p.{}, p.{}, p.{}, p.{}, a.{} actua_en, t.{} dirige
        FROM personas p LEFT JOIN actua a
        ON p.codigo=a.cod_pers LEFT JOIN titulos t
            ON p.codigo=t.director
        ORDER BY p.codigo
    """.format(*cols_pers)
    pers = db.select(query)
    resul = []
    act = {}
    for per in pers:
        if per[0]in act:
            dict = resul[-1]
            if per[6] not in act[per[0]][0] and per[6] is not None:
                url = url_root + f"api/titulos/{per[6]}/"
                dict["actua"].append(url)
                act[per[0]][0].add(per[6])
            if per[7] not in act[per[0]][1] and per[7] is not None:
                url = url_root + f"api/titulos/{per[7]}/"
                dict["dirige"].append(url)
                act[per[0]][0].add(per[7])
        else:
            dict = {}
            for i, etiq in enumerate(cols_pers):
                value = per[i]
                if i == 2 and value is not None:
                    dict[etiq] = date_to_str(value)
                elif i == 6:
                    dict["actua"] = []
                    if value is not None:
                        url = url_root + f"api/titulos/{value}/"
                        dict["actua"].append(url)
                elif i == 7:
                    dict["dirige"] = []
                    if value is not None:
                        url = url_root + f"api/titulos/{per[7]}/"
                        dict["dirige"].append(url)
                else:
                    if value is not None:
                        dict[etiq] = value
            if "actua" not in dict:
                dict["actua"] = []
            if "dirige" not in dict:
                dict["dirige"] = []
            resul.append(dict)
            act[per[0]] = (set(), set())
            act[per[0]][0].add(per[6])
            act[per[0]][1].add(per[7])
    return resul, 200

def persona(cod, url_root):
    cols_pers = ("codigo", "nombre", "fecha_nac", "pais", "nominaciones", "premios", "cod_titu", "codigo")
    query ="""
        SELECT p.{}, p.{}, p.{}, p.{}, p.{}, p.{}, a.{} actua_en, t.{} dirige
        FROM personas p LEFT JOIN actua a
        ON p.codigo=a.cod_pers LEFT JOIN titulos t
            ON p.codigo=t.director
        WHERE p.codigo='{}'
    """.format(*cols_pers, cod)
    persona = db.select(query)
    if len(persona) == 0:
        return {"estado":404, "mensaje": "La persona introducida no existe"}, 404
    actua = set()
    dirige = set()
    dict = {}
    persona_0 = persona[0]
    for i, etiq in enumerate(cols_pers):
        value = persona_0[i]
        if i == 2 and value is not None:
            dict[etiq] = date_to_str(value)
        elif i == 6:
            dict["actua"] = []
            if value is not None:
                url = url_root + f"api/titulos/{value}/"
                dict["actua"].append(url)
                actua.add(value)
        elif i == 7:
            dict["dirige"] = []
            if value is not None:
                url = url_root + f"api/titulos/{value}/"
                dict["dirige"].append(url)
        else:
            if value is not None:
                dict[etiq] = value
    for per in persona[1:]:
        if per[6] not in actua and per[6] is not None:
                url = url_root + f"api/titulos/{per[6]}/"
                dict["actua"].append(url)
                actua.add(per[6])
        if per[7] not in dirige and per[7] is not None:
            url = url_root + f"api/titulos/{per[7]}/"
            dict["dirige"].append(url)
            dirige.add(per[7])
    return dict, 200

def crear_persona(json, url_root):
    query = f"""
        SELECT codigo
        FROM personas
        ORDER BY codigo DESC
    """
    cods = db.select(query)
    if len(cods) < 1:
        cod = 1
    else:
        cod = cods[0][0]
        cod = int(cod[1:])+1
    n_cod = f"P{cod:04}"
    cols = ("nombre", "fecha_nac", "pais", "nominaciones", "premios")
    valores = []
    for i in cols:
        valor = json.get(i, None)
        if type(valor) == str:
            if "'" in valor:
                valor = valor.replace("'", " ")
        valores.append(valor)
    if None in valores:
        return {"estado":400, "mensaje":f"Son necesarios los siguientes datos: {', '.join(cols)}"}, 400
    elif type(valores[0]) != str:
        return {"estado":400, "mensaje":"El nombre ha de ser una cadena de texto (ej. 'Aaron Paul')"}, 400
    elif not comprobar_fecha(valores[1]):
        return {"estado":400, "mensaje":f"La fecha de nacimiento ha de ser una cadena de texto con la siguiente estructura (dd-mm-aaaa)"}, 400
    elif type(valores[2]) != str:
        return {"estado":400, "mensaje":"El pais ha de ser una cadena de texto (ej. 'España')"}, 400
    elif type(valores[3]) != int:
        return {"estado":400, "mensaje":"El nº de nominaciones ha de ser un entero (ej. 24)"}, 400
    elif type(valores[4]) != int:
        return {"estado":400, "mensaje":"El nº de premios ha de ser un entero (ej. 4)"}, 400
    vals_per = [n_cod]
    for i in valores:
        vals_per.append(i)
    db.insert("personas", vals_per)
    url = url_root + f"personas/{n_cod}/"
    return {"estado":201, "mensaje":"Persona creada de forma correcta", "url":url}, 201

def actualizar_persona(cod, json, url_root):
    cols = ("nombre", "fecha_nac", "pais", "nominaciones", "premios")
    if len(json) != 1:
        return {"estado":400, "mensaje":"Solo se puede actualizar un campo"}, 400
    query = """
        SELECT codigo
        FROM personas
        WHERE codigo='{}'
    """.format(cod)
    persona = db.select(query)
    if len(persona) == 0:
        return {"estado":404, "mensaje": "La persona introducida no existe"}, 404
    if list(json.keys())[0] not in cols:
        return {"estado":400, "mensaje":f"Solo se puede actualizar uno de los siguientes campos: {', '.join(cols)}"}, 400
    col = list(json.keys())[0]
    val = json[col]
    if val is None:
        return {"estado":400, "mensaje":f"El campo {col} debe tener algun valor"}, 400
    elif col == cols[0] and type(val) != str:
        return {"estado":400, "mensaje":"El nombre ha de ser una cadena de texto (ej. 'Aaron Paul')"}, 400
    elif col == cols[1] and not comprobar_fecha(val):
        return {"estado":400, "mensaje":f"La fecha de nacimiento ha de ser una cadena de texto con la siguiente estructura (dd-mm-aaaa)"}, 400
    elif col == cols[2] and type(val) != str:
        return {"estado":400, "mensaje":"El pais ha de ser una cadena de texto (ej. 'España')"}, 400
    elif col == cols[3] and type(val) != int:
        return {"estado":400, "mensaje":"El nº de nominaciones ha de ser un entero (ej. 24)"}, 400
    elif col == cols[4] and type(val) != int:
        return {"estado":400, "mensaje":"El nº de premios ha de ser un entero (ej. 4)"}, 400
    else:
        if type(val) == str:
            val = val.replace("'", " ")
        db.update("personas", {col:val}, cod)
        url = url_root + f"personas/{cod}/"
        return {"estado":202, "mensaje":"Persona actualizada de forma correcta", "url":url}, 202

def eliminar_persona(cod):
    query = """
        SELECT codigo
        FROM personas
        WHERE codigo='{}'
    """.format(cod)
    persona = db.select(query)
    if len(persona) == 0:
        return {"estado":404, "mensaje": "La persona introducida no existe"}, 404
    else:
        db.delete("personas", cod)
        return {"estado":202, "mensaje":"Persona eliminado de forma correcta"}, 202

def generos(url_root):
    cols = ("codigo", "nombre", "cod_titu")
    query = """
        SELECT g.{}, g.{}, c.{}
        FROM generos g LEFT JOIN clasificado c
            ON g.codigo=c.cod_gen
        ORDER BY g.codigo
    """.format(*cols)
    gens = db.select(query)
    resul = []
    act = {}
    for gen in gens:
        if gen[0]in act:
            dict = resul[-1]
            if gen[2] not in act[gen[0]]:
                url = url_root + f"api/titulos/{gen[2]}/"
                dict["titulos"].append(url)
                act[gen[0]].add(gen[2])
        else:
            dict = {}
            for i, etiq in enumerate(cols):
                value = gen[i]
                if i == 2:
                    dict["titulos"] = []
                    if value is not None:
                        url = url_root + f"api/titulos/{value}/"
                        dict["titulos"].append(url)
                else:
                    if value is not None:
                        dict[etiq] = value
            resul.append(dict)
            act[gen[0]] = set()
            act[gen[0]].add(gen[2])
    return resul, 200

def genero(cod, url_root):
    cols = ("codigo", "nombre", "cod_titu")
    query = """
        SELECT g.{}, g.{}, c.{}
        FROM generos g LEFT JOIN clasificado c
            ON g.codigo=c.cod_gen
        WHERE g.codigo='{}'
    """.format(*cols, cod)
    genero = db.select(query)
    if len(genero) == 0:
        return {"estado":404, "mensaje": "El género introducido no existe"}, 404
    titus = set()
    dict = {}
    genero_0 = genero[0]
    for i, etiq in enumerate(cols):
        value = genero_0[i]
        if i == 2:
            dict["titulos"] = []
            if value is not None:
                url = url_root + f"api/titulos/{value}/"
                dict["titulos"].append(url)
        else:
            if value is not None:
                dict[etiq] = value
    titus.add(genero_0[2])
    for gen in genero[1:]:
        if gen[2] not in titus and gen[2] is not None:
            url = url_root + f"api/titulos/{gen[2]}/"
            dict["titulos"].append(url)
            titus.add(gen[2])
    return dict, 200

def crear_genero(json, url_root):
    query = f"""
        SELECT codigo
        FROM generos
        ORDER BY codigo DESC
    """
    cods = db.select(query)
    if len(cods) < 1:
        cod = 1
    else:
        cod = cods[0][0]
        cod = int(cod[1:])+1
    n_cod = f"G{cod:03}"
    nombre = json.get("nombre", None)
    if nombre is None:
        return {"estado":400, "mensaje":"Son necesarios los siguientes datos: nombre"}, 400
    elif type(nombre) != str:
        return {"estado":400, "mensaje":"El nombre ha de ser una cadena de texto (ej. 'Comedia')"}, 400
    nombre = nombre.replace("'", " ")
    db.insert("generos", (n_cod, nombre))
    url = url_root + f"generos/{n_cod}/"
    return {"estado":201, "mensaje":"Género creado de forma correcta", "url":url}, 201

def actualizar_genero(cod, json, url_root):
    if len(json) != 1:
        return {"estado":400, "mensaje":"Solo se puede actualizar un campo"}, 400
    query = """
        SELECT codigo
        FROM generos
        WHERE codigo='{}'
    """.format(cod)
    genero = db.select(query)
    if len(genero) == 0:
        return {"estado":404, "mensaje": "El género introducido no existe"}, 404
    nombre = json.get("nombre", None)
    if nombre is None:
        return {"estado":400, "mensaje":"Es necesario el siguiente campo: nombre"}, 400
    elif type(nombre) != str:
        return {"estado":400, "mensaje":"El nombre ha de ser una cadena de texto (ej. 'Comedia')"}, 400
    else:
        if type(nombre) == str:
            nombre = nombre.replace("'", " ")
        db.update("generos", {"nombre":nombre}, cod)
        url = url_root + f"generos/{cod}/"
        return {"estado":202, "mensaje":"Género actualizado de forma correcta", "url":url}, 202
    

def eliminar_genero(cod):
    query = """
        SELECT codigo
        FROM generos
        WHERE codigo='{}'
    """.format(cod)
    genero = db.select(query)
    if len(genero) == 0:
        return {"estado":404, "mensaje": "El género introducido no existe"}, 404
    else:
        db.delete("generos", cod)
        return {"estado":202, "mensaje":"Género eliminado de forma correcta"}, 202