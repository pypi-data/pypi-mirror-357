# PyControlAudacity-cli
[![Documentation Status](https://app.readthedocs.org/projects/pycontrolaudacity-cli/badge/?version=latest&style=plastic)](https://app.readthedocs.org/projects/pycontrolaudacity-cli/badge/?version=latest&style=plastic)

PyControlAudacity-cli é um CLI (*Command Line Interface*) Python para gerenciar rótulos em uma instância do Audacity, por meio do seu sistema de scripts.

### Nome

**PyControlAudacity-cli** - cria rótulos e atualiza o timestamp de uma trilha de áudio no Audacity, possibilitando seu posterior particionamento em fragmentos.

### Instalação

Para instalar o **PyControlAudacity-cli**, recomendamos o uso do `poetry`.

~~~
poetry add pycontrolaudacity-cli
~~~

Embora seja apenas uma recomendação, a instalação pode ser realizada com seu gerenciador de pacotes Python favorito.

~~~
# Usando o pip
pip install pycontrolaudacity-cli

# Usando o pipx
pipx install pycontrolaudacity-cli
~~~

### Descrição

**PyControlAudacity-cli** é um CLI Python que foi pensando para rodar a partir do Python puro, sem dependências externas. Sua execução faz sentido em conjunto com uma instância do Audacity, utilizando o suporte a scripts ([mod-script-pipe](https://manual.audacityteam.org/man/scripting.html)) daquele software.

> **IMPORTANTE:** É preciso habilitar o módulo mod-script-pipe no Audacity antes de usar o módulo PyControlAudacity-cli.


### Como usar

~~~
usage: PyControlAudacity-cli.py [--rotulo TEXT] [--sobreposicao INT] [--help] [--version] [--docs]

Cria rótulos em uma trilha de áudio do Audacity, acrescentando timestamp atualizado.

options:
  --rotulo TEXT       string que será acrescentada ao rótulo (padrão: Audacity)
  --sobreposicao INT  define o valor, em segundos, da sobreposição entre os rótulos (padrão: 5)
  --help              exibe essa mensagem e sai
  --version           exibe a versão do programa e sai
  --docs              exibe uma documentação rápida e sai
~~~
