from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
import random

author = "Philip Chapkovski, chapkovski@gmail.com"

doc = """
Public Good Game with heterogeneous endowments

"""


class Constants(BaseConstants):
    name_in_url = 'pgg'
    players_per_group = 3
    num_others_per_group = players_per_group - 1
    num_rounds = 10
    instructions_template = 'pggfg/Instructions.html'
    endowment = c(20)
    endowment_lb = c(10)
    endowment_ub = c(30)
    efficiency_factor = 1.6
    GENDERCHOICES = ['Male', 'Female']


class Subsession(BaseSubsession):
    gender = models.BooleanField()
    hetero = models.BooleanField()

    def creating_session(self):
        self.gender = self.session.config.get('gender')
        self.hetero = self.session.config.get('hetero')

        for p in self.get_players():
            if self.round_number == 1:
                if self.hetero:
                    p.endowment = c(random.randint(Constants.endowment_lb,
                                                   Constants.endowment_ub))
                else:
                    p.endowment = Constants.endowment
            else:
                p.endowment = p.in_round(1).endowment


class Group(BaseGroup):
    total_contribution = models.IntegerField()
    average_contribution = models.FloatField()
    individual_share = models.CurrencyField()

    def set_payoffs(self):
        self.total_contribution = sum([p.contribution for p in self.get_players()])
        self.average_contribution = round(self.total_contribution / Constants.players_per_group, 2)
        self.individual_share = self.total_contribution * Constants.efficiency_factor / Constants.players_per_group
        for p in self.get_players():
            p.payoff = sum([+ p.endowment,
                            - p.contribution,
                            + self.individual_share,
                            ])


class Player(BasePlayer):
    endowment = models.CurrencyField(doc='initial endowment of a player')
    gender = models.StringField(choices=Constants.GENDERCHOICES, label='What is your gender?',
                                widget=widgets.RadioSelectHorizontal)
    contribution = models.PositiveIntegerField(
        min=0,
        doc="""The amount contributed by the player""",

    )
