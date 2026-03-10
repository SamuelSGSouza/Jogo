
Os 4 pilares:
    - Nina
    - Orc caído no labirinto
    - Chefe da vila humana
    - Chefe dos orcs

Loop 1: Esse é o início da jornada do jogador. Ele acaba no momento em que o jogador morrer ou ver a vila destruída. Aqui serve apenas para ele entender que está em um loop.

Loop 2: Esse loop só acaba quando o jogador falar com o orc caído na floresta e ver a vila destruída.

Loop 3: Esse loop acaba quando o jogador falar com o Orc Caído na floresta e com o chefe da vila. Ao fim desse loop ele vai entender que os orcs estão famintos.

Loop 4: Esse loop acaba quando o jogador falar com o orc caído na floresta e com o chefe dos orcs. Aqui o jogador consegue, pela primeira vez, conversar com o chefe dos orcs e entender um pouco seu lado.

Loop 5: Esse loop se mantém até o jogador conseguir convencer o chefe dos orcs a cancelar o ataque e em seguida convencer o chefe da vila a dividir a comida.

# Nina - Ela é a jóia da vila, mas cresceu acostumada com o trabalho duro exigido de quem vive em um local tão extremo graças ao seu pai, o Lenhador da vila, Holz. Ela é uma das poucas pessoas da sua geração na vila, juntamente com Nash e Dash, o que a faz não ter muitas expectativas de casamento a menos que saia para uma das cidades grandes. Mas isso não a afeta, pois já decidiu que vai continuar o legado de seu pai como a lenhadora (e, como seu pai gosta de dizer: "O pilar da vila"). Apesar de tudo, ela ainda ama esse lugar. Ela já aprendeu tudo que podia com o seu pai e é até melhor que ele nas suas tarefas, e justamente por isso, ela se dá ao luxo de começar as manhãs olhando para o vale do topo das montanhas antes de começar sua rotina.

# abrir a parte da mata logo atrás do personagem e adicionar coisas dependendo de quando ele quiser sair
## Loop 1
### adicionar fala "Bom, acabei de chegar então acho que posso explorar o lugar antes de ir embora" não deixar o jogador ir embora

## Loop 2
### adicionar fala "Eu preciso entender melhor o que está acontecendo aqui." não deixar o jogador ir embora

## Loop 3
### adicionar fala "Droga, esse lugar realmente tem algum tipo de maldição. Eu preciso sair daqui!"

## Loop 4
### adicionar fala "Pra mim chega! Isso não é problema meu!"

## Loop 5
### adicionar fala "Eu não aguento mais esse lugar..."

# Adicionar final do cansado/covarde. Se o jogador decidir fugir, ele recebe esse final

# Adicionar mais flores, bonecos e detalhes pelo mapa
# construir a história
# dar falas e um pouco de personalidade para os orcs
# Adicionar corpos de mercenários mortos na floresta dos fantasmas (são os caras que morreram protegendo o Verloren)
# adicionar sombras de nuvens passando pelo mapa

# Regra geral dos loops:
## Por causa da movimentação dos Orcs, os monstros fogem para as montanhas. Nina fica presa lá e provavelmente acaba morrendo.
### Nash e Dash param de se mover muito e começam a conversar sobre a movimentação dos Orcs e sobre os monstros estarem fugindo para as montanhas

## O Golem percebe o movimento estranho dos monstros e algo se ativa. Ele começa a vagar pelo vale destruindo tudo no caminho dele. Primeiro passa no agrupamento dos Orcs e depois na vila humana.
### Quando o golem sai de controle, os moradores da vila começam a se juntar no centro da vila. Lá o assunto principal passa a ser o descontrole do Golem e o que pode ter acontecido para ele agir assim. Alguns também podem falar sobre a Nina que não está sendo encontrada.

# Loop 1 -

## Frase Inicial:
### Quem eu sou, que eu fui e o que eu fiz... Isso não importa.
### Todo mundo tem arrependimentos na vida, e eu estou aqui pra tentar consertar os meus.

## Conversas devem ser focadas na curiosidade do personagem, então ele está curioso e entendendo um pouco sobre aquele lugar

## Nina - 
### "Está perdido, viajante?"
#### "Talvez um pouco. (Honesto / Pensativo)" - Honesto / Pensativo
#### "Acho que estou exatamente onde eu deveria estar (Filosófico / Reflexivo)" - Filosófico / Reflexivo
#### "Eu estou onde eu quero estar (Direto / Rude)" - Direto / Rude

