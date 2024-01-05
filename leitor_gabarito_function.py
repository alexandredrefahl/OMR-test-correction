# -*- coding: utf-8 -*-
# USo
# python test_grader.py --image images/test_01.png

# Importar os pacotes necessarios
from imutils.perspective import four_point_transform
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import os
import sqlite3


def extrair_matricula(imgMatricula):
    # Le a imagem inteira
    image = cv2.imread(imgMatricula)
    # StartY EndY Start X EndX
    #image = image[310:650, 100:640]
    image = image[310:670, 120:640]
    #image = image[250:650, 100:640]
    # Passa pra tons de cinza
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Filtro para eliminar ruidos
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Tratamento para detectar contornos
    edged = cv2.Canny(blurred, 75, 200)
    # Aplica metodo Otsu's thresholding para binarizar a imagem corrigida (coluna 1 e 2)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    #cv2.imshow("Recorte_Matricula", image)
    #cv2.waitKey(0)

    # Encontra o contorno na imagem distorcida, e inicializa a lista de contornos que correspondem a questao
    # 	Col1
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    numMatricula = []

    #print("Numero de contornos Matricula: {:.2f}\r" . format(len(cnts)))
    # looping nos contornos da Matricula
    for c in cnts:
        # computa o contorno de cada bounding box entao usa o bounding box para calcular o aspect ratio
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)

        # para nomear o contorno como número de matricula a região precisa ser
        # suficientemente larga e alta e ter um aspect ratio de aproximadamente 1
        if w >= 28 and h >= 28 and ar >= 0.8 and ar <= 1.2:
            numMatricula.append(c)
    #print("Numero linhas detectadas na matrícula: {:.2f}\r" . format(len(numMatricula)/10))
    
    #todos = cv2.drawContours(image,numMatricula,-1,255,3)
    #cv2.imshow("Todos",todos)

    numMatricula = contours.sort_contours(numMatricula, method="top-to-bottom")[0]
    numeroMatricula =""
    
    for (q, i) in enumerate(np.arange(0, len(numMatricula), 10)):
        # organiza os contornos da questao atual da esquerda pra direita
        cnts = contours.sort_contours(numMatricula[i:i + 10])[0]
        bubbled = None
        # Passa por todos os contornos que foram organizados
        for (j, c) in enumerate(cnts):
    		# constroi uma mascara para revelar qual bolinha esta marcada
            mask = np.zeros(thresh.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)

            # aplica a mascara na imagem e conta quantos pixels nao zero aparecem dentro da bolinha
            mask = cv2.bitwise_and(thresh, thresh, mask=mask)
            total = cv2.countNonZero(mask)
            #print(j," - ",total,"\t")

            # se o total é maior do que o total de pixels nao zero entao esta e a bolinha que foi marcada
            if bubbled is None or total > bubbled[0]:
                bubbled = (total, j)
        numeroMatricula = numeroMatricula + str(bubbled[1])
    return numeroMatricula
                

# Função que converte o Gabarito fornecido em forma de texto para a forma usada pelo software
def monta_AnswareKey(Gabarito_texto):
    Answare_Key = []
    for letra in Gabarito_texto:
        if letra == "A":
            Answare_Key.append(0)
        if letra == "B":
            Answare_Key.append(1)
        if letra == "C":
            Answare_Key.append(2)
        if letra == "D":
            Answare_Key.append(3)
        if letra == "E":
            Answare_Key.append(4)
    return Answare_Key


