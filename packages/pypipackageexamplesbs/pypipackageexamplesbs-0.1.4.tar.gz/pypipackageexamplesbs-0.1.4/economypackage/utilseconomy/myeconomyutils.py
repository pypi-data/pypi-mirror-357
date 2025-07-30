def divisaConverter(money,valueOfTheMoment):
    if(money==0 or money==0.0):
        raise Exception("Money cannot be zero")
    else:
        return round(money*valueOfTheMoment)