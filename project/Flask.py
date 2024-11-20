from flask import Flask, render_template, request, flash, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

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

    try:
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
                cursor.execute(existing_email_query, (customer_email, customer_email, customer_email,))
                existing_user = cursor.fetchone()
                if existing_user:
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
                
                cursor.execute(existing_email_query, (agent_email, agent_email, agent_email,))
                existing_agent = cursor.fetchone()
                if existing_agent:
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
                
                cursor.execute(existing_email_query, (staff_email,staff_email, staff_email,))
                existing_staff = cursor.fetchone()
                if existing_staff:
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
            
    except mysql.connector.Error as err:
            print(f"Database error: {err}")
            flash("Database error. Please try again later.", "error")
            return redirect(url_for('register'))
    finally:
        if db.is_connected():
            print('register-finally')
            cursor.close()

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
                print(f"Redirecting to {identity}_dashboard")
                return redirect(url_for('agent_dashboard'))
            elif identity == 'staff':
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
    
    clear_filter = request.args.get('clear_filter', False)
    if clear_filter:
        start_date = None
        end_date = None
    else:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date') 
        print(start_date,end_date)
    
        
    customer_email = session['user']['email']
    cursor = db.cursor(dictionary=True)

    booked_flights = []


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
            WHERE p.customer_email = %s
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
        flash('Please select both date!', 'danger') 
        
    booked_flights = cursor.fetchall()
    print(booked_flights) 
    print(booked_flights) 
    print(booked_flights) 



         
    db.commit()
    cursor.close()

    return render_template('dashboard/customer.html', booked_flights = booked_flights, start_date = start_date, end_date = end_date)




@app.route('/dashboard/agent', methods=['GET', 'POST'])
def agent_dashboard():
    # 如果没有登录，跳转到登录页
    if 'user' not in session:
        return redirect(url_for('login'))  
    
    agent_email = session['user']['email']
    cursor = db.cursor(dictionary=True)
    
    # airline agent not working for, 给selector用
    cursor.execute("""
        SELECT airline_name 
        FROM airline 
        WHERE airline_name NOT IN (
            SELECT airline_name 
            FROM booking_agent_work_for 
            WHERE email = %s
        )
    """, (agent_email,))
    airlines_not_working_for = cursor.fetchall()  

    # 从目前的booking_agent_work_for里面拉数据出来
    cursor.execute("SELECT airline_name FROM booking_agent_work_for WHERE email = %s", (agent_email,))
    airlines_working_for = cursor.fetchall()  

    if request.method == 'POST':
        action = request.form.get('action')
        airline_name = request.form.get('airline_name')

        if request.form.get('action') == 'add_working_airline':
            # 添加航空公司到booking_agent_work_for
            cursor.execute("INSERT INTO booking_agent_work_for (email, airline_name) VALUES (%s, %s)", (agent_email, airline_name))
            db.commit()
            flash('Airline added successfully!', 'success')

        elif action == 'remove_working_airline':
            # 从booking_agent_work_for中删除航空公司
            cursor.execute("DELETE FROM booking_agent_work_for WHERE email = %s AND airline_name = %s", (agent_email, airline_name))
            db.commit()
            flash('Airline removed successfully!', 'success')

        return redirect(url_for('agent_dashboard'))

    cursor.close()
    return render_template('dashboard/agent.html', airlines_not_working_for=airlines_not_working_for, airlines_working_for=airlines_working_for)




@app.route('/dashboard/staff')
def staff_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))  
    
    staff_email = session['user']['email']
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT permission_type FROM permission WHERE email = %s", (staff_email,))
    staff_permission = cursor.fetchall() 
    print(staff_permission)
    

    return render_template('dashboard/staff.html', staff_permission = staff_permission)








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







    
