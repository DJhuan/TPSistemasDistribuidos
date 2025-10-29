# Têmis
Repositório do trabalho prático de Sistemas Distribídos, envolvendo RAG, agentes de IA e segurança.

## Descriçao do projeto

O Têmis é um sistema distribuído baseado em RAG (Retrieval-Augmented Generation) desenvolvido para auxiliar a Comp Júnior — empresa júnior da UFLA — na análise de ações e ocorrências internas, conforme suas normas, estatutos e manuais de conduta.

O projeto foi desenvolvido na disciplina de Sistemas Distribuídos, e tem como objetivo aplicar conceitos de arquitetura distribuída, segurança, conteinerização e integração entre microserviços, unindo tecnologia de IA generativa com recuperação inteligente de informações.

De forma geral, o sistema permite que um usuário descreva uma ação ou situação ocorrida na empresa. A partir dessa descrição, o Têmis analisa os documentos normativos da Comp Júnior para identificar:

- Como a ação se relaciona com as regras e políticas internas;
- Quais medidas ou procedimentos devem ser tomados de acordo com essas normas.

Para isso, o Têmis utiliza uma arquitetura composta por diferentes componentes interligados:

- Um frontend, onde o usuário insere a descrição da ocorrência;
- Uma API central, responsável por orquestrar as comunicações entre os serviços;
- Um módulo RAG, que realiza a busca dos trechos mais relevantes em um banco vetorial de normas e documentos;
- Um LLM (Large Language Model), que interpreta o contexto e gera uma resposta detalhada e orientada conforme as regras institucionais.

Através dessa integração, o sistema entrega respostas contextualizadas, consistentes e alinhadas às diretrizes internas, funcionando como um assistente de conformidade normativa inteligente.

## Descrição da arquitetura
![Imagem da Arquitetura](https://github.com/DJhuan/TPSistemasDistribuidos/blob/main/T%C3%AAmis%20-%20Sistemas%20Distribu%C3%ADdos.jpg)
  
### Front-End
Módulo utilizado pelo usuário (Membro da empresa) para receber auxílio de como a como a conduta pode ser avaliada/penalizada.

### API-Gateway
Módulo responsável por coordenar requisições do Front-End, solicitando partes interessadas da documentação ao RAG, enviando a descrição da conduta e documentação para o LLM e, por fim, retornando uma resposta ao usuário.
Além disso, é responsabilidade desta API autenticar o usuário e gerar LOGs de acessos ao sistema.

### RAG
Módulo de Recuperação Generativa Aumentada, responsável por realizar embedding dos documentos (gerar representações vetoriais de uma frase ou palavra), armazenar estas informações no banco de dados vetorial e permitir a consulta por similaridade a partir de um prompt de entrada. A saída são os trechos da fonte mais relevante para análise feita pelo LLM.

### LLM
Módulo de consulta a um grande modelo de linguagem. Ele recebe o promp de entrada (dado pelo usuário), saída da busca do rag e prompt do sistema (instruções de como o agente de IA deve se comportar e utilizar os outros dados fornecidos). O retorno (enviado para API) descreve como as ações se relacionam com as regras e políticas da empresa e como prosseguir a partir disso.

## Justificativa da arquitetura

A arquitetura do sistema foi projetada com base em princípios de modularidade, escalabilidade e distribuição de responsabilidades entre diferentes componentes. O objetivo é permitir que a aplicação realize análises automáticas de conduta e sugestão de ações corretivas de forma eficiente, segura e facilmente expansível.

O sistema é composto por dois agentes principais — o Processador de Conduta (Agente 1) e o Sugeridor de Ação (Agente 2) — que se comunicam por meio de uma API central. Essa abordagem segue o modelo de microsserviços, favorecendo a independência de cada módulo e possibilitando o desenvolvimento paralelo pela equipe.

A comunicação entre os módulos é feita via API, que atua como intermediária entre o frontend, os agentes e o módulo RAG. O uso de uma API facilita a integração com diferentes interfaces e garante um ponto único de acesso às funcionalidades do sistema, mantendo o acoplamento baixo e a coesão alta.

A escolha pela arquitetura RAG (Retrieval-Augmented Generation) se justifica pela necessidade de interpretar descrições de ocorrências e associá-las com documentos de conduta. O RAG consulta uma base vetorial com embeddings gerados a partir de documentos da Comp Júnior, permitindo que o sistema encontre trechos relevantes antes de enviar o prompt final ao modelo de linguagem (LLM). Essa combinação aumenta a precisão das respostas e garante que o chatbot utilize informações reais e atualizadas da documentação, reduzindo o risco de alucinações por parte do modelo.

Foram definidos bancos de dados distintos para diferentes propósitos:

- DB RAG: contém os embeddings e documentos de conduta usados nas consultas;
- Banco de usuários: mantém informações de autenticação e controle de acesso.


Essa separação segue o princípio da especialização de dados, evitando sobrecarga de um único repositório e permitindo otimizações específicas.
