from otree.api import *
import random
import json

doc = """
A Cheap Talk Game(Gneezy, 2005)
Author: Xuhang Fan

Describtion: in a two-agent group, the sender knows two investment options(e.g. [x1,y1,x2,y2]), and choose to send a recommendation message to receiver. However, the receiver knows nothing about the investment choices and should decide whether to accept the sender's recommendation or not. Their payoff is determined by the final choice of the receiver. 

Feature: 
1. you can determine the each round's investment options by easily changing the Constants.settings. And the settings will display randomly in multi-rounds and the option place(i.e. show in A or B) automatically.
2. Final payoff is randomly determined. Each participant will get paid at a random round, and their decisions will be shown in Results page.
3. Instruction and Comprehension page included, please add it at page sequence if you want.

"""


class Constants(BaseConstants):
    name_in_url = 'cheap_talk'
    players_per_group = 2
    num_rounds = 3

    # Determine the roles
    Sender_Role = 'Sender'
    Receiver_Role = 'Receiver'

    # <settings> randomize the settings and determine the final sequence.
    settings = [[1,-4,18,23],[2,5,14,25],[23,13,12,6]] # [x1,y1,x2,y2] is the setting for every round
    random.shuffle(settings)
    # print(settings)
    for i in range(len(settings)):
        a = random.randint(1,100)
        if a <= 50:
            pass
        else:
            temp_set = settings[i]
            s1 = temp_set[2:4]
            s2 = temp_set[0:2]
            temp_set = s1 + s2
            settings[i] = temp_set

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    sender_deception = models.StringField(
        label = "Your message is: ",
        choices=['Choice A can make you earn more than Choice B','Choice A can make you earn more than Choice B','Choice B can make you earn more than Choice A'],  
        widget=widgets.RadioSelect
    )
    receiver_decision = models.StringField(
        label="Please decide to accept or reject the recommendation",
        choices=['accept', 'reject','reject'],  
        widget=widgets.RadioSelect
    )
    setting = models.StringField(initial='') # store the setting in each round
    is_deception = models.IntegerField(initial=-99)
    externality = models.IntegerField(initial=-99)
class Player(BasePlayer):
    quiz1 = models.StringField(
        label='Which option is better for Sender?',
        choices=['choice A', 'choice B'],  
        widget=widgets.RadioSelect
    )
    quiz2 = models.StringField(
        label='Which option is better for Receiver?',
        choices=['choice A', 'choice B'],  
        widget=widgets.RadioSelect
    )
    quiz3 = models.StringField(
        label='Can Receiver know any information in the formal experiment?',
        choices=['Yes', 'No'],  
        widget=widgets.RadioSelect
    )
    quiz4 = models.IntegerField(
        label='If the sender sent the message: <strong>\'Choice A can make you earn more than Choice B\'</strong>, and the receiver decide to <strong>\'accept\'</strong>。<br>What is sender\'s payoff in this round?'
    )
    quiz5 = models.IntegerField(
        label='What is receiver\'s payoff in this round?'
    )
    quiz6 = models.IntegerField(
        label='If the sender sent the message:<strong>\'Choice B can make you earn more than Choice A\'</strong>, and the receiver decide to <strong>\'reject\'</strong>。<br>What is sender\'s payoff in this round?'
    )
    quiz7 = models.IntegerField(
        label='What is receiver\'s payoff in this round?'
    )
    quiz8 = models.StringField(
        label='Message<strong>\'Choice B can make you earn more than Choice A\'</strong> is consistent with the truth',
        choices=['Yes', 'No'],  
        widget=widgets.RadioSelect
    )

# Functions
def creating_session(subsession: Subsession):
    # store the group_matrix in session_field
    session = subsession.session
    if subsession.round_number == 1:
        session.vars['gm'] = subsession.get_group_matrix()

