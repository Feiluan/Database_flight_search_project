from flask import Flask, render_template, request, flash, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import random

app = Flask(__name__)
app.secret_key = 'key' #不配置这条会报错

# 配置数据库连接

db = mysql.connector.connect(host='localhost',
                            user='root',
                            password='',
                            database='finalproject')

@app.route('/')
def home():
    if 'user' in session:
        identity = session['user']['identity']
        return render_template('home.html', logged_in = True, identity=identity)
    else:
        return render_template('home.html', logged_in = False)
    # return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    def check_email_exists(email, cursor):
        query = """
        SELECT 1 FROM customer WHERE email = %s
        UNION
        SELECT 1 FROM booking_agent WHERE email = %s
        UNION
        SELECT 1 FROM airline_staff WHERE email = %s
        """
        cursor.execute(query, (email, email, email))
        return cursor.fetchone()

    # try:
    a = 1
    if a==1 :
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT airline_name FROM airline")
        airlines = cursor.fetchall()

        if request.method == 'POST':
            form_type = request.form.get('form_type')
            # print(form_type)

            existing_email_query = """
                SELECT 1 FROM customer WHERE email = %s
                UNION
                SELECT 1 FROM booking_agent WHERE email = %s
                UNION
                SELECT 1 FROM airline_staff WHERE email = %s
                """

            if form_type == 'customer':
                customer_email = request.form.get('customer_email').lower().split('@')[0] + '@' + request.form.get('customer_email').lower().split('@')[1]
                customer_name = request.form.get('customer_name')
                customer_password = request.form.get('customer_password')
                customer_building_number = request.form.get('customer_building_number')
                customer_street = request.form.get('customer_street')
                customer_city = request.form.get('customer_city')
                customer_state = request.form.get('customer_state')
                customer_phone = request.form.get('customer_phone')
                customer_passport = request.form.get('customer_passport')
                customer_passport_expire = request.form.get('customer_passport_expire')
                customer_nationality = request.form.get('customer_nationality')
                customer_birthday = request.form.get('customer_birthday')
                # print(customer_email, customer_name, customer_password) 

                # 验证注册输入信息是否为空
                if not all([
                    customer_email, customer_name, customer_password, 
                    customer_building_number, customer_street, customer_city, 
                    customer_state, customer_phone, customer_passport, 
                    customer_passport_expire, customer_nationality, customer_birthday
                ]):
                    flash('All fields are required!', 'danger')
                    return redirect(url_for('register'))

                # 检查是否已存在用户
                if check_email_exists(customer_email, cursor):
                    flash('Email already exists!', 'danger')
                    return redirect(url_for('register'))

                # 对密码进行加密
                hashed_password = generate_password_hash(customer_password, method='pbkdf2:sha256')

                # 将用户数据插入数据库
                query = """
                INSERT INTO customer (
                    email, name, password, building_number, street, city, state, phone_number, 
                    passport_number, passport_expiration, passport_country, date_of_birth
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                values = (customer_email, customer_name, hashed_password, customer_building_number, customer_street, customer_city, customer_state, customer_phone, customer_passport, customer_passport_expire, customer_nationality, customer_birthday)
                cursor.execute(query, values)
                db.commit()
                cursor.close()

                flash('Registration successful! You can now log in.', 'success')
                return redirect(url_for('register'))  # 注册成功后重定向到主页或其他页面
            
            elif form_type == 'agent':
                agent_email = request.form.get('agent_email').lower().split('@')[0] + '@' + request.form.get('agent_email').lower().split('@')[1]
                agent_password = request.form.get('agent_password')
                agent_id = request.form.get('agent_id')

                if not all([agent_email, agent_password, agent_id]):
                    flash('All fields are required!', 'danger')
                    return redirect(url_for('register'))
                
                if check_email_exists(agent_email, cursor):
                    flash('Email already exists!', 'danger')
                    return redirect(url_for('register'))
                
                # Check if agent_id already exists
                existing_agent_id_query = "SELECT 1 FROM booking_agent WHERE booking_agent_id = %s"
                cursor.execute(existing_agent_id_query, (agent_id,))
                existing_agent_id = cursor.fetchone()
                if existing_agent_id:
                    flash('Agent ID already exists!', 'danger')
                    return redirect(url_for('register'))

                
                hashed_password = generate_password_hash(agent_password, method='pbkdf2:sha256')
                query = """
                    INSERT INTO booking_agent (
                        email, password, booking_agent_id
                    ) VALUES (%s, %s, %s)
                    """
                values = (agent_email, hashed_password, agent_id)
                cursor.execute(query, values)
                db.commit()
                cursor.close()

                flash('Booking Agent registration successful!', 'success')
                return redirect(url_for('register'))
            
            elif form_type == 'staff':
                staff_email = request.form.get('staff_email').lower().split('@')[0] + '@' + request.form.get('staff_email').lower().split('@')[1]
                staff_password = request.form.get('staff_password')
                staff_first_name = request.form.get('staff_first_name')
                staff_last_name = request.form.get('staff_last_name')
                staff_birthday = request.form.get('staff_birthday')
                staff_airline_name = request.form.get('staff_airline_name')
                # print(staff_airline_name)

                if not all([staff_email, staff_password, staff_first_name, staff_last_name, staff_birthday, staff_airline_name]):
                    flash('All fields are required!', 'danger')
                    return redirect(url_for('register'))
                
                if check_email_exists(staff_email, cursor):
                    flash('Email already exists!', 'danger')
                    return redirect(url_for('register'))
            
                hashed_password = generate_password_hash(staff_password, method='pbkdf2:sha256')
                query = """
                    INSERT INTO airline_staff (
                        email, password, first_name, last_name, date_of_birth, airline_name
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    """
                values = (staff_email, hashed_password, staff_first_name, staff_last_name, staff_birthday, staff_airline_name)
                cursor.execute(query, values)
                db.commit()
                cursor.close()

                flash('Airline Staff registration successful!', 'success')
                return redirect(url_for('register'))
            
    # except mysql.connector.Error as err:
    #         print(f"Database error: {err}")
    #         flash("Database error. Please try again later.", "error")
    #         return redirect(url_for('register'))
    # finally:
    #     if db.is_connected():
    #         print('register-finally')
    #         cursor.close()

    return render_template('register.html',airlines=airlines)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #get what user input in the login page
        email = request.form.get('login_email').lower().split('@')[0] + '@' + request.form.get('login_email').split('@')[1]
        password = request.form.get('login_password')  #这里get到的密码应该是输入进去什么就是什么，输入1这里就是1
        identity = request.form.get('login_identity')
        # print(email, password, identity)

        #通过identity定位我从哪个table里面查找我的用户
        table_map = {
            'staff': 'airline_staff',
            'customer': 'customer',
            'agent': 'booking_agent'
        }
        table_name = table_map[identity]
        print(table_name) 

        # try:
        cursor = db.cursor(dictionary=True)

        query = f"SELECT * FROM {table_name} WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        print("this is a user test,",user)

        if user and check_password_hash(user['password'], password):
            session['user'] = {
                'email': user['email'],
                'identity': identity
            }

            flash("Login successful!", "success")
            print(f"Redirecting to {identity}_dashboard test")

            if identity == 'customer':
                print(f"Redirecting to {identity}_dashboard")
                return redirect(url_for('customer_dashboard'))
                # print(f"Redirecting to {identity}_dashboard")
            elif identity == 'agent':
                session['user']['agent_id'] = user['booking_agent_id']
                print(session)
                print(f"Redirecting to {identity}_dashboard")
                return redirect(url_for('agent_dashboard'))
            elif identity == 'staff':
                session['user']['airline_name'] = user['airline_name']
                cursor.execute("SELECT permission_type FROM permission WHERE email = %s", (email,))
                permissions = cursor.fetchall()
                # print("permission get from database",permissions)

                if permissions:
                    # 提取权限类型的值
                    session['user']['permissions'] = [permission['permission_type'] for permission in permissions]
                else:
                    session['user']['permissions'] = []  # 没有权限时为空列表
                # print("permissions after processing:", session['user']['permissions'])   
                             
                # 权限为空 设置一个默认值
                if not session['user']['permissions']:
                    session['user']['permissions'] = ['None']
    
                print(session)
                print(f"Redirecting to {identity}_dashboard")

                return redirect(url_for('staff_dashboard'))
        else:
            # 登录失败
            flash("Invalid email or password. Please try again.", "error")
            return redirect(url_for('login'))
        
        # except mysql.connector.Error as err:
        #     print(f"Database error: {err}")
        #     flash("Database error. Please try again later.", "error")
        #     return redirect(url_for('login'))
        # finally:
        #     print('login-finally')
        #     cursor.close()

    return render_template('login.html')


@app.route('/dashboard/customer', methods=['GET', 'POST'])
def customer_dashboard():
    if 'user' not in session:
        return redirect(url_for('login')) 
    
    customer_email = session['user']['email']
    cursor = db.cursor(dictionary=True)
    booked_flights = []
    
    #给clear_filter用，传递上一次按filter selector的日期
    clear_filter = request.args.get('clear_filter', False)
    if clear_filter:
        start_date = None
        end_date = None

    if not clear_filter:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date') 
        # print("filter my flight: ", start_date,end_date)
    
    #没select日期的话直接显示所有你预定过的航班
    #part: my flights
    if not start_date and not end_date:
        query = """
            SELECT 
                f.airline_name,
                f.flight_num,
                f.departure_airport,
                f.departure_time,
                f.arrival_airport,
                f.arrival_time,
                f.status,
                p.ticket_id
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
            WHERE p.customer_email = %s AND f.status = 'upcoming'
            ORDER BY f.departure_time ASC;
        """
        cursor.execute(query, (customer_email,))
    elif start_date and end_date:
        if start_date > end_date:
            flash('Start Date cannot be later than End Date!', 'danger')
        query = """
            SELECT 
                f.airline_name,
                f.flight_num,
                f.departure_airport,
                f.departure_time,
                f.arrival_airport,
                f.arrival_time,
                f.status,
                p.ticket_id
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
            WHERE p.customer_email = %s AND f.departure_time BETWEEN %s AND %s
            ORDER BY f.departure_time ASC;
        """
        cursor.execute(query, (customer_email, start_date, end_date))

    elif (not start_date and end_date) or (start_date and not end_date):
        flash('Please select both date!', 'danger') #已经javascript加过了但是这里也警告一下
        
    booked_flights = cursor.fetchall()
    print("booked flights:",booked_flights) 











    if request.method == 'POST':
        money_start_date = request.form.get('money_start_date')
        money_end_date = request.form.get('money_end_date')
    else:
        money_start_date = None
        money_end_date = None
    
    money_spend = []
    monthly_spending = []
    print("money count range:", money_start_date,money_end_date)


    if money_start_date and money_end_date:
        # 显示选择范围内的总spending
        query_total_spent = """
                SELECT 
                    SUM(f.price) as money_spend_in_range
                FROM purchases p
                JOIN ticket t ON p.ticket_id = t.ticket_id
                JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
                WHERE p.customer_email = %s
                AND p.purchase_date BETWEEN %s AND %s;
            """
        cursor.execute(query_total_spent, (customer_email, money_start_date, money_end_date))
        total_spent_result = cursor.fetchone()
        if total_spent_result and total_spent_result['money_spend_in_range']:
            money_spend = total_spent_result['money_spend_in_range']
        else:
            money_spend = 0
        # print("money_spend_in select range: ", money_spend)

        # 显示选择范围内的总spending里面如果这个月有开销的话bar chart
        query_monthly_spending = """
            SELECT 
                DATE_FORMAT(p.purchase_date, '%Y-%m') AS month,  -- 格式化为 YYYY-MM
                SUM(f.price) AS monthly_money_spent
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
            WHERE p.customer_email = %s
            AND p.purchase_date BETWEEN %s AND %s
            GROUP BY month
            ORDER BY month;
        """
        cursor.execute(query_monthly_spending, (customer_email, money_start_date, money_end_date))
        monthly_spending = cursor.fetchall()

        money_time_range_label = f"from {money_start_date} to {money_end_date}"


    else:
        #part: 显示money_spend_last_year,默认显示前365天的，但是可以通过filter调整
        query_money_spend_last_year = """
                SELECT 
                    SUM(f.price) as money_spend_last_year
                FROM purchases p
                JOIN ticket t ON p.ticket_id = t.ticket_id
                JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
                WHERE p.customer_email = %s
                AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR);
            """
        cursor.execute(query_money_spend_last_year, (customer_email, ))
        money_spend_last_year = cursor.fetchone()
        if money_spend_last_year and money_spend_last_year['money_spend_last_year']:
            money_spend = money_spend_last_year['money_spend_last_year']
        else:
            money_spend = 0
        # print("money_spend_last_year: ", money_spend)


        # part:画表bar chart for past 6 month
        # -- 格式化为 YYYY-MM
        last_6_months_spending = []
        
        query_last_6_months = """
            SELECT 
                DATE_FORMAT(p.purchase_date, '%Y-%m') AS month,  
                SUM(f.price) AS monthly_money_spent
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
            WHERE p.customer_email = %s
            AND p.purchase_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY month
            ORDER BY month;
        """
        cursor.execute(query_last_6_months, (customer_email,))
        last_6_months_spending = cursor.fetchall()
        # print("last_6_months_spending: ",last_6_months_spending)

        #last_6_months_spending = 从数据库里面拉出来了的last_6_months_soending
        months = [(datetime.today() - timedelta(days=30 * i)).strftime("%Y-%m") for i in range(5, -1, -1)]
        last_6_months_spending = {item['month']: item['monthly_money_spent'] for item in last_6_months_spending}
        # print("last_6_months_spending: ",last_6_months_spending)

        #last_6_months_spending, 如果某个月不存在支出记录，补全为0
        monthly_spending = [
            {"month": month, "monthly_money_spent": last_6_months_spending.get(month, 0)} for month in months
        ]
        print("last_6_months_spending python fix: ",last_6_months_spending)

        money_time_range_label = "in the past 12 months"


    for item in monthly_spending:
        item['monthly_money_spent'] = float(item['monthly_money_spent'])

    monthly_spending_json = json.dumps(monthly_spending)
    print("last_6_months_spending_json:", monthly_spending_json)  # 在后端打印输出 JSON

    db.commit()
    cursor.close()

    return render_template('dashboard/customer.html', 
                           booked_flights = booked_flights, start_date = start_date, end_date = end_date,
                           money_spend = money_spend, monthly_spending = monthly_spending_json, money_time_range_label = money_time_range_label)


@app.route('/cancel/<ticket_id>', methods=['POST'])
def cancel_ticket(ticket_id):
    if 'user' not in session:
        return redirect(url_for('login'))

    customer_email = session['user']['email']
    cursor = db.cursor()

    try:
        # 删除购买记录
        cursor.execute("DELETE FROM purchases WHERE ticket_id = %s AND customer_email = %s", (ticket_id, customer_email))

        # 删除票务记录
        cursor.execute("DELETE FROM ticket WHERE ticket_id = %s", (ticket_id,))
        db.commit()

        flash("Flight successfully canceled.", "success")
    except Exception as e:
        db.rollback()
        flash("An error occurred while canceling the flight. Please try again.", "danger")
        # print(f"Error: {e}")
    finally:
        cursor.close()

    return redirect(url_for('customer_dashboard'))


@app.route('/dashboard/agent', methods=['GET', 'POST'])
def agent_dashboard():
    # 如果没有登录，跳转到登录页
    if 'user' not in session:
        return redirect(url_for('login'))  
    
    agent_email = session['user']['email']
    agent_id = session['user']['agent_id']
    cursor = db.cursor(dictionary=True)
    
    # airline agent not working for
    cursor.execute("""
        SELECT airline_name 
        FROM airline 
        WHERE airline_name NOT IN (
            SELECT airline_name 
            FROM booking_agent_work_for 
            WHERE email = %s
        )""", (agent_email,))
    airlines_not_working_for = cursor.fetchall()  

    # 目前的booking_agent_work_for
    cursor.execute("SELECT airline_name FROM booking_agent_work_for WHERE email = %s", (agent_email,))
    airlines_working_for = cursor.fetchall()  
    airlines_working_for = [record['airline_name'] for record in airlines_working_for]
    print("this is test", airlines_working_for)


    # if request.method == 'POST':
    #     action = request.form.get('action')
    #     airline_name = request.form.get('airline_name')

    #     if request.form.get('action') == 'add_working_airline':
    #         # 添加航空公司到booking_agent_work_for
    #         cursor.execute("INSERT INTO booking_agent_work_for (email, airline_name) VALUES (%s, %s)", (agent_email, airline_name))
    #         db.commit()
    #         flash('Airline added successfully!', 'success')

    #     elif action == 'remove_working_airline':
    #         # 从booking_agent_work_for中删除航空公司
    #         cursor.execute("DELETE FROM booking_agent_work_for WHERE email = %s AND airline_name = %s", (agent_email, airline_name))
    #         db.commit()
    #         flash('Airline removed successfully!', 'success')

    #     return redirect(url_for('agent_dashboard'))





    #View My flights
    booked_flights = []

    #给clear_filter用，传递上一次按filter selector的日期
    clear_filter = request.args.get('clear_filter', False)
    if clear_filter:
        start_date = None
        end_date = None
    else:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date') 
        print("filter my flight: ", start_date,end_date)
    
    #没select日期的话直接显示所有你预定过的航班，默认只显示upcoming的
    #part: my flights
    if not start_date and not end_date:
        query = """
            SELECT 
                p.customer_email,
                f.airline_name,
                f.flight_num,
                f.departure_airport,
                f.departure_time,
                f.arrival_airport,
                f.arrival_time,
                f.status
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
            WHERE p.booking_agent_id = %s AND status = 'upcoming'
            ORDER BY f.departure_time ASC;
        """
        cursor.execute(query, (agent_id, ))
        booked_flights = cursor.fetchall()
        print(booked_flights) 

    elif (start_date and end_date):
        if start_date > end_date:
            flash('Start Date cannot be later than End Date!', 'danger')
            
        query = """
            SELECT 
                p.customer_email,
                f.airline_name,
                f.flight_num,
                f.departure_airport,
                f.departure_time,
                f.arrival_airport,
                f.arrival_time,
                f.status
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
            WHERE p.booking_agent_id = %s AND f.departure_time BETWEEN %s AND %s
            ORDER BY f.departure_time ASC;
        """
        cursor.execute(query, (agent_id, start_date, end_date))
        booked_flights = cursor.fetchall()
        print(booked_flights) 

    elif (not start_date and end_date) or (start_date and not end_date):
        flash('Please select both date!', 'danger') #已经javascript加过了但是这里也警告一下
        
    


    # View my commission
    now = datetime.now()
    if request.form.get('clear_filter'):  # 用户点击清除筛选按钮
        my_commission_start_date = (now - timedelta(days=30)).strftime('%Y-%m-%d')  # 默认过去一个月
        my_commission_end_date = now.strftime('%Y-%m-%d')
    else:  # 使用用户选择的日期范围或默认值
        my_commission_start_date = request.form.get('my_commission_start_date') or (now - timedelta(days=30)).strftime('%Y-%m-%d')
        my_commission_end_date = request.form.get('my_commission_end_date') or now.strftime('%Y-%m-%d')


    query = """
        SELECT 
            SUM(flight.price * 0.1) AS total_commission,
            COUNT(ticket.ticket_id) AS total_tickets
        FROM ticket
        JOIN purchases ON ticket.ticket_id = purchases.ticket_id
        JOIN flight ON ticket.flight_num = flight.flight_num
        WHERE purchases.booking_agent_id = %s 
        AND purchases.purchase_date BETWEEN %s AND %s;
    """
    cursor.execute(query, (agent_id, my_commission_start_date, my_commission_end_date))
    my_commission = cursor.fetchone()
    total_commission = my_commission['total_commission'] or 0.0
    total_tickets = my_commission['total_tickets'] or 0
    average_commission = total_commission / total_tickets if total_tickets > 0 else 0.0




    #customer的barchart两张
    # if request.method == 'POST':
    #     ticket_start_date = request.form.get('ticket_start_date')
    #     ticket_end_date = request.form.get('ticket_end_date')
    # else:
    #     ticket_start_date = None
    #     ticket_end_date = None
    # print("ticket date:",ticket_start_date,ticket_end_date)
    ticket_end_date = datetime.now()
    ticket_start_date = ticket_end_date - timedelta(days=6*30)
    print()
    # print('this is day filter:',ticket_end_date,ticket_start_date)

    query = """
        SELECT p.customer_email, COUNT(*) as ticket_count
        FROM purchases p
        JOIN ticket t ON p.ticket_id = t.ticket_id
        WHERE p.booking_agent_id = %s AND p.purchase_date BETWEEN %s AND %s
        GROUP BY p.customer_email
        ORDER BY ticket_count DESC
        LIMIT 5;
    """
    # query = """
    #     SELECT p.passport_number, COUNT(*) as ticket_count
    #     FROM purchases p
    #     JOIN ticket t ON p.ticket_id = t.ticket_id
    #     WHERE p.booking_agent_id = %s AND p.purchase_date BETWEEN %s AND %s
    #     GROUP BY p.passport_number
    #     ORDER BY ticket_count DESC
    #     LIMIT 5;
    # """
    cursor.execute(query, (agent_id, ticket_start_date, ticket_end_date))
    top_customers_ticket = cursor.fetchall()
    print('top customer ticket:', top_customers_ticket)
    
    top_customers_ticket_json = json.dumps(top_customers_ticket)
    print('top customer ticket json:',top_customers_ticket_json)



    commission_end_date = datetime.now()
    commission_start_date = commission_end_date - timedelta(days=12*30)
    print()
    print('this is day filter:',commission_end_date,commission_start_date)

    query = """
        SELECT p.customer_email, SUM(f.price*0.1) AS ticket_commission
        FROM purchases p
        JOIN ticket t ON p.ticket_id = t.ticket_id
        JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
        WHERE p.booking_agent_id = %s 
        AND p.purchase_date BETWEEN %s AND %s
        GROUP BY p.customer_email
        ORDER BY ticket_commission DESC
        LIMIT 5;
    """
    # query = """
    #     SELECT p.passport_number, SUM(f.price*0.1) AS ticket_commission
    #     FROM purchases p
    #     JOIN ticket t ON p.ticket_id = t.ticket_id
    #     JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
    #     WHERE p.booking_agent_id = %s 
    #     AND p.purchase_date BETWEEN %s AND %s
    #     GROUP BY p.passport_number
    #     ORDER BY ticket_commission DESC
    #     LIMIT 5;
    # """

    cursor.execute(query, (agent_id, commission_start_date, commission_end_date))
    top_customers_commission = cursor.fetchall()
    print('top customer commision:', top_customers_commission)

    for item in top_customers_commission:
        item['ticket_commission'] = float(item['ticket_commission'])
    print(top_customers_commission)
    
    top_customers_commission_json = json.dumps(top_customers_commission)
    print('top customer ticket json:',top_customers_commission)


    
    cursor.close()
    return render_template('dashboard/agent.html', 
                           airlines_not_working_for=airlines_not_working_for, airlines_working_for=airlines_working_for, 
                           booked_flights = booked_flights, start_date = start_date, end_date = end_date,
                           ticket_start_date = ticket_start_date,ticket_end_date = ticket_end_date,
                           commission_start_date = commission_start_date, commission_end_date = commission_end_date,
                           top_customers_ticket = top_customers_ticket_json, top_customers_commission = top_customers_commission_json,
                           total_commission = total_commission,total_tickets = total_tickets, average_commission = average_commission,
                           my_commission_start_date = my_commission_start_date, my_commission_end_date = my_commission_end_date)


