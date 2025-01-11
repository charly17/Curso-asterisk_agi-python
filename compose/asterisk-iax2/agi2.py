#!/root/virtualenv/bin/python
import pystrix

# Se crea el objeto agi con el cual se podran usar las funciones de agi
agi = pystrix.agi.AGI()
# con execute manejamos el SDTDOUT, enviamos el comando utilizando pystrix.
agi.execute(pystrix.agi.core.Verbose('Validando identificacion', level=1))
# enviamos la accion para contestar el canal.
agi.execute(pystrix.agi.core.Answer())


identi_confirm = False

while identi_confirm is False:

    identificacion = agi.execute(
        #pystrix.agi.core.GetData('custom/identificacion', 5000, 10)
        pystrix.agi.core.GetData('custom/llamada_exitosa', 5000, 10)

    )
    if identificacion:
        identificacion = identificacion[0]
        agi.execute(pystrix.agi.core.StreamFile('custom/llamada_exitosa'))
        agi.execute(pystrix.agi.core.SayDigits(identificacion))
        option = agi.execute(
            pystrix.agi.core.GetOption('custom/llamada_exitosa', [1, 2])
        )
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
