# SMaRT_files

Após realizar medidas de impedância no SMaRT, os arquivos '.dat' precisam ser convertidos para '.csv', tratados e salvos como '.txt' para serem ajustados no ZView.  
Em posse dos arquivos '.csv' (convertidos no próprio SMaRT), podemos utilizar do programa para tratar os dados.

Ao executá-lo, será solicitado o endereço do diretório de dados onde deve conter os arquivos com a extensão '.csv', podendo haver subpastas. 

O programa irá buscar as colunas 'Frequency (Hz)', 'Impedance Magnitude (Ohms)' e 'Impedance Phase Degrees (')' para, a partir delas, calcular a parte real (Z'=|Z|cos(\theta)) e a parte imaginária (Z''=|Z|sin(\theta)) correspondentes a cada frequência (Hz) apresentada nos arquivos '.csv'. Se houver mais de uma temperatura, os arquivos serão separados automaticamente levando em consideração o Set Point (°C). 

O arquivo final contém três colunas separadas por tab: Frequência  Z'  Z''