@app.route('/dashboard/staff')
def staff_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))  
    
    staff_email = session['user']['email']
    staff_airline = session['user']['airline_name']
    staff_permission = session['user']['permissions']
    cursor = db.cursor(dictionary=True)


    print("permission:",staff_permission)
    print("staff airline name:",staff_airline)
    print()


    # if request.method == 'POST':
    form_type = request.form.get('form_type')
    print("form_type:", form_type)
    print()

   



    # if form_type == 'default':
    



    # View all the flights of airline功能
    flight_start_date = request.args.get('flight_start_date')
    flight_end_date = request.args.get('flight_end_date')
    flight_departure_airport = request.args.get('flight_departure_airport')
    flight_arrival_airport = request.args.get('flight_arrival_airport')
    flight_status_selector = request.args.get('flight_status_selector')

    #clear_filter用，传递上一次按filter selector的日期
    clear_filter = request.args.get('clear_filter', False)
    if clear_filter:
        flight_start_date = None
        flight_end_date = None
        flight_departure_airport = None
        flight_arrival_airport = None
        flight_status_selector = None
    
    now = datetime.now()
    default_flight_start_date = now
    default_flight_end_date = now + timedelta(days=30)
    default_status = 'Upcoming'

    query = """
        SELECT * 
        FROM flight
        WHERE airline_name = %s
    """
    search_condition = [staff_airline]

    if flight_start_date or flight_end_date:
        # 输入了时间范围，不限制 status
        query += " AND departure_time BETWEEN %s AND %s"
        search_condition.append(flight_start_date if flight_start_date else default_flight_start_date)
        search_condition.append(flight_end_date if flight_end_date else default_flight_end_date)
        
        if flight_start_date and flight_end_date:
            if (flight_start_date > flight_end_date):
                flash('Start Date cannot be later than End Date!', 'danger')

    else:
        # 使用默认时间范围
        query += " AND departure_time BETWEEN %s AND %s"
        search_condition.append(default_flight_start_date)
        search_condition.append(default_flight_end_date)
        
    if flight_status_selector and flight_status_selector != "*":
        query += " AND status = %s"
        search_condition.append(flight_status_selector)
    elif not (flight_start_date or flight_end_date):
        # 默认状态为 'upcoming'，仅在没有用户提供时间范围时应用
        query += " AND status = %s"
        search_condition.append(default_status)
    
    if flight_departure_airport:
        query += " AND departure_airport = %s"
        search_condition.append(flight_departure_airport)

    # 目的地条件
    if flight_arrival_airport:
        query += " AND arrival_airport = %s"
        search_condition.append(flight_arrival_airport)

    cursor.execute(query,tuple(search_condition))
    airline_flight = cursor.fetchall()
    # print(airline_flight)
    #View all the flights of airline功能




    #view top 5 booking agent 买票最多功能,分last month和year
    query_tickets_month = """
        SELECT ba.email AS agent_email, COUNT(p.ticket_id) AS ticket_sales
        FROM booking_agent ba
        JOIN purchases p ON ba.booking_agent_id = p.booking_agent_id
        JOIN ticket t ON p.ticket_id = t.ticket_id
        WHERE t.airline_name = %s AND p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 MONTH) AND NOW()
        GROUP BY ba.email
        ORDER BY ticket_sales DESC
        LIMIT 5;
    """
    cursor.execute(query_tickets_month, (staff_airline,))
    top_ticket_booking_agents_month = cursor.fetchall()

    top_ticket_booking_agents_month_json = json.dumps(top_ticket_booking_agents_month)
    print('top customer ticket month json:',top_ticket_booking_agents_month_json)

    query_tickets_year = """
        SELECT ba.email AS agent_email, COUNT(p.ticket_id) AS ticket_sales
        FROM booking_agent ba
        JOIN purchases p ON ba.booking_agent_id = p.booking_agent_id
        JOIN ticket t ON p.ticket_id = t.ticket_id
        WHERE t.airline_name = %s AND p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 12 MONTH) AND NOW()
        GROUP BY ba.email
        ORDER BY ticket_sales DESC
        LIMIT 5;
    """
    cursor.execute(query_tickets_year, (staff_airline,))
    top_ticket_booking_agents_year = cursor.fetchall()

    top_ticket_booking_agents_year_json = json.dumps(top_ticket_booking_agents_year)
    print('top customer ticket year json:',top_ticket_booking_agents_year_json)

    #view top 5 booking agent commission最多功能
    query_commissions = """
        SELECT ba.email AS agent_email, SUM(f.price * 0.1) AS total_commission
        FROM booking_agent ba
        JOIN purchases p ON ba.booking_agent_id = p.booking_agent_id
        JOIN ticket t ON p.ticket_id = t.ticket_id
        JOIN flight f ON t.flight_num = f.flight_num AND t.airline_name = f.airline_name
        WHERE t.airline_name = %s AND p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 YEAR) AND NOW()
        GROUP BY ba.email
        ORDER BY total_commission DESC
        LIMIT 5;
    """
    cursor.execute(query_commissions, (staff_airline,))
    top_commission_booking_agents = cursor.fetchall()
    # print("top_commission_booking_agents:", top_commission_booking_agents)

    for item in top_commission_booking_agents:
        item['total_commission'] = float(item['total_commission'])
    
    top_commission_booking_agents_json = json.dumps(top_commission_booking_agents)
    print('top customer ticket json:',top_commission_booking_agents_json)
    print()
    #view top 5 booking agent
    
    




    #view most frequent customer
    query_frequent_customer = """
        SELECT p.customer_email, COUNT(*) AS flight_count
        FROM purchases p
        JOIN ticket t ON p.ticket_id = t.ticket_id
        JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
        WHERE f.airline_name = %s
        AND p.purchase_date BETWEEN DATE_SUB(NOW(), INTERVAL 1 YEAR) AND NOW()
        GROUP BY p.customer_email
        ORDER BY flight_count DESC
        LIMIT 1;
    """
    cursor.execute(query_frequent_customer, (staff_airline,))
    most_frequent_customer = cursor.fetchone()
    print("frequent_customer:",most_frequent_customer)






    

    #view top 5 booking agent功能
    airline_booking_agent = []
    print()

    db.commit()
    cursor.close()
    
    return render_template('dashboard/staff.html', airline_booking_agent = airline_booking_agent, airline_flight = airline_flight, 
                           flight_start_date = flight_start_date, flight_end_date = flight_end_date,
                           flight_departure_airport = flight_departure_airport, flight_arrival_airport = flight_arrival_airport,
                           flight_status_selector = flight_status_selector,
                           top_ticket_booking_agents_month = top_ticket_booking_agents_month_json, 
                           top_ticket_booking_agents_year = top_ticket_booking_agents_year_json, 
                           top_commission_booking_agents =  top_commission_booking_agents_json,
                           frequent_customer = most_frequent_customer)

