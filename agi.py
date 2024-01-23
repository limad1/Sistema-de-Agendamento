
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Rede de Saude Vitality Health Solutions
# Versao FUNCIONAL

# Importamos as bibliotecas:
import sys
import mysql.connector
from asterisk.agi import *
from datetime import datetime

# Cria uma instncia da interface AGI
agi = AGI()

# Funcao para formatar o CPF
def format_cpf(cpf):
    return '{0}.{1}.{2}-{3}'.format(cpf[:3], cpf[3:6], cpf[6:9], cpf[9:])

# Funcao para formatar a data de nascimento
def format_birthdate(birthdate):
    return '{0}-{1}-{2}'.format(birthdate[4:], birthdate[2:4], birthdate[:2])

# Funcao para formatar a data
def format_data(date_str):
    return '{0}-{1}-{2}'.format(date_str[4:], date_str[2:4], date_str[:2])

# Funcao para obter a saudao
def get_greeting():
    current_hour = datetime.now().hour
    saudacao=''
    if 6 <= current_hour < 12:
        saudacao = "bom-dia"
    elif 12 <= current_hour < 18:
        saudacao = "boa-tarde"
    else:
        saudacao = "boa-noite"
        
    agi.verbose("Saudacao %s" % saudacao)
    
    agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/%s" % saudacao)
    agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/A01-seja-bem-vindo")

# Funcao para obter os dados do cliente
def obter_dados_do_cliente():
    agi.verbose("Obetendo dados do cliente.")
    agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/A02-digite-cpf")
    agi.stream_file("/var/lib/asterisk/sounds/beep")
    cpf = ''
    for _ in range(11):
        digit = agi.wait_for_digit(-1)
        cpf += str(digit)
    agi.verbose("Digitos = %s" % cpf)
    cpf = format_cpf(cpf)

    agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/A03-digite-data")
    agi.stream_file("/var/lib/asterisk/sounds/beep")
    birthdate = ''
    for _ in range(8):
        digit = agi.wait_for_digit(-1)
        birthdate += str(digit)
    agi.verbose("Digitos = %s" % birthdate)
    birthdate = format_birthdate(birthdate)

    return cpf, birthdate

# Funcao para selecionar uma op
def selecione_as_opcoes(options, prompt):
    agi.verbose("Selecionando opcoes")
    for option in options:
        agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/esp_med_Op/%s" % option, escape_digits='')
    while True:
        agi.stream_file(prompt)
        option = agi.get_data('/var/lib/asterisk/sounds/beep', timeout=60000, max_digits=1)
        if option.isdigit() and 1 <= int(option) <= len(options):
            return options[int(option) - 1]
        else:
            agi.stream_file('Opcao invalida. Tente novamente.')
            agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/A07-op-invalida")
    
# Funcao para verificar consultas ja marcadas    
def consultar_consultas(conexao, user_id):
    agi.verbose("Consultando agendamento.")
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM agendamento WHERE id_usuario = %s", (user_id,))
        consultas = cursor.fetchall()
        if consultas:
            agi.verbose("Consultas encontradas:")
            agi.verbose("Consultas:%s" % consultas)
            for consulta in consultas:
                especialidade = consulta[2]
                medico = consulta[3]
                data = consulta[4]
                data_str = str(data)
                # Divida a data em partes
                ano, mes, dia = data_str.split("-")
                agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/A12-Sua_consulta_esta_ma")
                agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/esp_med_con/%s" % especialidade)
                agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/com")
                agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/esp_med_con/%s" % medico)
                agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/dia")
                agi.say_number(dia)
                agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/do")
                agi.say_number(mes)
                agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/de")
                agi.say_number(ano)
            return True
        else:
            agi.verbose("Nenhuma consulta encontrada para o usuario.")
            agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/A13-Nao_encontramos_nenh")
            return None
    except Exception as e:
        agi.verbose("Erro ao consultar consultas:%s" % e)

