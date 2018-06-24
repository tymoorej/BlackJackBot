from Classes import Deck
from Classes import Player
from Classes import Dealer

printing=True

def setup():
    player = Player()
    dealer = Dealer()
    deck = Deck()
    return player, dealer, deck

def ifprint(text):
    if printing:
        print(text)

def prompt_player(question,numeric=False):
    answer = input(question + '\n')
    while numeric and not(answer.isdigit()):
        answer = input (question + ' Please insert a numerical value\n')
    return answer

def pre_round(player, dealer, deck):
    bet=int(prompt_player('How much would you like to bet?',True))
    if bet > player.get_chips():
        ifprint('You have bet more chips than you have. Instead you go all in')
    player.set_current_bet(min(bet,player.get_chips()))
    deck.deal(player,2)
    deck.deal(dealer,2)
    
def get_insurance(player, dealer):
    if dealer.get_cards()[0][0] == 14 and player.get_current_bet() * 1.5 <= player.get_chips():
        if prompt_player('Would you like insurance? y or n?') == 'y':
            return int(player.get_current_bet() * 0.5)
    else:
        return 0

def first_round(player, dealer, deck):
    skip_to_end = False
    if player.has_blackjack():
        ifprint('You have BlackJack! You cannot make any more moves this round.')
        skip_to_end = True
    else:
        options = ['Hit', 'Stand']

        if player.get_current_bet() * 2 <= player.get_chips():
            options.append('Double Down')

        if player.get_cards()[0][0] == player.get_cards()[1][0]:
            options.append('Split')
        
        choice = ''
        while choice.lower() not in [o.lower() for o in options]:
            choice = prompt_player('What would you like to do? Your options are: ' + str(options) + '. Please spell your choice correctly')
        
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
            # TODO
            pass

    return skip_to_end

def middle_round(player, dealer, deck):
    skip_to_end = False
    options = ['Hit', 'Stand']
    choice = ''
    while choice.lower() not in [o.lower() for o in options]:
        choice = prompt_player('What would you like to do? Your options are: ' + str(options) + '. Please spell your choice correctly')
    
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
    

def end_round(player, dealer, deck):
    ifprint('The dealer\'s cards are: ' + str(dealer.get_cards()))
    if dealer.has_blackjack():
        player.add_chips(2 * player.get_insurance_bet())

        if player.has_blackjack():
            ifprint('Dealer has BlackJack and so do you. It\'s a tie!')
            return

        player.remove_chips(player.get_current_bet())
        ifprint('Dealer has BlackJack and you do not. You lose!')
        return

    if player.has_blackjack():
        player.add_chips(int(player.get_current_bet() * 1.5))
        return



    while (not dealer.is_busted()) and dealer.can_hit():
        ifprint('The dealer hit')
        deck.deal(dealer,1)
        ifprint('The dealer\'s cards are: ' + str(dealer.get_cards()))

    result = compare_hands(player, dealer)

    if result == 'tie':
        ifprint('It\'s a tie!')
        return
    
    if result == 'player':
        player.add_chips(int(player.get_current_bet()))
        ifprint('You win!')
        return
    
    if result == 'dealer':
        player.remove_chips(player.get_current_bet())
        ifprint('You lose!')
        return
    

def play_round(player, dealer, deck):
    deck.shuffle()
    ifprint('You have ' + str(player.get_chips()) + ' chips')
    pre_round(player, dealer, deck)
    ifprint('Your cards are: ' + str(player.get_cards()))
    ifprint('The dealer\'s face up card is: ' + str(dealer.get_cards()[0]))
    player.set_insurance_bet(get_insurance(player, dealer))
    ifprint('Your current bet is ' + str(player.get_current_bet()))
    if player.get_insurance_bet() > 0:
        ifprint('Your insurance bet is ' + str(player.get_insurance_bet()) )
    skip_to_end=first_round(player, dealer, deck)
    ifprint('Your cards are: ' + str(player.get_cards()))
    while not skip_to_end:
        skip_to_end = middle_round(player, dealer, deck)
        ifprint('Your cards are: ' + str(player.get_cards()))
    end_round(player, dealer, deck)
    deck.collect([dealer,player])
    player.set_current_bet(0)
    player.set_insurance_bet(0)
    ifprint('You now have ' + str(player.get_chips()) + ' chips')

def play(player, dealer, deck):
    while(player.get_chips()>0):
        play_round(player, dealer, deck)
    ifprint('You\'re all out of money :(')



def main():
    player, dealer, deck = setup()
    play(player, dealer, deck)

if __name__ == '__main__':
    main()