@app.route('/operator', methods=['GET', 'POST'])
def operator():
    # 验证用户是否登录和权限
    if 'user' not in session or session['user']['identity'] != 'staff' or 'Operator' not in session['user']['permissions']:
        flash("You do not have the required operator permissions.", "danger")
        return redirect(url_for('login'))

    airline_name = session['user']['airline_name']
    cursor = db.cursor(dictionary=True)

    # 显示航班信息（GET 请求）
    if request.method == 'GET':
        query = """
            SELECT flight_num, departure_airport, arrival_airport, departure_time, arrival_time, status
            FROM flight
            WHERE airline_name = %s AND status != 'Completed'
        """
        cursor.execute(query, (airline_name,))
        airline_flight = cursor.fetchall()

        cursor.close()

        return render_template('operator.html', airline_flight=airline_flight)

    # 更新航班状态（POST 请求）
    elif request.method == 'POST':
        flight_num = request.form.get('flight_num')
        new_status = request.form.get('status')

        if not flight_num or not new_status:
            flash("Flight number and status are required.", "danger")
            return redirect(url_for('change_flight_status'))

        # 更新航班状态
        cursor.execute("""
            UPDATE flight
            SET status = %s
            WHERE flight_num = %s AND airline_name = %s
        """, (new_status, flight_num, airline_name))
        db.commit()
        flash(f"Flight {flight_num} status updated to {new_status}.", "success")
        cursor.close()

        return redirect(url_for('operator'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # print('\n', session['user']['permissions'])
    if 'user' not in session or session['user']['identity'] != 'staff' or 'Admin' not in session['user']['permissions']:
        flash("You do not have the required admin permissions.", "danger")
        return redirect(url_for('login'))

    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add_airplane':
            airplane_id = request.form.get('airplane_id')
            airline_name = session['user']['airline_name']
            seats = request.form.get('seats')

            if not all([airplane_id, airline_name, seats]):
                flash("All fields are required to add a new airplane.", "danger")
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM airplane 
                    WHERE airplane_id = %s AND airline_name = %s """
                    , (airplane_id, airline_name))
                existing_airplane_count = cursor.fetchone()[0]

                if existing_airplane_count > 0:
                    flash("An airplane with the same ID already exists for this airline.", "danger")
                else:
                    cursor.execute("""
                        INSERT INTO airplane (airplane_id, airline_name, seats)
                        VALUES (%s, %s, %s)
                    """, (airplane_id, airline_name, seats))
                    db.commit()
                    flash("Airplane added successfully!", "success")

        elif action == 'add_airport':
            airport_name = request.form.get('airport_name')
            airport_city = request.form.get('airport_city')

            if not all([airport_name, airport_city]):
                flash("All fields are required to add a new airport.", "danger")
            else:
                cursor.execute("""
                    INSERT INTO airport (airport_name, airport_city)
                    VALUES (%s, %s)
                """, (airport_name, airport_city))
                db.commit()
                flash("Airport added successfully!", "success")

        elif action == 'add_agent':
            agent_email = request.form.get('agent_email').lower()

            if not agent_email:
                flash("Agent email is required.", "danger")
            else:
                cursor.execute("""
                    INSERT INTO booking_agent_work_for (email, airline_name)
                    VALUES (%s, %s)
                """, (agent_email, session['user']['airline_name']))
                db.commit()
                flash("Booking agent added successfully!", "success")

        elif action == 'grant_permission':
            staff_email = request.form.get('staff_email').lower()
            permission_type = request.form.get('permission_type')

            if not all([staff_email, permission_type]):
                flash("All fields are required to grant permissions.", "danger")
            else:
                cursor.execute("""
                    INSERT INTO permission (email, permission_type)
                    VALUES (%s, %s)
                """, (staff_email, permission_type))
                db.commit()
                flash(f"Permission '{permission_type}' granted to {staff_email}.", "success")

    # Fetch all airplanes
    cursor.execute("""
        SELECT airplane_id, seats
        FROM airplane
        WHERE airline_name = %s
    """, (session['user']['airline_name'],))
    airplanes = cursor.fetchall()

    cursor.close()
    return render_template('admin.html', airplanes=airplanes)


@app.route('/add_flight', methods=['GET', 'POST'])
def add_flight():
    if 'user' not in session or session['user']['identity'] != 'staff' or 'Admin' not in session['user']['permissions']:
        flash("You do not have the required admin permissions to add flights.", "danger")
        return redirect(url_for('login'))
    airplane_id = request.args.get('airplane_id')

    if airplane_id:
        session['airplane_id'] = airplane_id
        print("Saving Airplane ID:", airplane_id) 
    
    if not airplane_id and not session['airplane_id']:
        flash("Airplane ID is required to add a flight.", "danger")
        return redirect(url_for('admin'))
    
    print("Current Airplane ID:", airplane_id)

    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status
        FROM flight
        WHERE airplane_id = %s AND status != 'Completed'
        ORDER BY departure_time ASC
    """, (airplane_id,))
    flights = cursor.fetchall()
        
    if request.method == 'POST':
        airline_name = session['user']['airline_name']
        flight_num = request.form.get('flight_num')
        departure_airport = request.form.get('departure_airport')
        arrival_airport = request.form.get('arrival_airport')
        departure_time = request.form.get('departure_time')
        arrival_time = request.form.get('arrival_time')
        price = request.form.get('price')
        status = request.form.get('status')
        airplane_id = session['airplane_id']

        print("Inserting Airplane ID:", airplane_id) 
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO flight (airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, airplane_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price, status, airplane_id))
        db.commit()
        cursor.close()
        flash("Flight added successfully!", "success")
        return redirect(url_for('admin'))

    return render_template('add_flight.html', airplane_id=airplane_id, flights=flights)



