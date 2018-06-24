'''
This file handels the Classes Deck, Player, Table, and Bot.
'''

from random import randint # Used for shuffling and popping off random cards
 
class Deck:
    def __init__(self):
        self._cards=[]
        for i in range(13):
            for name in ['Hearts','Diamonds','Spades','Clubs']:
                self._cards.append((i+2, name))

    def print_cards(self):
        print('Length of deck: ',len(self._cards))
        print('Cards in deck: ',self._cards)

    def get_cards(self):
        return self._cards

    def shuffle(self):
        new_cards=[]
        size=len(self._cards)
        for i in range(size-1,-1,-1):
            new_cards.append(self._cards.pop(randint(0,i)))
        self._cards=new_cards

    def remove_random_card(self):
        if len(self._cards)==0:
            print('Deck is empty')
            return
        index=randint(0,len(self._cards)-1)
        random_card = self._cards[index]
        self._cards.remove(random_card) # O(n)
        return random_card

    def remove_top_card(self):
        if len(self._cards)==0:
            print('Deck is empty')
            return
        return self._cards.pop(0)

    def remove_card(self,current):
        if len(self._cards)==0:
            print('Deck is empty')
            return
        return self._cards.remove(current) # O(n)

    def deal(self,table_member,number_of_cards):
        assert number_of_cards <= len(self._cards)
        for i in range(number_of_cards):
            card=self.remove_top_card() # O(x)
            table_member.add_card(card)

    def collect(self,table_members):
        for t in table_members:
            while len(t.get_cards()) > 0:
                self._cards.append(t.pop_card())

    def have_all_cards(self):
        cards=set()
        for c in self._cards:
            cards.add(c)
        if len(cards)==52:
            return True
        else:
            return False

    def __str__(self):
        return 'Deck of cards'

class TableMember:
    def __init__(self,cards=None):
        if cards==None:
            self._cards=[]
        else:
            self._cards=cards

    def get_cards(self):
        return self._cards

    def print_cards(self):
        print(self,'\b:\t',end='')
        print('Cards : {}\n'.format(self._cards))

    def add_card(self,card):
        self._cards.append(card)

    def remove_card(self,card):
        if card not in self._cards:
            print('you dont have that card')
        self._cards.remove(card) # O(n)

    def pop_card(self):
        try:
            return self._cards.pop(0)
        except:
            print('No cards left')

    def has_blackjack(self):
        if len(self._cards)!=2:
            return False
        card0 = self._cards[0]
        card1 = self._cards[1]
        
        return ((card0[0]==14 and card1[0]>=10 and card1[0]<14) or (card1[0]==14 and card0[0]>=10 and card0<14))
    
    def is_busted(self):
        total = 0

        for c in self._cards:
            value = c[0]
            if value == 14:
                value = 1
            elif value > 10:
                value = 10
            total += value
        return total > 21
    
    def get_total_values(self):
        cards=[c[0] for c in self._cards]

        return list(set(get_values(cards)))

    def get_highest_non_bust_value(self):
        cards=[c[0] for c in self._cards]
        return max([v for v in get_values(cards) if v <=21])


class Player(TableMember):

    def __init__(self,chips=2000):
        super().__init__()

        self._current_bet=0
        self._insurance_bet=0
        self._chips=chips

    def __str__(self):
        return 'Player'

    def get_chips(self):
        return self._chips

    def remove_chips(self,value):
        self._chips-=value

    def add_chips(self,value):
        self._chips+=value

    def get_current_bet(self):
        return self._current_bet

    def set_current_bet(self, bet):
        self._current_bet = bet
        
    def get_insurance_bet(self):
        return self._insurance_bet

    def set_insurance_bet(self, bet):
        self._insurance_bet = bet

class Dealer(TableMember):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return 'Dealer'

    def can_hit(self):
        totals= [t for t in self.get_total_values() if t<=21 and t>=17]
        
        return len(totals) == 0


def offset_sum(cards):
    total=0
    for c in cards:
        if c < 11:
            total+=c
        elif c == 15:
            total+=11
        else:
            total+=10
    return total

def get_values(cards):
    if 14 not in cards:
        return [offset_sum(cards)]

    for i,c in enumerate(cards):
        if(c==14):
            v1 = get_values(cards[0:i] + [1] + cards[i+1:])
            v2 = get_values(cards[0:i] + [15] + cards[i+1:])
            
            return v1 + v2
