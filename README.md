# **Têmis**

Repositório do trabalho prático de Sistemas Distribídos, envolvendo RAG, agentes de IA e segurança.

## Descrição do projeto

O *Têmis* é um sistema distribuído baseado em RAG (Retrieval-Augmented Generation) desenvolvido para auxiliar a Comp Júnior — empresa júnior da UFLA — na análise de ações e ocorrências internas, conforme suas normas, estatutos e manuais de conduta.

O projeto foi desenvolvido na disciplina de Sistemas Distribuídos, e tem como objetivo aplicar conceitos de arquitetura distribuída, análise de ameaça, conteinerização e integração entre microserviços, unindo tecnologia de IA generativa com recuperação inteligente de informações.

De forma geral, o sistema permite que um usuário descreva uma ação ou situação ocorrida na empresa. A partir dessa descrição, o *Têmis* analisa os documentos normativos da Comp Júnior para identificar:

- Como a ação se relaciona com as regras e políticas internas;
- Quais medidas ou procedimentos devem ser tomados de acordo com essas normas.

Para isso, o *Têmis* utiliza uma arquitetura composta por diferentes componentes interligados:

- Um frontend, onde o usuário insere a descrição da ocorrência;
- Uma API central, responsável por orquestrar as comunicações entre os serviços;
- Um controlador para gerenciar uma requisição em processo de rede separado;
- Um módulo RAG, que realiza a busca dos trechos mais relevantes em um banco vetorial de normas e documentos;
- Um LLM (Large Language Model), que interpreta o contexto e gera uma resposta detalhada e orientada conforme as regras institucionais.

Através dessa integração, o sistema entrega respostas contextualizadas, consistentes e alinhadas às diretrizes internas, funcionando como um assistente de conformidade. A aplicação está inteiramente implementada usando a ferramenta Docker, com o objetivo de implementar um sistema que é de fato distribuído e com possibilidade de orquestração.

## Descrição da arquitetura

