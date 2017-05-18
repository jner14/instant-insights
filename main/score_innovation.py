import os

# Formula Parameters
ASSOCtoMGR = 1.0 / 1.1
RISKtoFAIL = 1.5 / 1.0
RISKtoYOS = 100.0 / 1.0
MIF = 0.5  # manager influence factor
YIntercept = 100.0

riskD = -YIntercept / (1 + 1 / RISKtoYOS + 1 / RISKtoFAIL)
riskC = riskD * 2 / 3
riskB = riskD / 3
failC = riskD / RISKtoFAIL
failB = failC / 2
yosE = riskD / RISKtoYOS
yosD = yosE * 3 / 4
yosC = yosE / 2
yosB = yosE / 4


def _get_score(x, y, z):
    score = ((ASSOCtoMGR if x == "ASSOC" else 1) *
             ((riskB if y == "b" else 0) +
              (riskC if y == "c" else 0) +
              (riskD if y == "d" else 0) +
              (failB if z == "b" else 0) +
              (failC if z == "c" else 0) +
              YIntercept
              ))
    return score


def get_rating(responses):
    if len(responses) < 1:
        return "NON EXISTENT", 0
    pctMgr = 1.0 * sum([1 for x, y, z in responses if x == "MGR"]) / len(responses)
    pctAssoc = 1.0 * sum([1 for x, y, z in responses if x == "ASSOC"]) / len(responses)

    mgrScores = [_get_score(x, y, z) for x, y, z in responses if x == "MGR"]
    assocScores = [_get_score(x, y, z) for x, y, z in responses if x == "ASSOC"]

    mgrMean = 0.0 if len(mgrScores) < 1 else 1.0 * sum(mgrScores) / len(mgrScores)
    assocMean = 0.0 if len(assocScores) < 1 else 1.0 * sum(assocScores) / len(assocScores)
    score = pctMgr * mgrMean + pctAssoc * assocMean + MIF * (mgrMean - YIntercept / 2.0)

    if score >= 90:
        rating = "HOT"
    elif score >= 80:
        rating = "HOT to WARM"
    elif score >= 70:
        rating = "WARM"
    elif score >= 60:
        rating = "WARM to COLD"
    else:
        rating = "COLD"

    return rating, score

if __name__ == "__main__":
    import pandas as pd
    df = pd.read_csv("Company 2.csv", header=0)
    myResponses = [[row.Type, row.Risk, row.Fail] for k, row in df.iterrows()]
    myRating, myScore = get_rating(myResponses)
    print("Finished")
