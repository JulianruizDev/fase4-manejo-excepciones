# ============================================================
# Sistema de Inventario - Fase 4: Manejo de excepciones
# ======================================================================
# Sistema Integral de Gestión de Clientes, Servicios y Reservas
# Curso: Programación 213023 - UNAD - Fase 4 (Manejo de excepciones)
# Autor: Julian Ruiz Acevedo
# ======================================================================

import json                              # Módulo para guardar y leer datos en formato JSON
import os                                # Módulo para comprobar si el archivo de datos existe
from datetime import datetime            # Clase para validar y comparar fechas y horas

ARCHIVO = "datos_gestion.json"           # Nombre del archivo donde se guardan los datos


# ======================================================================
# EXCEPCIONES PERSONALIZADAS
# ======================================================================

class GestionError(Exception):
    """Excepción base: de ella heredan todos los errores propios del sistema."""


class ClienteInvalidoError(GestionError):
    """Se lanza cuando los datos de un cliente no son válidos o ya existe."""


class ServicioInvalidoError(GestionError):
    """Se lanza cuando los datos de un servicio no son válidos o ya existe."""


class ClienteNoEncontradoError(GestionError):
    """Se lanza cuando se busca un cliente que no está registrado."""


class ServicioNoEncontradoError(GestionError):
    """Se lanza cuando se busca un servicio que no está registrado."""


class ReservaNoEncontradaError(GestionError):
    """Se lanza cuando se busca una reserva que no existe."""


class ReservaInvalidaError(GestionError):
    """Se lanza cuando la fecha o la hora de la reserva no son válidas."""


class CupoAgotadoError(GestionError):
    """Se lanza cuando un servicio ya no tiene cupos en la fecha y hora pedidas."""


class ReservaDuplicadaError(GestionError):
    """Se lanza cuando el cliente ya tiene una reserva en esa fecha y hora."""


class ArchivoDatosError(GestionError):
    """Se lanza cuando hay problemas al guardar o cargar el archivo de datos."""


# ======================================================================
# CLASE CLIENTE
# ======================================================================

class Cliente:
    """Representa a un cliente del negocio."""

    def __init__(self, id_cliente, nombre, correo, telefono):
        # Validamos que el identificador sea un entero positivo
        if not isinstance(id_cliente, int) or id_cliente <= 0:
            raise ClienteInvalidoError("El ID del cliente debe ser un entero mayor a 0.")
        # Validamos que el nombre sea texto con al menos 3 caracteres
        if not isinstance(nombre, str) or len(nombre.strip()) < 3:
            raise ClienteInvalidoError("El nombre debe tener al menos 3 caracteres.")
        # Validamos que el correo tenga arroba y un punto después de la arroba
        if not isinstance(correo, str) or "@" not in correo or "." not in correo.split("@")[-1]:
            raise ClienteInvalidoError("El correo no tiene un formato válido (ej: ana@correo.com).")
        # Validamos que el teléfono tenga solo dígitos y entre 7 y 10 caracteres
        if not str(telefono).isdigit() or not 7 <= len(str(telefono)) <= 10:
            raise ClienteInvalidoError("El teléfono debe tener entre 7 y 10 dígitos.")

        self.id_cliente = id_cliente                 # Guardamos el identificador
        self.nombre = nombre.strip()                 # Guardamos el nombre sin espacios sobrantes
        self.correo = correo.strip()                 # Guardamos el correo sin espacios sobrantes
        self.telefono = str(telefono)                # Guardamos el teléfono como texto

    def a_diccionario(self):
        """Convierte el cliente en un diccionario para guardarlo en JSON."""
        return {"id_cliente": self.id_cliente, "nombre": self.nombre,
                "correo": self.correo, "telefono": self.telefono}

    def __str__(self):
        # Texto con el que se muestra el cliente al imprimirlo
        return f"[{self.id_cliente}] {self.nombre} | {self.correo} | Tel: {self.telefono}"


# ======================================================================
# CLASE SERVICIO
# ======================================================================