@app.route('/passengers', methods = ['GET', 'POST'])
def passengers():
    cursor = db.cursor(dictionary=True)
    flight_num = request.args.get('flight_num')
    airline_name = request.args.get('airline_name')
    print("flight num and airline name:", flight_num, airline_name)

    if not flight_num or not airline_name:
        flash("Invalid flight details provided.", "danger")
        return redirect('/dashboard/staff.html')  
    
    query = """
        SELECT *
        FROM ticket
        JOIN purchases ON ticket.ticket_id = purchases.ticket_id
        WHERE ticket.flight_num = %s AND ticket.airline_name = %s
    """
    cursor.execute(query, (flight_num, airline_name))
    passengers = cursor.fetchall()
    print("this is passengers for this flight:", passengers)

    cursor.close()
    return render_template('passengers.html',passengers = passengers, flight_num = flight_num)


@app.route('/customer_history', methods=['GET','POST'])
def frequent_customers():
    cursor = db.cursor(dictionary=True)
    customer_email = request.form.get('customer_email')

    if not customer_email:
        flash("Please provide a valid email address.", "danger")
        return redirect('/dashboard/staff')  # 返回到某个默认页面

    # 查询数据库获取与该客户相关的飞行记录
    query = """
        SELECT ticket.ticket_id, ticket.flight_num, flight.departure_time
        FROM ticket
        JOIN purchases ON ticket.ticket_id = purchases.ticket_id
        JOIN flight ON flight.flight_num = ticket.flight_num
        WHERE purchases.customer_email = %s
    """
    cursor.execute(query, (customer_email,))
    flight_history = cursor.fetchall()
    print("this is flight history for customer", flight_history)

    cursor.close()
    return render_template('customer_history.html', flight_history=flight_history, customer_email=customer_email)


