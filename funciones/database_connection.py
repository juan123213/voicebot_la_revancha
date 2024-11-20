from pymongo import MongoClient

def conectar_base_de_datos():
    """
    Función para establecer conexión con la base de datos 'hackaton'.
    Retorna el cliente y la base de datos.
    """
    try:
        # Configura la cadena de conexión
        MONGO_URI = "mongodb+srv://silversonic87:Np1AalGnm4FYDtqV@cluster0.pkjga.mongodb.net/hackaton?retryWrites=true&w=majority"
        
        # Conexión al cliente de MongoDB
        client = MongoClient(MONGO_URI)

        # Seleccionar la base de datos
        db = client["hackaton"]
        return client, db

    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None, None


def obtener_usuarios(db):
    """
    Función para obtener los documentos de la colección 'users'.
    Requiere como parámetro la base de datos.
    """
    try:
        # Seleccionar la colección "users"
        collection = db["users"]

        # Obtener todos los documentos de la colección
        usuarios = collection.find()

        # Imprimir cada documento
        for usuario in usuarios:
            print(usuario)

    except Exception as e:
        print(f"Error al obtener usuarios: {e}")


def cerrar_conexion(client):
    """
    Función para cerrar la conexión con la base de datos.
    Requiere como parámetro el cliente de MongoDB.
    """
    try:
        client.close()
        print("Conexión cerrada correctamente.")
    except Exception as e:
        print(f"Error al cerrar la conexión: {e}")


# Uso de las funciones
client, db = conectar_base_de_datos()  # Conecta a la base de datos

if db is not None:  # Si la conexión es exitosa
    obtener_usuarios(db)  # Obtén los usuarios
    cerrar_conexion(client)  # Cierra la conexión