class Servicio:
    """Representa un servicio que el negocio ofrece y que se puede reservar."""

    def __init__(self, id_servicio, nombre, precio, cupos):
        # Validamos que el identificador sea un entero positivo
        if not isinstance(id_servicio, int) or id_servicio <= 0:
            raise ServicioInvalidoError("El ID del servicio debe ser un entero mayor a 0.")
        # Validamos que el nombre no esté vacío
        if not isinstance(nombre, str) or not nombre.strip():
            raise ServicioInvalidoError("El nombre del servicio no puede estar vacío.")
        # Validamos que el precio sea un número positivo
        if not isinstance(precio, (int, float)) or precio <= 0:
            raise ServicioInvalidoError("El precio debe ser un número mayor a 0.")
        # Validamos que los cupos por turno sean un entero de al menos 1
        if not isinstance(cupos, int) or cupos < 1:
            raise ServicioInvalidoError("Los cupos por turno deben ser un entero mayor o igual a 1.")

        self.id_servicio = id_servicio               # Guardamos el identificador
        self.nombre = nombre.strip()                 # Guardamos el nombre limpio
        self.precio = precio                         # Guardamos el precio
        self.cupos = cupos                           # Guardamos los cupos disponibles por turno

    def a_diccionario(self):
        """Convierte el servicio en un diccionario para guardarlo en JSON."""
        return {"id_servicio": self.id_servicio, "nombre": self.nombre,
                "precio": self.precio, "cupos": self.cupos}

    def __str__(self):
        # Texto con el que se muestra el servicio al imprimirlo
        return f"[{self.id_servicio}] {self.nombre} | ${self.precio:,.0f} | Cupos por turno: {self.cupos}"


# ======================================================================
# CLASE RESERVA
# ======================================================================

class Reserva:
    """Representa la reserva de un servicio hecha por un cliente."""

    def __init__(self, id_reserva, id_cliente, id_servicio, fecha, hora, validar_futuro=True):
        try:
            # Convertimos fecha y hora de texto a un objeto datetime (lanza ValueError si el formato falla)
            momento = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
        except ValueError:
            # Cambiamos el error técnico por uno propio con un mensaje claro
            raise ReservaInvalidaError("Fecha u hora inválidas. Use AAAA-MM-DD y HH:MM (ej: 2026-12-05 14:30).")
        # Si se pide, verificamos que la reserva no sea en el pasado
        if validar_futuro and momento <= datetime.now():
            raise ReservaInvalidaError("La reserva debe ser en una fecha y hora futuras.")

        self.id_reserva = id_reserva                 # Guardamos el identificador de la reserva
        self.id_cliente = id_cliente                 # Guardamos a qué cliente pertenece
        self.id_servicio = id_servicio               # Guardamos qué servicio se reservó
        self.fecha = fecha                           # Guardamos la fecha (texto AAAA-MM-DD)
        self.hora = hora                             # Guardamos la hora (texto HH:MM)

    def a_diccionario(self):
        """Convierte la reserva en un diccionario para guardarla en JSON."""
        return {"id_reserva": self.id_reserva, "id_cliente": self.id_cliente,
                "id_servicio": self.id_servicio, "fecha": self.fecha, "hora": self.hora}

    def __str__(self):
        # Texto con el que se muestra la reserva al imprimirla
        return (f"Reserva #{self.id_reserva} | Cliente {self.id_cliente} | "
                f"Servicio {self.id_servicio} | {self.fecha} {self.hora}")


# ======================================================================
# CLASE SISTEMA (administra clientes, servicios y reservas)
# ======================================================================

