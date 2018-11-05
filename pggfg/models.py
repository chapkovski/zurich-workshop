from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random

author = "Philip Chapkovski, chapkovski@gmail.com"

doc = """
Public Good Game with Punishment (Fehr and Gaechter).
Fehr, E. and Gachter, S., 2000.
 Cooperation and punishment in public goods experiments. American Economic Review, 90(4), pp.980-994.
"""


class Constants(BaseConstants):
    name_in_url = 'pggfg'
    players_per_group = 3
    num_others_per_group = players_per_group - 1
    num_rounds = 20
    instructions_template = 'pggfg/Instructions.html'
    endowment = 20
    efficiency_factor = 1.6
    punishment_endowment = 10
    punishment_factor = 3
    GENDERCHOICES = ['Male', 'Female']


class Subsession(BaseSubsession):
    gender = models.BooleanField()
    punishment = models.BooleanField()

    def creating_session(self):
        self.gender = self.session.config.get('gender')
        self.punishment = self.session.config.get('punishment')


class Group(BaseGroup):
    total_contribution = models.IntegerField()
    average_contribution = models.FloatField()
    individual_share = models.CurrencyField()

    def set_pd_payoffs(self):
        self.total_contribution = sum([p.contribution for p in self.get_players()])
        self.average_contribution = round(self.total_contribution / Constants.players_per_group, 2)
        self.individual_share = self.total_contribution * Constants.efficiency_factor / Constants.players_per_group
        for p in self.get_players():
            p.pd_payoff = sum([+ Constants.endowment,
                               - p.contribution,
                               + self.individual_share,
                               ])

    def set_punishments(self):
        for p in self.get_players():
            p.set_punishment()


class Player(BasePlayer):
    gender = models.StringField(choices=Constants.GENDERCHOICES, label='What is your gender?',
                                widget=widgets.RadioSelectHorizontal)
    contribution = models.PositiveIntegerField(
        min=0, max=Constants.endowment,
        doc="""The amount contributed by the player""",
        label="How much will you contribute to the project (from 0 to {})?".format(Constants.endowment)
    )
    punishment_sent = models.CurrencyField(initial=0)
    punishment_received = models.CurrencyField(initial=0)
    pd_payoff = models.CurrencyField(doc='to store payoff from contribution stage', initial=0)
    punishment_endowment = models.IntegerField(initial=0, doc='punishment endowment')
    pun1, pun2, pun3 = [models.CurrencyField() for i in range(3)]

    def set_payoff(self):
        self.payoff = self.pd_payoff - self.punishment_sent - self.punishment_received

    def set_punishment_endowment(self):
        assert self.pd_payoff is not None, 'You have to set pd_payoff before setting punishment endowment'
        self.punishment_endowment = min(self.pd_payoff, Constants.punishment_endowment)

    def set_punishment(self):
        puns_sent = [getattr(self, 'pun{}'.format(p.id_in_group)) for p in self.get_others_in_group()]
        self.punishment_sent = sum(puns_sent)
        puns_received = [getattr(p, 'pun{}'.format(self.id_in_group)) for p in self.get_others_in_group()]
        self.punishment_received = sum(puns_received) * Constants.punishment_factor
