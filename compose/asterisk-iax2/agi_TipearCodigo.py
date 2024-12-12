import pystrix

# Se crea el objeto agi con el cual se podran usar las funciones de agi
agi = pystrix.agi.AGI()
# con execute manejamos el SDTDOUT, enviamos el comando utilizando pystrix.
agi.execute(pystrix.agi.core.Verbose('Validando identificacion, level=1'))

agi.execute(pystrix.agi.core.Answer())

identi_confirm = False


while identi_confirm is False:

    # se utiliza la clase getData con la cual se reproduce un audio al cliente
    #  con sus respectivos parametros indicados en la documentacion.
    identificacion = agi.execute(pystrix.agi.core.GetData('custom/identificacion', 5000, 10))
    if identificacion:
        identificacion = identificacion[0]
        agi.execute(pystrix.agi.core.StreamFile('custom/lectura'))
        agi.excecute(pystrix.agi.core.SayDigits(identificacion))

        option =agi.execute(pystrix.agi.core.GetOption('custom/confirmacion', [1, 2]))

        if option:
            option = option[0]
            if option == '1':
                agi.execute(pystrix.agi.core.Verbose('Identificacion Confirmada', level=1))
                identi_confirm = True
            else:
                agi.execute(pystrix.agi.core.Verbose('Identificacion sin confirmar'))

agi.execute(pystrix.agi.core.Hangup())