from flask import Flask, render_template, request, redirect, url_for, flash, session  # из библиотеки импортировать класс Flask
import psycopg2
from datetime import datetime, timedelta
from datetime import time
# import tempfile


app = Flask(__name__)
app.secret_key = "super secret key"

def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='IceMovieBD',
                            user='postgres',
                            password='Lada$')
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM kinoteatrs;')
    kinoteatrs = cur.fetchall()
    cur.close()
    conn.close()
    # zal = 5
    # kol_r = 7
    # kol_mest_v_r = 12
    # for i in range(kol_r):
    #     for j in range(kol_mest_v_r):
    #         bob = (zal, i+1, j+1)
    #         cur.execute(
    #             "INSERT INTO places (id_zal, nom_ryd, nom_place) VALUES (%s, %s, %s)",
    #         bob)
    #         conn.commit()
    return render_template('index_kino.html', kinoteatrs=kinoteatrs)

@app.route('/<int:id>')
def films(id):
    conn = get_db_connection()
    cur = conn.cursor()

    d = datetime.now().date()
    # Проверяем фильмы (только те, которые в прокате)
    cur.execute('SELECT * FROM films WHERE data_okon_procat >= %s and data_nach_procat <= %s;', (d, d,))
    film = cur.fetchall()

    cur.execute('SELECT * FROM films WHERE data_nach_procat > %s;', (d,))
    skorvprokat = cur.fetchall()


    cur.execute("SELECT * FROM kinoteatrs where id_kinoteatrs=%s", (id,))
    kinoteatr = cur.fetchall()


    cur.close()
    conn.close()
    print(id)
    return render_template('index.html', film=film, id=id, kinoteatr=kinoteatr, skorvprokat=skorvprokat)


@app.route('/<int:id>/films/<int:id_f>')
def seans(id, id_f):
    conn = get_db_connection()
    cur = conn.cursor()

    d = datetime.now().date()
    t = datetime.now().time()


    cur.execute("""
                SELECT id_seans, id_film, id_zal, format, data_seans, time_seans, price FROM seans
                JOIN zals USING (id_zal)
                WHERE id_film=%s AND data_seans >= %s AND kinoteatr = %s
                ORDER BY data_seans, time_seans;
            """,
                (id_f, d, id,))
    seans = cur.fetchall()

    #
    # cur.execute("SELECT * FROM seans where id_film=%s AND data_seans >= %s ORDER BY time_seans, data_seans;", (id_f, id, d,))
    # seans = cur.fetchall()

    cur.execute("SELECT * FROM zals where kinoteatr=%s", (id,))
    zal = cur.fetchall()

    # print(seans)
    cur.close()
    conn.close()

    DATA = []
    TIME = []
    DATA_TIME = []
    ERROR = 0

    if len(seans) == 0:
        ERROR = 1
        return render_template('datatimelist.html', ERROR=ERROR, id=id)

    # print(seans[0])
    # print(seans[0][0])
    # print(seans[0][4])


    for i in range(len(seans)):
        if seans[i][4] != seans[i-1][4]:
            DATA.append(seans[i][4])
        if seans[i][5] != seans[i-1][5]:
            TIME.append(seans[i][5])
        if (seans[i][4] != seans[i - 1][4]) or (
                seans[i][5] != seans[i - 1][5]):
            DATA_TIME.append([seans[i][4], seans[i][5], seans[i][0]])
    if (len(DATA_TIME) == 0):
        DATA.append(seans[0][4])
        TIME.append(seans[0][5])
        DATA_TIME.append([seans[0][4], seans[0][5], seans[0][0]])
    if (len(DATA_TIME) != 0) and (len(DATA) == 0):
        DATA.append(seans[0][4])
    print(DATA)
    print("Уже не дата")
    print(seans)
    print(zal)
    return render_template('datatimelist.html',  id_f=id_f, zal=zal, DATA=DATA, TIME=TIME, DATA_TIME=DATA_TIME, id=id, ERROR=ERROR, seans=seans, t=t, d=d)

