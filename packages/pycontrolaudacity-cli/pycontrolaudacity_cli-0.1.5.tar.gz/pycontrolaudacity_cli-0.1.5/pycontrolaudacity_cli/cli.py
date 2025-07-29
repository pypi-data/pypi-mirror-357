"""Controle de rótulos no Audacity via mod-script-pipe.

PyControlAudacity-cli é um script de linha de comando que cria rótulos em tempo de execução
no Audacity por meio da interface mod-script-pipe. Seu uso é justificado em conjunto com
uma instância do Audacity. Requer: Python 3 ou superior; Audacity 2.5.4 ou superior.

======================
Command Line Interface
======================

    uso: PyControlAudacity-cli [--rotulo TEXT] [--sobreposicao {0, 5}] [--help] [--version] [--docs]

Argumentos
----------
    --rotulo: string, opcional
        string que será usada na criação do rótulo
    --sobreposicao: int, opcional
        define o valor, em segundos, da sobreposição entre os rótulos [0 ou 5] (padrão: 5)
    --help: opcional
        exibe a ajuda e sai
    --version: opcional
        exibe a versão do programa e sai (default: 10)
    --docs: opcional
        exibe esse documentação e sai

Copyright 2025 by dUnIO
Lançada sob os termos da GNU General Public License versão 3:
<https://www.gnu.org/licenses/gpl-3.0.en.html />
"""

# Variáveis de configuração de escopo global no script
INTERVALO = 300     # Duração, em segundos, de um rótulo (Padrão: 5 minutos)
SOBREPOSICAO = 5    # Sobreposição de tempo entre os fragmentos (Padrão: 5 segundos)
ROTULO = 'Audacity' # String para compor e identificar o rótulo (Padrão: 'Audacity')

STRPIPELEITURA = PIPELEITURA = None
STRPIPEESCRITA = PIPEESCRITA = None
EOL = None

thread_escrita = thread_leitura = None

import datetime
import os
import sys
import threading
import time
import errno
import argparse

import json


# Configuração de Parse do Script.
from datetime import datetime, timedelta
from threading import Thread
from pycontrolaudacity_cli import __version__

cmd_parser = argparse.ArgumentParser(
    prog='PyControlAudacity-cli',
    usage='PyControlAudacity-cli [--rotulo TEXT] [--sobreposicao INT]',
    description="""\nCria rótulos em uma trilha de áudio do Audacity, acrescentando timestamp atualizado.""",
    add_help=False,
    epilog='Para mais informações sobre como usar o script, digite: PyControlAudacity-cli --help',
)
cmd_parser.add_argument(
    '--rotulo',
    action='store',
    default='Audacity',
    type=str,
    help='string que será acrescentada ao rótulo',
    metavar='TEXT',
)
cmd_parser.add_argument(
    '--sobreposicao',
    action='store',
    choices=[0, 5],
    default=5,
    type=int,
    help='define o valor, em segundos, da sobreposição entre os rótulos {0 ou 5}. Padrão é 5.',
    metavar='INT',
)
cmd_parser.add_argument(
    '--docs',
    action='store_true',
    help='exibe a documentação e sai'
)
cmd_parser.add_argument(
    '--help', action='help', help='exibe essa mensagem e sai'
)
cmd_parser.add_argument(
    '--version',
    action='version',
    version=f'%(prog)s {__version__}',
    help='exibe a versão do programa e sai',
)
args = cmd_parser.parse_args()

# Documentação do script
if args.docs:
    print(__doc__)
    sys.exit(0)

# Caso usuário especifique um rótulo ou sobreposição via argumento,
# atualizar as variáveis globais com o valor informado.
if args.rotulo != 'Audacity': ROTULO = args.rotulo
if args.sobreposicao != 5: SOBREPOSICAO = args.sobreposicao

# Inicializando variáveis que irão tratar os pipes de comunicação
if sys.platform == 'win32':
    STRPIPEESCRITA = TONAME = '\\\\.\\pipe\\ToSrvPipe'
    STRPIPELEITURA = FROMNAME = '\\\\.\\pipe\\FromSrvPipe'
    EOL = '\r\n\0'
else:
    STRPIPEESCRITA = TONAME = '/tmp/audacity_script_pipe.to.' + str(os.getuid())
    STRPIPELEITURA = FROMNAME = '/tmp/audacity_script_pipe.from.' + str(os.getuid())
    EOL = '\n'


