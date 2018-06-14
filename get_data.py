def getDialogState():
    try:
        f = open('dialog_state', 'r')
        return f.read()
    finally:
        if f:
            f.close()


def getCardData():
    try:
        df = open('card_data', 'r')
        return df.read()
    finally:
        if df:
            df.close()
