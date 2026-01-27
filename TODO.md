



# adicionar a Nina
* = Frase da Nina
% = ações tomadas
@ = condicionais
Rotas nina:
Econtra o jogador
    %Pede para andar com o jogador - ["Mandar para casa", "Aceitar Pedido", "Acompanhar até em casa"]
    @ se mandar para casa
        * "Tá bom... Mas eu vou explorar um pouco antes!"
        %no caminho de volta nina decide dar uma olhada na floresta sombria e acaba se perdendo e morrendo por lá
        * Final 1 - Quando o jogador chega na vila, as pessoas estão tristes e comentam que é estranho ela ter ido pra lá. Normalmente ela só brinca na floresta de cogumelos mas que alguém viu ela indo para a floresta sombria
    
    @ Se aceitar pedido ou Acompanhar até em casa
        % nina passa a seguir os passos do jogador. Ela começa a falar um pouco sobre como ela também sempre quis ser forte pra poder ajudar os outros. Nina não luta, mas se a vida do jogador ficar abaixo de 30%, ela vai tentar lutar para ajudar e pode acabar morrendo
        **frases da nina
            Falas 1:
                [“Você anda tão firme… parece que nada te derruba.”, “Se eu fosse grande, eu ia proteger a vila inteira.”, “Você acha que dói muito aprender a lutar?”]
            Falas 2 - Quando o jogador combater algum monstro:
                [“Eu queria ser assim. Não pra machucar… só pra ajudar.”, “Sabe, se eu fosse forte, ninguém ia se perder por aqui.”]

            Falas 3 - Quando o jogador derrota um monstro:
                [“Quando tudo fica perigoso… eu queria não ser só alguém que observa.”,
                “Você sempre vai na frente. Eu fico pensando se um dia eu conseguiria também.”]
    
            Falas 4 - Quando a vida do jogador abaixa de 30%
                [“Ser forte deve ser isso, né? Fazer alguma coisa quando importa.”, “Se alguém se machucar por minha causa… eu ia tentar ajudar. Mesmo com medo.”]

        Final 2 - Quando o jogador estiver pra morrer, ele não morre, fica com 1 de vida enquanto a nina fala "Eu... também vou ser um herói"
        Ela tenta atacar mas não tem quase nada de vida então morre. 5 segundos depois o jogador morre também.

        @ Se aceitar pedido
            %Nina nunca para de seguir o jogador até que ele morra.
        @ Acompanhar até em casa
            %Quando o jogador chegar na vila, nina agradece e deixa de seguir o jogador 


# Criar rotina dos orcs.

## Orcs terão profissões então sua rotina vai depender da profissão.

### Chefe Orc - 1
#### Passa o dia dentro da caverna dos orcs "Planejando" o ataque. 

# Às 17h os orcs que receberam a mensagem do mensageiro devem se reunir na caverna ao redor do Chefe.
# O Chefe deve falar sobre como tem sido tempos difíceis, falar sobre como o relacionamento com os humanos nunca foi positivo mas também nunca foi totalmente hostil. Falar sobre como o desespero levou ele a planejar o que estão prestes a executar.
# Ás 19h Todos os orcs juntos se encaminham para a vila humana onde vão realizar um massacre


# Trocar o som de ataque dos slimes
# Melhorar design das montanhas
# Colocar um velho sábio que sempre sabe como você morreu e pode dar dicas do que fazer
## Se o jogador conseguir 10+ finais, pode se transformar nele.

# Às 18:30h Nash e Dash se encaminham para a próximo da entrada da caverna dos orcs por que lá é um bom local para caça nessa época. Eles vão ser os primeiros a fazer contato com os orcs

# Adicionar botão de "Matar-se"
# Adicionar check point 1 ao deixar a nina na vila