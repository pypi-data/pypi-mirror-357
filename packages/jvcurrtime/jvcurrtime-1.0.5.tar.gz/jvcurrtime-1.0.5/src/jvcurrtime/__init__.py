from jvcore import Communicator, SkillBase
from jvcore.testing import TestCommunicator
from .currtime import CurrTimeSkill


def getSkill(communicator: Communicator) -> SkillBase:
    return CurrTimeSkill(communicator)

def test():
    skill = getSkill(TestCommunicator())
    skill.getDate('')