# Procedimentos que antecedem a instalação do automaterials (Windows 10):

1. Baixar e instalar a versão Miniconda3 Windows 64-bit mais recente em https://docs.conda.io/en/latest/miniconda.html

2. Abrir o Anaconda Prompt (Miniconda3), no menu Iniciar

3. Criar um novo ambiente executando no Anaconda Prompt (Miniconda3):
        
   
   ```
   conda create -n automat python
   ```
   
   Esse novo ambiente, criado pelo comando acima, terá nome 'automat'. Você pode trocar esse nome no comando por outro de sua preferência, se desejar. Em alguns casos, pode ser necessário desativar temporariamente o antivírus antes de executar este passo.
   
4. Ativar o novo ambiente criado executando no Anaconda Prompt (Miniconda3):
        conda activate automat
   Caso você tenha optado por chamar o ambiente por outro nome em vez de 'automat', use no comando acima o nome escolhido.
   
5. Instalar o pymatgen  executando no Anaconda Prompt (Miniconda3):
        
    
    ```
    conda install --channel conda-forge pymatgen
    ```
    
    
    
6. Ainda no Anaconda Prompt (Miniconda3), navegue (usando o comando cd) até o diretório automaterials e, dentro dele, execute:
    
   ```
   pip install .
   ```
   
   Caso você queira usar no modo desenvolvedor (ou seja, contribuindo com novos códigos), execute em vez disso:
   
   Caso você queira usar no modo desenvolvedor (ou seja, contribuindo com novos códigos), execute em vez disso:
   
   ```
   pip install -e .
   ```
   
   
   
7. Para executar códigos do automaterials no VS Code dentro do ambiente que você criou, será preciso primeiro selecionar o ambiente (explicado no passo seguinte), e depois rodar o código no terminal do VS Code. Para rodar no terminal do VS Code, vá no explorador de arquivos que fica no painel à esquerda, clique com o botão direito do mouse no arquivo que você quer executar (assumindo que você já tenha aberto no explorador o diretório que o contém) e escolha "Run python file in Terminal" (ou o equivalente em português). Uma forma mais prática/conveniente é usar a extensão Code Runner. Caso você já tenha ela, clique no símbolo de engrenagem da extensão, e acesse as configurações. Vai ser aberto uma aba. No campo de busca (parte superior), digite 'terminal', sem apagar o que já está escrito no campo de busca. Vai aparecer a opção 'Run in Terminal'; marque-a para ativar essa funcionalidade. Você pode agora fechar a aba das configurações. A partir de agora será possível rodar o código usando o atalho Ctrl+Alt+N.

8. Para selecionar no VS Code (o que deve ser feito antes de rodar seu código) o ambiente criado, clique no canto inferior esquerdo da tela do VS Code. Vai aparecer uma lista de interpretadores para selecionar. Selecione o que contenha o nome do ambiente criado (automat neste exemplo). Caso aparece posteriormente uma mensagem de que não há um interpretador selecionado, apenas selecione novamente. Caso você procure o ambiente automat e ele tenha sumido das opções, o antivírus pode ter excluído o arquivo python.exe de dentro da pasta do ambiente. Nesse caso, você deverá procurar o python.exe na lista de arquivos excluídos ou em quarentena do antivírus, tentar reverter isso e adicionar o arquivo à lista de exceções.

9. Para que o ambiente possa ser ativado automaticamente no terminal do VS Code com base na seleção que você fez na lista (passo anterior), é preciso mudar o shell padrão do terminal para cmd em vez do PowerShell. Para isso, use Ctrl+Shift+P, digite 'user settings' no campo de busca e selecione a única opção que aparece (Open User Settings). Vai ser aberta uma aba de configurações. No campo de busca dela, digite 'terminal default windows'. Na única configuração filtrada, selecione Command Prompt na lista suspensa. Já pode fechar a aba.

10. Agora já é possível executar o código dentro do ambiente. Se estiver usando a extensão Code Runner, selecione no explorador de arquivos do VS Code aquele que você quer executar e dê um clique duplo nele para abrir em uma nova aba. Dê um clique simples em uma linha qualquer do código do arquivo e use Ctrl+Alt+N para rodar o código. Caso o terminal do VS Code não estivesse aberto antes, aparecerá uma mensagem de erro no terminal, mas basta usar Ctrl+Alt+N novamente para funcionar a partir de então. Se não estiver usando o Code Runner, será necessário ir no explorador de arquivos do VS Code, clicar com o botão direito no arquivo, e selecionar '

    ```
    Run python file in terminal'.
    ```

    