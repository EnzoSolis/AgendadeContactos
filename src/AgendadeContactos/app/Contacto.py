import re
import csv
from qrcode import QRCode
from PIL import Image
from pathlib import Path

#RFC 5322
EMAIL_PATTERN = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
PHONE_PATTERN = r"\d{10}"
SEP_COLON = ":"
SEP_SEMICOLON = ";"
PROP_PATTERN = rf"^(?P<PROP>\w+)({SEP_SEMICOLON}|{SEP_COLON})"

re_email = re.compile(EMAIL_PATTERN, re.UNICODE)
re_phone = re.compile(PHONE_PATTERN)

verificarCorreo   = lambda correo : re_email.match(correo) is not None
verificarTelefono = lambda telefono: re_phone.match(telefono) is not None

class Contacto:
    def __init__(self, apellido : str, nombre : str, telefono : str, correo : str):
        self.apellido = apellido
        self.nombre = nombre
        self.telefono = telefono
        self.correo = correo

    def obtenerNombre(self) -> str:
        '''
        Retorna el nombre de la persona
        '''
        return self.nombre + " " + self.apellido
    
    def toVcard(self) -> str:
        vcard  =  "BEGIN:VCARD\nVERSION:3.0"
        vcard += f"FN;CHARSET=UTF-8:{self.obtenerNombre()}\n"
        vcard += f"N;CHARSET=UTF-8:{self.apellido};{self.nombre};;;\n"
        vcard += f"TEL;CELL;VOICE:+54{self.telefono}\n"
        vcard += f"EMAIL;CHARSET=UTF-8;type=INTERNET:{self.correo}\n"
        vcard += "END:VCARD"
        return vcard
    
    def toQR(self):
        qr = QRCode(version=1, box_size=10, border=5)
        qr.add_data(self.toVcard())
        # elige la version automáticamente según el tamaño
        # de los datos
        qr.make(fit=True)
        return qr

    def __str__(self) -> str:
        '''
        Retorno el nombre del contacto
        '''
        return self.obtenerNombre()
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __hash__(self) -> int:
        return hash((self.apellido, self.nombre))
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Contacto):
            return False
        
        res  = self.apellido == value.apellido and self.nombre == value.nombre
        res &= self.correo == value.correo and self.telefono == value.telefono
        return res;
        
class ParserVcard:
    def __init__(self, vcard_filepath = ""):
        self.vcard_filepath = vcard_filepath

    def getValue(self, prop : str, values : str):
        if prop == "TEL":
            #obtener el número en formato de 10 dígitos
            sub = re.sub(r"[\+\-\s]|;(.)+$", "", values)    #elimina los espacio y símbolos
            match = re.match(r".*(\d{10})$", sub)          #obtiene los últimos 10 dígitos
            return match.group(1) if match else ""
        elif prop == "N":
            #obtiene el apellido y nombre si es que existen
            match = re.match("(\w*;\w*)", values)
            return match.group(0) if match else ";"
        
        #ignorar otras propiedades y retornar los valores ingresados
        return values

    def parseOneContact(self, tokens : list) -> Contacto:
        d = dict()
        for prop, values in tokens:
            d[prop] = self.getValue(prop, values)

        names = d.get("N", ";").split(";")
        return Contacto(
            names[0],
            names[1],
            d.get("TEL", ""),
            d.get("EMAIL", "")  
        )

    def parse(self) -> list:
        contacts = dict()

        if not Path(self.vcard_filepath).exists():
            return contacts
        
        #abrir archivo
        with open(self.vcard_filepath, "r", encoding="UTF-8") as vcard_file:
            vcard_src = vcard_file.readlines()
            tokens = []
            
            for line in vcard_src:
                prop = re.match(PROP_PATTERN, line)
                if not prop:
                    continue
                
                prop = prop.group("PROP")
                lstr = line.split(SEP_COLON)
                values = lstr[1] if len(lstr) > 1 else ""

                #print((prop, values))
                tokens.append((prop, values))

                if prop.upper() == "END":
                    c = self.parseOneContact(tokens)
                    contacts[str(c)] = c

        return contacts
    
class ListaContactos:
    def __init__(self):
        self.contactos = dict()

    def toList(self):
        return self.contactos.values()

    def importarCsv(self, csv_filepath):
        count = 0
        with open(csv_filepath, "r", encoding="UTF-8") as file:
            csv_file = csv.DictReader(file)
            
            for row in csv_file:
                count += 1
                self.añadir(Contacto(
                    row["Last name"],
                    row["First name"],
                    row["Mobile"],
                    row["Email"]
                ))
        return count

    def exportarCsv(self, csv_filepath):
        count = 0
        with open(csv_filepath, "w+", encoding="UTF-8") as file:
            csv_file = csv.DictWriter(file, fieldnames=["Last name", "First name", "Mobile", "Email"])
            csv_file.writeheader()

            for k, c in self.contactos.items():
                count += 1
                csv_file.writerow({
                    "Last name" : c.apellido,
                    "First name" : c.nombre,
                    "Mobile" : c.telefono,
                    "Email" : c.correo
                })
        return count

    def importarVcard(self, vcard_filepath):
        pv = ParserVcard(vcard_filepath)
        vcards = pv.parse()
        count = len(vcards)
        self.contactos.update(vcards)
        return count

    def exportarVcard(self, vcard_filepath):
        count = 0
        with open(vcard_filepath, "w+", encoding="UTF-8") as vfile:
            for k, c in self.contactos.items():
                count += 1
                vfile.write(c.toVcard())
                vfile.write("\n")
        
        return count                

    def añadir(self, c : Contacto) -> bool:
        '''
        Añade un nuevo contacto a la lista.
        '''
        if self.contactos.get(c.obtenerNombre(), None) is not None:
            return False
        
        self.contactos[c.obtenerNombre()] = c
        return True

    def pop(self, nombre_contacto : str, default = None):
        return self.contactos.pop(nombre_contacto, default)

    def eliminar(self, nombre_contacto : str):
        '''
        Elimina un contacto de la lista
        '''
        self.contactos.pop(nombre_contacto, None)

    def buscar(self, clave : str):
        res = []
        for k, c in self.contactos.items():
            #unir todo en una cadena
            text = k + " " + c.telefono + " " + c.correo
            if text.find(clave) >= 0:
                res.append(c)

        return res

    def __getitem__(self, nombre_contacto : str):
        return self.contactos.get(nombre_contacto, None)

