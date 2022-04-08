#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 07:22:29 2021

@author: heri
"""

import os
from fnmatch import fnmatch
import pandas as pd
import math
import pathlib


def ajustpath(path):
    """
    Ajusta o path acrescentado a barra final ('/') caso já não haja.

    Parameters
    ----------
    path : TYPE
        DESCRIPTION.

    Returns
    -------
    path : TYPE
        DESCRIPTION.

    Exemplo
    -------
        ajustpath('/home/usuario/Downloads')
        retorna '/home/usuario/Downloads/'

    """
    if path[-1] != "/":
        path = path + "/"
    return path


def pega_arquivos(root, pattern, profundidade=0):
    """
    Pega todos os arquivos no diretório e subdiretórios combinando com
    um dado padrão (por exemplo *.txt).
    Retorna um objeto do tipo lista.

    Parâmetros
    ----------
        root: str.
            Diretório a partir do qual serão procurados os arquivos.

        pattern: str.
            Por exemplo, '*.txt', '*.xml', '*.jpg'.

        profundidade: int.
            Define até quantos subníveis de diretório os arquivos serão
            procurados. O padrão é 0, o que significa que não há limite;
            1 (um), a procura será feita apenas no diretório passado como
            root.

    Retorno
    -------
        Retorna um objeto do tipo list com zero, um ou mais nomes de arquivos.

    Exemplo
    -------
    listaDeArquivos = pegaListaDeArquivos('./path/', '*.txt')
    print(listaDeArquivos)

    """

    lfiles = []

    lenroot = len(root.split('/'))

    for path, subdirs, files in os.walk(root):
        path = ajustpath(path)
        lenpath = len(os.path.split(path)[0].split('/')) + \
            len(os.path.split(path)[1].split('/'))
        if profundidade == 0 or (lenpath - lenroot) <= profundidade:
            for name in files:
                if fnmatch(name, pattern):
                    # print os.path.join(path, name)
                    fname = os.path.join(path, name)
                    # print fname
                    lfiles.append(fname)

    return lfiles


def ajusta_arquivo(file_name):
    with open(file_name, 'r') as f:
        file_ext = pathlib.Path(file_name).suffix
        pos = file_name.rfind(file_ext)
        filename_temp = file_name[:pos] + '.tmp'
        ftemp = open(filename_temp, 'w')
        for row in f.readlines():
            row = row.replace('\n', '')
            if row.find('Exported SMaRT Impedance Data') > -1 \
                    or row.find('Experiment start time') > -1 \
                    or row.strip() == '':
                continue
            if row.find('Result Number,') > -1:
                # Ajusta a linha ref. ao cabeçalho de dados, substituindo delimitador
                row = row.replace(',', ';')
            # Troca vírgula por ponto
            row = row.replace(',', '.')
            # Adiciona delimitador ao final da linha
            if row[-1:] != ';':
                row = row + ';'
            # Grava linha
            ftemp.write(row + '\n')
    ftemp.close()
    return filename_temp


def gera_result(file_name):
    df = pd.read_csv(file_name, sep=';')
    file_ext = pathlib.Path(file_name).suffix
    pos_ext = file_name.rfind(file_ext)
    filename_txt = ""
    last_setpoint_c = None
    for irow in range(df.shape[0]):
        setpoint_c = str(df.iloc[irow]["Set Point ('C)"])
        if setpoint_c != last_setpoint_c:
            if filename_txt != "":
                fresult.close()
            if setpoint_c == "-":
                filename_txt = file_name[:pos_ext] + '.txt'
            else:
                filename_txt = file_name[:pos_ext]
                pos = filename_txt.find("ppd_")
                if pos > -1:
                    filename_txt = filename_txt[:pos + len("ppd_")] \
                        + "{0:.0f}".format(float(setpoint_c)) + 'C.txt'
                else:
                    filename_txt = file_name[:pos_ext] + '__' \
                        + "{0:.0f}".format(float(setpoint_c)) + 'C.txt'
            fresult = open(filename_txt, 'w')
            last_setpoint_c = setpoint_c
        frequency_Hz = df.iloc[irow]["Frequency (Hz)"]
        impedance_MO = df.iloc[irow]["Impedance Magnitude (Ohms)"]
        impedance_PD = df.iloc[irow]["Impedance Phase Degrees (')"]
        parte_real_Z1 = impedance_MO * math.cos(math.radians(impedance_PD))
        parte_imag_Z2 = impedance_MO * math.sin(math.radians(impedance_PD))
        row_str = "{}\t{}\t{}".format("{:.5f}".format(frequency_Hz),
                                     "{:.5f}".format(parte_real_Z1),
                                     "{:.5f}".format(parte_imag_Z2))
        # Troca ponto por vírgula
        troca_ponto = False
        if troca_ponto:
            row_str = row_str.replace('.', ',')
        # Grava linha no arquivo
        fresult.write(row_str + '\n')
    fresult.close()


def main():
    # dados_path = "C:/Users/neyve/Desktop/temp/medidas-smart/"
    dados_path = ""
    input_str = ""
    if dados_path == "":
        input_str = input("Diretório de dados: ")
        dados_path = input_str.strip().replace('\\', '/')
    if os.path.exists(dados_path):
        arquivos_list = pega_arquivos(dados_path, "*.csv")
        if len(arquivos_list) == 0:
            print("Aviso: Nenhum arquivo '.csv' encontrado em '{}'."\
                  .format(input_str))
        print('')
        icount = 0
        for arquivo in arquivos_list:
            icount += 1
            print("\nProcessando arquivo '{}'...".format(arquivo))
            filename_tmp = ajusta_arquivo(arquivo)
            gera_result(filename_tmp)
            # apaga arquivo .tmp
            os.remove(filename_tmp)
            print('Concluído')
        print("\n{} arquivo(s) processado(s).".format(icount))
    elif input_str.strip() != '':
        print("\nErro: Diretório de dados '{}' não encontrado."\
              .format(input_str))
    else:
        print("\nErro: Diretório de dados não especificado.")


if __name__ == '__main__':
    main()
