#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 18 16:06:52 2021

@author: heri
"""

import os
import re
from datetime import datetime
from fnmatch import fnmatch

import matplotlib.pyplot as plt
import numpy as np
from automaterials.experiment.eis.zview import ZViewCircuit


def __ajustpath(path: str) -> str:
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
        __ajustpath('/home/usuario/Downloads')
        retorna '/home/usuario/Downloads/'

    """
    if path[-1] != '/':
        path = path + '/'
    return path


def __natural_keys(text: str) -> str:
    """
    O método __natural_keys() é usado para definir ordenação natural/humana
    em objetos do tipo list.

    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)

    Exemplo de uso:
        files_list.sort(key=__natural_keys)
    """

    def atoi(text):
        return int(text) if text.isdigit() else text

    return [atoi(c) for c in re.split(r'(\d+)', text)]


def __get_data_exp(filename: str) -> list:
    """
    Retorna uma lista com os dados de todas as linhas contidas no arquivo.

    Os dados obtidos são referentes a Frequência, Parte real(Z'),
    Parte imaginária (Z'').

    É esperado um arquivo do tipo texto (TXT) delimitado por tabulação ('\t').

    filename : Str. Nome do arquivo.
    """

    data_list = []

    with open(filename, 'r') as frequency:
        line = frequency.readline()
        while line:
            if line.strip():
                data = re.split(r'\t', line.strip())
                data_list.append(data)
            line = frequency.readline()

    return data_list


def __get_data_fit(filename: str) -> list:
    """
    Retorna uma lista com os dados de todas as linhas contidas no arquivo.

    Os dados obtidos são referentes a Freq(HZ), Ampl, Bias, Time(Sec),
    Z'(a), Z''(b), GD, Err, Range.

    É esperado um arquivo do tipo texto (.z) delimitado por vírgula (',').

    filename : Str. Nome do arquivo.
    """

    data_list = []
    with open(filename, 'r') as f:
        line = f.readline()
        while line:
            # line = line.strip()
            line = re.sub('^"', '', line)
            line = re.sub('"$', '', line.strip())
            if line.find('Freq(Hz)') == 0 and line.rfind('Range') > 0:
                # line = re.sub("\s+", " ", line.strip())
                line = f.readline()
                while line:
                    line = f.readline()
                    if line.strip():
                        data = re.split(r',\s', line.strip())
                        data_list.append(data)
                    else:
                        break
            line = f.readline()
    return data_list