@app.route('/sales_report', methods=['GET','POST'])
def sales_report():
    if 'user' not in session:
        return redirect(url_for('login')) 
 
    cursor = db.cursor(dictionary=True)
    airline_name = session['user']['airline_name']
    
    now = datetime.now()
    if request.form.get('clear_filter'):
        start_date = (now - timedelta(days=365)).strftime('%Y-%m-%d')  # 默认过去一年
        end_date = now.strftime('%Y-%m-%d')
    else:
        start_date = request.form.get('start_date') or (now - timedelta(days=365)).strftime('%Y-%m-%d')
        end_date = request.form.get('end_date') or now.strftime('%Y-%m-%d')

    #动态，查询Total Sales from srart to end ，默认一年
    query = """
        SELECT 
            DATE_FORMAT(purchases.purchase_date, '%Y-%m') AS month, 
            COUNT(ticket.ticket_id) AS total_tickets, 
            SUM(flight.price) AS total_amount
        FROM ticket
        JOIN purchases ON ticket.ticket_id = purchases.ticket_id
        JOIN flight ON flight.flight_num = ticket.flight_num
        WHERE (purchases.purchase_date BETWEEN %s AND %s)
            AND ticket.airline_name = %s
        GROUP BY month
        ORDER BY month ASC;
    """
    cursor.execute(query, (start_date, end_date,airline_name))
    monthly_report = cursor.fetchall()
    total_sales = sum(float(row['total_amount']) for row in monthly_report)

    #固态，画yearly_report那个chart bar用
    query = """
        SELECT 
            DATE_FORMAT(purchases.purchase_date, '%Y-%m') AS month, 
            COUNT(ticket.ticket_id) AS total_tickets, 
            SUM(flight.price) AS total_amount
        FROM ticket
        JOIN purchases ON ticket.ticket_id = purchases.ticket_id
        JOIN flight ON flight.flight_num = ticket.flight_num
        WHERE (purchases.purchase_date BETWEEN %s AND %s)
            AND ticket.airline_name = %s
        GROUP BY month
        ORDER BY month ASC;
    """
    cursor.execute(query, ((now - timedelta(days=365)).strftime('%Y-%m-%d'), now.strftime('%Y-%m-%d'),airline_name))
    yearly_report = cursor.fetchall()

    for item in yearly_report:
        item['total_amount'] = float(item['total_amount'])
    
    yearly_report_json = json.dumps(yearly_report)
    print('yearly_report_json:',yearly_report_json)



    #查询pie chart
    last_month_start = (now - timedelta(days=30)).strftime('%Y-%m-%d')
    last_year_start = (now - timedelta(days=365)).strftime('%Y-%m-%d')
    today = now.strftime('%Y-%m-%d')

    query_direct = """
        SELECT SUM(flight.price) AS total_amount
        FROM ticket
        JOIN purchases ON ticket.ticket_id = purchases.ticket_id
        JOIN flight ON flight.flight_num = ticket.flight_num
        WHERE ticket.airline_name = %s
        AND purchases.booking_agent_id IS NULL
        AND purchases.purchase_date BETWEEN %s AND %s;
    """

    query_indirect = """
        SELECT SUM(flight.price) AS total_amount
        FROM ticket
        JOIN purchases ON ticket.ticket_id = purchases.ticket_id
        JOIN flight ON flight.flight_num = ticket.flight_num
        WHERE ticket.airline_name = %s
        AND purchases.booking_agent_id IS NOT NULL
        AND purchases.purchase_date BETWEEN %s AND %s;
    """

    # 获取过去一个月收入
    cursor.execute(query_direct, (airline_name, last_month_start, today))
    direct_last_month = cursor.fetchone()['total_amount'] or 0

    cursor.execute(query_indirect, (airline_name, last_month_start, today))
    indirect_last_month = cursor.fetchone()['total_amount'] or 0

    # 获取过去一年的收入
    cursor.execute(query_direct, (airline_name, last_year_start, today))
    direct_last_year = cursor.fetchone()['total_amount'] or 0

    cursor.execute(query_indirect, (airline_name, last_year_start, today))
    indirect_last_year = cursor.fetchone()['total_amount'] or 0
    #查询pie chart








    #View Top destinations
    last_3_months_start = (now - timedelta(days=90)).strftime('%Y-%m-%d')
    last_year_start = (now - timedelta(days=365)).strftime('%Y-%m-%d')
    today = now.strftime('%Y-%m-%d')

    query_last_3_months = """
        SELECT flight.arrival_airport, airport.airport_city, COUNT(ticket.ticket_id) AS total_tickets
        FROM ticket
        JOIN flight ON ticket.flight_num = flight.flight_num AND ticket.airline_name = flight.airline_name
        JOIN purchases ON ticket.ticket_id = purchases.ticket_id
        JOIN airport ON airport.airport_name = flight.arrival_airport
        WHERE ticket.airline_name = %s AND purchases.purchase_date BETWEEN %s AND %s
        GROUP BY flight.arrival_airport
        ORDER BY total_tickets DESC
        LIMIT 3;
    """

    # 查询过去 1 年的热门目的地
    query_last_year = """
        SELECT flight.arrival_airport, airport.airport_city, COUNT(ticket.ticket_id) AS total_tickets
        FROM ticket
        JOIN flight ON ticket.flight_num = flight.flight_num AND ticket.airline_name = flight.airline_name
        JOIN purchases ON ticket.ticket_id = purchases.ticket_id
        JOIN airport ON airport.airport_name = flight.arrival_airport
        WHERE ticket.airline_name = %s AND purchases.purchase_date BETWEEN %s AND %s
        GROUP BY flight.arrival_airport
        ORDER BY total_tickets DESC
        LIMIT 3;
    """

    # 执行查询
    cursor.execute(query_last_3_months, (airline_name, last_3_months_start, today))
    top_destinations_last_3_months = cursor.fetchall()

    cursor.execute(query_last_year, (airline_name, last_year_start, today))
    top_destinations_last_year = cursor.fetchall()


    cursor.close()
    return render_template('sales_report.html', yearly_report=yearly_report_json, 
                           start_date=start_date, end_date=end_date, total_sales = total_sales,
                           direct_last_month = direct_last_month,indirect_last_month = indirect_last_month,
                           direct_last_year = direct_last_year, indirect_last_year = indirect_last_year,
                           top_destinations_last_3_months = top_destinations_last_3_months, top_destinations_last_year = top_destinations_last_year)


