import unittest
from unittest.mock import MagicMock, patch

from aider.models import Model
from aider.plus.team import AIEngineeringTeam


class TestTeam(unittest.TestCase):
    @patch("aider.plus.team.Model")
    def test_team_initialization_and_roles(self, MockModel):
        # Mock Model instances
        mock_main_model = MagicMock()
        mock_coder_model = MagicMock()
        mock_reviewer_model = MagicMock()

        # Configure MockModel to return different mocks for different names
        def model_side_effect(name, **kwargs):
            if name == "main-model":
                return mock_main_model
            if name == "coder-model":
                return mock_coder_model
            if name == "reviewer-model":
                return mock_reviewer_model
            return MagicMock()

        MockModel.side_effect = model_side_effect

        main_model_instance = MockModel("main-model")

        team_config = {
            "coder": "coder-model",
            "reviewer": "reviewer-model",
            "test_writer": "main-model",  # Use main model as default
        }

        team = AIEngineeringTeam(main_model=main_model_instance, team_config=team_config)

        # Assertions
        self.assertIs(team.get_coder(), mock_coder_model)
        self.assertIs(team.get_reviewer(), mock_reviewer_model)
        self.assertIs(team.get_test_writer(), mock_main_model)

        # Test fallback to main model
        team_config_fallback = {
            "coder": "coder-model",
            # reviewer and test_writer not specified
        }

        team_fallback = AIEngineeringTeam(
            main_model=main_model_instance, team_config=team_config_fallback
        )

        self.assertIs(team_fallback.get_coder(), mock_coder_model)
        self.assertIs(team_fallback.get_reviewer(), mock_main_model)  # Should fall back
        self.assertIs(team_fallback.get_test_writer(), mock_main_model)  # Should fall back


if __name__ == "__main__":
    unittest.main()