def get_filenames(root, pattern, profundidade=0):
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
    filenames_list = get_filenames('./path/', '*.txt')

    """

    lfiles = []

    lenroot = len(root.split('/'))

    for path, subdirs, files in os.walk(root):
        path = __ajustpath(path)
        lenpath = len(os.path.split(path)[0].split('/')) + len(
            os.path.split(path)[1].split('/')
        )
        if profundidade == 0 or (lenpath - lenroot) <= profundidade:
            for name in files:
                if fnmatch(name, pattern):
                    fname = os.path.join(path, name)
                    lfiles.append(fname)

    lfiles.sort(key=__natural_keys)
    return lfiles


def savefigure(figname=None, figpath=None, dpi=None, bbox_inches=None):
    """
    Salva imagem plotata.

    Parameters
    ----------
    figname : TYPE, optional
        DESCRIPTION. The default is None.
    figpath : TYPE, optional
        DESCRIPTION. The default is None.
    dpi : TYPE, optional
        DESCRIPTION. The default is None.
    bbox_inches : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    None.

    """

    if figname is None:
        figname = 'plot_'
    if figpath is None:
        figpath = './figures'
    if dpi is None:
        dpi = 200
    if bbox_inches is None:
        bbox_inches = 'tight'
    if not os.path.exists(figpath):
        os.mkdir(figpath)
    figname = os.path.join(
        figpath, figname + datetime.now().strftime('%Y%m%d_%H%M%S%f') + '.png'
    )
    plt.savefig(figname, dpi=dpi, bbox_inches=bbox_inches)


def yaxis_fmt(axis_y, position):
    """Retorna y formatado.

    Positional arguments:
       axis_y -- Posição y no gráfico
    Keyword arguments:
        position -- Posição
    """
    # result = "{:.0f}".format(y)

    # numero_string = '{:,.9f}'.format(round(axis_y, 0))
    numero_string = f'{round(axis_y, 0):,.9f}'
    result_str = numero_string
    result_str = result_str.replace(',', '_')
    result_str = result_str.replace('.', ',')
    result_str = result_str.replace('_', '.')
    position = result_str.find(',')
    if position > -1:
        result_str = str(result_str)[:position]

    return result_str


def xaxis_fmt(axis_x, position):
    """Retorna x formatado.

    Positional arguments:
        eixo_x -- Posição x no gráfico
    Keyword arguments:
        posicao -- Posição
    """
    # result = format(x, ".0f") + ""
    # numero_string = '{:,.9f}'.format(round(axis_x, 0))
    numero_string = f'{round(axis_x, 0):,.9f}'
    result_str = numero_string
    result_str = result_str.replace(',', '_')
    result_str = result_str.replace('.', ',')
    result_str = result_str.replace('_', '.')
    position = result_str.find(',')
    if position > -1:
        result_str = str(result_str)[:position]

    return result_str


# def yaxis_fmte(axis_y, position):
#    """
#    Aplica formato Notação Científica a y.
#
#    Parameters
#    ----------
#    y : TYPE
#        DESCRIPTION.
#    pos : TYPE
#        DESCRIPTION.
#
#    Returns
#    -------
#    Retorna uma string com o valor formatado.
#
#    Exemplo:
#        ax.yaxis.set_major_formatter(ticker.FuncFormatter(yaxis_fmtE))
#
#    """
#    # result = "{:.1E}".format(y)
#    result = np.format_float_scientific(axis_y, precision=1, exp_digits=1)
#    result = result.replace('+', '')
#
#    return result


# def xaxis_fmte(axis_x, position):
#     """
#     Aplica formato Notação Científica a x.
#
#     Parameters
#     ----------
#     x : TYPE
#         DESCRIPTION.
#     pos : TYPE
#         DESCRIPTION.
#
#     Returns
#     -------
#     Retorna uma string com o valor formatado.
#
#     Exemplo:
#         ax.xaxis.set_major_formatter(ticker.FuncFormatter(xaxis_fmtE))
#
#     """
#     # result = "{:.1E}".format(x)
#     result = np.format_float_scientific(axis_x, precision=1, exp_digits=1)
#     result = result.replace('+', '')
#
#     return result


def get_data_exp(datapath: str, pattern: str) -> dict:
    """
    Retorna um objeto dictionary contendo os dados lidos a partir de
    todos os arquivos encontrados no diretório datapath.

    Aqui são esperados arquivos do tipo texto com extenção .txt.

    Para cada conjuto de dados, são criadas duas chaves no dicionário
    retornado. As chaves têm a seguinte estrutura:

        "z1_XXXC"
        "z2_XXXC"

    onde XXX é o valor da temperatura extraído do nome do arquivo.

    Cada item do dicionário é um array contendo os valores relativos a
    z1 (valores x) e z2 (valores y).

    """
    result = {}

    filenames_list = get_filenames(
        datapath,
        pattern,
        1,
    )

    for filename in filenames_list:
        ret = re.search(r'_\d+C[.]', filename)
        if ret:
            tempkey = ret.group()[1:-1]
        else:
            raise NameError(
                'Não foi encontrado valor da temperatura '
                + " no nome de arquivo '{}'."
            )

        filedata = []
        for datalist in __get_data_exp(filename):
            ddict = {}
            ddict['freq'] = float(datalist[0])
            ddict['z1'] = float(datalist[1])
            ddict['z2'] = float(datalist[2])
            filedata.append(ddict)

        x_list = []
        y_list = []
        for row in filedata:
            x_list.append(row['z1'])
            y_list.append(row['z2'])

        tempkeys = tempkey.split('C')
        result[int(tempkeys[0])] = np.column_stack((x_list, y_list))

    return result