@app.route('/logout')
def logout():
    # print('test')
    session.clear()
    flash("You have successfully logged out!", "success")

    return redirect(url_for('home'))


@app.route('/search', methods=['GET', 'POST'])
def search_flights():
    # 获取表单中的用户输入
    departure_city = request.form.get('departure_city')  # 出发城市
    arrival_city = request.form.get('arrival_city')  # 到达城市
    departure_airport = request.form.get('departure_airport')  # 出发机场
    arrival_airport = request.form.get('arrival_airport')  # 到达机场
    start_date = request.form.get('start_date')  # 起飞时间（最早）
    end_date = request.form.get('end_date')  # 到达时间（最晚）

    cursor = db.cursor(dictionary=True)

    # 构造查询逻辑
    query = """
    SELECT f.* FROM flight f
    JOIN airport d ON f.departure_airport = d.airport_name
    JOIN airport a ON f.arrival_airport = a.airport_name
    WHERE 1=1
    """  # 初始化查询语句
    params = []  # 用于存储动态参数

    if departure_city and departure_airport:
        query = "SELECT 1 FROM airport WHERE airport_city = %s AND airport_name = %s"
        cursor.execute(query, (departure_city, departure_airport))
        if not cursor.fetchone():
            flash("Departure city and departure airport do not match. Please try again.", "danger")
            return redirect(url_for('home'))

    if arrival_city and arrival_airport:
        query = "SELECT 1 FROM airport WHERE airport_city = %s AND airport_name = %s"
        cursor.execute(query, (arrival_city, arrival_airport))
        if not cursor.fetchone():
            flash("Arrival city and arrival airport do not match. Please try again.", "danger")
            return redirect(url_for('home'))
            
    # 处理出发城市和到达城市
    if departure_city and not departure_airport:
        query += " AND d.airport_city = %s"
        params.append(departure_city)

    if arrival_city and not arrival_airport:
        query += " AND a.airport_city = %s"
        params.append(arrival_city)

    # 优先处理出发机场和到达机场
    if departure_airport:
        query += " AND f.departure_airport = %s"
        params.append(departure_airport)

    if arrival_airport:
        query += " AND f.arrival_airport = %s"
        params.append(arrival_airport)

    # 处理起飞时间和到达时间
    if start_date:
        query += " AND f.departure_time >= %s"
        params.append(start_date)

    if end_date:
        query += " AND f.arrival_time <= %s"
        params.append(end_date)

    # 排序航班时间
    query += " ORDER BY f.departure_time ASC"

    # 执行查询
    cursor.execute(query, params)
    flights = cursor.fetchall()

    cursor.close()

    return render_template('search.html', flights=flights)