# Funcao para para cancelar consultas       
def cancelar_consulta(conexao, user_id):
    agi.verbose("Cancelamento de consultas.")
    try:
        cursor = conexao.cursor()
        agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/A18-Informa_a_data_da")
        date_str = agi.get_data('/var/lib/asterisk/sounds/beep', timeout=60000, max_digits=8)
        data_para_cancelar = format_data(date_str)
        cursor.execute("SELECT * FROM agendamento WHERE id_usuario = %s AND data_consulta = %s", (user_id, data_para_cancelar))
        consultas = cursor.fetchall()
        if consultas:
            cursor.execute("DELETE FROM agendamento WHERE id_usuario = %s AND data_consulta = %s", (user_id, data_para_cancelar))
            conexao.commit()
            agi.verbose("Consulta cancelada com sucesso.")
            agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/A15-Seu_pedido_de_cancel")
        else:
            agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/A16-Ops_algo_deu_errado")
    except Exception as e:
        agi.verbose("Erro ao cancelar consulta:{}".format(e))
        agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/A16-Ops_algo_deu_errado")

# Funo para marcar uma consulta
def marcar_consulta(conexao, user_id, especialidade, medico, dia_atendimento):
    agi.verbose("Marcando consulta.")
    try:
        # Cria um cursor para o banco de dados
        cursor = conexao.cursor()
        # Define a consulta como uma tupla contendo o ID do usurio, a especialidade, o mdico e a data do atendimento
        consulta = (user_id, especialidade, medico, dia_atendimento)
        # Define a consulta SQL para inserir a consulta no banco de dados
        consulta_query = "INSERT INTO agendamento (id_usuario, especialidade, medico, data_consulta, confirmado) VALUES (%s, %s, %s, %s, TRUE)"
        # Executa a consulta SQL
        cursor.execute(consulta_query, consulta)
        # Salva as alteraes no banco de dados
        conexao.commit()
        # Informa ao usurio que a consulta foi marcada com sucesso
        agi.verbose("Consulta marcada com sucesso.")
        agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/A10-Parabens_sua_consult")
    except Exception as e:
        #Se ocorrer um erro ao tentar marcar a consulta, imprime uma mensagem de erro
        agi.verbose("Erro ao marcar consulta:{}".format(e))
        agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/Ops_algo_deu_errado")
        
# Funcao para verificar se ha vagas disponveis
def encaixe_disponivel(user_id, especialidade, medico, dia_atendimento, conexao):
    # Cria um cursor para o banco de dados
    agi.verbose("Verificando encaixe diponivel.")
    try:
        cursor = conexao.cursor()
        agi.verbose("cursor conectado")

        # Verifica se o usuario tem uma consulta marcada para a data escolhida
        agi.verbose(user_id, dia_atendimento)        
        query_teste = "SELECT * FROM agendamento WHERE id_usuario = {0} AND data_consulta = {1}".format(user_id, dia_atendimento)
        cursor.execute(query_teste)
        result_teste = cursor.fetchone()
        if result_teste is not None:
            return False
        try:
            #query_teste2 = "SELECT * FROM agendamento WHERE especialidade = {0} AND medico = {1} AND data_consulta = {2}".format(especialidade, medico, dia_atendimento)
            query_teste2 = "SELECT * FROM agendamento WHERE id_usuario = {0} AND data_consulta = {1}".format(user_id, dia_atendimento)

            cursor.execute(query_teste2)
            
            result3 = cursor.fetchone()

        except Exception as err:
            agi.verbose('ERROOO', err)
            return False
        
        return True
    except mysql.connector.Error as err:
        agi.verbose("Erro MySQL em encaixe_disponivel: {}".format(err))
        return False
    except Exception as e:
        agi.verbose("Erro em encaixe_disponivel: {}".format(e))
        return False
    finally:
        if cursor:
            cursor.close()


# Funcao para obter informacoes sobre a consulta
def obter_informacoes_do_compromisso(conexao, user_id):
    especialidades = ['Cardiologia','Dermatologia','Endocrinologia', 'Ginecologia','Neurologia','Otorrinolaringologia','Clinico_Geral']
    medicos_por_especialidade = {
        'Cardiologia': ['Dr_Anielton_Santiago','Dra_Marina_Correa'],
        'Dermatologia': ['Dr_Rafael_Costa','Dra_Juliana_Silva'],
        'Endocrinologia': ['Dr_Pedro_Lima','Dra_Ana_Clara'],
        'Ginecologia': ['Dr_Joao_Paulo', 'Dra_Fernanda_Oliveira'],
        'Neurologia': ['Dr_Gabriel_Santos', 'Dra_Camila_Rocha'],
        'Otorrinolaringologia': ['Dr_Teobaldo_Medeiros', 'Dra_Beatriz_Martins'],
        'Clinico_Geral': ['Dr_Leonardo_Araujo', 'Dra_Sara_Maria']
    }

    especialidade = selecione_as_opcoes(especialidades, "/var/lib/asterisk/sounds/pt_BR/projeto/dig_opc")
    medicos = medicos_por_especialidade[especialidade]
    medico = selecione_as_opcoes(medicos, "/var/lib/asterisk/sounds/pt_BR/projeto/dig_opc")
    while True:
        agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/dig_data_cons")
        date_str = agi.get_data('/var/lib/asterisk/sounds/beep', timeout=10000, max_digits=8)
        dia_atendimento = format_data(str(date_str))
        try:
            if encaixe_disponivel(user_id, especialidade, medico, dia_atendimento, conexao):
                #agi.verbose("Dentro if do encaixe_disponivel")
                return especialidade, medico, dia_atendimento
            else:
                agi.verbose("Limite de consultas atingido para esta especialidade e medico. Escolha outra data.")
                agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/A19-Limite_de_consultas")
        except Exception as e:
            agi.verbose("Erro em encaixe_disponivel: {}".format(e))

