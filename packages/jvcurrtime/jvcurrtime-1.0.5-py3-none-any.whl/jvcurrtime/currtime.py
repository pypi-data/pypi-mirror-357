import datetime
from jvcore import Communicator, SkillBase, ActionDescription, ActionType
from jvopenai import OpenAIConversation

class CurrTimeSkill(SkillBase):
    def __init__(self, comm: Communicator) -> None:
        self.__communicator = comm
        self.__openai = OpenAIConversation()
    
    def getDate(self, utterance):
        text = self.__openai.getResponse(f'''question: <datetime string>
            answer: <datetime text formatted so that it can be read by polish speech synthesiser>
            question: {datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}
            answer:''')
        self.__communicator.sayAndPrint('data: ' + text)

    @staticmethod
    def getDescription() -> ActionDescription:
        return {'actionType':ActionType.Command, 'description': 'Tells the current time', 'parameters': None}