@app.route('/<int:id>/films/<int:id_f>/buy/<int:id_s>', methods=['GET', 'POST'])
def places(id, id_f, id_s):
    conn = get_db_connection()
    cur = conn.cursor()


    cur.execute('SELECT * FROM seans WHERE id_seans=%s;', (id_s, ))
    seans = cur.fetchall()
    id_z = seans[0][2]

    cur.execute('SELECT * FROM places WHERE id_zal=%s;', (id_z,))
    places = cur.fetchall()

    cur.execute('SELECT * FROM films WHERE id_film=%s;', (id_f,))
    film = cur.fetchall()

    cur.execute('SELECT * FROM tickets WHERE id_seans=%s ORDER BY id_ticket;', (id_s,))
    tickets = cur.fetchall()

    cur.execute('SELECT * FROM zals WHERE id_zal=%s;', (id_z,))
    zal = cur.fetchall()

    # print("Залы", zal)
    # print("Места")
    # print(places)
    # print("Сейчас нужно")
    # print(tickets)
    # print(seans)
    # print(id_z)
    # print(places)

    cur.close()
    conn.close()

    if len(tickets) == 0:
        ERROR = 1
        return render_template('place_choose.html', ERROR=ERROR, id=id, id_f=id_f, id_s=id_s, film=film, seans=seans, zal=zal)
    RYD = []
    PLACE = []
    STATUS = []

    for i in range(len(places)):
        PLACE.append([places[i][2], places[i][3], places[i][0], tickets[i][0], tickets[i][4]])


    # print("Это PLACE")
    # print(PLACE)
    N = len(PLACE)


    if request.method == 'POST':
        a = request.form.getlist('mybox')
        conn = get_db_connection()
        cur = conn.cursor()

        if len(a) == 0:
            pass
            # return redirect('/buy/{{id}}/{{id_s}}')
        else:
            RYD = []
            PLACE = []
            TICKET_ID = []
            # print(a)
            b = list(map(int, a))
            print("Печатаю b")
            print(b)
            sum=0
            for i in range(len(b)):
                cur.execute('SELECT * FROM tickets WHERE id_ticket=%s;', (b[i],))
                tick = cur.fetchall()
                if len(tick) != 1:
                    return "Ошибка"

                cur.execute('SELECT * FROM places WHERE id_place=%s;', (tick[0][2],))
                pl = cur.fetchall()
                sum += seans[0][6]
                RYD.append(pl[0][2])
                PLACE.append(pl[0][3])
                TICKET_ID.append(tick[0][0])
            print(TICKET_ID)
            N = len(TICKET_ID)
    #         # print(b)
            print(RYD)
            print(PLACE)
    #         print(TICKET_ID)
    #         print(STATUS)
            cur.close()
            conn.close()
            return render_template('ticket_buy.html', id=id, id_s=id_s, id_f=id_f, RYD=RYD, PLACE=PLACE, N=N, TICKET_ID=TICKET_ID, b=b, film=film, seans=seans, zal=zal, sum=sum)
    else:
        return render_template('place_choose.html', film=film, seans=seans, zal=zal, N=N, PLACE=PLACE)


@app.route('/<int:id>/films/<int:id_f>/buy/<int:id_s>/prodag', methods=['GET', 'POST'])
def prodag(id, id_f, id_s):
    conn = get_db_connection()
    cur = conn.cursor()

    # ch_film_buy = Film.query.filter_by(id=id).first()
    # film_r = Seans.query.filter_by(id=id_s).first()
    a = request.form.getlist('box')
    b = list(map(int, a))
    if request.method == "POST":
        FIO = request.form['FIO']
        e_mail = request.form['e_mail']
        try:
            cur.execute('SELECT * FROM seans WHERE id_seans=%s;', (id_s,))
            seans = cur.fetchall()
            sum = []
            for i in range(len(b)):
                sum.append(seans[0][6])
                cur.execute("UPDATE tickets SET status=%s WHERE id_ticket=%s", ("продан", b[i]))
                conn.commit()
            bob = (FIO, e_mail)
            cur.execute("INSERT INTO customers (FIO, e_mail) VALUES (%s, %s) RETURNING id_customers", bob)
            id_c = cur.fetchall()[0]
            print("ID покупателя: ", id_c[0])
            for i in range(len(b)):
                bob = (id_c, b[i], 1, sum[i])
                cur.execute("INSERT INTO prodag (id_customers, id_ticket, id_employee, sum_prodag) VALUES (%s, %s, %s, %s)", bob)
                conn.commit()
            # выполняем транзакцию
            print("Успех 4")
            cur.execute('SELECT * FROM films WHERE id_film=%s;', (id_f,))
            film = cur.fetchall()

            cur.close()
            conn.close()

            return render_template('inf.html', id=id, if_f=id_f, id_s=id_s, FIO=FIO, e_mail=e_mail, cseans=seans,
                                   film=film)
        except:
            return "Ошибка"
    else:
        return redirect('/')