def _start_thread_escrita():
    """Inicia a thread de escrita no pipe."""
    global thread_escrita, STRPIPEESCRITA, PIPEESCRITA
    
    if not os.path.exists(STRPIPEESCRITA):
        sys.exit(f'PIPE de Escrita não está definido!   Certifique-se de que o Audacity esteja rodando com mod-script-pipe ativado.')
    print(f'--- pipe de escrita encontrado ---')
    # O Pipe é aberto em uma nova thread para que o aplicativo
    # não congele se o Audacity não estiver em execução.
    thread_escrita = threading.Thread(target=_abrir_pipe_escrita)
    thread_escrita.daemon = True
    thread_escrita.start()
    # Aguardar um pouco para que a conexão seja estabelecida.
    time.sleep(0.1)
    if not PIPEESCRITA:
        sys.exit('PIPE de Escrita não pôde ser aberto!   Certifique-se de que o Audacity esteja rodando e com mod-script-pipe ativado.')

def _abrir_pipe_escrita():
    """Abre o Pipe de escrita."""
    global PIPEESCRITA, STRPIPEESCRITA

    PIPEESCRITA = open(STRPIPEESCRITA, 'w', encoding='utf-8')
    print(f'--  pipe de escrita foi aberto')


def _start_thread_leitura():
    """Inicia a thread de leitura do pipe."""
    global thread_leitura, STRPIPELEITURA, PIPELEITURA

    if not os.path.exists(STRPIPELEITURA):
        sys.exit(f'PIPE de Leitura não está definido!   Certifique-se de que o Audacity esteja rodando com mod-script-pipe ativado.')
    print(f'--- pipe de leitura encontrado ---')
    thread_leitura = threading.Thread(target=_abrir_pipe_leitura)
    thread_leitura.daemon = True
    thread_leitura.start()

def _abrir_pipe_leitura():
    """Abre o Pipe de leitura."""
    global PIPELEITURA, STRPIPELEITURA
    
    PIPELEITURA = open(STRPIPELEITURA, 'rt', encoding='utf-8')
    print(f'--  pipe de leitura foi aberto')

_start_thread_escrita()
# Aguardar um pouco para que a conexão seja estabelecida.
time.sleep(0.1)
_start_thread_leitura()
# Aguardar um pouco para que a conexão seja estabelecida.
time.sleep(0.1)
#sys.exit('finalizando script e saindo dos testes iniciais')

def send_command(command):
    """Envia um comando ao Audacity."""
    global PIPEESCRITA
    PIPEESCRITA.write(command + EOL)
    PIPEESCRITA.flush()


def get_response() -> str:
    """Resposta do Audacity ao comando executado."""
    global PIPELEITURA
    result = ''
    line = ''
    while True:
        result += line
        line = PIPELEITURA.readline()
        if line == '\n' and len(result) > 0:
            break
    return result


def do_command(command: str) -> str:
    """
    Envia um comando ao Audacity e retorna a resposta.

    Parameters:
        command: Comando a ser executado no Audacity

    Returns:
        Resultado da execução do comando no Audacity
    """
    send_command(command)
    response = get_response()
    return response


# Inicia a gravação do áudio no Audacity
do_command('Record2ndChoice:')

# Inicializando variáveis
gravacao_hora_inicio_obj = gravacao_hora_final_obj = datetime.now().time()
gravacao_hora_inicio_str = gravacao_hora_inicio_obj.strftime('%H:%M:%S')
gravacao_hora_final_str = gravacao_hora_inicio_str
primeirorotulo = totalderotulos = 0
listadetimestamps = []

# Calcular as configurações do primeiro rótulo a ser registrado
# O corte é definido em segmentos de 5 em 5 minutos
minutos = 4 - gravacao_hora_inicio_obj.minute % 5
segundos = 60 - gravacao_hora_inicio_obj.second

if segundos == 60:
    # Vai gerar um incremento de minuto no timestamp do rótulo
    minutos += 1
    segundos = 0

# Calcular o valor, em segundos, do primeiro rótulo
# Esse valor deve ser o complemento, em segundos, até o próximo valor arredondado
# para 5 minutos (tamanho do intervalo padrão adotado pela SAVID).
primeirorotulo = minutos * 60 + segundos
if primeirorotulo == 0:
   primeirorotulo = INTERVALO

# Log de controle no terminal para informar ao usuário que a gravação iniciou
print(f'CTRL >>> A gravação iniciou às {gravacao_hora_inicio_obj}')

# Finalizada toda a inicialização necessária para o funcionamento do script
# #    Gerar interface com usuário, e iniciar o registro dos rótulo


