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

# Monta o processador de argumentos e processa os argumentos
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,	help="Caminho para a imagem de entrada")
args = vars(ap.parse_args())

# define o mapa de respostas corretas de acordo com cada questao
ANSWER_KEY = [3, 4, 1, 3, 0, 3, 1, 2, 4, 3, 3, 2, 2, 2, 4, 3, 2, 1, 1, 0, 2, 4, 4, 3, 1, 2, 4, 4, 3, 2, 3, 4, 0, 1, 3, 2, 4, 4, 1, 4]
GABARITO = "DEBDADBCEDDCCCEDCBBACEEDBCEEDCDEABDCEEBE"

# Carrega a imagem, converte para tons de cinza, desfoca um pouco
# Encontra as bordas
image = cv2.imread(args["image"])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(blurred, 75, 200)

# encontra o contorno no mapa e entao inicializa
# o contorno para o documento correspondente ao documento
#cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#cnts = imutils.grab_contours(cnts)
#docCnt = None

# garante que pelo menos um contorno foi encontrado
#if len(cnts) > 0:#
#	# classifica os contornos de acordo com seu tamanho em ordem descendente
#	cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

#	# faz um looping em todos os contornos classificados
#	for c in cnts:
#		# aproxima o contorno 
#		peri = cv2.arcLength(c, True)
#		approx = cv2.approxPolyDP(c, 0.02 * peri, True)
#
#		# Se o contorno tem pelo menos 4 pontos
#		# entao assumimos que encontramos os cantos do papel
#		if len(approx) == 4:
#			docCnt = approx
#			break

# aplica a transformacao de perspectiva de 4 pontos, tano na imagem original quanto na cinza
#paper = four_point_transform(image, docCnt.reshape(4, 2))
#warped = four_point_transform(gray, docCnt.reshape(4, 2))

# Vetor da imagem original que representa StartY:EndY,StartX:EndX
col1_ori = image[705:1930, 130:620]
col1_gry = gray[705:1930, 130:620]
col2_ori = image[705:1930, 625:1125]
col2_gry = gray[705:1930, 625:1125]
matr_ori = image[340:480, 100:570]
matr_gry = gray[340:480, 100:570]

crop_orig = image[724:2120, 130:490] 
cropped = gray[724:2120, 130:490]

