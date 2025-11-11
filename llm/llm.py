from pydantic_ai import Agent

MODEL = 'google-gla:gemini-2.5-flash'

PROMPT = "Um pato e uma vaca foram competir, quem correu mais rápido até a chegada?"

class LLM():
    def __init__(self, model: str):
        self.model = self._quick_model(model) if model else MODEL
        self.agent = Agent(self.model)
        
    def _judge_problem(self, problem: str) -> str:
        result = self.agent.run_sync(problem)
        
        return result.output
        
    def _quick_model(self, model: str) -> str:
        match model:
            case 'gf':
                return 'google-gla:gemini-2.5-flash'
            case 'gp':
                return 'google-gla:gemini-2.5-pro'
            case _:
                return MODEL

if __name__ == "__main__":
    llm = LLM(MODEL)
    try:
        answer = llm._judge_problem(PROMPT)
        print(f"Resposta: {answer}")

    except Exception as e:
        print(f"Ocorreu um erro (Verifique GOOGLE_API_KEY): {e}")