class Sistema:
    """Contiene toda la lógica de negocio del sistema."""

    def __init__(self):
        self.clientes = {}                           # Diccionario: id_cliente -> Cliente
        self.servicios = {}                          # Diccionario: id_servicio -> Servicio
        self.reservas = {}                           # Diccionario: id_reserva -> Reserva
        self.siguiente_reserva = 1                   # Contador para asignar IDs de reserva

    # ----- Clientes -----
    def registrar_cliente(self, cliente):
        # Evitamos IDs de cliente repetidos
        if cliente.id_cliente in self.clientes:
            raise ClienteInvalidoError(f"Ya existe un cliente con ID {cliente.id_cliente}.")
        self.clientes[cliente.id_cliente] = cliente  # Guardamos el cliente

    def buscar_cliente(self, id_cliente):
        try:
            return self.clientes[id_cliente]         # Intentamos obtener el cliente
        except KeyError:
            # Si la clave no existe, lanzamos nuestro error propio
            raise ClienteNoEncontradoError(f"No existe un cliente con ID {id_cliente}.")

    # ----- Servicios -----
    def registrar_servicio(self, servicio):
        # Evitamos IDs de servicio repetidos
        if servicio.id_servicio in self.servicios:
            raise ServicioInvalidoError(f"Ya existe un servicio con ID {servicio.id_servicio}.")
        self.servicios[servicio.id_servicio] = servicio  # Guardamos el servicio

    def buscar_servicio(self, id_servicio):
        try:
            return self.servicios[id_servicio]       # Intentamos obtener el servicio
        except KeyError:
            raise ServicioNoEncontradoError(f"No existe un servicio con ID {id_servicio}.")

    # ----- Reservas -----
    def crear_reserva(self, id_cliente, id_servicio, fecha, hora):
        cliente = self.buscar_cliente(id_cliente)    # Puede lanzar ClienteNoEncontradoError
        servicio = self.buscar_servicio(id_servicio) # Puede lanzar ServicioNoEncontradoError
        # Creamos la reserva (valida formato y que sea futura); el ID se asigna con el contador
        nueva = Reserva(self.siguiente_reserva, cliente.id_cliente, servicio.id_servicio, fecha, hora)

        # Contamos cuántas reservas ya tiene ese servicio en ese mismo turno
        ocupados = sum(1 for r in self.reservas.values()
                       if r.id_servicio == id_servicio and r.fecha == fecha and r.hora == hora)
        if ocupados >= servicio.cupos:
            raise CupoAgotadoError(f"No hay cupos para '{servicio.nombre}' el {fecha} a las {hora}.")

        # Verificamos que el cliente no tenga otra reserva a la misma fecha y hora
        for r in self.reservas.values():
            if r.id_cliente == id_cliente and r.fecha == fecha and r.hora == hora:
                raise ReservaDuplicadaError(f"{cliente.nombre} ya tiene una reserva el {fecha} a las {hora}.")

        self.reservas[nueva.id_reserva] = nueva      # Guardamos la reserva
        self.siguiente_reserva += 1                  # Avanzamos el contador de IDs
        return nueva

    def cancelar_reserva(self, id_reserva):
        try:
            return self.reservas.pop(id_reserva)     # Quitamos y devolvemos la reserva
        except KeyError:
            raise ReservaNoEncontradaError(f"No existe la reserva #{id_reserva}.")

    def reservas_de_cliente(self, id_cliente):
        self.buscar_cliente(id_cliente)              # Confirma que el cliente existe
        return [r for r in self.reservas.values() if r.id_cliente == id_cliente]

    def promedio_por_reserva(self):
        # Suma el precio de cada servicio reservado
        total = sum(self.servicios[r.id_servicio].precio for r in self.reservas.values())
        # Si no hay reservas, esta división lanza ZeroDivisionError (se controla en el menú)
        return total, total / len(self.reservas)

    # ----- Archivos -----
    def guardar(self):
        """Guarda todos los datos en un archivo JSON."""
        datos = {                                    # Armamos un diccionario con todo el sistema
            "clientes": [c.a_diccionario() for c in self.clientes.values()],
            "servicios": [s.a_diccionario() for s in self.servicios.values()],
            "reservas": [r.a_diccionario() for r in self.reservas.values()],
            "siguiente_reserva": self.siguiente_reserva,
        }
        try:
            with open(ARCHIVO, "w", encoding="utf-8") as f:   # Abrimos el archivo para escribir
                json.dump(datos, f, indent=4, ensure_ascii=False)
        except OSError as e:                         # Errores de disco, permisos, etc.
            raise ArchivoDatosError(f"No se pudo guardar el archivo: {e}")

    def cargar(self):
        """Carga los datos desde el archivo JSON, si existe."""
        if not os.path.exists(ARCHIVO):              # Si no existe, empezamos con el sistema vacío
            return False                             # Indicamos que no había datos previos
        try:
            with open(ARCHIVO, "r", encoding="utf-8") as f:   # Abrimos el archivo para leer
                datos = json.load(f)                 # Convertimos el JSON a diccionarios
            for c in datos["clientes"]:              # Recreamos cada cliente
                self.registrar_cliente(Cliente(c["id_cliente"], c["nombre"], c["correo"], c["telefono"]))
            for s in datos["servicios"]:             # Recreamos cada servicio
                self.registrar_servicio(Servicio(s["id_servicio"], s["nombre"], s["precio"], s["cupos"]))
            for r in datos["reservas"]:              # Recreamos cada reserva (sin exigir fecha futura)
                reserva = Reserva(r["id_reserva"], r["id_cliente"], r["id_servicio"],
                                  r["fecha"], r["hora"], validar_futuro=False)
                self.reservas[reserva.id_reserva] = reserva
            self.siguiente_reserva = datos["siguiente_reserva"]   # Recuperamos el contador
            return True                              # Indicamos que se cargaron datos previos
        except json.JSONDecodeError:                 # El archivo no es un JSON válido
            raise ArchivoDatosError("El archivo de datos está dañado.")
        except KeyError as e:                        # Falta algún campo en el JSON
            raise ArchivoDatosError(f"Al archivo le falta el campo {e}.")
        except GestionError as e:                    # Algún dato guardado no es válido
            raise ArchivoDatosError(f"Datos inválidos en el archivo: {e}")
        except OSError as e:                         # Error al leer el archivo
            raise ArchivoDatosError(f"No se pudo leer el archivo: {e}")


# ======================================================================
# FUNCIONES AUXILIARES DE ENTRADA
# ======================================================================

