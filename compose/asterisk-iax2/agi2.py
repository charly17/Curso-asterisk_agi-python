#!/root/virtualenv/bin/python
import pystrix

agi = pystrix.agi.AGI()
agi.execute(pystrix.agi.core.Verbose('Validando identificacion', level=1))
agi.execute(pystrix.agi.core.Answer())

identi_confirm = False

while identi_confirm is False:

    identificacion = agi.execute(
        pystrix.agi.core.GetData('custom/identificacion', 5000, 10)
    )
    if identificacion:
        identificacion = identificacion[0]
        agi.execute(pystrix.agi.core.StreamFile('custom/lectura'))
        agi.execute(pystrix.agi.core.SayDigits(identificacion))
        option = agi.execute(
            pystrix.agi.core.GetOption('custom/confirmacion', [1, 2])
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