@app.route('/admin', methods=['GET', 'POST'])
def adm():

    # conn = get_db_connection()
    # cur = conn.cursor()
    # cur.execute('SELECT * FROM kinoteatrs;')
    # kinoteatrs = cur.fetchall()
    # cur.close()
    # conn.close()

    if request.method == "POST":
        id = request.form['id']
        password = request.form['pd']
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            print("Прошел 1")
            cur.execute('SELECT * FROM employee WHERE id_employee=%s and password_em=%s;', (id, password))
            print("Прошел 2")
            res = cur.fetchall()
            if len(res) != 1:
                return "Ошибка 1"
            print("Прошел 3")
            print(password)
            print(res[0][2])
            if int(password) == int(res[0][2]):
                print("Прошел 4")
                session['loggedin'] = True
                session['id'] = res[0][0]
                session['username'] = res[0][1]
                cur.close()
                conn.close()
                return redirect(url_for('adm_bl'))
            else:
                print("Прошел 5")
                # Account doesnt exist or username/password incorrect
                cur.close()
                conn.close()
                flash('Incorrect username/password')
        except:
            print("Прошел 6")
            return "Ошибка 2"
    return render_template('avtorization.html')

@app.route('/admin/ad_block')
def adm_bl():
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('admin_block.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('adm'))

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('adm'))

@app.route('/admin/ad_block/create_film', methods=['POST', 'GET'])
def create_films():
    if 'loggedin' in session:
        conn = get_db_connection()
        cur = conn.cursor()
        d = datetime.now().date()
        if request.method == "POST":
            title_film = request.form['title_film']
            data = request.form['data']
            data2 = request.form['data2']
            country_of_production = request.form['country_of_production']
            year_of_production = request.form['year_of_production']
            age_ratings = request.form['age_ratings']
            text = request.form['text']
            genre = request.form['genre']
            director = request.form['director']
            starring = request.form['starring']
            img = request.form['img']
            dlitel = request.form['dlitel']

            # Проверяем дату (нельзя < текущей)
            data_nach_proat = datetime.strptime(data, "%Y-%m-%d").date()
            if d > data_nach_proat:
                return "Нельзя добавлять новый фильм с датой начала проката на прошедшую дату!"

            data_okon_proat = datetime.strptime(data2, "%Y-%m-%d").date()
            if d > data_okon_proat:
                return "Нельзя добавлять новый фильм с датой окончания проката на прошедшую дату!"

            if data_nach_proat >= data_okon_proat:
                return "Дата начала проката не может быть больше или равна дате окончания проката!"

            d3 = datetime.now().date() + timedelta(days=30)
            if data_nach_proat > d3:
                return "Дата начала проката не должна быть больше 30 дней от текущей даты!"


            try:
                god_proizv = datetime.strptime(year_of_production, "%Y").date()
            except ValueError:
                return "Неверный формат года производства"

            # Проверяем введенный формат времени
            import time
            try:
                valid_date = time.strptime(dlitel, '%H:%M:%S')
            except ValueError:
                return "Неверный формат времени"
            bob = (title_film, data, data2, country_of_production, year_of_production, age_ratings, text, genre, director, starring, img, dlitel)
            account = session['id']
            try:
                cur.execute("""
                                INSERT INTO films (name_film , data_nach_procat, data_okon_procat, contry, year_pr, reiting, description, genre, director, st_cast, img, dliteln)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_film;
                        """,
                            (bob))
                conn.commit()

                id_f = cur.fetchall()[0]
                bob = (id_f, account)

                cur.execute(
                    "INSERT INTO createfilm (id_film, id_emp) VALUES (%s, %s)",
                    bob)
                conn.commit()

                cur.close()
                conn.close()
                return "Фильм добавлен"
            except:
                return "Ошибка"

        else:
            return render_template('create.html')
    return redirect(url_for('adm'))

