import random
import string
import database
import smtplib
from email.mime.text import MIMEText
from decouple import config

db = database.DB()

class Email:
    def __init__(self):
        self.server_smtp = smtplib.SMTP("smtp.gmail.com", 587)
        self.from_email = "apirestatd@gmail.com"
        self.server_smtp.starttls()
        self.server_smtp.login(self.from_email, config("MAIL_PSW"))

    def load_content(self, key, url_root):
        with open("templates/email.html") as f:
            html = f.read()
        html = html.replace("-key-", key)
        html = html.replace("-ruta-", url_root)
        ruta_eliminar = url_root + "/api/eliminar_clave/?api_key="
        html = html.replace("-ruta_eliminar-", ruta_eliminar)
        return html

    def send_email(self, to_email, key, url_root):
        html = self.load_content(key, url_root)
        msg = MIMEText(html, "html")
        msg["Subject"] = "API KEY"
        msg["From"] = self.from_email
        msg["To"] = to_email
        text = msg.as_string()
        self.server_smtp.sendmail(self.from_email, to_email, text)

    def is_valid(self, email):
        query = f"""
            SELECT *
            FROM claves_api
            WHERE correo='{email}'
        """
        data = db.select(query)
        if len(data)==0:
            return True
        else:
            return False

class ApiKey:
    def __init__(self):
        self.keys = {}
        self.store_keys()

    def store_keys(self):
        query = f"""
            SELECT clave, permisos
            FROM claves_api
        """
        keys = db.select(query)
        for key in keys:
            self.keys[key[0]] = key[1]
        return None

    def is_valid(self, api_key):
        if len(api_key) != 64 or api_key is None:
            return False, ""
        elif api_key in self.keys:
            return True, self.keys[api_key]
        else:
            self.store_keys()
            if api_key is self.keys:
                return True, self.keys[api_key]
            else:
                return False, ""

    def generate_key(self, length=64):
        key = "".join(random.choice(string.ascii_letters + string.digits) for i in range(length))
        return key

    def create_apikey(self, email, cond="u"):
        key = self.generate_key()
        values = (email, key, cond)
        db.insert("claves_api", values)
        self.store_keys()
        return key

    def delete(self, clave):
        db.delete("claves_api", clave, "clave")
        self.store_keys()
        return {"estado":202, "mensaje":"Clave eliminada"}, 202


def formato_dicc(dicc):
    if type(dicc) == dict:
        resul = [("{", 0)]
        for k, v in dicc.items():
            if type(v) == str:
                resul.append((f"'{k}' : '{v}',", 1))
            elif type(v) == int:
                resul.append((f"'{k}' : {v},", 1))
            elif type(v) == list:
                resul.append((f"'{k}' : [", 1))
                for elem in v:
                    resul.append((f"'{elem}',", 2))
                resul.append(("],", 1))
        resul.append(("}", 0))
    elif type(dicc) == list:
        resul = [("[", 0)]
        for i in dicc:
            resul.append(("{", 1))
            for k, v in i.items():
                if type(v) == str:
                    resul.append((f"'{k}' : '{v}',", 2))
                elif type(v) == int:
                    resul.append((f"'{k}' : {v},", 2))
                elif type(v) == list:
                    resul.append((f"'{k}' : [", 2))
                    for elem in v:
                        resul.append((f"'{elem}',", 3))
                    resul.append(("],", 2))
            resul.append(("}", 1))
        resul.append(("]", 0))
    return resul