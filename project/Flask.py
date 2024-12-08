from flask import Flask, render_template, request, flash, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json

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
        return render_template('home.html', logged_in=True, identity=identity)
    else:
        return render_template('home.html', logged_in=False)
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
            print(form_type)

            existing_email_query = """
                SELECT 1 FROM customer WHERE email = %s
                UNION
                SELECT 1 FROM booking_agent WHERE email = %s
                UNION
                SELECT 1 FROM airline_staff WHERE email = %s
                """

            if form_type == 'customer':
                customer_email = request.form.get('customer_email').lower().split('@')[0] + '@' + request.form.get('customer_email').split('@')[1]
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
                print(customer_email, customer_name, customer_password) 

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
                hashed_password = generate_password_hash(customer_password, method='sha256')

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
                agent_email = request.form.get('agent_email').lower().split('@')[0] + '@' + request.form.get('agent_email').split('@')[1]
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

                
                hashed_password = generate_password_hash(agent_password, method='sha256')
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
                staff_email = request.form.get('staff_email').lower().split('@')[0] + '@' + request.form.get('staff_email').split('@')[1]
                staff_password = request.form.get('staff_password')
                staff_first_name = request.form.get('staff_first_name')
                staff_last_name = request.form.get('staff_last_name')
                staff_birthday = request.form.get('staff_birthday')
                staff_airline_name = request.form.get('staff_airline_name')
                print(staff_airline_name)

                if not all([staff_email, staff_password, staff_first_name, staff_last_name, staff_birthday, staff_airline_name]):
                    flash('All fields are required!', 'danger')
                    return redirect(url_for('register'))
                
                if check_email_exists(staff_email, cursor):
                    flash('Email already exists!', 'danger')
                    return redirect(url_for('register'))
            
                hashed_password = generate_password_hash(staff_password, method='sha256')
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
        password = request.form.get('login_password') #这里get到的密码应该是输入进去什么就是什么，输入1这里就是1
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
        print(user)

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
                print(f"Redirecting to {identity}_dashboard")
            elif identity == 'agent':
                session['user']['agent_id'] = user['booking_agent_id']
                print(session)
                print(f"Redirecting to {identity}_dashboard")
                return redirect(url_for('agent_dashboard'))
            elif identity == 'staff':
                session['user']['airline_name'] = user['airline_name']
                cursor.execute("SELECT permission_type FROM permission WHERE email = %s", (email,))
                permissions = cursor.fetchall()
                print("permissions",permissions)

                permission_types = [permission['permission_type'] for permission in permissions]
                combined_permissions = ', '.join(permission_types)
                session['user']['permissions'] = [{'permission_type': combined_permissions}]

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
    # print(f"Redirecting to customer_dashboard")
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
    else:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date') 
        print("filter my flight: ", start_date,end_date)
    
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
                f.status
            FROM purchases p
            JOIN ticket t ON p.ticket_id = t.ticket_id
            JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
            WHERE p.customer_email = %s AND f.status = 'upcoming'
            ORDER BY f.departure_time ASC;
        """
        cursor.execute(query, (customer_email, ))

    elif (start_date and end_date):
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
                f.status
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
    # print(booked_flights) 











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
    print('this is day filter:',ticket_end_date,ticket_start_date)

    query = """
        SELECT p.customer_email, COUNT(*) as ticket_count
        FROM purchases p
        JOIN ticket t ON p.ticket_id = t.ticket_id
        WHERE p.booking_agent_id = %s AND p.purchase_date BETWEEN %s AND %s
        GROUP BY p.customer_email
        ORDER BY ticket_count DESC
        LIMIT 5;
    """
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
                           top_customers_ticket = top_customers_ticket_json,
                           top_customers_commission = top_customers_commission_json)



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


    # if request.method == 'POST':
    form_type = request.form.get('form_type')
    print("form_type:", form_type)


    # if form_type == 'default':

    flight_start_date = request.args.get('start_date')
    flight_end_date = request.args.get('end_date')
    status_filter = request.args.get('status')

    now = datetime.now()
    default_flight_start_date = now
    default_flight_end_date = now + timedelta(days=30)

    query_start_date = flight_start_date if flight_start_date else default_flight_start_date.strftime('%Y-%m-%d')
    query_end_date = flight_end_date if flight_end_date else default_flight_start_date.strftime('%Y-%m-%d')
    query_status = status_filter if status_filter else 'upcoming'

    print("datetime test:",query_start_date,query_end_date,query_status)









    query = """
        SELECT bf.email, booking_agent.booking_agent_id, bf.airline_name
        FROM booking_agent_work_for AS bf
        JOIN booking_agent ON bf.email = booking_agent.email
        WHERE bf.airline_name = %s 
    """
    cursor.execute(query, (staff_airline, ) )
    airline_booking_agent = cursor.fetchall()
    print('airline booking agent:', airline_booking_agent)












    

    return render_template('dashboard/staff.html', staff_permission = staff_permission, staff_airline = staff_airline,
                           airline_booking_agent = airline_booking_agent)








@app.route('/logout')
def logout():
    # print('test')
    session.clear()
    flash("You have successfully logged out!", "success")

    return redirect(url_for('home'))












@app.route('/search', methods=['GET', 'POST'])
def search_flights():
    keyword = request.form.get('keyword')  # 从表单获取关键词
    cursor = db.cursor(dictionary=True)
    
    if keyword:
        query = """
        SELECT * FROM flight 
        WHERE departure_city LIKE %s 
        ORDER BY departure_time
        """
        like_keyword = f"%{keyword}%"
        cursor.execute(query, (like_keyword, like_keyword))
    else:
        cursor.execute("SELECT * FROM flight ORDER BY departure_time")
    
    flights = cursor.fetchall()
    cursor.close()
    return render_template('search.html', flights=flights, keyword=keyword)

if __name__ == '__main__':
    app.run(debug=True)







    