@app.route('/admin/ad_block/create_seans', methods=['POST', 'GET'])
def create_seans():
    if 'loggedin' in session:
        conn = get_db_connection()
        cur = conn.cursor()
        d = datetime.now().date()
        d2 = datetime.now().date() + timedelta(days=2)
        # Проверяем фильмы (только те, которые в прокате + фильмы, чья дата проката через <= 2 дня)
        cur.execute('SELECT * FROM films WHERE data_okon_procat >= %s and data_nach_procat <= %s;', (d, d2,))
        film = cur.fetchall()

        cur.execute('SELECT * FROM zals;')
        zals = cur.fetchall()

        if request.method == "POST":
            film = request.form['film']
            data_seans = request.form['data']
            zal = request.form['zal']
            forma = request.form['forma']
            time_of_pokaz = request.form['time_of_pokaz']
            price = request.form['price']

            # Проверяем дату (нельзя < текущей)
            data_sean = datetime.strptime(data_seans, "%Y-%m-%d").date()
            if d > data_sean:
                return "Нельзя вводить дату на сеанс меньше текущего дня!"

            # Ограничение на создание нового сеанса - 7 дней
            data_sean = datetime.strptime(data_seans, "%Y-%m-%d").date()
            end_date = d + timedelta(days=7)
            if end_date < data_sean:
                return "Ограничение на создание сеанса - 7 дней от текущей даты!"

            # Проверяем введенный формат времени
            import time
            date = time_of_pokaz
            try:
                valid_date = time.strptime(date, '%H:%M:%S')
            except ValueError:
                return "Неверный формат времени"
            # Если текущая дата, проверяем чтоб нельзя было добавить сеанса на уже прошедшее время
            if d == data_sean:
                tek_vrem = datetime.today().strftime("%H:%M:%S")
                tek_vrem = datetime.strptime(str(tek_vrem), '%H:%M:%S').time()
                time_vved = datetime.strptime(str(time_of_pokaz), '%H:%M:%S').time()
                if time_vved < tek_vrem:
                    return "Указанное время уже прошло. Выберите более позднее время."
            # Проверяем прокат фильма
            cur.execute('SELECT * FROM films WHERE data_okon_procat >= %s and data_nach_procat <= %s and id_film = %s;', (data_seans, data_seans, film,))
            film_prokat = cur.fetchall()
            if len(film_prokat) == 0:
                return "В эту дату фильм не будет в прокате"
            # Проверяем по часам работы кинотеатра
            cur.execute("""
                    SELECT kinoteatr, time_otkrt, time_zakrt FROM zals 
                    JOIN kinoteatrs ON zals.kinoteatr = kinoteatrs.id_kinoteatrs
                    where id_zal = %s;
                        """,
                        (zal, ))
            rab_kinoteatr = cur.fetchall()
            time = datetime.strptime(str(time_of_pokaz), '%H:%M:%S').time()
            if time < rab_kinoteatr[0][1] and time >= rab_kinoteatr[0][2]:
                return "Кинотетр закрыт в веденное время"
            # cur.execute('SELECT * FROM seans WHERE id_zal = %s and data_seans= %s and time_seans= %s;', (d,))
            # film = cur.fetchall()
            # Проверяем что нет предыдущих незаконченных сеансов
            cur.execute("""
                    SELECT id_seans, time_seans, dliteln, (time_seans + dliteln) as okon_seans FROM seans 
                    JOIN films USING (id_film)
                    WHERE id_zal = %s AND data_seans = %s AND time_seans <= %s
                    ORDER BY okon_seans DESC
                    LIMIT 1;
            """,
                        (zal, data_seans, time_of_pokaz))
            res = cur.fetchall()
            if len(res) != 0:
                time1 = datetime.strptime(str(res[0][3]), '%H:%M:%S').time()
                time2 = datetime.strptime(str(time_of_pokaz), '%H:%M:%S').time()
                if time1 > time2:
                    return "Предыдущий фильм еще не окончен!"

            # Проверяем что не мешаем следующему сеансу
            cur.execute("""
                    SELECT id_seans, time_seans FROM seans 
                    WHERE id_zal = %s AND data_seans = %s AND time_seans >= %s
                    ORDER BY time_seans
                    LIMIT 1;
            """,
                        (zal, data_seans, time_of_pokaz))
            res1 = cur.fetchall()

            cur.execute("""
                           SELECT (%s + dliteln) as okon_vveden_seans 
                           FROM films where id_film = %s
                   """,
                        (time_of_pokaz, film))
            res2 = cur.fetchall()
            if len(res1) != 0:
                time1 = datetime.strptime(str(res1[0][1]), '%H:%M:%S').time()
                time2 = datetime.strptime(str(res2[0][0]), '%H:%M:%S').time()
                if time1 < time2:
                    print(res2[0][0])
                    return "На это время или позже уже поставлен сеанс на другой фильм. Зал не будет особожден для начала следующего сеанса!"

            # Проверяем чтоб сеанс успел закончится до закрытия кинотетра
            a = res2[0][0]
            # if type(a) != "class 'datetime.timedelta'":
            #     print('Это список')
            # print(type(res2[0][0]))
            n = a.seconds
            import time
            time_okon = time.strftime("%H:%M:%S", time.gmtime(n))
            time = datetime.strptime(str(time_okon), '%H:%M:%S').time()
            if time > rab_kinoteatr[0][2] and time < rab_kinoteatr[0][1]:
                print(time)
                print(rab_kinoteatr[0][2])
                return "Сеанс должен закончится до закрытия кинотеатра"

            print(film)
            print(data_seans)
            print(zal)
            print(forma)
            print(time_of_pokaz)
            print(price)
            bob = (film, zal, forma, data_seans, time_of_pokaz, price)
            account = session['id']
            try:
                cur.execute("INSERT INTO seans (id_film, id_zal, format, data_seans, time_seans, price) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_seans",
                        bob)
                conn.commit()

                id_s = cur.fetchall()[0]
                bob = (id_s, account)

                cur.execute(
                    "INSERT INTO createseans (id_seans, id_emp) VALUES (%s, %s)",
                    bob)
                conn.commit()

                cur.close()
                conn.close()
                return "Сеанс добавлен"
            except:
                return "Ошибка"
        else:
            return render_template('createTimeLisst.html', film=film, zals=zals)
    return redirect(url_for('adm'))

