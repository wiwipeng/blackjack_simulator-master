import random

suits = ('黑桃', '紅心', '梅花', '方塊')


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        if self.rank == 1:
            self.card_scores = [1, 11]
        elif self.rank >= 11 and self.rank <= 13:
            self.card_scores = [10, 10]
        else:
            self.card_scores = [self.rank, self.rank]

        if self.rank == 1:
            self.short_rank = 'A'
        elif self.rank == 11:
            self.short_rank = 'J'
        elif self.rank == 12:
            self.short_rank = 'Q'
        elif self.rank == 13:
            self.short_rank = 'K'
        else:
            self.short_rank = str(self.rank)

        if self.suit == '黑桃':
            self.short_suit = 'S'
        elif self.suit == '紅心':
            self.short_suit = 'H'
        elif self.suit == '梅花':
            self.short_suit = 'C'
        else:
            self.short_suit = 'D'

        self.image_location = 'static/images/{}{}.png'.format(
            self.short_rank, self.short_suit)

    def __repr__(self):
        if self.rank == 1:
            true_rank = 'Ace'
        elif self.rank == 11:
            true_rank = 'Jack'
        elif self.rank == 12:
            true_rank = 'Queen'
        elif self.rank == 13:
            true_rank = 'King'
        else:
            true_rank = str(self.rank)
        return '{} of {}'.format(true_rank, self.suit)


class Deck:
    def __init__(self, number_of_decks):
        self.number_of_decks = number_of_decks
        self.cards = []
        self.create(self.number_of_decks)

    def __repr__(self):
        return 'Game deck has {} cards remaining'.format(len(self.cards))

    def create(self, number_of_decks):
        decks = [Card(rank, suit) for suit in suits for rank in range(1, 14)
                 for deck in range(number_of_decks)]
        decks = random.sample(decks, len(decks))
        self.cards.extend(decks)

    def draw(self):
        drawn_card = self.cards[0]
        self.cards.remove(self.cards[0])
        return drawn_card

    def reset(self):
        self.cards = []
        self.create(self.number_of_decks)


class Dealer:
    def __init__(self):
        self.cards = []
        self.hand_scores = [0, 0]
        self.best_outcome = '等待中'

    def __repr__(self):
        return '莊家的牌: {}, 點數: {}, 最佳牌面: {}'.format(self.cards, list(set(self.hand_scores)), self.best_outcome)

    def hit(self, game_deck):
        draw_card = game_deck.draw()
        self.cards.append(draw_card)
        card_scores = draw_card.card_scores
        self.hand_scores = [a + b for a,
                            b in zip(self.hand_scores, card_scores)]
        if len(self.cards) <= 1:
            self.best_outcome = '等待中'
        elif 21 in self.hand_scores and len(self.cards) == 2:
            self.best_outcome = 'Blackjack'
        elif self.hand_scores[0] > 21 and self.hand_scores[1] > 21:
            self.best_outcome = 'Bust爆牌'
        else:
            self.best_outcome = max([i for i in self.hand_scores if i <= 21])

    def reset(self):
        self.cards.clear()
        self.hand_scores = [0, 0]
        self.best_outcome = '等待中'


class Player(Dealer):
    def __init__(self):
        self.cards = []
        self.hand_scores = [0, 0]
        self.best_outcome = '等待中'
        self.possible_actions = ['No deal yet']

    def __repr__(self):
        return '你的手牌: {}, 點數: {}, 最佳牌面: {}'.format(self.cards, list(set(self.hand_scores)), self.best_outcome)

    def stand(self, game_play):
        self.possible_actions = []
        game_play.commentary.append('玩家停牌')

    def double_down(self, game_deck, game_play):
        self.hit(game_deck)
        game_play.commentary.append('玩家雙倍下注')
        self.possible_actions = []

    def player_hit(self, game_deck, game_play):
        self.hit(game_deck)
        game_play.commentary.append('玩家繼續發牌')
        self.get_possibilities(game_play)

    def get_possibilities(self, game_play):
        if self.best_outcome in ['Blackjack', 'Bust爆牌', 21]:
            self.possible_actions = []
            game_play.commentary.append('哈哈，你爆了')
        elif len(self.cards) == 2:
            self.possible_actions = ['Hit', 'Stand', 'Double Down']
            game_play.commentary.append(
                '你現在在可以發牌或雙倍下注或停牌')
        else:
            self.possible_actions = ['Hit', 'Stand']
            game_play.commentary.append('你現在可以發牌或停牌')

    def reset(self):
        self.cards = []
        self.hand_scores = [0, 0]
        self.best_outcome = 'Awaiting deal'
        self.possible_actions = []
        self.has_doubled_down = False


