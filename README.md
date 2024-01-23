# Sistema-de-Agendamento

## Projeto: Sistema de Agendamento - Vitality Health Solutions


Olá, pessoal! Hoje eu quero compartilhar com vocês um projeto muito interessante que eu e meus colegas desenvolvemos na disciplina de Implantação de Serviços de VoIP, ministrada pelo professor Teobaldo Adelino Dantas de Medeiros. Trata-se de um sistema de agendamento para a Vitality Health Solutions, uma empresa(ficticia) que oferece soluções de saúde integradas e personalizadas.

O sistema consiste em um script Python que roda como um script AGI (Asterisk Gateway Interface) no servidor Asterisk, que é uma plataforma de comunicação baseada em software livre. O script permite que os usuários liguem para um número de telefone e interajam com o sistema por meio de prompts de voz. O script também se conecta a um banco de dados MySQL, usando o módulo pymysql, para consultar e atualizar as informações sobre as consultas médicas disponíveis.

O objetivo do sistema é facilitar o agendamento de consultas médicas para os clientes da Vitality Health Solutions(ficticia), permitindo que eles escolham o médico, a data e o horário desejados, sem precisar falar com um atendente humano.


## Funcionalidades

1. **Saudação Personalizada:** O script inicia cumprimentando os usuários com base na hora do dia.

2. **Obtenção de Dados do Cliente:** Solicita ao usuário o CPF e a data de nascimento, formatando adequadamente as entradas.

3. **Consulta e Marcação de Consultas:**
   - Permite ao usuário escolher entre consultar, marcar ou cancelar consultas.
   - Verifica se o usuário está no banco de dados e, em caso afirmativo, prossegue com as operações.

4. **Seleção de Especialidade e Médico:**
   - Oferece ao usuário a opção de escolher uma especialidade médica e, em seguida, um médico disponível para a consulta.

5. **Consulta de Consultas Marcadas:**
   - Exibe ao usuário as consultas médicas previamente agendadas.

6. **Cancelamento de Consultas:**
   - Permite ao usuário cancelar uma consulta marcada, após escolher a data desejada.

7. **Segurança contra SQL Injection:**
   - Utiliza parâmetros em consultas SQL para evitar vulnerabilidades de injeção de SQL.

8. **Gerenciamento de Conexão:**
   - Garante o fechamento adequado das conexões, mesmo em caso de exceções, usando a cláusula `finally`.

## Requisitos

- Python
- MySQL
- Asterisk com AGI habilitado

## Configuração

1. **Banco de Dados:**
   - Certifique-se de ter um banco de dados MySQL configurado.
   - Atualize as informações de conexão no script (`user`, `passwd`, `host`, `db`).

2. **Arquivos de Som:**
   - Configure os caminhos dos arquivos de som conforme necessário.

3. **Estrutura do Banco de Dados:**
   - Certifique-se de que o banco de dados possui as tabelas necessárias (e.g., `users`, `agendamento`).

4. **Execução:**
   - Execute o script como um script AGI no ambiente Asterisk.

## Como Usar

- Ao ligar para o sistema, siga as instruções de voz para interagir com o sistema, digitando os números correspondentes às opções desejadas.

## Notas Importantes

- Este script é fornecido como exemplo e pode precisar ser adaptado conforme os requisitos específicos do seu ambiente e aplicação.

## Conclusão

O projeto foi um grande desafio e uma ótima oportunidade de aprender sobre os conceitos e as ferramentas envolvidas na implantação de serviços de VoIP. Nós ficamos muito satisfeitos com o resultado e esperamos que ele possa ser útil para a Vitality Health Solutions(ficticia) e seus clientes. Se vocês quiserem saber mais sobre o projeto, podem acessar o código-fonte aqui no GitHub ou entrar em contato conosco pelos nossos e-mails. Obrigado pela atenção e até a próxima!

## Autores

Aluno A,
Aluno B,
Aluno C.

**Observação:** Este README assume que você está familiarizado com o ambiente Asterisk, MySQL e Python. Certifique-se de compreender as implicações de segurança ao lidar com dados sensíveis do cliente.