@app.route('/admin/ad_block/createTicket', methods=['POST', 'GET'])
def createTicket():
    if 'loggedin' in session:
        conn = get_db_connection()
        cur = conn.cursor()
        d = datetime.now().date()
        t = datetime.now().time()
        # Выбираем сеансы, на которые нет билетов + дата сеанса >= текущей даты
        cur.execute("""
                    SELECT id_seans, name_film, id_zal, format, data_seans, time_seans FROM seans
                    JOIN films USING (id_film)
                            WHERE NOT EXISTS(SELECT id_seans FROM tickets 
                                                WHERE id_seans = seans.id_seans 
                                                group by id_seans) and data_seans >= %s;
                            """,
                    (d,))
        seans = cur.fetchall()

        if request.method == "POST":
            id_seans = request.form['id_seans']
            cur.execute('SELECT * FROM seans WHERE id_seans = %s;', (id_seans,))
            seans = cur.fetchall()
            # data_sean = datetime.strptime(seans[0][4], "%Y-%m-%d").date()
            if d == seans[0][4]:
                if t > seans[0][5]:
                    return "Нельзя добавлять билеты на сеанс, время которого уже прошло"
            zal = seans[0][2]
            cur.execute("""
                           SELECT count(id_place) FROM places
                                where id_zal = %s;
                                    """,
                        (zal,))
            k_mest = cur.fetchall()

            cur.execute("""
                            SELECT id_place FROM places
                                where id_zal = %s;
                                            """,
                        (zal,))
            id_places = cur.fetchall()

            account = session['id']

            try:
                for i in range(k_mest[0][0]):
                    bob = (id_seans, id_places[i][0], account)
                    cur.execute(
                        "INSERT INTO tickets (id_seans, place, emp) VALUES (%s, %s, %s) RETURNING id_ticket",
                        bob)
                    conn.commit()

                    id_t = cur.fetchall()[0]
                    bob = (id_t, account)

                    cur.execute(
                        "INSERT INTO createtickets (id_ticket, id_emp) VALUES (%s, %s)",
                        bob)
                    conn.commit()

                cur.close()
                conn.close()
                return "Билеты добавлены"
            except:
                return "Ошибка"
        else:
            return render_template('createTicket.html', seans=seans)
    return redirect(url_for('adm'))

