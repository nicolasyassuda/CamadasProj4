#####################################################
# Camada Física da Computação
# Carareto
# 11/08/2022
# Aplicação
####################################################


# esta é a camada superior, de aplicação do seu software de comunicação serial UART.
# para acompanhar a execução e identificar erros, construa prints ao longo do código!


from enlace import *
import time
import numpy as np
import random
from datetime import datetime

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

# use uma das 3 opcoes para atribuir à variável a porta usada
# serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
# serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM6"                  # Windows(variacao de)


def main():
    try:
        print("Iniciou o main")
        # declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        # para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)
        origem = 33
        com1.enable()
        print("Abriu a comunicação")
        imageW = "./recebida.jpg"
        img=b''
        # Ativa comunicacao. Inicia os threads e a comunicação seiral
        ocioso = True
        limpaLog = open("logServidor.txt", "w").write("--------------------------------------------\n")
        log = open("logServidor.txt", "a")
        while ocioso:

            print("esperando 1 byte de sacrificio")
            rxBuffer, nRx = com1.getData(1)
            com1.rx.clearBuffer()
            time.sleep(.1)

            # Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.

            handShake = com1.getData(14)[0]
            log.write(f"{datetime.now()} /receb/ {len(handShake)}\n")
            if handShake[0] == 1:
                if handShake[1] != 33:
                    print("Não é para mim.")
                elif handShake[-4:] != b'\xaa\xbb\xcc\xdd':
                    print("Não é o EOP correto")
                else:
                    print("É para mim.")
                    ocioso = False
        headRespostaLista = [2, 33, 12, handShake[3],
                             0, handShake[5], 0, 0, 0, 0]
        headResposta = bytearray(headRespostaLista)
        eop = handShake[-4:]
        respostaHandShake = headResposta + eop
        a = com1.rx.getBufferLen()
        print(a)
        com1.sendData(respostaHandShake)
        log.write(f"{datetime.now()} /envio/ {len(respostaHandShake)}\n")
        cont = 0
        contSucesso = 0
        while cont < handShake[3]:
            inicial1 = time.time()
            inicial2 = time.time()
            a = com1.rx.getBufferLen()
            while a < 10:
                a = com1.rx.getBufferLen()
                final1 = time.time()
                final2 = time.time()
                if final1 - inicial1 > 2:
                    headT4Lista = [4, 33, 12, handShake[3],
                                   cont, 0, cont, contSucesso, 0, 0]
                    headT4 = bytearray(headT4Lista)
                    packT4 = headT4 + eop
                    com1.sendData(packT4)
                    log.write(f"{datetime.now()} /envio/{packT4[0]}/ {len(packT4)}\n")
                    print("Pedindo Pacote")
                    inicial1 = time.time()
                if final2 - inicial2 > 20:
                    ocioso = True
                    headT5Lista = [4, 33, 12, handShake[3],
                                   cont, 0, cont, contSucesso, 0, 0]
                    headT5 = bytearray(headT5Lista)
                    packT5 = headT5 + eop
                    com1.sendData(packT5)
                    log.write(f"{datetime.now()} /envio/{packT5[0]}/ {len(packT5)}\n")
                    raise Exception("Timeout")

            head = com1.getData(10)[0]
            tipo = head[0]

            totalPacotes = handShake[3]
            num_pacote = head[4]
            tamanho_payload = head[5]
            rec = head[6]
            ultimo = contSucesso
            payload = com1.getData(tamanho_payload)[0]
            log.write(f"{datetime.now()} /receb/ {tamanho_payload+14}\n")
            
            print(f"{0}-esse é o payload {1}-tamanho payload",(payload, tamanho_payload))
            eop = com1.getData(4)[0]

            if tipo == 3:
                if num_pacote != cont:
                    print("Pacote fora de ordem")
                    headT6Lista = [6,33,12,totalPacotes,contSucesso,0,contSucesso,contSucesso,0,0]
                    headT6 = bytearray(headT6Lista)
                    packT6 = headT6 + eop
                    com1.sendData(packT6)
                    log.write(f"{datetime.now()} /envio/{packT6[0]}/ {len(packT6)}\n")

                elif eop != b'\xaa\xbb\xcc\xdd':
                    print("EOP errado")
                    raise Exception("EOP errado")
                elif num_pacote == totalPacotes-1:
                    img += payload
                    headT4Lista = [4, 33, 12, handShake[3],
                                   cont, 0, cont, contSucesso, 0, 0]
                    headT4 = bytearray(headT4Lista)
                    packT4 = headT4 + eop
                    com1.sendData(packT4)
                    log.write(f"{datetime.now()} /envio/{packT4[0]}/ {len(packT4)}\n")

                    print("Imagem recebida")
                    print("Salvando dadods no arquivo: ")
                    print(" - {}".format(imageW))
                    f = open(imageW, 'wb')
                    print(f"img- {img}")
                    f.write(img)
                    com1.disable()
                    raise Exception("Imagem recebida")
                else:
                    print(num_pacote, totalPacotes)
                    img += payload
                    headT4Lista = [4, 33, 12, handShake[3],
                                   cont, 0, cont, contSucesso, 0, 0]
                    cont += 1
                    headT4 = bytearray(headT4Lista)
                    packT4 = headT4 + eop
                    com1.sendData(packT4)
                    log.write(f"{datetime.now()} /envio/{packT4[0]}/ {len(packT4)}\n")

                    time.sleep(.1)
                    print("Pacote Recebido")
                    contSucesso = cont
        '''

        #Fecha arquivo de imagem
        # f.close()

        # for i in range(len(rxBuffer)):
        #     print("recebeu {}" .format(rxBuffer[i]))
        

        # Encerra comunicação
        '''
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()

    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()

    # so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
