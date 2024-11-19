import escuchador
import transcriptor
import negociador
import hablador
import buscar_deuda #recibe el dni del cliente y busca en la base de datos los datos del cliente incluido el valor de la deuda
import escribir_datos_radicado #al final de llamada, se conecta con la base de datos creando una fila con numero de radicado y reporte de la solución a la que se llegó
import buscar_dni_nombre #busca en el texto del cliente sus datos de nombre completo y dni, y los guarda en las variables dni y nombre, tipo str


#Escuchador: Captura el audio del microfono
audio=escuchador() #devuelve un .wav (mp3?)

#transcriptor: transcribe el audio a texto
texto=transcriptor(audio) #devuelve una string

#buscar_dni_nombreextraer nombre y dni
dni,nombre=buscar_dni_nombre(texto)

#buscar_deuda: busca los datos de deuda a partir del dni
deuda=buscar_deuda(dni)

#negociador: responde al texto en el contexto de negociación financiera
respuesta=negociador(texto)

#hablador: Devuelve en voz clonada la respuesta del negociador
voz=hablador(respuesta)

import escuchador
import transcriptor
import negociador
import hablador
import buscar_deuda
import escribir_datos_radicado
import buscar_dni_nombre

def procesar_datos_cliente(texto, contexto):
    """
    Procesa el texto del cliente intentando extraer nombre y DNI.
    Retorna una tupla (dni, nombre, mensaje_respuesta)
    """
    try:
        dni_temp, nombre_temp = buscar_dni_nombre(texto)
        
        # Caso 1: Tenemos ambos datos
        if dni_temp and nombre_temp:
            deuda = buscar_deuda(dni_temp)
            mensaje = f"Gracias {nombre_temp}. He encontrado su información. Veo que tiene una deuda pendiente de {deuda}. ¿Cómo podemos ayudarle con esto?"
            return dni_temp, nombre_temp, deuda, mensaje
            
        # Caso 2: Solo tenemos nombre pero no DNI
        elif nombre_temp and not dni_temp:
            mensaje = f"Gracias {nombre_temp}. ¿Podría proporcionarme también su número de documento?"
            return None, nombre_temp, None, mensaje
            
        # Caso 3: Solo tenemos DNI pero no nombre
        elif dni_temp and not nombre_temp:
            mensaje = "He registrado su número de documento. ¿Podría decirme su nombre completo?"
            return dni_temp, None, None, mensaje
            
        # Caso 4: No tenemos ningún dato
        else:
            mensaje = "Por favor, necesito su nombre completo y número de documento para poder ayudarle."
            return None, None, None, mensaje
            
    except Exception as e:
        mensaje = "Disculpe, no pude entender bien sus datos. ¿Podría proporcionarme su nombre completo y número de documento?"
        return None, None, None, mensaje

def main():
    # Variables de control
    conversacion_activa = True
    dni = None
    nombre = None
    deuda = None
    contexto = []
    
    print("Sistema iniciado. Esperando interacción del cliente...")
    
    while conversacion_activa:
        # Captura del audio del cliente
        audio = escuchador()
        
        # Transcripción del audio a texto
        texto_cliente = transcriptor(audio)
        contexto.append({"rol": "cliente", "mensaje": texto_cliente})
        
        # Si no tenemos los datos completos del cliente
        if dni is None or nombre is None:
            dni_temp, nombre_temp, deuda_temp, mensaje_respuesta = procesar_datos_cliente(texto_cliente, contexto)
            
            # Actualizamos los datos que hayamos obtenido
            if dni_temp:
                dni = dni_temp
            if nombre_temp:
                nombre = nombre_temp
            if deuda_temp:
                deuda = deuda_temp
            
            contexto.append({"rol": "asistente", "mensaje": mensaje_respuesta})
            voz = hablador(mensaje_respuesta)
            
            # Si ya tenemos todos los datos, continuamos con la negociación
            if dni and nombre:
                continue
            else:
                continue
        
        # Si ya tenemos los datos completos, procedemos con la negociación
        respuesta, fin, acuerdo, tipo_acuerdo = negociador(texto_cliente, contexto)
        contexto.append({"rol": "asistente", "mensaje": respuesta})
        
        # Reproducir respuesta
        voz = hablador(respuesta)
        
        # Verificar si la conversación debe terminar
        if fin == 1:
            conversacion_activa = False
    
    # Registrar la conversación al finalizar
    numero_radicado = escribir_datos_radicado({
        "dni": dni,
        "nombre": nombre,
        "deuda_inicial": deuda,
        "acuerdo_alcanzado": acuerdo,
        "tipo_acuerdo": tipo_acuerdo,
        "historial_conversacion": contexto
    })
    
    # Mensaje final
    mensaje_despedida = "Gracias por su tiempo. La conversación ha sido registrada con el número de radicado: " + str(numero_radicado)
    voz = hablador(mensaje_despedida)
    print(f"Conversación finalizada. Número de radicado: {numero_radicado}")
    print(f"Acuerdo alcanzado: {'Sí' if acuerdo == 1 else 'No'}")
    if acuerdo == 1:
        print(f"Tipo de acuerdo: {tipo_acuerdo}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSistema detenido por el usuario")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
