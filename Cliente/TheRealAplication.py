from datetime import datetime
import numpy as np
import time
from enlace import *
serialName = "COM4"


def main():
    try:
        inicia = False
        com1 = enlace(serialName)
        com1.enable()
        imageR = './image.jpg'
        limpaLog= open("./log.txt","w").write("----------------------------------\n")
        log = open("./log.txt","a")
        txBuffer = open(imageR, 'rb').read()
        tamanhoLista = len(bytearray(txBuffer))
        numeroPacotesInt = tamanhoLista//114
        numeroUltimoPacote = tamanhoLista % 114
        QuantPacotes = 0

        if numeroUltimoPacote == 0:
            QuantPacotes = numeroPacotesInt
        else:
            QuantPacotes = numeroPacotesInt+1

        if inicia == False:
            # ENVIA A MENSAGEM CONVIDANDO O SERVIDOR COM O IDENTIFICADOR COM TIPO 1
            head_lista = [1, 33, 12,
                          QuantPacotes, 0, txBuffer[0], 0, 0, 0, 0]
            head = bytearray(head_lista)
            eop = b'\xAA\xBB\xCC\xDD'
            handShake = head + eop
            time.sleep(.1)
            com1.sendData(b'00')
            time.sleep(1)
            inicial = time.time()
            a = com1.rx.getBufferLen()
            com1.sendData(handShake)
            log.write(f'{datetime.now()}-envio/{handShake[0]}/10/0/{QuantPacotes}\n')
            while a == 0:
                a = com1.rx.getBufferLen()
                final = time.time()
                if final-inicial >= 5 and a == 0:
                    inicial = time.time()
                    time.sleep(.1)
                    com1.sendData(b'00')
                    time.sleep(1)
                    com1.sendData(handShake)
                    log.write(f'{datetime.now()}-envio/{handShake[0]}/10/0/{QuantPacotes}\n')
                    open(log, 'a').write(
                        'Enviando Handshake')
                    print("servidor offline")
            respostaHandshake = com1.getData(14)[0]
            if respostaHandshake[2] == 12:
                print("é pra mim")
                log.write(f'{datetime.now()}-receb/{respostaHandshake[0]}/10/0/{14}\n')
            else:
                print("não é pra mim.")
            cont = 0
            print(12312312312312312)
            contSucesso = 0
            erro=2
            while cont < QuantPacotes:
                payload = txBuffer[cont*114:(cont+1)*114]
                print(cont)
                if erro == 1:
                    tamanhoDoPacote = 2
                if (erro == 2) and (cont == 90):
                    print(100000000000000)
                    cont=20
                    tamanhoDoPacote = len(payload)
                    erro=0
                else:
                    tamanhoDoPacote = len(payload)
                headDadoLista = [3, 33, 12, QuantPacotes, cont,
                                 tamanhoDoPacote, cont, contSucesso, 0, 0]
                headDado = bytearray(headDadoLista)
                package = headDado+payload+eop
                com1.sendData(package)
                log.write(f'{datetime.now()}-envio/{package[0]}/{len(package)}/{cont}/{QuantPacotes}\n')
                inicial1 = time.time()
                inicial2 = time.time()
                a = com1.rx.getBufferLen()
                while a < 14:
                    a = com1.rx.getBufferLen()
                    final1 = time.time()
                    final2 = time.time()
                    if final2-inicial2 >= 20 and a == 0:
                        print("servidor offline")
                        head5Lista = [5, 33, 12, QuantPacotes,
                                      cont, 0, cont, contSucesso, 0, 0]
                        head5 = bytearray(head5Lista)
                        packageT5 = head5+eop
                        com1.sendData(packageT5)
                        log.write(f'{datetime.now()}-envio/{packageT5[0]}/{len(packageT5)}\n')
                        raise Exception("Timeout")

                    elif final1-inicial1 >= 5 and a == 0:
                        print(package)
                        print("reenviando pacote")
                        com1.sendData(package)
                        log.write(f'{datetime.now()}-envio/{package[0]}/{len(package)}/{cont}/{QuantPacotes}\n')
                        inicial1 = time.time()
                mensagem = com1.getData(14)[0]
                log.write(f'{datetime.now()}-receb/{mensagem[0]}/{len(mensagem)}\n')
                if mensagem[0] == 4 and mensagem[4] == cont:
                    cont += 1
                    contSucesso = mensagem[7]
                if mensagem[0] == 6:
                    print("mensagem T6")
                    cont = mensagem[6]
            raise Exception("Enviou tudo com sucesso")

    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()

    # so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