@app.route('/admin/ad_block/ydalseans', methods=['POST', 'GET'])
def ydalseans():
    if 'loggedin' in session:
        conn = get_db_connection()
        cur = conn.cursor()
        d = datetime.now().date()
        t = datetime.now().time()
        # Выбираем сеансы, на которые нет билетов + дата сеанса >= текущей даты
        cur.execute("""
                    SELECT id_seans, name_film, id_zal, format, data_seans, time_seans FROM seans
                    JOIN films USING (id_film);
                            """,
                    )
        seans = cur.fetchall()

        if request.method == "POST":
            id_seans = request.form['id_seans']
            try:
                cur.execute('DELETE FROM seans WHERE id_seans = %s;', (id_seans,))
                conn.commit()
                cur.close()
                conn.close()
                return "Сеанс удален"
            except:
                return "Ошибка"
        else:
            return render_template('ydalseans.html', seans=seans)
    return redirect(url_for('adm'))

@app.route('/admin/ad_block/ydalfilm', methods=['POST', 'GET'])
def ydalfilm():
    if 'loggedin' in session:
        conn = get_db_connection()
        cur = conn.cursor()
        # Выбираем сеансы, на которые нет билетов + дата сеанса >= текущей даты
        cur.execute("""
                    SELECT id_film, name_film FROM films;
                            """,
                    )
        films = cur.fetchall()

        if request.method == "POST":
            id_film = request.form['id_film']

            try:
                cur.execute('DELETE FROM films WHERE id_film = %s;', (id_film,))
                conn.commit()
                cur.close()
                conn.close()
                return "Фильм удален"
            except:
                return "Ошибка"
        else:
            return render_template('ydalfilm.html', films=films)
    return redirect(url_for('adm'))

