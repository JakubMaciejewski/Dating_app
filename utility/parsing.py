
def parse_nickname(nickname: str) -> str or None:
    ''' returning nickname or None-type if nickname incorrect'''
    if isinstance(nickname, str):
        if len(nickname) > 1:
            return nickname

        else:
            return None
    return None


def parse_edit_gender(gender: str) -> int or None:
    ''' returning gender.id or None-type if gender incorrect'''
    try:
        #int(gender)
        return int(gender)

    except ValueError:
        return None

    except TypeError:
        return None


def parse_edit_sexuality(sexuality: str) -> int or None:
    ''' returning sex.id or None-type if sex incorrect'''
    try:
        #int(gender)
        return int(sexuality)

    except ValueError:
        return None

    except TypeError:
        return None

def parse_edit_age(age: str) -> int or None:
    ''' returning age or None-type if age incorrect'''
    try:
        #int(gender)
        return int(age)

    except ValueError:
        return None

    except TypeError:
        return None