def ui():
    """Controla a interrupção do script e da gravação no Audacity"""
    global gravacao_hora_final_obj, gravacao_hora_final_str
    while True:
        mensagem = input(
            "Para interromper o script, tecle 'S' e pressione [ ENTER ]: "
        )
        if mensagem.lower() == 's':
            # Parar a gravação no Audacity
            do_command('Stop')

            # Registrar o final da gravação na variável global 'gravacao_hora_final_obj'; e
            # Converter o final da gravação em string para usar na interface com usuário
            gravacao_hora_final_obj = datetime.now().time()
            gravacao_hora_final_str = gravacao_hora_final_obj.strftime(
                '%H:%M:%S'
            )

            # Inserir o timestamp nos rótulos que foram criados no Audacity
            carimbar(listadetimestamps)
            break
        else:
            # Usuário pressionou qualquer tecla diferente de 's' no terminal
            # Desconsiderar comando e continuar executando modelo para criar rótulos no áudio
            pass
    return


def rotuladora():
    """Calcula os rótulos e registra no Audacity"""
    global totalderotulos, listadetimestamps
    global INTERVALO, SOBREPOSICAO

    ponteiro1 = time.time()
    acumulador = 0
    while thread1.is_alive():
        ponteiro2 = time.time()
        if acumulador == 0:     # Registrar o primeiro rótulo no Audacity
            if ponteiro2 - ponteiro1 >= primeirorotulo:
                tmp = datetime.now().time().strftime('%H:%M:%S')
                listadetimestamps.append(gravacao_hora_inicio_str)
                # Registra o rótulo no Audacity
                do_command('AddLabelPlaying')
                ponteiro1 = ponteiro2
                acumulador += 1
                # Incrementa o total de rótulos registrados (variável global do script)
                totalderotulos += 1
                pass
        else:                   # Registrar demais rótulos no Audacity, a cada INTERVALO segundos
            if ponteiro2 - ponteiro1 >= INTERVALO:
                listadetimestamps.append(tmp)
                tmp = datetime.now().time().strftime('%H:%M:%S')
                # Registra o rótulo no Audacity
                do_command('AddLabelPlaying')
                ponteiro1 = ponteiro2
                acumulador += 1
                # Incrementa o total de rótulos registrados (variável global do script)
                totalderotulos += 1
                continue
            else:
                pass
    return


