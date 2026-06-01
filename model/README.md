# Model

## Stack

O que usei (e o que você precisa, caso queira treinar esse modelo):

- Python 3.10+
    
- CUDA/cuDNN (se tiver uma GPU NVIDIA)
    

---

Bora lá. Depois de estudar mais o problema, conversar com alguns amigos que trabalham na área, ler alguns posts no Reddit sobre redes convolucionais para encontrar padrões em imagens e chorar um pouco para o GPT, um colega me indicou usar o Dlib.
Por que o Dlib? Eu me fiz a mesma pergunta. Fui pesquisar um pouco e descobri que, diferente de um pipeline de treinamento de uma rede como uma R-CNN, por exemplo, o Dlib oferece algumas abordagens diferentes que achei bem interessantes, por sinal.
Por possuir o algoritmo MMOD com SVM (diferente do HOG + SVM), conseguimos um resultado bem interessante com um dataset pequeno. O David mostrou o treinamento de um detector de rostos com apenas 4 imagens. Como meu dataset do Waldo, naquele momento, tinha apenas 24 imagens, resolvi testar o Dlib.
Ele funcionou até que bem, mas tive dificuldade com objetos muito pequenos, pois o Dlib lida melhor com objetos maiores. Além disso, o Dlib não é uma forma muito escalável de estruturar uma rede, já que sua pipeline para objetos pequenos (menores que 80x80) se torna um desafio, principalmente em imagens maiores.
Então, depois de testar o Dlib, chorei mais um pouco no Reddit, conversei novamente com alguns amigos, e um deles me deu uma sugestão bem interessante: R-CNN.

Agora sim. Fui pesquisar um pouco sobre o pipeline da R-CNN (e logo vou explicar por que optei por uma R-CNN e não por um modelo mais moderno, como o YOLO :D).
O YOLO possui um pipeline mais focado em eficiência. Ele foi projetado principalmente para detecção em tempo real. O YOLO também tem dificuldade com imagens que possuem muito ruído (algumas digitalizações do Waldo apresentam um nível considerável de ruído).
Como, na detecção do Waldo, o foco não é velocidade, mas sim precisão, o YOLO não me pareceu a melhor opção, pelo menos com base na minha breve pesquisa. O YOLO passa apenas uma vez pelo pipeline, enquanto uma R-CNN pode executar duas etapas envolvendo a RPN (Region Proposal Network) e a Detection Head.
Esses dois estágios de refinamento da localização me permitiram obter mais precisão ao encontrar o Waldo.



Ok, eu sei que o YOLO11 e versões mais recentes reduziram bastante essa diferença. Mas eu não preciso de algo em tempo real; isso seria um caso de engenharia excessiva (overengineering).
A R-CNN é uma tecnologia madura, bem documentada e que me oferece uma ótima precisão, ainda que com um custo computacional maior. Mas esse custo não é importante neste cenário. Não estamos em um ambiente limitado nem em um sistema operacional de tempo real (RTOS), então está tranquilo. :)
Além disso, consegui encontrar um dataset maravilhoso no Roboflow com 400 imagens do Waldo. Eu lembrava que um participante havia encontrado algo semelhante durante o hackathon, então resolvi procurar também.
Era um dataset com 400 imagens, acompanhado de labels e bounding boxes, o que me permitiu treinar a R-CNN com uma precisão muito boa.

O dataset eu encontrei no Roboflow. Era um dataset no formato COCO, então essa parte foi bem simples.
Fiz um script em Go para converter as anotações do dataset do Roboflow para o formato VOC utilizado pela R-CNN. Com isso, tive acesso a cerca de 400 imagens para treinamento.
Infelizmente, não estou conseguindo encontrar novamente o link de download desse dataset. Mas a maioria do datset está carregado no repositorio. :D

Enfim, acho que é isso. Minha semana se resumiu a estudar esse desafio, aprender a fundo sobre redes convolucionais e entender por que usamos uma determinada arquitetura, e não outra, para trabalhar com imagens.
- Fiz até um post sobre isso, que vou publicar no meu blog depois. Achei o tema bem interessante, por sinal. :D

# Como configurar o ambiente

Configure um ambiente virtual Python e instale as dependências (estou assumindo que você esteja utilizando macOS ou Linux):

```bash
python -m venv python && source ./python/bin/activate && pip install -r requirements.txt
```

## Executando com Docker

Você pode usar o Docker para treinar ou testar o modelo sem instalar o PyTorch diretamente na sua máquina. Isso é especialmente útil para ambientes isolados.

### 1. Compilar a imagem Docker

```bash
docker build -t waldo-model .
```

### 2. Treinar o modelo

Você precisa montar o dataset dentro do contêiner para que o modelo consiga acessar os dados de treinamento.

```bash
docker run --gpus all -v $(pwd)/dataset:/app/dataset -v $(pwd):/app waldo-model train.py
```

_(Remova `--gpus all` caso você não tenha uma GPU NVIDIA, embora o treinamento fique significativamente mais lento.)_

### 3. Testar o modelo

```bash
docker run --gpus all -v $(pwd)/imagetest:/app/imagetest -v $(pwd):/app waldo-model test.py
```
