# PCS3643 - Laboratório de Engenharia de Software

O projeto da disciplina é um sistema para leilões online. O deploy foi feito utilizando **Heroku** e pode ser acessado no link [https://projetoleilao.herokuapp.com/](https://projetoleilao.herokuapp.com/)

Os diagramas e relatórios produzidos ao longo do curso se encontram na pasta **Documentação**.

## Pasta Screenshots

Para esclarecer o fluxo de usuário no projeto e criar uma memória visual do projeto, adicionamos uma pasta **Screenshots** contendo capturas de tela da versão atual do projeto em funcionamento.

![Homepage](Screenshots/homepage.png)

## O que foi implementado no projeto ?

### Funcionalidades

- Signup de usuários Leiloeiros e Clientes

- Login e Logout de usuários

#### Para usuário cliente

- Ofertar lote de produto (vendedor paga taxa de comissão)

- Realizar lance em lote de produto (saldo de compradores e vendedores envolvidos é atualizado) 

- Atualizar saldo bancário

- Conferir saldo bancário

#### Para usuário Leiloeiro

- Gerar Relatório de Faturamento

- Gerar Relatório de Desempenho

- Liberar Lote para leilão

- Finalizar Leilão

## Referências e recursos importantes

- Livro **Django for Beginners, William S. Vincent**

- [User Authentication in Django](https://docs.djangoproject.com/en/3.2/topics/auth/)

- [How to raise form validation errors](https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#overriding-the-clean-method)

- [Linking user model to a custom profile model](https://prog.world/one-to-one-relationship-linking-a-user-model-to-a-custom-profile-model-in-django/)

- [Making database queries in Django](https://docs.djangoproject.com/en/3.2/topics/db/queries/)