![Imagem da Arquitetura](https://github.com/DJhuan/TPSistemasDistribuidos/blob/main/Imagens/T%C3%AAmis%20-%20Sistemas%20Distribu%C3%ADdos.jpg)

### Front-End

Módulo utilizado pelo usuário (Membro da empresa) para receber auxílio de como a como a conduta pode ser avaliada/penalizada.

### API-Gateway

Módulo responsável por coordenar requisições do Front-End encaminhando-as para o controller.

### Controller

Módulo responsável por orquestrar a lógica de negócio do sistema, coordenando o fluxo sequencial entre a recuperação de documentos (RAG) e o processamento inteligente (LLM) para gerar a análise de conduta final e as sugestões de ação.

### RAG

Módulo de Recuperação Generativa Aumentada, responsável por realizar embedding dos documentos (gerar representações vetoriais de uma frase ou palavra), armazenar estas informações no banco de dados vetorial e permitir a consulta por similaridade a partir de um prompt de entrada. A saída são os trechos da fonte mais relevante para análise feita pelo LLM.

### LLM

Módulo de consulta a um grande modelo de linguagem. Ele recebe o promp de entrada (dado pelo usuário), saída da busca do rag e prompt do sistema (instruções de como o agente de IA deve se comportar e utilizar os outros dados fornecidos). O retorno (enviado para o Controller) descreve como as ações se relacionam com as regras e políticas da empresa e como prosseguir a partir disso.

## Justificativa da arquitetura

A arquitetura do sistema foi projetada com base em princípios de modularidade, escalabilidade e distribuição de responsabilidades entre diferentes componentes. O objetivo é permitir que a aplicação realize análises automáticas de conduta e sugestão de ações corretivas de forma eficiente, segura e facilmente expansível.

O sistema é composto por dois agentes principais — o Processador de Conduta (Agente 1) e o Sugestor de Ação (Agente 2) — que se comunicam por meio de uma API central. Essa abordagem segue o modelo de microsserviços, favorecendo a independência de cada módulo e possibilitando o desenvolvimento paralelo pela equipe.

O *Processador de Conduta* tem como responsabilidade principal gerar os embeddings (representações vetoriais) dos textos dos pdf's disponibilizados e realizar a busca de similaridade. Para isso, nós utilizamos o Ollama agindo como servidor em um container, com o *nomic-embed-text* atuando na geração dos embeddings. A busca semântica é feita gerando um embedding da query original, e retornando os chunks mais semelhantes em relação a ela.

Para armazenar os embeddings dos documentos, utilizamos: 

- Bando de Dados Vetorial FAISS: contém os embeddings e documentos de conduta usados nas consultas;

O *Sugestor de Ação* deve receber o contexto retornado pelo *Processador de Conduta* junto da query original, somadas à um prompt de sistema definido no código. Este texto contatenado é enviado para a API do Gemini, que usa o modelo *google-gla:gemini-2.5-flash*  para analisar o ocorrido e as normas da empresa.

A comunicação entre os módulos é feita via API, que atua como intermediária entre o frontend, os agentes e o módulo RAG. O uso de uma API facilita a integração com diferentes interfaces e garante um ponto único de acesso às funcionalidades do sistema, mantendo o acoplamento baixo e a coesão alta.

A escolha pela arquitetura RAG (Retrieval-Augmented Generation) se justifica pela necessidade de interpretar descrições de ocorrências e associá-las com documentos de conduta. O RAG consulta uma base vetorial com embeddings gerados a partir de documentos da Comp Júnior, permitindo que o sistema encontre trechos relevantes antes de enviar o prompt final ao modelo de linguagem (LLM). Essa combinação aumenta a precisão das respostas e garante que o chatbot utilize informações reais e atualizadas da documentação, reduzindo o risco de alucinações por parte do modelo.

## Modelagem de Ameaças

![Arquitetura pré-ameaças](https://github.com/DJhuan/TPSistemasDistribuidos/blob/main/Imagens/temis_pre_ameaca.jpg)

![Tabela de ameaças](https://github.com/DJhuan/TPSistemasDistribuidos/blob/main/Imagens/tabela_de_ameacas.png)

## Como utilizar os contêineres

1. Crie o arquivo .env na pasta root com as variáveis de ambiente necessárias. No arquivo *example.env*, substitua a chave de API de exemplo pela sua chave de API do Gemini, e depois mude o nome do arquivo para apenas *.env*.

2. Na pasta */retriever/pdfs* (crie uma, se não existir), insira os pdf's a serem analisados pelo RAG. Nós não deixamos nossos documentos disponíveis, pois eles são privados à Comp Júnior.

3. Em seguida, execute o comando:

```bash
docker compose up --build
```

4. Acesse o [front-end](http://localhost:8501/) para realizar suas consultas!

## Possíveis melhorias

1. Testar outras maneiras de gerar embeddings dos documentos. Procurar por modelos usados em meio jurídico ou compliance;
2. Filtrar o texto inicial do usuário usando outro LLM;
3. Criar uma forma de estruturar os documentos PDF antes de alimentá-los ao RAG;
4. Criar um formulário estruturado para que o usuário preencha os dados da ocorrência, ao invés de um campo de texto livre;
5. Sistema de autenticação;
6. Implementar as medidas de mitigação da modelagem de ameaças;
7. Testar outros llms;
8. Conseguir mais documentos para usar na consulta;
9. Utilizar um orquestrador para gerenciar os contêineres (Kubernetes, Docker Swarm ou similar);
10. Fazer o sistema rodar em produção (usando serviços de nuvem e outros);
11. Implementar usando outras arquiteturas;

## Contribuidores
- Matheus Piassi de Carvalho
- Jhuan Carlos Sabaini Dassie
- Marina Hermógenes Siqueira
- Bernardo Coelho Pavani Marinho