# Função que corrige a prova
def corrige_prova(Gabarito,arqImagem,Salvar):
    # Usa a imagem para extrair a matricula
    matricula = extrair_matricula(arqImagem)
    # Carrega a imagem, converte para tons de cinza, desfoca um pouco
    image = cv2.imread(arqImagem)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    #edged = cv2.Canny(blurred, 75, 200)
    # Vetor da imagem original que representa StartY:EndY,StartX:EndX
    col1_ori = image[705:1930, 130:620]
    col1_gry = gray[705:1930, 130:620]
    col2_ori = image[705:1930, 625:1125]
    col2_gry = gray[705:1930, 625:1125]
    #crop_orig = image[724:2120, 130:490] 
    #cropped = gray[724:2120, 130:490]
    # Aplica metodo Otsu's thresholding para binarizar a imagem corrigida (coluna 1 e 2)
    thresh_col1 = cv2.threshold(col1_gry, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    thresh_col2 = cv2.threshold(col2_gry, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    #cv2.imshow("tresh", thresh_col1)
    # Encontra o contorno na imagem distorcida, e inicializa a lista de contornos que correspondem a questao
    # 	COL1
    cnts_col1 = cv2.findContours(thresh_col1.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_col1 = imutils.grab_contours(cnts_col1)
    # 	COL2
    cnts_col2 = cv2.findContours(thresh_col2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_col2 = imutils.grab_contours(cnts_col2)
    # Define as variáveis que vão receber as questões na Coluna1 e 2
    questionCol1 = []
    questionCol2 = []
    # Para Debug
    #print("Numero de contornos coluna 1: {:.2f}\r" . format(len(cnts_col1)))
    #print("Numero de contornos coluna 2: {:.2f}" . format(len(cnts_col2)))
    # função que separa os contornos da coluna
    questionCol1 = conta_contornos(cnts_col1)
    questionCol2 = conta_contornos(cnts_col2)
    
    if questionCol1 == -1 or questionCol2 == -1:
        print("Erro na correção da prova... Contornos não detectados. Pulando arquivo: ", arqImagem)
        return None
    
    #print("Numero de questoes detectadas na coluna 1: {:.2f}\r" . format(len(questionCol1)/5))
    #print("Numero de questoes detectadas na coluna 2: {:.2f}\r" . format(len(questionCol2)/5))
    # Classifica os contornos de modo que possam ser corrigidos
    questionCol1 = contours.sort_contours(questionCol1, method="top-to-bottom")[0]
    questionCol2 = contours.sort_contours(questionCol2, method="top-to-bottom")[0]
    # Inicializa as variáveis
    certas = 0
    Gabarito_aluno = ""
    chave_aluno = ""
    # Função que faz o looping para correção das questões da coluna
    # Coluna 1
    Gabarito_Col1,chave_col1,certas_col1,col1_ori = corrige_questoes(questionCol1,Gabarito,thresh_col1,col1_ori)
    # Coluna 2
    Gabarito_Col2,chave_col2,certas_col2,col2_ori = corrige_questoes(questionCol2,Gabarito,thresh_col2,col2_ori)
    certas = certas_col1 + certas_col2
    Gabarito_aluno = Gabarito_Col1 + Gabarito_Col2
    chave_aluno = chave_col1 + chave_col2
    # Reescreve o arquivo com as questões corrigidas
    image[705:1930, 130:620] = col1_ori
    image[705:1930, 625:1125] = col2_ori
    # Coloca na posição da imagem o score
    # Calcula o score/pontuação
    Nota = (certas / 40.0) * 100
    cv2.putText(image, "Pontuacao: {:.2f}%".format(Nota), (1200, 800),cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 0, 255), 2)
    # Acrescenta o sufixo corrigida à imagem
    imgCorrigida = arqImagem[:-4] + "_corrigida.png" 
    cv2.imwrite(imgCorrigida, image)
    print("[Resultado] Pontuacao: {:.2f}%".format(Nota))
    #cv2.imshow("Coluna1", col1_ori)
    #cv2.imshow("Coluna2", col2_ori)
    #cv2.waitKey(0)
    if Salvar == "Sim" or Salvar == "sim" or Salvar == "s" or Salvar == "S":
        nome_aluno,fase_aluno,periodo_aluno = consulta_matricula(matricula)
        conn = sqlite3.connect('dados_alunos.db')
        cursor = conn.cursor()
        cod_prova=6
        cursor.execute("""INSERT INTO Resultados (matricula,gabarito_aluno,chave_resposta,percentual,cod_prova,nome,fase,periodo) VALUES (?,?,?,?,?,?,?,?)""", (matricula,Gabarito_aluno,chave_aluno,Nota,cod_prova,nome_aluno,fase_aluno,periodo_aluno))
        # gravando no bd
        conn.commit()
        conn.close
    return None


def corrige_questoes(cntsColuna,GabaritoGeral,imgTreshCol,imgColOri):
    # Usa a função para montar o vetor resposta com base no gabarito de letras
    ANSWER_KEY = monta_AnswareKey(GabaritoGeral)
    # Inicializa a variável gabarito do aluno
    Gabarito_aluno=""
    chave_aluno=""
    certas = 0
    # Cada questao tem 5 respostas possiveis para processar os contornos em lotes de 5
    for (q, i) in enumerate(np.arange(0, len(cntsColuna), 5)):
        # organiza os contornos da questao atual da esquerda pra direita
        # depois inicializa a variavel indice da questao correta
        cnts = contours.sort_contours(cntsColuna[i:i + 5])[0]
        bubbled = None
        # Passa por todos os contornos que foram organizados
        for (j, c) in enumerate(cnts):
    		# constroi uma mascara para revelar qual bolinha esta marcada
            mask = np.zeros(imgTreshCol.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)
            # aplica a mascara na imagem e conta quantos pixels nao zero aparecem dentro da bolinha
            mask = cv2.bitwise_and(imgTreshCol, imgTreshCol, mask=mask)
            total = cv2.countNonZero(mask)
            #print(j," - ",total,"\t")

            # se o total é maior do que o total de pixels nao zero entao esta e a bolinha que foi marcada
            if bubbled is None or total > bubbled[0]:
                bubbled = (total, j)
        # inicializa a cor do contorno e a cor da questao correta
        color = (0, 0, 255)
        k1 = GabaritoGeral[q:q+1]
        k = ANSWER_KEY[q]

        # confere se a bolinha marcada é a correta
        padrao = ["A", "B", "C", "D", "E"]
        Gabarito_aluno = Gabarito_aluno + padrao[bubbled[1]]
        if k == bubbled[1]:
            color = (0, 255, 0)
            certas += 1
            chave_aluno += "1"
        else:
            chave_aluno += "0"
        # desenha um circulo naquela que estiver correta
        cv2.drawContours(imgColOri, [cnts[k]], -1, color, 3)
        #print("Questão: ",q+1," - Correta: ",k1," Marcada: ",padrao[bubbled[1]],"\r")
    # Retornar o Gabarito do Aluno, o número de certas e a imagem corrigida
    return Gabarito_aluno,chave_aluno,certas,imgColOri


# Função que conta, classifica e adiciona os contornos válidos
def conta_contornos(cnts_col):
    Questoes = []
    # looping nos contornos COLUNA
    for c in cnts_col:
        # computa o contorno de cada bounding box entao usa o bounding box para calcular o aspect ratio
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)
        # para nomear o contorno como uma questao a regiao precisa ser
        # suficientemente larga e alta e ter um aspect ratio de aproximadamente 1
        if w >= 29 and h >= 29 and ar >= 0.65 and ar <= 1.6:
            Questoes.append(c)
        if w >=29 and h >=29 and not (ar >= 0.75 and ar <= 1.225):
            print("Verificar: w={:.3f}".format(w)," h={:.3f}".format(h), " ar={:.3f}".format(ar))
    print("Numero de questoes detectadas na coluna: {:.2f}\r" . format(len(Questoes)/5))
    if (len(Questoes)/5)<20:
        return -1
    else:
        return Questoes


def consulta_matricula(num_matricula):
    conn = sqlite3.connect('dados_alunos.db')
    cursor = conn.cursor()
    # lendo os dados
    cursor.execute("""SELECT nome,fase,periodo FROM cadastro_alunos WHERE matricula="""+str(num_matricula))
    linha = cursor.fetchone()
    conn.close()
    if linha != None:
        print("Aluno: ",linha[0])
        return linha[0],linha[1],linha[2]
    else:
        print("Aluno não encontrado com a matricula: ",num_matricula)
        return "",0,""
               


#Se for rodar direto do terminal pode usar essa função
def main():
    """Função principal da aplicação.
    """
    # Monta o processador de argumentos e processa os argumentos
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--imagem", required=False,  help = "Arquivo da prova a ser corrigida")
    ap.add_argument("-p","--pasta", required=False,   help = "Caminho para a pasta que contém os arquivos de imagem")
    ap.add_argument("-s","--save", required=False,   help = "Define se salva no banco de dados ou não Sim ou Não")
    args = vars(ap.parse_args())
    GABARITO = "ABBADEEBDDCDAEDDECDDEACEEBBBCCDEEEACDEEB"
    # Se for fornecido o nome específico da prova
    if args["imagem"]:
        arqImagem = args["imagem"]
        matricula = extrair_matricula(arqImagem)
        print("Processando o arquivo", arqImagem, " - Matrícula: ",matricula)
        corrige_prova(GABARITO,arqImagem,args["save"])
    # Se for fornecida a Pasta onde estão as provas
    if args["pasta"]:
        # Esta etapa é necessária para que a cada interação não sejam acrescentados os arquivos recém criados.
        lista_arquivos = os.listdir(args["pasta"]) 
        for arquivo in lista_arquivos:
            arqImagem = args["pasta"] + arquivo
            matricula = extrair_matricula(arqImagem)
            print("Processando o arquivo", arquivo, " - Matrícula: ",matricula)
            corrige_prova(GABARITO,arqImagem,args["save"])

if __name__ == "__main__":
    main()
       