def get_data_fit(datapath: str, pattern: str) -> dict:
    """
    Retorna um objeto dictionary contendo os dados lidos a partir de
    todos os arquivos encontrados no diretório datapath.

    Aqui são esperados arquivos do tipo texto com extenção .z.

    Para cada conjuto de dados, são criadas duas chaves no dicionário
    retornado. As chaves têm a seguinte estrutura:

        "z1_XXXC"
        "z2_XXXC"

    onde XXX é o valor da temperatura extraído do nome do arquivo.

    Cada item do dicionário é um array contendo os valores relativos a
    z1 (valores x) e z2 (valores y).

    """
    result = {}

    filenames_list = get_filenames(
        datapath,
        pattern,
        1,
    )

    for filename in filenames_list:
        ret = re.search(r'_\d+C[.]', filename)
        if ret:
            tempkey = ret.group()[1:-1]
        else:
            raise NameError(
                'Não foi encontrado valor da temperatura '
                + "no nome de arquivo f'{filename}'."
            )

        filedata = []
        for data in __get_data_fit(filename):
            ddict = {}
            ddict['freq'] = float(data[0])
            ddict['ampl'] = float(data[1])
            ddict['bias'] = float(data[2])
            ddict['time'] = float(data[3])
            ddict['z1'] = float(data[4])
            ddict['z2'] = float(data[5])
            ddict['gd'] = float(data[6])
            ddict['err'] = float(data[7])
            ddict['range'] = float(data[8])
            filedata.append(ddict)

        x_list = []
        y_list = []
        for row in filedata:
            x_list.append(row['z1'])
            y_list.append(row['z2'])

        tempkeys = tempkey.split('C')
        result[int(tempkeys[0])] = np.column_stack((x_list, y_list))

    return result


def get_data_mdl(datapath: str, pattern: str, frequency=None) -> dict:
    """
    Retorna um objeto dictionary contendo os dados lidos a partir de
    todos os arquivos encontrados no diretório datapath.

    Aqui são esperados arquivos do tipo texto com extenção .mdl.

    Para cada conjuto de dados, é criado uma array com os valores de x e y:

        "{keys: array([[x, y]])"

    onde XXX é o valor da temperatura extraído do nome do arquivo.

    Cada item do dicionário é um array contendo os valores relativos a
    Z_re (valores x) e Z_im (valores y).

    f=[start: Union[float, int] = 1.0, stop: Union[float, int] = 1.0e6,
        pts_per_decade: int = 30]
    esses são os valores por padrão
    """

    result = {}

    filenames_list = get_filenames(
        datapath,
        pattern,
        1,
    )

    for filename in filenames_list:
        ret = re.search(r'_\d+C[.]', filename)
        if ret:
            tempkey = ret.group()[1:-1]
        else:
            raise NameError(
                'Não foi encontrado valor da temperatura '
                + " no nome de arquivo '{}'."
            )

        filedata = []
        if frequency is None:
            zviewecircuit = ZViewCircuit(filename)
        else:
            zviewecircuit = ZViewCircuit(filename(frequency))

        circuit = zviewecircuit.circuit
        dict_ = circuit.zdata_as_dict()
        filedata.append(dict_)

        x_list = []
        y_list = []
        for row in filedata:
            x_list.append(row['Z_re'])
            y_list.append(row['Z_im'])

        tempkey = tempkey.split('C')
        result[int(tempkey[0])] = np.column_stack(
            (x_list[0].tolist(), y_list[0].tolist())
        )

    return result


def get_data_txt(datapath: str, pattern: str) -> dict:

    result = {}

    filenames_list = get_filenames(
        datapath,
        pattern,
        1,
    )

    for filename in filenames_list:
        ret = re.search(r'_\d+C[.]', filename)
        if ret:
            tempkey = ret.group()[1:-1]
        else:
            raise NameError(
                'Não foi encontrado valor da temperatura'
                + ' no nome de arquivo "{}".'
            )

        filedata = []
        for datalist in __get_data_exp(filename):
            ddict = {}
            ddict['z_re'] = float(datalist[0])
            ddict['z_im'] = float(datalist[0])
            filedata.append(ddict)

        z_re = []
        z_im = []
        for row in filedata:
            z_re.append(row['z_re'])
            z_im.append(row['z_im'])

        tempkeys = tempkey.split('C')
        result[int(tempkeys[0])] = np.column_stack((z_re, z_im))

        return result
