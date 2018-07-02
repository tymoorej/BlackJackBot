from Classes import Deck
from Classes import Player
from Classes import Dealer
from Classes import TableMember
from database import write_to_blackjack_table
from database import getRows
import random
from sklearn.neural_network import MLPClassifier


actions = {0 : 'Stand', 1: 'Hit', 2: 'Double Down', 3: 'Split'}
actions_rev = {v: k for k, v in actions.items()}

completed_results = []
player_results = []
second_hand_results = []

def setup():
    player = Player()
    dealer = Dealer()
    deck = Deck()
    return player, dealer, deck

def should_print():
    global game_mode, watching_bot
    return game_mode == 'p' or (game_mode == 'b' and watching_bot)

def ifprint(text):
    if should_print():
        print(text)
        if game_mode == 'b':
            input('\nPress enter to continue\n')
    

def prompt_player(question,numeric=False):
    answer = input(question + '\n')
    while numeric and not(answer.isdigit()):
        answer = input (question + ' Please insert a numerical value\n')
    return answer

def pre_round(player, dealer, deck):
    if game_mode == 'p':
        bet=int(prompt_player('How much would you like to bet?',True))
    else:
        bet = 1
        ifprint('You bet 1 chip')
    if bet > player.get_chips():
        ifprint('You have bet more chips than you have. Instead you go all in')
    player.set_current_bet(min(bet,player.get_chips()))
    deck.deal(player,2)
    deck.deal(dealer,2)
    
def get_insurance(player, dealer):
    if dealer.get_cards()[0][0] == 14 and player.get_current_bet() * 1.5 <= player.get_chips():
        if game_mode == 'b':
            print('You chose not to get insurance')
        elif prompt_player('Would you like insurance? y or n?') == 'y':
            return int(player.get_current_bet() * 0.5)
    return 0

def can_split(cards):
    if(cards[0][0]<10 or cards[0][0]==14):
        return cards[0][0] == cards[1][0]
        
    return (cards[1][0] < 14 and cards[1][0] >= 10)

def first_round(player, dealer, deck):
    global player_results
    second_hand = None
    skip_to_end = False
    if player.has_blackjack():
        ifprint('You have BlackJack! You cannot make any more moves this round.')
        skip_to_end = True
    else:
        options = ['Hit', 'Stand']

        if player.get_current_bet() * 2 <= player.get_chips():
            options.append('Double Down')

        if can_split(player.get_cards()):
            options.append('Split')
        
        choice = ''
        while choice.lower() not in [o.lower() for o in options]:
            if game_mode == 'b':
                ifprint('What would you like to do? Your options are: ' + str(options))
                choice = random.choice(options)
                ifprint('You chose ' + choice)
            else:
                choice = prompt_player('What would you like to do? Your options are: ' + str(options) + '. Please spell your choice correctly')
        
        player_results.append([min(player.get_total_values()),dealer.get_cards()[0][0],actions_rev[choice]])

        if choice.lower() == 'Hit'.lower():
            deck.deal(player, 1)
            if player.is_busted():
                skip_to_end = True
        
        elif choice.lower() == 'Stand'.lower():
            skip_to_end = True
        
        elif choice.lower() == 'Double Down'.lower():
            player.set_current_bet(player.get_current_bet() * 2)
            deck.deal(player, 1)
            skip_to_end = True
        
        elif choice.lower() == 'Split'.lower():
            second_hand = TableMember()
            second_hand.add_card(player.pop_card())
            deck.deal(player,1)
            deck.deal(second_hand,1)

    return skip_to_end, second_hand

def middle_round(player, dealer, deck):
    global player_results, second_hand_results
    skip_to_end = False
    options = ['Hit', 'Stand']
    choice = ''

    if 21 in player.get_total_values():
        ifprint('You have 21! You cannot make anymore moves.')
        return True

    while choice.lower() not in [o.lower() for o in options]:
        if game_mode == 'b':
            ifprint('What would you like to do? Your options are: ' + str(options))
            choice = random.choice(options)
            ifprint('You chose ' + choice)
        else:
            choice = prompt_player('What would you like to do? Your options are: ' + str(options) + '. Please spell your choice correctly')


    if str(player)=='Player':
        player_results.append([min(player.get_total_values()),dealer.get_cards()[0][0],actions_rev[choice]])

    else:
        second_hand_results.append([min(player.get_total_values()),dealer.get_cards()[0][0],actions_rev[choice]])

    if choice.lower() == 'Hit'.lower():
        deck.deal(player, 1)
        if player.is_busted():
            skip_to_end = True
    
    elif choice.lower() == 'Stand'.lower():
        skip_to_end = True
    return skip_to_end

def compare_hands(player, dealer):
    if player.is_busted():
        if dealer.is_busted():
            return 'tie'
        else:
            return 'dealer'
    if dealer.is_busted():
        return 'player'
    
    if player.get_highest_non_bust_value() == dealer.get_highest_non_bust_value():
        return 'tie'
    if player.get_highest_non_bust_value() > dealer.get_highest_non_bust_value():
        return 'player'
    else:
        return 'dealer'
    