@app.route('/admin/ad_block/ydalcust', methods=['POST', 'GET'])
def ydalcust():
    if 'loggedin' in session:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
                            SELECT * FROM customers;
                                    """)
        cust = cur.fetchall()

        if request.method == "POST":
            id_cust = request.form['id_cust']
            try:
                cur.execute('DELETE FROM customers WHERE id_customers = %s;', (id_cust,))
                conn.commit()
                cur.close()
                conn.close()
                return "Покупатель удален"
            except:
                return "Ошибка"
        else:
            return render_template('ydalcust.html', cust=cust)
    return redirect(url_for('adm'))

@app.route('/admin/ad_block/create_vozvrat', methods=['POST', 'GET'])
def createVozvrat():
    if 'loggedin' in session:
        conn = get_db_connection()
        cur = conn.cursor()

        d = datetime.now().date()
        d2 = datetime.now().date() + timedelta(days=2)
        # Проверяем фильмы (только те, которые в прокате + фильмы, чья дата проката через <= 2 дня)
        cur.execute('SELECT * FROM films WHERE data_okon_procat >= %s and data_nach_procat <= %s;', (d, d2,))
        film = cur.fetchall()

        cur.execute('SELECT * FROM zals;')
        zals = cur.fetchall()

        if request.method == "POST":
            id_c = request.form['id_c']
            film = request.form['film']
            data_seans = request.form['data']
            time_of_pokaz = request.form['time_of_pokaz']
            zal = request.form['zal']
            ryd = request.form['ryd']
            pl = request.form['pl']

            # Проверяем введенный формат времени
            import time
            date = time_of_pokaz
            try:
                valid_date = time.strptime(date, '%H:%M:%S')
            except ValueError:
                return "Неверный формат времени"

            # Проверяем дату (нельзя < текущей)
            data_sean = datetime.strptime(data_seans, "%Y-%m-%d").date()
            if d > data_sean:
                return "Нельзя возвращать билеты на уже прошедшие сеансы!"


            # Если текущая дата, проверяем чтоб нельзя было добавить сеанса на уже прошедшее время
            if d == data_sean:
                tek_vrem = datetime.today().strftime("%H:%M:%S")
                tek_vrem = datetime.strptime(str(tek_vrem), '%H:%M:%S').time()
                time_vved = datetime.strptime(str(time_of_pokaz), '%H:%M:%S').time()

                # t = datetime.now().time()
                # t = t + timedelta(minutes=30)
                #
                # clock_in_half_hour = datetime.today().strftime("%H:%M:%S")
                # tek_vrem_plus_h = datetime.strptime(str(clock_in_half_hour), '%H:%M:%S').time()
                # tek_vrem_plus_h += timedelta(minutes=30)

                x = datetime.now()
                y = x + timedelta(minutes=30)
                y = y.strftime("%H:%M:%S")
                tek_vrem_plus_h = datetime.strptime(str(y), '%H:%M:%S').time()

                if time_vved < tek_vrem:
                    return "Указанное время уже прошло. Нельзя возвращать билеты на уже прошедшие сеансы!"
                if time_vved <= tek_vrem_plus_h:
                    return "Нельзя возвращать билеты за пол часа до начала сеанса!"

            # Покупатель не найден
            cur.execute('SELECT * FROM customers WHERE e_mail >= %s;',
                        (id_c,))
            cust = cur.fetchall()
            if len(cust) == 0:
                return "Покупатель не найден"

            bob = (id_c, film, data_seans, time_of_pokaz, pl, ryd, zal)
            account = session['id']
            print(bob)
            cur.execute("""
                                   SELECT id_customers, e_mail, id_proda, id_ticket, id_employee, data_prodag, sum_prodag FROM customers 
                                    JOIN prodag USING (id_customers)
                                    JOIN tickets USING (id_ticket)
                                    JOIN seans USING (id_seans)
                                    JOIN films USING (id_film)
                                    JOIN places ON tickets.place = places.id_place
                                    JOIN zals ON zals.id_zal = places.id_zal
                                        WHERE e_mail = %s and id_film = %s
            	                                and data_seans = %s
            	                                and time_seans = %s and nom_place = %s and nom_ryd = %s
            	                                and zals.id_zal = %s
                            """,
                        (bob))
            res = cur.fetchall()
            print()
            if len(res) == 0:
                return "Билет не найден!"

            cur.execute('SELECT * FROM tickets WHERE id_ticket = %s;',
                        (res[0][3],))
            tick = cur.fetchall()

            if tick[0][4] == "в продаже":
                return "Билет находится в продаже!"

            bob = (res[0][3], account, res[0][0])
            print(bob)
            cur.execute("INSERT INTO vozvrats (id_ticket, id_emp, id_cust) VALUES (%s, %s, %s);",
                        bob)
            conn.commit()

            cur.execute("UPDATE tickets SET status=%s WHERE id_ticket=%s", ("в продаже", res[0][3]))
            conn.commit()

            cur.close()
            conn.close()
            return "Возврат сделан"
            # try:
            #
            # except:
            #     return "Ошибка"
        else:
            return render_template('createvozvrat.html', film=film, zals=zals)
    return redirect(url_for('adm'))

@app.route('/discounts')
def discounts():
    return render_template('discounts.html')

@app.route('/halls')
def Halls():
    return render_template('halls.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/polsSogl')
def PolsSogl():
    return render_template('polsSogl.html')

@app.route('/test')
def test():
    return render_template('TEST.html')

@app.route('/test2')
def test2():
    return render_template('TEST2.html')



@app.route('/test3')
def test3():
    return render_template('TEST3.html')


@app.route('/test4')
def test4():
    return render_template('test4.html')


if __name__ == "__main__":
    app.run(debug=True)