class GamePlay:
    def __init__(self, player, dealer, game_deck, blackjack_multiplier):
        self.player = player
        self.dealer = dealer
        self.game_deck = game_deck
        self.blackjack_multiplier = blackjack_multiplier
        self.commentary = []

    def __repr__(self):
        return "Commentary: {}".format(self.commentary)

    def dealer_turn(self):
        self.dealer.hit(self.game_deck)
        if self.dealer.best_outcome == 'Blackjack':
            self.commentary.append('哈哈笑你！我拿到21點')
        elif self.dealer.best_outcome == 'Bust爆牌':
            self.commentary.append('我爆了:(')
        elif int(self.dealer.best_outcome) < 17:
            self.commentary.append(
                '我拿到 {}, 我繼續發牌'.format(self.dealer.best_outcome))
            self.dealer_turn()
        elif int(self.dealer.best_outcome) == 17 and 1 in [card.rank for card in self.dealer.cards]:
            self.commentary.append('我小於17點，我要繼續發牌')
            self.dealer_turn()
        else:
            self.commentary.append(
                '我有 {} 點'.format(self.dealer.best_outcome))

    def update(self):
        if len(self.player.possible_actions) == 0:
            if self.player.best_outcome == 'Bust爆牌':
                self.commentary.append(
                    "你爆牌了。錢錢是我的了:)")
            elif self.player.best_outcome == 'Blackjack' and self.dealer.cards[0].rank not in [1, 10]:
                self.commentary.append("拿到Blackjack. 我輸了:(  你贏了 {} 倍的獎金(;´༎ຶД༎ຶ`)".format(
                    str(self.blackjack_multiplier)))
            else:
                self.commentary.append("莊家繼續")
                self.dealer_turn()
                if self.dealer.best_outcome == 'Bust爆牌':
                    self.commentary.append(
                        "哇!! 我爆牌了，你可以拿走錢錢了(⑉꒦ິ^꒦ິ⑉)")
                elif self.dealer.best_outcome == 'Blackjack' and self.player.best_outcome == 'Blackjack':
                    self.commentary.append(
                        "我們運氣真好 都拿到21點. 你可以拿走你的錢錢了")
                elif self.dealer.best_outcome == 'Blackjack' and self.player.best_outcome != 'Blackjack':
                    self.commentary.append(
                        "我拿到21點了，我要拿走你的錢錢了，哈哈")
                elif self.dealer.best_outcome != 'Blackjack' and self.player.best_outcome == 'Blackjack':
                    self.commentary.append("該死！你怎麼拿到Blackjack. 你贏了 {} 倍的獎金(;´༎ຶД༎ຶ`)".format(
                        str(self.blackjack_multiplier)))
                elif int(self.dealer.best_outcome) == int(self.player.best_outcome):
                    self.commentary.append(
                        "和局")
                elif int(self.dealer.best_outcome) > int(self.player.best_outcome):
                    self.commentary.append("我有 {} 點，你拿到了 {} 點. 你的錢錢是我的了(˶˚ ᗨ ˚˶)".format(
                        str(self.dealer.best_outcome), str(self.player.best_outcome)))
                else:
                    self.commentary.append("我有 {}，你拿到了  {}點.我的錢錢是你的了".format(
                        str(self.dealer.best_outcome), str(self.player.best_outcome)))
        else:
            pass

    def reset(self):
        self.commentary = []

    def deal_in(self):
        self.dealer.reset()
        self.player.reset()
        self.game_deck.reset()
        self.reset()
        self.player.hit(self.game_deck)
        self.dealer.hit(self.game_deck)
        self.player.hit(self.game_deck)
        self.player.get_possibilities(self)
