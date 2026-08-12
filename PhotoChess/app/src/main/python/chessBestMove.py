import berserk

API_TOKEN = "lip_AogrJ6dUu8ruSPMBZNUW"


def getbestmove(fen):
    session = berserk.TokenSession(API_TOKEN)
    client = berserk.Client(session=session)

    analysis = client.analysis.get_cloud_evaluation(fen, 1)
    dict = analysis["pvs"]
    return(dict.pop(0)['moves'].split(' ')[0])