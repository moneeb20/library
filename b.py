from flask import Flask, render_template, request, url_for,redirect,flash,session,sessions
import pyodbc

from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'munibmunib'  

# اتصال بقاعدة البيانات
conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=DESKTOP-RPEHURA\\SQLEXPRESS;'
    'DATABASE=Librarydb2;'
    'Trusted_Connection=yes;'
)

# الدالة العامة لجلب البيانات

def get_db_connection():
    return pyodbc.connect(conn_str)



@app.route('/')
def index():
    title = request.args.get('title', default='')
    author = request.args.get('author', default='')
    category_id = request.args.get('category', default='')

    query = '''
        SELECT b.book_id, b.title, b.author, b.price, b.book_type, 
               b.cover_image, b.description, c.name AS category_name,
               c.category_id, b.digital_file
        FROM Books b
        JOIN Categories c ON b.category_id = c.category_id
        WHERE (b.title LIKE ? OR ? = '')
          AND (b.author LIKE ? OR ? = '')
          AND (c.category_id = ? OR ? = '')
    '''

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. جلب الكتب
    cursor.execute(query, 
                  ('%' + title + '%', title, 
                   '%' + author + '%', author, 
                   category_id, category_id))
    books = [dict(zip([column[0] for column in cursor.description], row)) 
            for row in cursor.fetchall()]

    # 2. جلب التصنيفات
    cursor.execute('SELECT category_id, name FROM Categories')
    categories = [dict(zip(['id', 'name'], row)) for row in cursor.fetchall()]

    # 3. إذا المستخدم داخل، جلب الكتب التي اشتراها
    purchased_book_ids = []
    if 'user_id' in session:
        cursor.execute("SELECT book_id FROM Orders WHERE user_id = ?", (session['user_id'],))
        purchased_book_ids = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template('index1.html', 
                           books=books, 
                           categories=categories,
                           selected_category=category_id,
                           purchased_book_ids=purchased_book_ids)



@app.route('/books')
def books():
    title = request.args.get('title', default='')
    author = request.args.get('author', default='')
    category_id = request.args.get('category', default='')

    query = '''
        SELECT b.book_id, b.title, b.author, b.price, b.book_type, 
               b.cover_image, b.description, c.name AS category_name,
               c.category_id, b.digital_file
        FROM Books b
        JOIN Categories c ON b.category_id = c.category_id
        WHERE (b.title LIKE ? OR ? = '')
          AND (b.author LIKE ? OR ? = '')
          AND (c.category_id = ? OR ? = '')
    '''

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. جلب الكتب
    cursor.execute(query, 
                  ('%' + title + '%', title, 
                   '%' + author + '%', author, 
                   category_id, category_id))
    books = [dict(zip([column[0] for column in cursor.description], row)) 
            for row in cursor.fetchall()]

    # 2. جلب التصنيفات
    cursor.execute('SELECT category_id, name FROM Categories')
    categories = [dict(zip(['id', 'name'], row)) for row in cursor.fetchall()]

    # 3. جلب الكتب التي اشتراها المستخدم إن كان مسجلاً
    purchased_book_ids = []
    if 'user_id' in session:
        cursor.execute("SELECT book_id FROM Orders WHERE user_id = ?", (session['user_id'],))
        purchased_book_ids = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template('books.html', 
                           books=books, 
                           categories=categories,
                           selected_category=category_id,
                           search_title=title,
                           search_author=author,
                           purchased_book_ids=purchased_book_ids)


from flask import Flask, render_template, request, redirect, url_for
import pyodbc
from datetime import datetime



conn = pyodbc.connect(conn_str)
cursor = conn.cursor()