def dealers_turn(dealer, deck):
    ifprint('The dealer\'s cards are: ' + str(dealer.get_cards()))
    while (not dealer.is_busted()) and dealer.can_hit():
        ifprint('The dealer hit')
        deck.deal(dealer,1)
        ifprint('The dealer\'s cards are: ' + str(dealer.get_cards()))

def end_round(player, dealer, deck):
    global player_results, second_hand_results
    ifprint('The dealer\'s cards are: ' + str(dealer.get_cards()))
    if dealer.has_blackjack():
        player.add_chips(2 * player.get_insurance_bet())

        if player.has_blackjack():
            ifprint('Dealer has BlackJack and so do you. It\'s a tie!')
            return 't'

        player.remove_chips(player.get_current_bet())
        ifprint('Dealer has BlackJack and you do not. You lose!')
        return 'd'

    if player.has_blackjack():
        player.add_chips(int(player.get_current_bet() * 1.5))
        return 'p'

    result = compare_hands(player, dealer)

    if result == 'tie':
        ifprint('It\'s a tie!')
        return 't'
    
    if result == 'player':
        player.add_chips(int(player.get_current_bet()))
        ifprint('You win!')
        return 'p'
    
    if result == 'dealer':
        player.remove_chips(player.get_current_bet())
        ifprint('You lose!')
        return 'd'
    
def play_round(player, dealer, deck):
    global player_results, completed_results, second_hand_results
    deck.shuffle()
    ifprint('You have ' + str(player.get_chips()) + ' chips')
    pre_round(player, dealer, deck)
    ifprint('Your cards are: ' + str(player.get_cards()))
    ifprint('The dealer\'s face up card is: ' + str(dealer.get_cards()[0]))
    
    if game_mode == 'p':
        player.set_insurance_bet(get_insurance(player, dealer))
        ifprint('Your current bet is ' + str(player.get_current_bet()))
    
    if player.get_insurance_bet() > 0:
        ifprint('Your insurance bet is ' + str(player.get_insurance_bet()) )
        
    skip_to_end, second_hand=first_round(player, dealer, deck)

    ifprint('Your cards are: ' + str(player.get_cards()))

    if second_hand != None:
        ifprint('Your cards in your second hand are: ' + str(second_hand.get_cards()))
        ifprint('First Hand:')

    while not skip_to_end:
        skip_to_end = middle_round(player, dealer, deck)
        ifprint('Your cards are: ' + str(player.get_cards()))

    
    if second_hand != None:
        ifprint('Second Hand:')
        ifprint('Your cards in your second hand are: ' + str(second_hand.get_cards()))
        skip_to_end=False
        while not skip_to_end:
            skip_to_end = middle_round(second_hand, dealer, deck)
            ifprint('Your second hand cards are: ' + str(second_hand.get_cards()))
    
    dealers_turn(dealer, deck)
    
    if second_hand!= None:
        ifprint('First Hand:')


    winner = end_round(player, dealer, deck)
    for r in player_results:
        if winner == 'd':
            r.append(0)
        elif winner == 't':
            r.append(1)
        elif winner == 'p':
            r.append(2)
        else:
            raise Exception('player end round should returd one of t,d,p but it returned' + winner)
    player.set_insurance_bet(0)

    if second_hand!= None:
        ifprint('You now have ' + str(player.get_chips()) + ' chips')
        deck.collect([player])
        ifprint('Second Hand:')
        for c in second_hand.get_cards():
            second_hand.remove_card(c)
            player.add_card(c)
        winner = end_round(player, dealer, deck)
        for r in second_hand_results:
            if winner == 'd':
                r.append(0)
            elif winner == 't':
                r.append(1)
            elif winner == 'p':
                r.append(2)
            else:
                raise Exception('second hand end round should returd one of t,d,p but it returned' + winner)
        deck.collect([second_hand])
        

    deck.collect([dealer,player])
    player.set_current_bet(0)
    player.set_insurance_bet(0)
    ifprint('You now have ' + str(player.get_chips()) + ' chips')

    completed_results+= player_results + second_hand_results
    player_results = []
    second_hand_results = []

def play(player, dealer, deck):
    games_played = 0
    while(player.get_chips()>0):
        print(games_played)
        play_round(player, dealer, deck)
        games_played +=1
        if games_played >= 10000:
            return
    if should_print:
        ifprint('You\'re all out of money. :(')

def train_bot():
    rows = getRows('Blackjack')
    x = [r[0:3] for r in rows]
    y = [r[3] for r in rows]
    MLP = MLPClassifier()
    MLP = MLP.fit(x,y)
    print(MLP.predict_proba([(20,5,0)])*100)

def main():
    global game_mode, watching_bot
    game_mode = False
    watching_bot = False
    if prompt_player('Player or Bot?, enter p for player or b for bot.').lower() != 'p':
        game_mode = 'b'
        print('You chose bot.')
        if prompt_player('Would you like to watch the bot play? y or n?').lower() == 'y':
            watching_bot = True
        #train_bot()
    else:
        game_mode = 'p'
        print('You chose player.')

    player, dealer, deck = setup()
    play(player, dealer, deck)
    
    write_to_blackjack_table(completed_results)


if __name__ == '__main__':
    main()