@app.route('/purchase/<int:flight_num>', methods=['GET', 'POST'])
def purchase_flight(flight_num):
    if 'user' not in session:
        # 如果未登录，跳转到登录界面
        flash("Please log in to purchase a flight.", "warning")
        return redirect(url_for('login'))

    # 获取用户身份
    identity = session['user']['identity']
    user_email = session['user']['email']

    cursor = db.cursor(dictionary=True)

    # 查询航班信息
    cursor.execute("""
        SELECT airline_name, flight_num, departure_airport, arrival_airport, departure_time, arrival_time, price
        FROM flight
        WHERE flight_num = %s
    """, (flight_num,))
    flight_info = cursor.fetchone()


    # 如果没有找到航班信息，提示用户
    if not flight_info:
        flash("The selected flight does not exist. Please try again.", "danger")
        return redirect(url_for('home'))

    # 如果是顾客
    if identity == 'customer':
        # 查询顾客注册时的信息，包括护照和出生日期
        cursor.execute("""
            SELECT name, phone_number, passport_number, passport_expiration, passport_country, date_of_birth
            FROM customer
            WHERE email = %s
        """, (user_email,))
        customer_info = cursor.fetchone()

        if request.method == 'POST':
            # 获取用户提交的信息
            name = request.form.get('name')
            phone_number = request.form.get('phone_number')
            passport_number = request.form.get('passport_number')
            passport_expiration = request.form.get('passport_expiration')
            passport_country = request.form.get('passport_country')
            date_of_birth = request.form.get('date_of_birth')

            # print('test1\n')
            # 验证信息完整性
            if not all([name, passport_number, passport_expiration, passport_country, date_of_birth]):
            #     flash("All fields are required to complete the purchase.", "danger")
                return render_template('customer_purchase.html', customer_info=customer_info, flight_info=flight_info)

            
            # 检查客户是否使用同一护照号码购买过机票
            cursor.execute("""
                SELECT t.ticket_id, p.customer_email, p.passport_number
                FROM ticket t
                JOIN purchases p ON t.ticket_id = p.ticket_id
                WHERE p.passport_number = %s AND t.flight_num = %s
            """, (passport_number, flight_num))
            existing_ticket = cursor.fetchone()

            if existing_ticket:
                # 如果找到匹配记录，返回前端弹窗提示信息
                return render_template(
                    'agent_purchase.html',
                    flight_info=flight_info,
                    error={
                        'message': f"A ticket for this flight ({flight_num}) has already been purchased by this customer.",
                        'ticket_id': existing_ticket['ticket_id'],
                        'email': existing_ticket['customer_email']
                    }
                )

            
            # 生成一个独立的9位 ticket_id
            while True:
                ticket_id = str(random.randint(10**8, 10**9 - 1))  # 生成9位随机数
                cursor.execute("SELECT 1 FROM ticket WHERE ticket_id = %s", (ticket_id,))
                if not cursor.fetchone():
                    break  # 如果 ticket_id 未被使用，退出循环

            # 插入 ticket 表
            cursor.execute("""
                INSERT INTO ticket (ticket_id, airline_name, flight_num)
                VALUES (%s, %s, %s)
            """, (ticket_id, flight_info['airline_name'], flight_num))

            # 插入 purchases 表
            cursor.execute("""
                INSERT INTO purchases (ticket_id, customer_email, purchase_date, phone_number, passport_number, passport_expiration, passport_country, date_of_birth)
                VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s)
            """, (ticket_id, user_email, phone_number, passport_number, passport_expiration, passport_country, date_of_birth))


            # 更新顾客信息（如果需要更新）
            # cursor.execute("""
            #     UPDATE customer
            #     SET name = %s,
            #         passport_number = %s,
            #         passport_expiration = %s,
            #         passport_country = %s,
            #         date_of_birth = %s
            #     WHERE email = %s
            # """, (name, passport_number, passport_expiration, passport_country, date_of_birth, user_email))

            db.commit()

            flash(f"Purchase completed successfully! Your ticket ID is {ticket_id}.", "success")
            return redirect(url_for('home'))

        return render_template('customer_purchase.html', customer_info=customer_info, flight_info=flight_info)



    # 如果是代理商
    elif identity == 'agent':
        if request.method == 'POST':
            # 获取用户提交的信息（如果代理商有特定的表单字段，可以扩展）
            phone_number = request.form.get('phone_number')
            name = request.form.get('name')
            passport_number = request.form.get('passport_number')
            passport_expiration = request.form.get('passport_expiration')
            passport_country = request.form.get('passport_country')
            date_of_birth = request.form.get('date_of_birth')

            if not all([phone_number, name, passport_number, passport_expiration, passport_country, date_of_birth]):
                # flash("Customer email is required for agent purchases.", "danger")
                return render_template('agent_purchase.html', flight_info=flight_info)

            # 检查客户是否使用同一护照号码购买过机票
            cursor.execute("""
                SELECT t.ticket_id, p.passport_number
                FROM ticket t
                JOIN purchases p ON t.ticket_id = p.ticket_id
                WHERE p.passport_number = %s AND t.flight_num = %s
            """, (passport_number, flight_num))
            existing_ticket = cursor.fetchone()

            if existing_ticket:
                # 如果找到匹配记录，返回前端弹窗提示信息
                return render_template(
                    'agent_purchase.html',
                    flight_info=flight_info,
                    error={
                        'message': f"A ticket for this flight ({flight_num}) has already been purchased by this passenger.",
                        'ticket_id': existing_ticket['ticket_id'],
                    }
                )
            while True:
                ticket_id = str(random.randint(10**8, 10**9 - 1))  # 生成9位随机数
                cursor.execute("SELECT 1 FROM ticket WHERE ticket_id = %s", (ticket_id,))
                if not cursor.fetchone():
                    break  # 如果 ticket_id 未被使用，退出循环

            # 插入 ticket 表
            cursor.execute("""
                INSERT INTO ticket (ticket_id, airline_name, flight_num)
                VALUES (%s, %s, %s)
            """, (ticket_id, flight_info['airline_name'], flight_num))

            # 插入购买记录
            cursor.execute("""
                INSERT INTO purchases (ticket_id, phone_number, booking_agent_id, purchase_date, passport_number, passport_expiration, passport_country, date_of_birth)
                VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s)
            """, (ticket_id, phone_number, session['user']['agent_id'], passport_number, passport_expiration, passport_country, date_of_birth))

            db.commit()

            flash(f"Purchase completed successfully! Ticket ID: {ticket_id}", "success")
            return redirect(url_for('agent_dashboard'))

        return render_template('agent_purchase.html', flight_info=flight_info)

    # 如果身份不允许购买
    else:
        flash("Only customers and agents can purchase flights.", "danger")
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)







    