@app.route('/support', methods=['GET', 'POST'])
def support():
    if request.method == 'POST':
        try:
            # التحقق من تسجيل الدخول
            if 'user_id' not in session:
                flash("يجب تسجيل الدخول أولاً", "error")
                return redirect(url_for('login'))

            # إدخال الرسالة
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Support_Messages (user_id, subject, message)
                VALUES (?, ?, ?)
            """, (
                session['user_id'],
                request.form.get('subject'),
                request.form.get('message')
            ))
            conn.commit()
            
            # إشعار النجاح - تأكد من استخدام "success"
            flash("تم إرسال رسالتك بنجاح وسيتم الرد عليك قريباً", "success")
            return redirect(url_for('support'))
            
        except Exception as e:
            # إشعار الخطأ
            flash(f"فشل في إرسال الرسالة: {str(e)}", "error")
            return redirect(url_for('support'))
        finally:
            cursor.close()

    return render_template('support.html')
##############################################

@app.route("/moder")
def moder():
    if "user_id" not in session or session.get("user_type") not in ["admin", "moderator"]:
        flash("⚠ ليس لديك صلاحيات للوصول إلى هذه الصفحة.", "danger")
        return redirect(request.referrer or url_for("index"))

    cursor = conn.cursor()
    cursor.execute("SELECT name, email, subject, message, message_date FROM Support_Messages ORDER BY message_date DESC")
    messages = [
        {
            "name": row[0],
            "email": row[1],
            "subject": row[2],
            "message": row[3],
            "message_date": row[4]
        }
        for row in cursor.fetchall()
    ]
    return render_template("moder.html", messages=messages)
from flask import jsonify

@app.route("/get-support-messages")
def get_support_messages():
    cursor.execute("SELECT name, email, subject, message, message_date FROM Support_Messages ORDER BY message_date DESC")
    messages = [
        {
            "name": row[0],
            "email": row[1],
            "subject": row[2],
            "message": row[3],
            "message_date": row[4].strftime("%Y-%m-%d %H:%M:%S")  # تنسيق التاريخ
        }
        for row in cursor.fetchall()
    ]
    return jsonify(messages)
################################################################
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        user_type = 'user'

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Users WHERE email = ?", (email,))
        if cursor.fetchone():
            flash('البريد الإلكتروني مستخدم من قبل.', 'error')
            conn.close()
            return redirect(url_for('register'))

        cursor.execute(
            "INSERT INTO Users (name, email, password, user_type) VALUES (?, ?, ?, ?)",
            (name, email, hashed_password, user_type)
        )
        conn.commit()
        conn.close()

        flash('تم إنشاء الحساب بنجاح. يمكنك تسجيل الدخول الآن.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # لاحظ أننا نضيف user_type هنا:
        cursor.execute("SELECT user_id, name, password, user_type FROM Users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['name'] = user[1]
            session['email'] = email
            session['user_type'] = user[3]  # 🟢 حفظ نوع المستخدم
            flash('تم تسجيل الدخول بنجاح.', 'success')
            return redirect(url_for('profile'))
        else:
            flash('بيانات تسجيل الدخول غير صحيحة', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    name = session.get('name')
    email = session.get('email')

    conn = get_db_connection()  # ✅ استخدم الاتصال الموحد
    cursor = conn.cursor()

    cursor.execute("""
        SELECT B.title, B.price
        FROM Orders O
        JOIN Books B ON O.book_id = B.book_id
        WHERE O.user_id = ?
    """, user_id)

    books = cursor.fetchall()

    free_books = [book[0] for book in books if book[1] == 0]
    paid_books = [book[0] for book in books if book[1] > 0]

    conn.close()

    return render_template('profile.html', name=name, email=email, free_books=free_books, paid_books=paid_books)

#################################################
@app.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج.', 'success')
    return redirect(url_for('login'))



from flask import request

@app.route('/buy/<int:book_id>', methods=['POST'])
def buy_book(book_id):
    if 'user_id' not in session:
        flash('يجب تسجيل الدخول أولاً لإجراء عملية الشراء.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # التحقق من أن المستخدم لم يشترِ الكتاب مسبقاً
    cursor.execute("SELECT * FROM Orders WHERE user_id=? AND book_id=?", (session['user_id'], book_id))
    if cursor.fetchone():
        flash('لقد قمت بشراء هذا الكتاب بالفعل.', 'info')
        return redirect(request.referrer or url_for('books'))

    # إدخال الطلب
    cursor.execute("INSERT INTO Orders (user_id, book_id) VALUES (?, ?)", (session['user_id'], book_id))
    conn.commit()

    cursor.close()
    conn.close()

    flash('تمت عملية الشراء بنجاح! يمكنك الآن تحميل الكتاب.', 'success')
    return redirect(request.referrer or url_for('books'))




# إدارة الكتب
@app.route('/show-books')
def show_books():
    if "user_id" not in session or session.get("user_type") not in ["admin", "moderator"]:
        flash("⚠ ليس لديك صلاحيات للوصول إلى هذه الصفحة.", "danger")
        return redirect(url_for("moder"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT book_id, title, author, price, book_type FROM Books")
    books = cursor.fetchall()
    conn.close()

    table_html = """
    <table border="1">
        <tr>
            <th>ID</th>
            <th>العنوان</th>
            <th>المؤلف</th>
            <th>السعر</th>
            <th>النوع</th>
        </tr>
    """
    for book in books:
        table_html += f"""
        <tr>
            <td>{book.book_id}</td>
            <td>{book.title}</td>
            <td>{book.author}</td>
            <td>{book.price}</td>
            <td>{book.book_type}</td>
        </tr>
        """
    table_html += "</table>"

    return render_template("moder.html",
                         show_results=True,
                         results_title="قائمة الكتب",
                         results_table=table_html)

@app.route('/add-book-page')
def add_book_page():
    if "user_id" not in session or session.get("user_type") not in ["admin", "moderator"]:
        flash("⚠ ليس لديك صلاحيات للوصول إلى هذه الصفحة.", "danger")
        return redirect(url_for("moder"))

    # جلب التصنيفات من قاعدة البيانات
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category_id, name FROM Categories")
    categories = cursor.fetchall()
    conn.close()

    # بناء قائمة التصنيفات لاستخدامها في القائمة المنسدلة
    categories_options = ""
    for category in categories:
        categories_options += f'<option value="{category.category_id}">{category.name}</option>'

    form_html = f"""
    <div class="form-group">
        <label for="title">عنوان الكتاب:</label>
        <input type="text" name="title" required>
    </div>
    <div class="form-group">
        <label for="author">المؤلف:</label>
        <input type="text" name="author" required>
    </div>
    <div class="form-group">
        <label for="isbn">ISBN:</label>
        <input type="text" name="isbn">
    </div>
    <div class="form-group">
        <label for="category_id">التصنيف:</label>
        <select name="category_id" required>
            {categories_options}
        </select>
    </div>
    <div class="form-group">
        <label for="price">السعر:</label>
        <input type="number" name="price" step="0.01" required>
    </div>
    <div class="form-group">
        <label for="book_type">نوع الكتاب:</label>
        <select name="book_type" required>
            <option value="ورقي">ورقي</option>
            <option value="إلكتروني">إلكتروني</option>
            <option value="صوتي">صوتي</option>
        </select>
    </div>
    <div class="form-group">
        <label for="description">الوصف:</label>
        <textarea name="description" required></textarea>
    </div>
    <div class="form-group">
        <label for="page_count">عدد الصفحات:</label>
        <input type="number" name="page_count">
    </div>
   
    """

    return render_template("moder.html",
                         show_form=True,
                         form_title="إضافة كتاب جديد",
                         form_content=form_html,
                         form_action=url_for("add_book"),
                         submit_btn_text="إضافة الكتاب")

@app.route('/add-book', methods=['POST'])
def add_book():
    if "user_id" not in session or session.get("user_type") not in ["admin", "moderator"]:
        flash("⚠ ليس لديك صلاحيات لهذه العملية.", "danger")
        return redirect(url_for("moder"))

    # جمع بيانات النموذج
    book_data = {
        'title': request.form['title'],
        'author': request.form['author'],
        'isbn': request.form.get('isbn', ''),
        'category_id': request.form['category_id'],
        'price': request.form['price'],
        'book_type': request.form['book_type'],
        'description': request.form['description'],
        'page_count': request.form.get('page_count'),
        'publish_date': request.form.get('publish_date')
    }

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # إدخال الكتاب في قاعدة البيانات
        cursor.execute("""
            INSERT INTO Books (title, author, ISBN, category_id, price, book_type, description, page_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            book_data['title'],
            book_data['author'],
            book_data['isbn'],
            book_data['category_id'],
            book_data['price'],
            book_data['book_type'],
            book_data['description'],
            book_data['page_count'],
            
        ))
        conn.commit()
        flash("تم إضافة الكتاب بنجاح", "success")
    except Exception as e:
        flash(f"حدث خطأ أثناء إضافة الكتاب: {str(e)}", "danger")
    finally:
        conn.close()

    return redirect(url_for("moder"))


