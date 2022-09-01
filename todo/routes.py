from todo import app
from flask import render_template, redirect, url_for, flash, request
from todo.models import Item, User, Completed
from flask_login import login_user, logout_user, login_required, current_user
from todo.forms import RegisterForm, LoginForm, AddItemForm, RemoveItemForm,CompleteItemForm,RemoveCompletedForm
from todo import db

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/mylist', methods=['GET', 'POST'])
@login_required
def list_page():
    remove_form = RemoveItemForm()
    complete_form = CompleteItemForm()
    if request.method == "POST":
        if remove_form.validate_on_submit():
            r_id = request.form.get('remove')
            Item.query.filter_by(id=r_id).delete()
            db.session.commit()
            if r_id:
                return redirect(url_for('list_page'))

        if complete_form.validate_on_submit():
            r_name = request.form.get('complete')
            print(r_name)
            completed_item = Completed(name = r_name,
                                        owner=current_user.username)
            db.session.add(completed_item)
            Item.query.filter_by(name=r_name).delete()
            db.session.commit()
            return redirect(url_for('list_page'))

    if request.method == "GET":
        items = Item.query.filter_by(owner=current_user.username)
        return render_template('mylist.html', items=items, remove_form=remove_form, complete_form=complete_form)

@app.route('/additem', methods=['GET', 'POST'])
@login_required
def add_item_page():
    form = AddItemForm()
    if form.validate_on_submit():
        item_to_create = Item(name=form.itemname.data,
                                duration=form.duration.data,
                                priority=form.priority.data,
                                owner=current_user.username)
        db.session.add(item_to_create)
        db.session.commit()
        return redirect(url_for('list_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating an item: {err_msg}', category='danger')
    return render_template('additem.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                                email_address=form.email_address.data,
                                password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('list_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
            attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('list_page'))
        else:
            flash('Username and password are not a match, try again', category='danger')
    else:
        print("something wrong")
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out", category='info')
    return redirect(url_for('home_page'))

@app.route('/completed', methods=['GET', 'POST'])
@login_required
def completed_page():
    remove_form = RemoveItemForm()
    complete_form = CompleteItemForm()
    remove_completed_form = RemoveCompletedForm()

    if remove_completed_form.validate_on_submit():
        r_c_id = request.form.get('removecompleted')
        Completed.query.filter_by(id=r_c_id).delete()
        db.session.commit()
        return redirect(url_for('completed_page'))

    completed_items = Completed.query.filter_by(owner=current_user.username)
    return render_template('completed.html',
                            completed_items=completed_items,
                            remove_form=remove_form,
                            complete_form=complete_form,
                            remove_completed_form=remove_completed_form)