def leer_entero(mensaje):
    """Pide un número entero y repite hasta que el usuario escriba uno válido."""
    while True:                                      # Repetimos hasta recibir un dato correcto
        try:
            return int(input(mensaje))               # Intentamos convertir la entrada a entero
        except ValueError:                           # Si no es un entero, avisamos y repetimos
            print("Error: ingrese un número entero válido.")


def leer_decimal(mensaje):
    """Pide un número decimal y repite hasta que el usuario escriba uno válido."""
    while True:
        try:
            return float(input(mensaje))             # Intentamos convertir la entrada a decimal
        except ValueError:
            print("Error: ingrese un número válido.")


# ======================================================================
# PROGRAMA PRINCIPAL
# ======================================================================

def mostrar_menu():
    print("\n===== GESTIÓN DE CLIENTES, SERVICIOS Y RESERVAS =====")
    print("1. Registrar cliente")
    print("2. Registrar servicio")
    print("3. Listar clientes")
    print("4. Listar servicios")
    print("5. Crear reserva")
    print("6. Cancelar reserva")
    print("7. Ver reservas de un cliente")
    print("8. Reporte de ingresos")
    print("9. Guardar y salir")


def main():
    sistema = Sistema()                              # Creamos el sistema vacío
    try:
        hay_datos = sistema.cargar()                 # Intentamos cargar los datos guardados
    except ArchivoDatosError as e:
        print(f"Aviso: {e} Se inicia con el sistema vacío.")
        sistema = Sistema()                          # Reiniciamos el sistema para no mezclar datos
    else:
        # Solo se ejecuta si no hubo error al cargar
        print("Datos cargados correctamente." if hay_datos else "No hay datos previos: se inicia un sistema nuevo.")

    try:
        while True:                                  # Bucle del menú principal
            mostrar_menu()
            opcion = input("Seleccione una opción: ").strip()
            try:
                if opcion == "1":
                    id_c = leer_entero("ID del cliente: ")
                    nombre = input("Nombre: ")
                    correo = input("Correo: ")
                    telefono = input("Teléfono: ")
                    sistema.registrar_cliente(Cliente(id_c, nombre, correo, telefono))
                    print("Cliente registrado.")
                elif opcion == "2":
                    id_s = leer_entero("ID del servicio: ")
                    nombre = input("Nombre del servicio: ")
                    precio = leer_decimal("Precio: ")
                    cupos = leer_entero("Cupos por turno: ")
                    sistema.registrar_servicio(Servicio(id_s, nombre, precio, cupos))
                    print("Servicio registrado.")
                elif opcion == "3":
                    if not sistema.clientes:
                        print("No hay clientes registrados.")
                    for c in sistema.clientes.values():
                        print(c)
                elif opcion == "4":
                    if not sistema.servicios:
                        print("No hay servicios registrados.")
                    for s in sistema.servicios.values():
                        print(s)
                elif opcion == "5":
                    id_c = leer_entero("ID del cliente: ")
                    id_s = leer_entero("ID del servicio: ")
                    fecha = input("Fecha (AAAA-MM-DD): ").strip()
                    hora = input("Hora (HH:MM): ").strip()
                    reserva = sistema.crear_reserva(id_c, id_s, fecha, hora)
                    print(f"Reserva creada: {reserva}")
                elif opcion == "6":
                    id_r = leer_entero("ID de la reserva a cancelar: ")
                    print(f"Cancelada: {sistema.cancelar_reserva(id_r)}")
                elif opcion == "7":
                    id_c = leer_entero("ID del cliente: ")
                    lista = sistema.reservas_de_cliente(id_c)
                    if not lista:
                        print("El cliente no tiene reservas.")
                    for r in lista:
                        print(r)
                elif opcion == "8":
                    total, promedio = sistema.promedio_por_reserva()
                    print(f"Ingresos totales: ${total:,.0f} | Promedio por reserva: ${promedio:,.0f}")
                elif opcion == "9":
                    sistema.guardar()                # Guardamos antes de salir
                    print("Datos guardados. ¡Hasta pronto!")
                    break                            # Salimos del bucle
                else:
                    print("Opción no válida.")
            except GestionError as e:                # Captura todos nuestros errores personalizados
                print(f"Error: {e}")
            except ZeroDivisionError:                # Se intentó promediar sin reservas
                print("Error: no hay reservas para calcular el promedio.")
            except Exception as e:                   # Cualquier otro error inesperado
                print(f"Error inesperado: {e}")
    except (KeyboardInterrupt, EOFError):            # El usuario presionó Ctrl+C o se cerró la entrada
        print("\nInterrumpido. Guardando datos...")
        try:
            sistema.guardar()
        except ArchivoDatosError as e:
            print(f"Error: {e}")
    finally:
        print("Fin del programa.")                   # Se ejecuta siempre, haya o no errores


if __name__ == "__main__":                           # Solo ejecuta main() si el archivo se corre directamente
    main()