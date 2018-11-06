from . import models
from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
from .models import Constants, Player


class Gender(Page):
    form_model = 'player'
    form_fields = ['gender']

    def is_displayed(self):
        return self.subsession.gender and self.round_number == 1

    def before_next_page(self):
        self.participant.vars['gender'] = self.player.gender


class Intro(Page):
    template_name = 'pggfg/Introduction.html'

    def is_displayed(self):
        return self.subsession.round_number == 1


class AfterGenderWP(WaitPage):
    def is_displayed(self):
        return self.subsession.gender


class Contribute(Page):
    timeout_seconds = 60
    timeout_submission = {'contribution': 0}
    form_model = 'player'
    form_fields = ['contribution']

    def contribution_max(self):
        return self.player.endowment

    def vars_for_template(self):
        return {'label': "How much will you contribute to the project (from 0 to {})?".
            format(self.player.endowment)}


class AfterContribWP(WaitPage):
    def after_all_players_arrive(self):
        self.group.set_payoffs()


class Results(Page):
    ...


class FinalResults(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds


page_sequence = [
    Gender,
    Intro,
    AfterGenderWP,
    Contribute,
    AfterContribWP,
    Results,
    FinalResults,
]