# Aplica metodo Otsu's thresholding para binarizar a imagem corrigida (coluna 1 e 2)
thresh_col1 = cv2.threshold(col1_gry, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
thresh_col2 = cv2.threshold(col2_gry, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
#cv2.imshow("tresh", thresh_col1)

# Encontra o contorno na imagem distorcida, e inicializa a lista de contornos que correspondem a questao
# 	Col1
cnts_col1 = cv2.findContours(thresh_col1.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts_col1 = imutils.grab_contours(cnts_col1)
# 	Col2
cnts_col2 = cv2.findContours(thresh_col2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts_col2 = imutils.grab_contours(cnts_col2)

questionCol1 = []
questionCol2 = []

print("Numero de contornos coluna 1: {:.2f}\r" . format(len(cnts_col1)))
print("Numero de contornos coluna 2: {:.2f}" . format(len(cnts_col2)))

# looping nos contornos COLUNA 1
for c in cnts_col1:
	# computa o contorno de cada bounding box entao usa o bounding box para calcular o aspect ratio
	(x, y, w, h) = cv2.boundingRect(c)
	ar = w / float(h)

	# para nomear o contorno como uma questao a regiao precisa ser
	# suficientemente larga e alta e ter um aspect ratio de aproximadamente 1
	if w >= 28 and h >= 28 and ar >= 0.8 and ar <= 1.2:
		questionCol1.append(c)
print("Numero de questoes detectadas na coluna 1: {:.2f}\r" . format(len(questionCol1)/5))

# looping nos contornos COLUNA 2
for c in cnts_col2:
	# computa o contorno de cada bounding box entao usa o bounding box para calcular o aspect ratio
	(x, y, w, h) = cv2.boundingRect(c)
	ar = w / float(h)

	# para nomear o contorno como uma questao a regiao precisa ser
	# suficientemente larga e alta e ter um aspect ratio de aproximadamente 1
	if w >= 28 and h >= 28 and ar >= 0.8 and ar <= 1.2:
		questionCol2.append(c)
print("Numero de questoes detectadas na coluna 2: {:.2f}\r" . format(len(questionCol2)/5))

#todos = cv2.drawContours(col2_ori,questionCol2,-1,255,3)
#cv2.imshow("Todos",todos)

# classifica os contornos das questoes de cima para baixo depois inicializa a variavel que vai armazenar
# o numero de questoes corretas
questionCol1 = contours.sort_contours(questionCol1, method="top-to-bottom")[0]
questionCol2 = contours.sort_contours(questionCol2, method="top-to-bottom")[0]
certas = 0
Gabarito_aluno=""

# Cada questao tem 5 respostas possiveis para processar as questoes em lotes de 5
for (q, i) in enumerate(np.arange(0, len(questionCol1), 5)):
	# organiza os contornos da questao atual da esquerda pra direita
    # depois inicializa a variavel indice da questao correta
	cnts = contours.sort_contours(questionCol1[i:i + 5])[0]
	bubbled = None

	marcada=False

	# Passa por todos os contornos que foram organizados
	for (j, c) in enumerate(cnts):
#		# constroi uma mascara para revelar qual bolinha esta marcada
		mask = np.zeros(thresh_col1.shape, dtype="uint8")
		cv2.drawContours(mask, [c], -1, 255, -1)

		# aplica a mascara na imagem e conta quantos pixels nao zero aparecem dentro da bolinha
		mask = cv2.bitwise_and(thresh_col1, thresh_col1, mask=mask)
		total = cv2.countNonZero(mask)
		#print(j," - ",total,"\t")

		# se o total é maior do que o total de pixels nao zero entao esta e a bolinha que foi marcada
		if bubbled is None or total > bubbled[0]:
			bubbled = (total, j)
			if marcada is False:
    				marcada = True
    		
	# inicializa a cor do contorno e a cor da questao correta
	color = (0, 0, 255)
	k1 = GABARITO[q:q+1]
	k = ANSWER_KEY[q]

	# confere se a bolinha marcada é a correta
	padrao = ["A", "B", "C", "D", "E"]
	Gabarito_aluno= Gabarito_aluno + padrao[bubbled[1]]
	if k == bubbled[1]:
		color = (0, 255, 0)
		certas += 1
	# desenha um circulo naquela que estiver correta
	cv2.drawContours(col1_ori, [cnts[k]], -1, color, 3)
	print("Questão: ",q+1," - Correta: ",k1," Marcada: ",padrao[bubbled[1]],"\r")

# ****** Coluna 2 *******
#Repete o processo para coluna 2 até que possa descobrir como transformar isso em uma função

# Cada questao tem 5 respostas possiveis para processar as questoes em lotes de 5
for (q, i) in enumerate(np.arange(0, len(questionCol2), 5)):
	# organiza os contornos da questao atual da esquerda pra direita
    # depois inicializa a variavel indice da questao correta
	cnts_d = contours.sort_contours(questionCol2[i:i + 5])[0]
	bubbled = None

	# Passa por todos os contornos que foram organizados
	for (j, c) in enumerate(cnts_d):
#		# constroi uma mascara para revelar qual bolinha esta marcada
		mask = np.zeros(thresh_col2.shape, dtype="uint8")
		cv2.drawContours(mask, [c], -1, 255, -1)

		# aplica a mascara na imagem e conta quantos pixels nao zero aparecem dentro da bolinha
		mask = cv2.bitwise_and(thresh_col2, thresh_col2, mask=mask)
		total = cv2.countNonZero(mask)

		# se o total é maior do que o total de pixels nao zero entao esta e a bolinha que foi marcada
		if bubbled is None or total > bubbled[0]:
			bubbled = (total, j)

	# inicializa a cor do contorno e a cor da questao correta
	color = (0, 0, 255)
	k1 = GABARITO[q+20:q+21]
	k = ANSWER_KEY[q+20]

	# confere se a bolinha marcada é a correta
	padrao = ["A", "B", "C", "D", "E"]
	Gabarito_aluno= Gabarito_aluno + padrao[bubbled[1]]
	if k == bubbled[1]:
		color = (0, 255, 0)
		certas += 1
	# desenha um circulo naquela que estiver corretas
	cv2.drawContours(col2_ori, [cnts_d[k]], -1, color, 3)
	print("Questão: ",q+21," - Correta: ",k1," Marcada: ",padrao[bubbled[1]],"\r")

print("\rGabarito do Aluno: ",Gabarito_aluno)

# Reescreve o arquivo com as questões corrigidas
image[705:1930, 130:620] = col1_ori
image[705:1930, 625:1125] = col2_ori

# Coloca na posição da imagem o score
# Calcula o score/pontuação
Nota = (certas / 40.0) * 100
cv2.putText(image, "{:.2f}%".format(Nota), (1350, 740),cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

cv2.imwrite("corrigida.png", image)
print("[Resultado] Pontuacao: {:.2f}%".format(Nota))
#cv2.putText(crop_orig, "{:.2f}%".format(score), (10, 30),
#	cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
#cv2.imshow("Original", crop_orig)
#cv2.imshow("Exam", paper)
cv2.imshow("Coluna1", col1_ori)
cv2.imshow("Coluna2", col2_ori)
cv2.waitKey(0)