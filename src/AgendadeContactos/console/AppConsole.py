from app.Contacto import Contacto, ListaContactos, verificarCorreo, verificarTelefono
from consolemenu import *
from consolemenu.items import *
from tabulate import tabulate
import os
from pathlib import Path

clear = lambda : os.system("cls") if os.name == "nt" else os.system("clear")

def continuar():
    while input("Presione enter para volver...") != "": pass

class AppConsole:
    def __init__(self, argv : str = ""):
        self.contactos = ListaContactos()

        #importar contactos iniciales
        current_dir = Path(__file__).parent.joinpath("data")
        self.contactos.importarCsv(
            current_dir.joinpath("contactos2.csv").absolute()
        )

        self.contactos.importarVcard(
            current_dir.joinpath("contactos.vcard").absolute()
        )

        menu = ConsoleMenu("Agenda de Contactos")

        new_item = FunctionItem("Nuevo contacto", self.nuevoContacto, [])
        show_item = FunctionItem("Mostrar lista de contactos", self.mostrarContactos)
        find_item = FunctionItem("Buscar contacto", self.buscarContacto)

        delete_item = FunctionItem("Eliminar contacto", self.eliminarContacto)
        edit_item = FunctionItem("Editar contacto", self.editarContacto)

        import_submenu = ConsoleMenu("Importar contactos")
        import_submenu.append_item(FunctionItem("Importar VCF/VCARD", self.importarVcf))
        import_submenu.append_item(FunctionItem("Importar CSV", self.importarCsv))
        
        export_submenu = ConsoleMenu("Exportar contactos")
        export_submenu.append_item(FunctionItem("Exportar VCF/VCARD", self.exportarVcf))
        export_submenu.append_item(FunctionItem("Exportar CSV", self.exportarCsv))

        import_item = SubmenuItem("Importar contactos", import_submenu, menu)
        export_item = SubmenuItem("Exportar contactos", export_submenu, menu)

        qr_item = FunctionItem("Mostrar QR de contacto", self.show_qr)

        menu.append_item(new_item)
        menu.append_item(show_item)
        menu.append_item(find_item)
        menu.append_item(delete_item)
        menu.append_item(edit_item)
        menu.append_item(import_item)
        menu.append_item(export_item)
        menu.append_item(qr_item)

        menu.show()

    def inputNombreContacto(self, prompt = ""):
        nombre_contacto = input(prompt)
        while self.contactos[nombre_contacto] is None:
            clear()
            nombre_contacto = input(f"No existe el contacto '{nombre_contacto}'.\n Ingrese el nombre del contacto: ")
        return nombre_contacto


    def nuevoContacto(self):
        apellido = input("Apellido: ")
        nombre = input("Nombre: ")

        telefono = input("Teléfono: ")
        while not verificarTelefono(telefono):
            telefono = input("Entrada inválida\n Teléfono: ")
        
        correo = input("Correo: ")
        while not verificarCorreo(correo):
            correo = input("Entrada inválida\n Correo: ")

        self.contactos.añadir(Contacto(
            apellido, nombre, telefono, correo
        ))

        print("\nContacto guardado...\n")
        continuar()

    def editarContacto(self):
        nombre_contacto = self.inputNombreContacto("Ingrese el nombre del contacto a editar: ")

        apellido = input("Apellido: ")
        nombre = input("Nombre: ")

        telefono = input("Teléfono: ")
        while (not verificarTelefono(telefono)) and len(telefono) != 0:
            telefono = input("Entrada inválida\n Teléfono: ")
        
        correo = input("Correo: ")
        while (not verificarCorreo(correo)) and len(correo) != 0:
            correo = input("Entrada inválida\n Correo: ")
        
        # Si la entrada está vacía, conserva el valor
        # anterior
        choose = lambda x, y : x if len(x) > 0 else y

        # extraer contacto
        c = self.contactos.pop(nombre_contacto)
        c.apellido = choose(apellido, c.apellido)
        c.nombre   = choose(nombre, c.nombre)
        c.telefono = choose(telefono, c.telefono)
        c.correo   = choose(correo, c.correo)

        self.contactos.añadir(c)

        print("\nContacto guardado...\n")
        continuar()

    def imprimirTabla(self, lcontactos):
        rows = []
        for c in lcontactos:
            rows.append([str(c), c.apellido, c.nombre, c.telefono, c.correo])
        
        # orderar usando el nombre de contacto de forma ascendente
        rows.sort(key = lambda x : x[0]) 
        print(tabulate(rows, headers=["Nombre de contacto", "Apellido", "Nombre", "Teléfono", "Correo"]))

    def mostrarContactos(self):
        lcontactos = self.contactos.toList()
        self.imprimirTabla(lcontactos)

        print("\nSin contactos\n" if len(lcontactos) == 0 else "\n")
        continuar()

    def eliminarContacto(self):
        nombre_contacto = self.inputNombreContacto("Ingrese el nombre del contacto a eliminar: ")
        self.contactos.eliminar(nombre_contacto)

        print("\nContacto eliminado...\n")
        continuar()
        
    def buscarContacto(self):
        clave = input("Buscar contacto: ")
        res = self.contactos.buscar(clave)
        self.imprimirTabla(res)

        while input("\nDesea realizar otra búsqueda? (y/n): ").lower() == "y":
            clear()
            clave = input("Buscar contacto: ")
            res = self.contactos.buscar(clave)
            self.imprimirTabla(res)

        print("\n")
        continuar()

    def importarCsv(self):
        file_path = input("Ingrese la ruta donde se encuentra el archivo .CSV\n  >> ")
        i = self.contactos.importarCsv(file_path)
        print(f"Se importaron {i} contactos con éxito\n")
        continuar()

    def exportarCsv(self):
        file_path = input("Ingrese la ruta donde desea guardar el archivo .CSV\n  >> ")
        i = self.contactos.exportarCsv(file_path)
        print(f"Se exportaron {i} contactos con éxito\n")
        continuar()

    def importarVcf(self):
        file_path = input("Ingrese la ruta donde se encuentra el archivo .VCF/.VCARD\n  >> ")
        i = self.contactos.importarVcard(file_path)
        print(f"Se importaron {i} contactos con éxito\n")
        continuar()

    def exportarVcf(self):
        file_path = input("Ingrese la ruta donde desea guardar el archivo .VCF/.VCARD\n  >> ")
        i = self.contactos.exportarVcard(file_path)
        print(f"Se exportaron {i} contactos con éxito\n")
        continuar()

    def show_qr(self):
        nombre_contacto = self.inputNombreContacto("Nombre de contacto: ")
        
        c = self.contactos[nombre_contacto];
        qr = c.toQR()
        qr.print_ascii(tty=True, invert=True)

        print("\n\n")
        continuar()