# set payoffs
def set_payoffs(group: Group):
    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)
    # Store the setting for each round. Encode Python objects into JSON strings
    group.setting=json.dumps(Constants.settings[group.round_number-1])
    # randomly determined each participant's round for payment, store as tmp while round=1
    if p1.round_number == 1:
        tmp1 = random.randint(1,Constants.num_rounds) # sender's payment round
        tmp2 = random.randint(1,Constants.num_rounds) # receiver's payment round
        p1.participant.pay_round = tmp1
        p2.participant.pay_round = tmp2
    # caculate the payoff in the payment round for p1
    # Store payoff and decision at the payment round into player.participant filed 
    if group.round_number == p1.participant.pay_round:
        settings_copy = Constants.settings
        list_chose = settings_copy[group.round_number-1]
        # get Sender's and Receiver's payoff
        if group.sender_deception == 'Choice A can make you earn more than Choice B' and group.receiver_decision == 'accept':
            p1.participant.payoff1 = list_chose[0]
        elif group.sender_deception == 'Choice B can make you earn more than Choice A' and group.receiver_decision == 'reject':
            p1.participant.payoff1 = list_chose[0]
        else:
            p1.participant.payoff1 = list_chose[2]
        p1.participant.dec = group.sender_deception
        p1.participant.dec_other = group.receiver_decision
    # caculate the payoff in the payment round for p2
    # Store payoff and decision at the payment round into player.participant filed 
    if group.round_number == p2.participant.pay_round:
        settings_copy = Constants.settings
        list_chose = settings_copy[group.round_number-1]
        # get Sender's and Receiver's payoff
        if group.sender_deception == 'Choice A can make you earn more than Choice B' and group.receiver_decision == 'accept':
            p2.participant.payoff1 = list_chose[1]
        elif group.sender_deception == 'Choice B can make you earn more than Choice A' and group.receiver_decision == 'reject':
            p2.participant.payoff1 = list_chose[1]
        else:
            p2.participant.payoff1 = list_chose[3]
        p2.participant.dec = group.receiver_decision
        p2.participant.dec_other = group.sender_deception

# PAGES
class welcome(Page):
    @staticmethod
    def is_displayed(player:Player):
        return player.round_number == 1
class instructions(Page):
    pass
class comprehension(Page):
    form_model = 'player'
    form_fields = ['quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5', 'quiz6', 'quiz7','quiz8']
    @staticmethod
    def is_displayed(player:Player):
        return player.round_number == 1
    @staticmethod
    def error_message(player: Player, values):
        # alternatively, you could make quiz1_error_message, quiz2_error_message, etc.
        # but if you have many similar fields, this is more efficient.
        solutions = dict(quiz1 = 'choice B', quiz2='choice A', quiz3 = 'No', quiz4=1, quiz5=4, quiz6=1, quiz7=4, quiz8='No')

        # error_message can return a dict whose keys are field names and whose values are error messages
        errors = {f: 'Wrong' for f in solutions if values[f] != solutions[f]}
        # print('errors is', errors)
        if errors:
            return errors
class understand(Page):
    @staticmethod
    def is_displayed(player:Player):
        return player.round_number == 1
class Deception(Page):
    form_model = 'group'
    form_fields = ['sender_deception']

    @staticmethod
    def is_displayed(player:Player):
        return player.role == Constants.Sender_Role
    def vars_for_template(player: Player):
        play_round = player.round_number - 1
        set_chosen = Constants.settings[play_round]
        pay_round = player.round_number
        return dict(play_round = play_round, set_chosen = set_chosen,pay_round=pay_round)
    def error_message(player: Player, values):
        play_round=player.round_number-1
        set_chosen=Constants.settings[play_round]
        if set_chosen[1]>set_chosen[3] and values['sender_deception']=='Choice B can make you earn more than Choice A':
            player.group.is_deception = 1
            player.group.externality =  set_chosen[1] - set_chosen[3]
        elif set_chosen[1]>set_chosen[3] and values['sender_deception']=='Choice A can make you earn more than Choice B':
            player.group.is_deception = 0
            player.group.externality =  set_chosen[1] - set_chosen[3]
        elif set_chosen[1] < set_chosen[3] and values['sender_deception'] == 'Choice A can make you earn more than Choice B':
            player.group.is_deception = 1
            player.group.externality =  set_chosen[3] - set_chosen[1]
        else:
            player.group.is_deception = 0
            player.group.externality =  set_chosen[3] - set_chosen[1]

class WaitforP1(WaitPage):
    template_name = '_templates/global/WaitforP1.html'
class Decision(Page):
    form_model = 'group'
    form_fields = ['receiver_decision']

    @staticmethod
    def is_displayed(player: Player):
        return player.role == Constants.Receiver_Role


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == Constants.num_rounds

class Wait(WaitPage):
    template_name = '_templates/global/Wait.html'
    wait_for_all_groups = True
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number== 1
class End(WaitPage):
    wait_for_all_groups = True
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number== Constants.num_rounds

page_sequence = [welcome, instructions, Wait, Deception, WaitforP1, Decision, WaitforP1, ResultsWaitPage,Results,End]
# comprehension, understand
 