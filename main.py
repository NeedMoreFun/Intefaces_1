import requests
import datetime
from collections import Counter

def analysis_gender(male_count, female_count):
    if male_count > female_count:
        verdict = 'мужчина'

    if female_count > male_count:
        verdict = 'женщина'

    if male_count == female_count:
        verdict = 'n/a'

    return verdict


def analysis_age(current_year, person_year):
    person_year = person_year.split('.')
    age = current_year - int(person_year[2])

    if age >= 60:
        age = 45	

    return age


def make_report(count, dic):
    male_count = 0
    female_count = 0
    handle = open('report.txt', 'w')
    now = datetime.datetime.now()
    current_year = now.year
    sum_age = 0
    count_person_with_age = 0
    frequent_cities = []
    hobbies_list = []

    for x in range(0, count):
        person_id = dic['response']['items'][x]['id']
        person_first_name = dic['response']['items'][x]['first_name']
        person_last_name = dic['response']['items'][x]['last_name']
        person_sex = dic['response']['items'][x]['sex']

        try:
            if person_sex == 2:
                person_sex = 'мужской'
                male_count += 1
            if person_sex == 1:
                person_sex = 'женский'
                female_count += 1

            try:
                person_bdate = dic['response']['items'][x]['bdate']
            except KeyError:
                handle.write(
                    f'{person_first_name} {person_last_name} id - {person_id}/дата рождения - n/a /пол - {person_sex}\n')
                continue

            try:
                age = analysis_age(current_year, person_bdate)
                sum_age += age
                count_person_with_age += 1
            except:
                handle.write(
                    f'{person_first_name} {person_last_name} id - {person_id}/дата рождения - {person_bdate}/возраст - n/a /пол - {person_sex}\n')
                continue

            try:
                person_city = dic['response']['items'][x]['city']['title']
                frequent_cities.append(person_city)
            except KeyError:
                handle.write(
                    f'{person_first_name} {person_last_name} id - {person_id}/дата рождения - {person_bdate}/возраст - {age}/пол - {person_sex}/город - n/a\n')
                continue

            try:
                person_phone = dic['response']['items'][x]['mobile_phone']
            except KeyError:
                handle.write(
                    f'{person_first_name} {person_last_name} id - {person_id}/дата рождения - {person_bdate}/возраст - {age}/пол - {person_sex}/город - {person_city}/моб.номер - n/a\n')
                continue

            handle.write(
                f'{person_first_name} {person_last_name} id - {person_id}/дата рождения - {person_bdate}/возраст - {age}/пол - {person_sex}/город - {person_city}/моб.номер - {person_phone}\n')
        except UnicodeEncodeError:
            continue

    # Часто встречающийся пол друзей
    verdict_gender = analysis_gender(male_count, female_count)

    # Среднее значение возраста друзей
    estimated_age = int(sum_age / count_person_with_age)

    # Часто встречающиеся города друзей
    frequent_cities = Counter(frequent_cities)
    one_city, two_city, three_city = frequent_cities.most_common(3)
    one_city = one_city[0]
    two_city = two_city[0]
    three_city = three_city[0]

    # Увлечения
    groups = get_user_group(id)

    for group_id in groups:
        try:
            hobbies_list.append(get_group_activiti(group_id))
        except KeyError:
            continue

    group_counter = Counter(hobbies_list)
    one_hobbie, two_hobbie, three_hobbie = group_counter.most_common(3)
    one_hobbie = one_hobbie[0]
    two_hobbie = two_hobbie[0]
    three_hobbie = three_hobbie[0]

    handle.write('Итого:')
    handle.write(
        f'\n\nМужчин - {male_count}/Женщин - {female_count} \nпредположительно объект - {verdict_gender} \nпредпологаемый возраст - {estimated_age}\nвозможный город - {one_city}/{two_city}/{three_city}\nвозможные увлечения - {one_hobbie}/{two_hobbie}/{three_hobbie}')
    handle.close()


def get_user_group(id):
    r = requests.get(f'https://api.vk.com/method/groups.get?user_id={id}&access_token={access_token}&v=5.103')
    groups = r.json()['response']['items']

    return groups


def get_group_activiti(id):
    r = requests.get(
        f'https://api.vk.com/method/groups.getById?group_id={id}&fields=activity&access_token={access_token}&v=5.103')

    return r.json()['response'][0]['activity']


def resolve_id(id):
    r = requests.get(
        f'https://api.vk.com/method/utils.resolveScreenName?screen_name={id}&oath=0&access_token={access_token}&v=5.103')
    return r.json()['response']['object_id']


def get_friends_info(id):
    r = requests.get(
        f'https://api.vk.com/method/friends.get?user_id={id}&fields=sex,bdate,city,contacts&order=name&access_token={access_token}&v=5.103')
    data = r.json()
    count = int(data['response']['count'])

    make_report(count, data)


def get_user_input():
    user_id = input('Введите id страницы: ')
    try:
        int(user_id)
    except:
        user_id = resolve_id(user_id)

    return user_id


if __name__ == '__main__':
    try:
        access_token = 'vk1.a.H6iFvcY72KX676ih1uXiatDqCKBEjfo80N4F_GvlGEetZ68zDk-mzg4uA1o--ZNhdQLBZYjiQu_H5PHFLii-u4tKPlty4IvI4AOuR7RBXKYdHamtcnBLY6_-NJnoU6W0la-D8V52Qu0l7fh8opIDKcYDgPp4XxOEwkY_9P-c4p2u0lAoNDpCTf1H2wysE81A'  # token

        if access_token == '':
            print('Токен не обнаружен, запишите его')
            exit()

        id = get_user_input()
        get_friends_info(id)
        print('\n[+] Отчет сгенерирован ./report.txt')
    except KeyboardInterrupt:
        print('\n\n[+] Выходим...')
        exit()
