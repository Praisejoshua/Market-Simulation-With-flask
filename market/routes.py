from market import app
from flask import render_template, url_for, redirect, flash, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user


@app.route("/")
@app.route("/home")
def home_page():
    return render_template("home.html")

@app.route("/market", methods = ['GET', 'POST'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    sell_form = SellItemForm()
    if request.method == "POST":

        # Purchase Item
        purchased_item = request.form.get('purchase_item')
        p_object = Item.query.filter_by(name = purchased_item).first()
        if p_object:
            if current_user.can_purchase(p_object):
                p_object.buy(current_user)

                flash(f"Congratulation! You have purchased {p_object.name} for {p_object.price}", category="success")
            else:
                flash(f"Sorry, you don't have enough budget to purchase {p_object.name}", category="danger")

        # Sell Item
        sold_item = request.form.get('sold_item')
        s_object = Item.query.filter_by(name = sold_item).first()
        if s_object:
            if current_user.can_sell(s_object):
                s_object.sell(current_user)
                flash(f"Congratulation! You have sold {s_object.name}", category="success")
            
            else:
                flash(f"Sorry, you can't sell {s_object.name}", category="danger")


        return redirect(url_for("market_page"))
    if request.method == "GET":        
        items = Item.query.filter_by(owner = None)
        owned_items = Item.query.filter_by(owner = current_user.id)

        return render_template("market.html", items = items, purchase_form = purchase_form,owned_items = owned_items, sell_form = sell_form)


@app.route("/register", methods = ["GET", "POST"])
def register_page():
    form = RegisterForm() #connecting the form defined for the Register page and passing it to this route
    if form.validate_on_submit():
        user_create = User(
            username = form.username.data,
            email_address = form.email_address.data,
            password = form.password1.data
        )
        db.session.add(user_create)
        db.session.commit()
        login_user("user_create.username")
        flash(f"Account has be created Successfully. You logged in as {user_create.username}", category="success")
        return redirect(url_for('market_page'))
    
    if form.errors != {}: # checking if there are errors in the defined dictionary
        for field in form.errors.values(): # you can use keys, values etc
            flash(f"There was an error {field}. Please check your details.", 'danger')


    return render_template('register.html', form = form)

@app.route("/login", methods = ["GET", "POST"])
def login_page():
    form  = LoginForm() #connecting the form defined for the login page and passing it to this route

    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        
        if attempted_user and attempted_user.check_password_correction(form.password.data):
            login_user(attempted_user)
            flash(f"You have successfully logged in as {attempted_user.username}", category="success")
            return redirect(url_for("market_page"))
        else:
            flash("Username and password are not matching! Please try again", category="danger")
    
            
    return render_template("login.html", form = form)

@app.route("/logout")
def log_out_page():
    logout_user()
    flash("You have been logged out.", category="info")
    return redirect(url_for("home_page"))