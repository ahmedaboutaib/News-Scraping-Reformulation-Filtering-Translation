def change_date_maj0(date):
    mois_dict = {
        '01': 'Janvier',
        '02': 'Février',
        '03': 'Mars',
        '04': 'Avril',
        '05': 'Mai',
        '06': 'Juin',
        '07': 'Juillet',
        '08': 'Août',
        '09': 'Septembre',
        '10': 'octobre',
        '11': 'Novembre',
        '12': 'Décembre'
    }


    element = date.split("-")
    date_format = f"{element[0]} {mois_dict[element[1]]} {element[2]}"
    return date_format


def change_date_maj(date):
    mois_dict = {
        '01': 'Janvier',
        '02': 'Février',
        '03': 'Mars',
        '04': 'Avril',
        '05': 'Mai',
        '06': 'Juin',
        '07': 'Juillet',
        '08': 'Août',
        '09': 'Septembre',
        '10': 'octobre',
        '11': 'Novembre',
        '12': 'Décembre'
    }
    jours_fr = {
        '01': '1', '02': '2', '03': '3', '04': '4', '05': '5', '06': '6', '07': '7', '08': '8', '09': '9',
        '10': '10', '11': '11', '12': '12', '13': '13', '14': '14', '15': '15', '16': '16', '17': '17',
        '18': '18', '19': '19', '20': '20', '21': '21', '22': '22', '23': '23', '24': '24', '25': '25',
        '26': '26', '27': '27', '28': '28', '29': '29', '30': '30', '31': '31'
    }

    element = date.split("-")
    date_format = f"{jours_fr[element[0].zfill(2)]} {mois_dict[element[1]]} {element[2]}"
    return date_format



def change_date_strucutre (date):
    mois_dict = {
    '01': 'Janvier',
    '02': 'Février',
    '03': 'Mars',
    '04': 'Avril',
    '05': 'Mai',
    '06': 'Juin',
    '07': 'Juillet',
    '08': 'Août',
    '09': 'Septembre',
    '10': 'octobre',
    '11': 'Novembre',
    '12': 'Décembre'
    }
    jours_fr = {
        '01': '1', '02': '2', '03': '3', '04': '4', '05': '5', '06': '6', '07': '7', '08': '8', '09': '9',
        '10': '10', '11': '11', '12': '12', '13': '13', '14': '14', '15': '15', '16': '16', '17': '17',
        '18': '18', '19': '19', '20': '20', '21': '21', '22': '22', '23': '23', '24': '24', '25': '25',
        '26': '26', '27': '27', '28': '28', '29': '29', '30': '30', '31': '31'
    }

    element = date.split("-")
    date_format = f"{mois_dict[element[1]]} {jours_fr[element[0]]}, {element[2]}"
    return date_format


def change_date_arabic(date):
    mois_dict = {
        '01': 'يناير',
        '02': 'فبراير',
        '03': 'مارس',
        '04': 'أبريل',
        '05': 'مايو',
        '06': 'يونيو',
        '07': 'يوليو',
        '08': 'أغسطس',
        '09': 'سبتمبر',
        '10': 'أكتوبر',
        '11': 'نوفمبر',
        '12': 'ديسمبر'
    }
    jours_fr = {
        '01': '1', '02': '2', '03': '3', '04': '4', '05': '5', '06': '6', '07': '7', '08': '8', '09': '9',
        '10': '10', '11': '11', '12': '12', '13': '13', '14': '14', '15': '15', '16': '16', '17': '17',
        '18': '18', '19': '19', '20': '20', '21': '21', '22': '22', '23': '23', '24': '24', '25': '25',
        '26': '26', '27': '27', '28': '28', '29': '29', '30': '30', '31': '31'
    }

    element = date.split("-")
    date_format = f"{jours_fr[element[0]]} {mois_dict[element[1]]} {element[2]}"
    return date_format
