#!/root/virtualenv/bin/python
import pystrix

# Se crea el objeto agi con el cual se podran usar las funciones de agi
agi = pystrix.agi.AGI()
# con execute manejamos el SDTDOUT, enviamos el comando utilizando pystrix.
agi.execute(pystrix.agi.core.Verbose('Validando identificacion', level=1))
# enviamos la accion para contestar el canal.
agi.execute(pystrix.agi.core.Answer())


identi_confirm = False

# Se inserta el codigo dentro de un while para asi se solicite de nuevo la identificacion hasta que ingrese un dato valido.
while identi_confirm is False:

    identificacion = agi.execute(
        #pystrix.agi.core.GetData('custom/identificacion', 5000, 10)
        pystrix.agi.core.GetData('custom/identificacion', 5000, 10)    # Nos devuelve el dtmf y el timeout en una tupla.

    )
    if identificacion:
        identificacion = identificacion[0]
        # Se reproduce un audio al cliente que indique el numero que ingreso.
        agi.execute(pystrix.agi.core.StreamFile('custom/lectura'))
        agi.execute(pystrix.agi.core.SayDigits(identificacion))
        # Aqui mandamos un audio que indique marque 1 para SI o marque 2 para NO y lo guardamos en la variable.
        option = agi.execute(
            pystrix.agi.core.GetOption('custom/confirmacion', [1, 2])
        )
        # Validamos si nuestra variable contine un dato y posterormente verificamos que opcion es.
        if option:
            option = option[0]
            if option == '1':
                agi.execute(
                    pystrix.agi.core.Verbose(
                        'identificación confirmada',
                        level=1
                    )
                )
                identi_confirm = True
            else:
                agi.execute(
                    pystrix.agi.core.Verbose('identificación sin confirmar'))

agi.execute(pystrix.agi.core.Hangup())