# إدارة المستخدمين
@app.route('/show-users')
def show_users():
    if "user_id" not in session or session.get("user_type") not in ["admin", "moderator"]:
        flash("⚠ ليس لديك صلاحيات للوصول إلى هذه الصفحة.", "danger")
        return redirect(url_for("moder"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, email, user_type FROM Users")
    users = cursor.fetchall()
    conn.close()

    table_html = """
    <table border="1">
        <tr>
            <th>ID</th>
            <th>الاسم</th>
            <th>البريد</th>
            <th>نوع المستخدم</th>
        </tr>
    """
    for user in users:
        table_html += f"""
        <tr>
            <td>{user.user_id}</td>
            <td>{user.name}</td>
            <td>{user.email}</td>
            <td>{user.user_type}</td>
        </tr>
        """
    table_html += "</table>"

    return render_template("moder.html",
                         show_results=True,
                         results_title="قائمة المستخدمين",
                         results_table=table_html)

@app.route('/add-user-page')
def add_user_page():
    if "user_id" not in session or session.get("user_type") not in ["admin", "moderator"]:
        flash("⚠ ليس لديك صلاحيات للوصول إلى هذه الصفحة.", "danger")
        return redirect(url_for("moder"))

    form_html = """
    <div class="form-group">
        <label for="name">الاسم:</label>
        <input type="text" name="name" required>
    </div>
    <div class="form-group">
        <label for="email">البريد الإلكتروني:</label>
        <input type="email" name="email" required>
    </div>
    <div class="form-group">
        <label for="password">كلمة المرور:</label>
        <input type="password" name="password" required>
    </div>
    <div class="form-group">
        <label for="user_type">نوع المستخدم:</label>
        <select name="user_type" required>
            <option value="user">مستخدم عادي</option>
            <option value="moderator">مشرف</option>
            <option value="admin">مدير</option>
        </select>
    </div>
    """

    return render_template("moder.html",
                         show_form=True,
                         form_title="إضافة مستخدم جديد",
                         form_content=form_html,
                         form_action=url_for("add_user"),
                         submit_btn_text="إضافة المستخدم")

@app.route('/add-user', methods=['POST'])
def add_user():
    if "user_id" not in session or session.get("user_type") not in ["admin", "moderator"]:
        flash("⚠ ليس لديك صلاحيات لهذه العملية.", "danger")
        return redirect(url_for("moder"))

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    user_type = request.form['user_type']

    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # التحقق من عدم وجود مستخدم بنفس البريد
        cursor.execute("SELECT * FROM Users WHERE email = ?", (email,))
        if cursor.fetchone():
            flash("البريد الإلكتروني مستخدم بالفعل", "warning")
            return redirect(url_for("moder"))

        cursor.execute(
            "INSERT INTO Users (name, email, password, user_type) VALUES (?, ?, ?, ?)",
            (name, email, hashed_password, user_type)
        )
        conn.commit()
        flash("تمت إضافة المستخدم بنجاح", "success")
    except Exception as e:
        flash(f"حدث خطأ أثناء إضافة المستخدم: {str(e)}", "danger")
    finally:
        conn.close()

    return redirect(url_for("moder"))



# عرض الطلبات
@app.route('/show-orders')
def show_orders():
    if "user_id" not in session or session.get("user_type") not in ["admin", "moderator"]:
        flash("⚠ ليس لديك صلاحيات للوصول إلى هذه الصفحة.", "danger")
        return redirect(url_for("moder"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.order_id, u.name as user_name, b.title as book_title, o.order_date 
        FROM Orders o
        JOIN Users u ON o.user_id = u.user_id
        JOIN Books b ON o.book_id = b.book_id
    """)
    orders = cursor.fetchall()
    conn.close()

    table_html = """
    <table border="1">
        <tr>
            <th>رقم الطلب</th>
            <th>اسم المستخدم</th>
            <th>عنوان الكتاب</th>
            <th>تاريخ الطلب</th>
        </tr>
    """
    for order in orders:
        table_html += f"""
        <tr>
            <td>{order.order_id}</td>
            <td>{order.user_name}</td>
            <td>{order.book_title}</td>
            <td>{order.order_date}</td>
        </tr>
        """
    table_html += "</table>"

    return render_template("moder.html",
                         show_results=True,
                         results_title="قائمة الطلبات",
                         results_table=table_html)

# عرض رسائل الدعم
@app.route('/show-support-messages')
def show_support_messages():
    if "user_id" not in session or session.get("user_type") not in ["admin", "moderator"]:
        flash("⚠ ليس لديك صلاحيات للوصول إلى هذه الصفحة.", "danger")
        return redirect(url_for("moder"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.name, u.email, s.subject, s.message, s.message_date 
        FROM Support_Messages s
        JOIN Users u ON s.user_id = u.user_id
        ORDER BY s.message_date DESC
    """)
    messages = cursor.fetchall()
    conn.close()

    return render_template("moder.html",
                         show_support_messages=True,
                         support_messages=messages)
# صفحة حذف الكتاب
@app.route('/delete-book-page')
def delete_book_page():
    if "user_id" not in session or session.get("user_type") not in ["admin", "moderator"]:
        flash("⚠ ليس لديك صلاحيات للوصول إلى هذه الصفحة.", "danger")
        return redirect(url_for("moder"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT book_id, title FROM Books")
    books = cursor.fetchall()
    conn.close()

    form_html = """
    <div class="form-group">
        <label for="book_id">اختر الكتاب للحذف:</label>
        <select name="book_id" required>
    """
    for book in books:
        form_html += f'<option value="{book.book_id}">{book.title}</option>'
    
    form_html += """
        </select>
    </div>
    """

    return render_template("moder.html",
                         show_form=True,
                         form_title="حذف كتاب",
                         form_content=form_html,
                         form_action=url_for("delete_book"),
                         submit_btn_text="حذف الكتاب")

# عملية حذف الكتاب
@app.route('/delete-book', methods=['POST'])
def delete_book():
    if "user_id" not in session or session.get("user_type") not in ["admin", "moderator"]:
        flash("⚠ ليس لديك صلاحيات لهذه العملية.", "danger")
        return redirect(url_for("moder"))

    book_id = request.form['book_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Books WHERE book_id = ?", (book_id,))
        conn.commit()
        flash("تم حذف الكتاب بنجاح", "success")
    except Exception as e:
        flash(f"حدث خطأ أثناء حذف الكتاب: {str(e)}", "danger")
    finally:
        conn.close()

    return redirect(url_for("moder"))

# صفحة حذف المستخدم
@app.route('/delete-user-page')
def delete_user_page():
    if "user_id" not in session or session.get("user_type") not in ["admin", "moderator"]:
        flash("⚠ ليس لديك صلاحيات للوصول إلى هذه الصفحة.", "danger")
        return redirect(url_for("moder"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, email FROM Users")
    users = cursor.fetchall()
    conn.close()

    form_html = """
    <div class="form-group">
        <label for="user_id">اختر المستخدم للحذف:</label>
        <select name="user_id" required>
    """
    for user in users:
        form_html += f'<option value="{user.user_id}">{user.name} ({user.email})</option>'
    
    form_html += """
        </select>
    </div>
    """

    return render_template("moder.html",
                         show_form=True,
                         form_title="حذف مستخدم",
                         form_content=form_html,
                         form_action=url_for("delete_user"),
                         submit_btn_text="حذف المستخدم")

# عملية حذف المستخدم
@app.route('/delete-user', methods=['POST'])
def delete_user():
    if "user_id" not in session or session.get("user_type") not in ["admin", "moderator"]:
        flash("⚠ ليس لديك صلاحيات لهذه العملية.", "danger")
        return redirect(url_for("moder"))

    user_id = request.form['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Users WHERE user_id = ?", (user_id,))
        conn.commit()
        flash("تم حذف المستخدم بنجاح", "success")
    except Exception as e:
        flash(f"حدث خطأ أثناء حذف المستخدم: {str(e)}", "danger")
    finally:
        conn.close()

    return redirect(url_for("moder"))

# صفحة تغيير صلاحيات المستخدم
@app.route('/change-role-page')
def change_role_page():
    if "user_id" not in session or session.get("user_type") not in ["admin", "moderator"]:
        flash("⚠ ليس لديك صلاحيات للوصول إلى هذه الصفحة.", "danger")
        return redirect(url_for("moder"))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, email, user_type FROM Users")
    users = cursor.fetchall()
    conn.close()

    form_html = """
    <div class="form-group">
        <label for="user_id">اختر المستخدم:</label>
        <select name="user_id" required>
    """
    for user in users:
        form_html += f'<option value="{user.user_id}">{user.name} ({user.email}) - {user.user_type}</option>'
    
    form_html += """
        </select>
    </div>
    <div class="form-group">
        <label for="new_role">اختر الصلاحية الجديدة:</label>
        <select name="new_role" required>
            <option value="user">مستخدم عادي</option>
            <option value="moderator">مشرف</option>
            <option value="admin">مدير</option>
        </select>
    </div>
    """

    return render_template("moder.html",
                         show_form=True,
                         form_title="تغيير صلاحيات المستخدم",
                         form_content=form_html,
                         form_action=url_for("change_role"),
                         submit_btn_text="تغيير الصلاحيات")

# عملية تغيير الصلاحيات
@app.route('/change-role', methods=['POST'])
def change_role():
    if "user_id" not in session or session.get("user_type") not in ["admin", "moderator"]:
        flash("⚠ ليس لديك صلاحيات لهذه العملية.", "danger")
        return redirect(url_for("moder"))

    user_id = request.form['user_id']
    new_role = request.form['new_role']

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Users SET user_type = ? WHERE user_id = ?", (new_role, user_id))
        conn.commit()
        flash("تم تغيير صلاحيات المستخدم بنجاح", "success")
    except Exception as e:
        flash(f"حدث خطأ أثناء تغيير الصلاحيات: {str(e)}", "danger")
    finally:
        conn.close()

    return redirect(url_for("moder"))


@app.route('/get-categories')
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category_id, name FROM Categories")
    categories = [dict(zip(['category_id', 'name'], row)) for row in cursor.fetchall()]
    conn.close()
    return jsonify(categories)

@app.route('/add-category', methods=['POST'])
def add_category():
    if "user_id" not in session or session.get("user_type") not in ["admin", "moderator"]:
        return jsonify({"error": "غير مصرح"}), 403

    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Categories (name, description) VALUES (?, ?)",
            (data['name'], data.get('description', ''))
        )
        conn.commit()
        return jsonify({"success": True, "message": "تمت إضافة التصنيف بنجاح"})
    except Exception as e:
        return jsonify({"success": False, "message": f"حدث خطأ: {str(e)}"})
    finally:
        conn.close()
if __name__ == '__main__':
    app.run(debug=True)