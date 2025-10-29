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
<ImagemAqui>
### Front-End
Módulo utilizado pelo usuário (Membro da empresa) para receber auxílio de como a como a conduta pode ser avaliada/penalizada.

### API-Gateway