## Honesto / Pensativo
### "Bom, pra começar, você está no Vale do Retorno, o vale mais ao norte do continente! Você veio aqui pelo Coração do Inverno, certo?"
#### Isso mesmo! Você sabe algo sobre ele? - O coração de gelo
#### Esse "Coração do Inverno", o que é? - O coração de gelo

## O coração de gelo
### "'O Coração do Inverno' é uma jóia com poderes lendários, que dizem ser a fonte das grandes nevascas que acontecem em todo o norte do continente. A lenda conta que aquele que o possuir pode não apenas governas todas as terras de gelo, mas também realizar um único desejo de proporções ilimitadas."
#### Fale mais, por favor. - O coração de gelo 2
#### Entendo... Mas não é por isso que estou aqui. - Fim Normal

## O coração de gelo 2
### "Os viajantes que vem sempre dizem que o Coração deve estar por aqui, mas já procuraram em todo o vale e nunca encontraram. Nos últimos anos tem aparecido cada vez menos gente procurando por ele."
#### Eu não sou como eles, pode apostar que eu vou encontrar o Coração! - Fim Normal
#### E quanto a você? Acha que ele existe e está escondido nesse vale? - Opiniao Nina

## Opiniao Nina
### "Sendo bem honesta, viajante, acho que são só histórias que alguém espalhou por aí e todos passaram a acreditar. Vivi minha vida inteira nesse vale, vi inúmeros caçadores de recompensa e viajantes vagarem por aqui tentando encontrar esse Coração e todos eles sempre iam embora com decepção e cansaço em seu olhar... Então não, acredito que essa jóia não existe. E se ela existe, ela não está aqui."
#### Entendo...Agradeço pelas informações! Mesmo assim, pretendo gastar um pouco de tempo procurando por ela. - Fim Normal
#### Agradeço pelas informações! Só mais uma coisa, pode me dizer seu nome? - Fim Normal


## Fim Normal
### "Hmmm... Interessante. Eu sou a Nina, muito prazer viajante! Quando passar pela vila não se esqueça de contratar os serviços do meu pai. Ele é o Holz, lenhador da vila." %player.confiança_vila += 1


## Filosófico / Reflexivo
### "Você é algum tipo de estudioso ou pesquisador? O último viajante que passou por aqui falando assim foi um elfo junto com um bando de guarda-costas."
#### O que aconteceu com esse elfo? - Sobre o Elfo
#### Esse estudioso viajante descobriu alguma coisa? - O coração de gelo 2

## Sobre o Elfo
### "Ele e os ajudantes foram para a floresta dos fantasmas, falando que o  Coração TINHA que estar lá. Isso já faz alguns dias e ele ainda não retornou, então acho que deve ter morrido por lá.
#### Me pergunto se ele realmente existe... - O coração de gelo 2
#### Esse "Coração", o que ele é? - O coração de gelo


TUDO ABAIXO SÃO DIÁLOGOS DESBLOQUEAVEIS

# Nina
# 1 Desbloquado quando tenta interagir com o corpo morto da Nina - "Na verdade, estou aqui pra te tirar dessa montanha".
# 2 Desbloqueado quando o jogador descobre que a movimentação dos Orcs, fez os monstros irem para a montanha.
# 3 Desbloqueado quando o jogador pergunta o nome da Nina

# Holz
# 4 Desbloqueado quando o jogador descobre o nome da Nina
# 5 Desbloqueado quando o jogador fala com a Nina

# Dash
# 6 Desbloqueado a partir do 3 loop 
# 7 Desbloqueado se o jogador já falou como Holz ou a Nina
# 8 Desbloqueado Se já passou das 10h e #13 não foi desbloqueado
# 9 Desbloqueado se já falou com o Holz
# 10 Desbloquado se já sabe do ataque dos Orcs

# Nash
# 11 Desbloqueado se já passou das 10h e não falou com o Dash
# 12 Desbloqueado se já passou das 10h e já falou com o Dash

# Verant
# 13 Desbloqueado se já passou do loop 2 ||  Desbloqueado se já passou das 10h
# 14 Se já ouviu sobre os Orcs
# 15 Desbloquado se já sabe do ataque dos Orcs
# 16 Desbloquado se já sabe que os Orcs estão famintos
# 17 Desbloquado se já sabe da doença que atingiu os Orcs