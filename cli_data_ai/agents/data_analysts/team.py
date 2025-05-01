# agents/agent_team.py
class DataAnalystTeam:
    def __init__(self, db_path: str, metabase_url: str):
        self.db_path = db_path
        self.metabase_url = metabase_url
        self.agents = self._initialize_agents()

    def _initialize_agents(self):
        # Create agents with tools (db reader, metabase reporter, etc.)
        pass

    def answer(self, question: str) -> str:
        # Let the agent process the question
        return self.agents.run(question)