def carimbar(listaderotulos: list):
    """
    Função executada após interrupção da gravação Audacity, para organizar os rótulos
    registrados durante a execução do script.

    Parameters:
        listaderotulos: Uma ista contendo os rótulos registrados durante a execução
    """
    # Recuperar informações do Audacity sobre o áudio gravado
    meu_json = do_command('GetInfo: Type=Clips Format=JSON')

    # Tratamento e limpeza das informações recuperadas do Audacity
    meu_json_str = meu_json.replace('BatchCommand finished: OK', '')
    str_temp = meu_json_str.replace('[', '')
    str_temp = str_temp.replace(']', '')
    meu_dicionario = dict(json.loads(str_temp))

    # Registra o tempo total do áudio informado pelo Audacity
    duracaodoaudio = meu_dicionario['end']

    # Registrar a data de hoje em string
    hoje_obj = datetime.now()
    hoje_str = hoje_obj.strftime('%Y-%m-%d')

    if duracaodoaudio < primeirorotulo or len(listaderotulos) == 0:
        rotulo_str = f"{ROTULO}-[{hoje_str}_{gravacao_hora_inicio_str.replace(':', '_')}]-000"

        cmd_audacity = f'SetLabel: Label=0 Text={rotulo_str} Start=0'
        if duracaodoaudio < primeirorotulo: cmd_audacity = f'{cmd_audacity} End={duracaodoaudio}'
        else: cmd_audacity = f'{cmd_audacity} End={primeirorotulo}'

        do_command('AddLabel')
        do_command(cmd_audacity)
        return

    if len(listaderotulos) == 1:
        # Mover cursor para o final da trilha
        do_command('CursTrackEnd:')
        # Criar o último rótulo
        do_command('AddLabel')
        rotulo_str = f"{ROTULO}-[{hoje_str}_{gravacao_hora_inicio_str.replace(':', '_')}]-000"
        cmd_audacity = f'SetLabel: Label=0 Text={rotulo_str} Start=0 End={primeirorotulo}'
        do_command(cmd_audacity)

        str_t1 = listaderotulos[0]
        hora_t1 = datetime.strptime(str_t1, '%H:%M:%S')
        t1 = timedelta(
            hours=hora_t1.hour, minutes=hora_t1.minute, seconds=hora_t1.second
        )
        t2 = timedelta(seconds=INTERVALO)
        t3 = t1 + t2
        rotulo_str = f'{ROTULO}-[{hoje_str}_{t3}]-001'.replace(':', '_')
        
        if primeirorotulo <= SOBREPOSICAO: cmd_audacity = f'SetLabel: Label=1 Text={rotulo_str} Start={primeirorotulo} End={duracaodoaudio}'
        else: cmd_audacity = f'SetLabel: Label=1 Text={rotulo_str} Start={primeirorotulo-SOBREPOSICAO} End={duracaodoaudio}'

        do_command(cmd_audacity)
        return
    
    # Lista que contém comandos para alterar os rótulos no Audacity
    listaaudacity = []
    # Lista para criar arquivo de rótulos exportados
    listaexportacao = []
    controle = 0
    for i in range(len(listaderotulos)):
        controle += 1
        rotulo_str = f"{ROTULO}-[{hoje_str}_{str(listaderotulos[i]).replace(':', '_')}]-{i:003}"
        if i == 0:
            cmd_audacity = f"SetLabel: Label=0 Text={rotulo_str} Start=0 End={primeirorotulo}"
            cmd_exportar = f'0.000000\t{primeirorotulo:,.6f}\t{rotulo_str}'
        else:
            ptr_inicio = primeirorotulo + INTERVALO * (i - 1)
            ptr_fim = min(ptr_inicio + INTERVALO, duracaodoaudio)
            if primeirorotulo <= SOBREPOSICAO:
                # Não descontar valor da sobreposição, pois a sobreposição é maior que o primeiro rótulo
                cmd_audacity = f"SetLabel: Label={i} Text={rotulo_str} Start={ptr_inicio} End={ptr_fim}"
                cmd_exportar = f"{ptr_inicio:,.6f}\t{ptr_fim:,.6f}\t{rotulo_str.replace(':', '_')}"
            else:
                cmd_audacity = f"SetLabel: Label={i} Text={rotulo_str} Start={ptr_inicio-SOBREPOSICAO} End={ptr_fim}"
                cmd_exportar = f"{ptr_inicio-SOBREPOSICAO:,.6f}\t{ptr_fim:,.6f}\t{rotulo_str.replace(':', '_')}"
        listaaudacity.append(cmd_audacity)
        listaexportacao.append(cmd_exportar)
        # Enviar comando ao Audacity para modificar o rótulo
        do_command(cmd_audacity)

    str_t1 = listaderotulos[len(listaderotulos) - 1]
    hora_t1 = datetime.strptime(str_t1, '%H:%M:%S')
    t1 = timedelta(
        hours=hora_t1.hour, minutes=hora_t1.minute, seconds=hora_t1.second
    )
    t2 = timedelta(seconds=INTERVALO)
    t3 = t1 + t2

    # Calcular o último rótulo, que não chegou a fechar em 5 minutos
    ult_sobreposicao = ptr_fim - SOBREPOSICAO
    # Preparar string do comando que será enviado ao Audacity
    rotulo_str = f'{ROTULO}-[{hoje_str}_{t3}]-{len(listaderotulos):003}'

    # Envia comando ao Audacity para selecionar o trecho do áudio para o último rótulo
    do_command(f'Select: Start={ult_sobreposicao} End={duracaodoaudio}')
    # Envia comando ao Audacity para criar o último rótulo
    do_command('AddLabel')
    # Envia comando ao Audacity para modificar o rótulo adicionado
    do_command(
        f"SetLabel: Label={len(listaderotulos)} Text={rotulo_str.replace(':', '_')}"
    )
    # Envia comando ao Audacity para não selecionar nenhum trecho do áudio gravado
    do_command('SelectNone')

    # Registro dos comando enviados ao Audacity em Log para controle posterior e tratamento de erros
    cmd_audacity = f"SetLabel: Label={len(listaderotulos)} Text={rotulo_str.replace(':', '_')} Start={ult_sobreposicao} End={duracaodoaudio}"
    cmd_exportar = f"{ult_sobreposicao:,.6f}\t{duracaodoaudio:,.6f}\t{rotulo_str.replace(':', '_')}"
    listaaudacity.append(cmd_audacity)
    listaexportacao.append(cmd_exportar)
    logfile = f"{os.path.dirname(__file__)}/PyControl-{hoje_str}_{gravacao_hora_inicio_str.replace(':', '_')}.txt"
    with open(logfile, 'w', encoding='utf-8') as arquivo:
        for tarefa in listaexportacao:
            arquivo.write(tarefa)
            arquivo.write('\n')
    arquivo.close
    return


thread1 = Thread(target=ui)
thread2 = Thread(target=rotuladora)

thread1.start()
thread2.start()

while thread1.is_alive() or thread2.is_alive():
    pass

# Log de controle para registrar o horário que a gravação finalizou
print(f'CTRL >>> A gravação finalizou às {gravacao_hora_final_str}')
sys.exit('Script finalizado.')