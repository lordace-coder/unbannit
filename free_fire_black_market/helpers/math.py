def reduce_by(amt,perc):
    redc = amt *(perc/100)
    return amt - redc


def get_discount(amt,red):
    perc =  abs(((100*red)-(100*amt))/amt)
    return "{}%".format(perc)