# Funo para verificar se o cliente est no banco de dados
def verificar_cliente_no_banco(cpf, birthdate, conexao):
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM users WHERE cpf = %s AND data_nascimento = %s", (cpf, birthdate))
        user = cursor.fetchone()
        if user is not None:
            agi.verbose("Usuario encontrado!")
            return user
        else:
            agi.verbose("Usuario nao encontrado.")
            return None
    except Exception as e:
        agi.verbose("Erro ao verificar o cliente no banco de dados: {e}")
        return None

# Funo principal
def main(agi):
    try:
        agi.verbose("Script AGI iniciado com sucesso")
        conexao = mysql.connector.connect(user='usuário', passwd='senha', host='IP', db='banco')
        agi.verbose("Conexao com o banco de dados estabelecida com sucesso!")
        get_greeting()
        cpf, birthdate = obter_dados_do_cliente()
        agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/A04-seus-dados")
        user_id=''  
        if cpf and birthdate:
            user = verificar_cliente_no_banco(cpf, birthdate, conexao)
            if user:
                user_id = user[0]
                agi.verbose("Usuario encontrado! ID: %s" % user_id)
                agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/A05-cadrastro-enc")
            else:
                agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/A08-Ops-dados-nao")
                conexao.close()
                agi.verbose("Conexao com o banco de dados encerrada.")
                agi.hangup()               

        while True:
            agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/A06-op-desejada")
            opcao = agi.get_data('/var/lib/asterisk/sounds/beep', timeout=3000, max_digits=1)
            if opcao == "1":
                user = verificar_cliente_no_banco(cpf, birthdate, conexao)
                if user:
                    user_id = user[0]
                    especialidade, medico, dia_atendimento = obter_informacoes_do_compromisso(conexao, user_id)
                    #agi.verbose("Dados de consulta: {0},{1},{2},{3}".format(user_id,especialidade,medico,dia_atendimento))
                    if especialidade and medico and dia_atendimento:
                        agi.verbose("CHEGOU NA MARCACAO")
                        marcar_consulta(conexao, user_id, especialidade, medico, dia_atendimento)

            elif opcao == "2":
                user = verificar_cliente_no_banco(cpf, birthdate, conexao)
                if user:
                    user_id = user[0]
                    consultar_consultas(conexao, user_id)

            elif opcao == "3":
                user = verificar_cliente_no_banco(cpf, birthdate, conexao)
                if user:
                    user_id = user[0]
                    consultas = consultar_consultas(conexao, user_id)
                    if consultas:
                        cancelar_consulta(conexao, user_id)
                    else:
                        agi.verbose("Nenhuma consulta encontrada para o usurio.")
                        agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/A13-Nao_encontramos_nenh")

            elif opcao == "0":
                agi.verbose("Saindo do Sistema de Agendamento. Ate logo!")
                agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/A09-foi-um-prazer")
                break

            else:
                agi.verbose("Opcao invalida. Tente novamente.")
                agi.stream_file("/var/lib/asterisk/sounds/pt_BR/projeto/A07-op-invalida")

    except mysql.connector.Error as err:
        agi.verbose("Erro no MySQL: {}".format(err))
    except AGIError as e:
        agi.verbose("Erro AGI: {}".format(e))
    except Exception as e:
        agi.verbose("Erro não especificado: {}".format(e))
    except:
        agi.verbose("ERRO....: {sys.exc_info()[0]}")

    finally:
        if conexao:
            conexao.close()
            agi.verbose("Conexao com o banco de dados encerrada.")

if __name__ == '__main__':
    main(agi)
