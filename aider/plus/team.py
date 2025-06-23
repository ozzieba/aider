from aider.models import Model


class AIEngineeringTeam:
    def __init__(self, main_model, team_config=None):
        self.main_model = main_model
        self.team_config = team_config or {}
        self.roles = {}

        for role, model_name in self.team_config.items():
            self.roles[role] = Model(model_name)

    def get_coder(self):
        return self.roles.get("coder") or self.main_model

    def get_reviewer(self):
        return self.roles.get("reviewer") or self.main_model

    def get_test_writer(self):
        return self.roles.get("test_writer") or self.main_model
