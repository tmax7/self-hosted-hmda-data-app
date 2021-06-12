
"""
Routes and views for the flask application.
"""

from datetime import datetime
import json

from flask import make_response, redirect, render_template, render_template_string, request, session, url_for, jsonify
import pandas as pd
import os

import argon2
from hmac import compare_digest as compare_hash
import pickle
import psycopg2

from hmda_data_app import plot_module
from hmda_data_app import ad_hoc
from hmda_data_app import flask_app
from hmda_data_app import tasks

# Reads the pickle containing the data for the application
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
file_name = "Changed 2019_state_AZ_actions_taken_1_loan_types_1.pkl"
abs_path_to_data_pickle = os.path.join(PROJECT_ROOT, f"static/data/{file_name}").replace("\\", "/")
original_data_frame = pd.read_pickle(abs_path_to_data_pickle)
name_of_original_data_frame_variable = "original_data_frame"
table_info = ad_hoc.TableInfo(file_name, original_data_frame.columns.format())

# Get json version of data frame for passing to Celery tasks
original_data_frame_json = original_data_frame.to_json()



# Creates PasswordHasher
password_hasher = argon2.PasswordHasher()

# Sets up the secret_key for the session
flask_app.secret_key = os.urandom(16)

# Initializes plot_types
plot_types = [plot_type.value for plot_type in ad_hoc.PlotType]

@flask_app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return login_user()
    else:
        return make_secure_response(render_template(
            "login.html",
            title="Login",
            year=datetime.now().year,
            message=""
        ))

def login_user():
    username = request.form.get("username")

    # Connects to password database.
    # IMPORTANT: must commit passwords_db_connection
    # IMPORTANT: alway close passwords_db_cursor and then passwords_db_connection
    # before the function returns.
    hashes_db_connection = psycopg2.connect("dbname=hmda_data_app_db user=postgres password=defaultPassword host=hmda-data-app-postgres-container")
    hashes_db_cursor = hashes_db_connection.cursor()

    # IMPORTANT:
    #  Must use this paraameter passing syntax or the other syntax shown on pyscopg's documentation
    # to avoid SQL injection attack!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    hashes_db_cursor.execute("""
        SELECT hash 
        FROM user_password_hashes
        WHERE username = %(username)s;
    """, {"username": username})
    
    # .fetchone() returns a tuple of the form (hash,)
    hash = hashes_db_cursor.fetchone()[0];
    
    if hash is None:
        hashes_db_cursor.close()
        hashes_db_connection.close()
        return make_secure_response(render_template(
            "login.html",
            title="Login",
            year=datetime.now().year,
            message="wrong username"
        ))
    
    password = request.form.get("password")
    is_correct_password = False
    try:
        password_hasher.verify(hash, password)
        is_correct_password = True
        if password_hasher.check_needs_rehash(hash):
            new_hash = password_hasher.hash(password)
            hashes_db_cursor.execute("""
                UPDATE user_password_hashes SET hash = %(hash)s
                WHERE username = %(username)s;
            """, {"hash": hash, "username": username})
    except argon2.exceptions.VerifyMismatchError:
        pass
    
    if is_correct_password:
        session["username"] = username
        hashes_db_connection.commit()
        hashes_db_cursor.close()
        hashes_db_connection.close()
        return make_secure_response(redirect(url_for("home")))
    else:
        hashes_db_cursor.close()
        hashes_db_connection.close()
        return make_secure_response(render_template(
            "login.html",
            title="Login",
            year=datetime.now().year,
            message="wrong password"
        ))


@flask_app.route("/home")
def home():
    """Renders the home page."""
    if "username" in session:
        return make_secure_response(render_template(
            "index.html",
            year=datetime.now().year,
        ))
    else:
        return make_secure_response(redirect(url_for("login")))

@flask_app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "username" in session:
        if request.method == "POST":
            return make_dashboard_plot()
        else:
            default_plot_options = [
                ad_hoc.PlotOption(ad_hoc.PlotType.PIE, y_axis="derived_dwelling_category"),
                ad_hoc.PlotOption(ad_hoc.PlotType.BOXPLOT, x_axis="loan_purpose", y_axis="property_value"),
                ad_hoc.PlotOption(ad_hoc.PlotType.SCATTER, x_axis="discount_points", y_axis="loan_amount"),
            ]
        
            #TEST !!!!!!!!!!!!!!!!!!!!!! PCA !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            #pca_columns = ["loan_amount", "loan_to_value_ratio", "interest_rate", "rate_spread", "loan_term", "property_value", "income", "debt_to_income_ratio", ]
            #pca_plot = plot_module.make_PCA_plot(original_data_frame, pca_columns)

            return make_secure_response(render_template(
                "dashboard.html",
                title='Dashboard',
                year=datetime.now().year,
                message="",
                default_plot_options=default_plot_options,
                #pca_plot=pca_plot,
                table_info=table_info,
                plot_types=plot_types,
            ))
    else:
        return make_secure_response(redirect(url_for("login")))

def make_dashboard_plot():
    form_index = request.form.get("formIndex")
    plot_id = f"plot{form_index}"

    plot_type = request.form.get(f"plotType")
    x_axis = request.form.get(f"xAxis")
    y_axis = request.form.get(f"yAxis")
   
    plot_option = ad_hoc.PlotOption(ad_hoc.PlotType[plot_type.upper()], x_axis=x_axis, y_axis=y_axis)
    
    # Starts task and return immediate response 
    task = tasks.make_dashboard_plot.delay(original_data_frame_json, json.dumps(plot_option, cls=ad_hoc.PlotOptionEncoder))
    return make_secure_response(({}, 202, {"Location": url_for("dashboard_plot_task_status", task_id=task.id), "plotId": plot_id}))


@flask_app.route("/dashboard_plot_task_status/<task_id>")
def dashboard_plot_task_status(task_id):
    task = tasks.make_dashboard_plot.AsyncResult(task_id)
   
    if task.state == "SUCCESS":
        response = {
            "state": task.state,
            "result": task.result
        }
        # IMPORTANT!!!!!: This frees up task resources now that result is ready:
        task.forget()
    else:
        response = {
            'state': task.state,
        }
    return jsonify(response)

@flask_app.route("/query", methods=["GET", "POST"])
def query():
    if "username" in session:
        if request.method == "POST":
            return do_query()
        else:

            return make_secure_response(render_template(
                "query.html",
                title="Query",
                year=datetime.now().year,
                message="",
                table_info=table_info,
                plot_types=plot_types
            ))
    else:
        return make_secure_response(redirect(url_for("login")))

def do_query():
    """Renders the contact page."""
    if "username" in session:
        query_type = request.form.get("sqlQueryType")
   
        if query_type == "SELECT":
            table_columns = request.form.getlist("tableColumns")
            # MIGHT BE USEFULE IN THE FUTURE: table_to_select_from = request.form.get("tableToSelectFrom")
            limit = int(request.form.get("limit"))        
            where_condition = ad_hoc.get_where_condition(request, name_of_original_data_frame_variable)
            sql_query =  ad_hoc.SqlSelectQuery(table_columns, where_condition, limit)
            try:
                result = ad_hoc.query_data_frame(sql_query, original_data_frame, abs_path_to_data_pickle)
                result = result.to_html(justify="center", classes="table")
            except SyntaxError as error:
                result = f"<h3> {str(error)} </h3>"
        elif query_type == "UPDATE":
            # MIGHT BE USEFUL IN THE FUTURE: table_to_update = request.form.get("tableToUpdate")
            table_columns = request.form.getlist("tableColumns")
            set_expression = request.form.get("setExpression")
            where_condition = ad_hoc.get_where_condition(request, name_of_original_data_frame_variable)
            sql_query = ad_hoc.SqlUpdateQuery(table_columns, set_expression, where_condition)
            try:
                result = ad_hoc.query_data_frame(sql_query, original_data_frame, abs_path_to_data_pickle).to_html(justify="center", classes="table")
                result = "<h3> update sucessful </h3>" + result
            except SyntaxError as error:
                result = f"<h3> {str(error)} </h3>"
       
        return make_secure_response(render_template_string(result))
    else:
        return make_secure_response(redirect(url_for("login")))

@flask_app.route("/plot", methods=["POST"])
def make_plot():
    if "username" in session:
        plot_type = request.form.get("plotType")
        x_axis = request.form.get("xAxis")
        y_axis = request.form.get("yAxis")

        table_columns = request.form.getlist("tableColumns")
        # MIGHT BE USEFUL IN THE FUTURE: table_to_select_from = request.form.get("tableToSelectFrom")
        where_condition = ad_hoc.get_where_condition(request, name_of_original_data_frame_variable)
        sql_query =  ad_hoc.SqlSelectQuery(table_columns, where_condition, None)
        try:
            df = ad_hoc.query_data_frame(sql_query, original_data_frame, abs_path_to_data_pickle)
            plot = plot_module.make_dashboard_plot(df, plot_options=[ad_hoc.PlotOption(ad_hoc.PlotType[plot_type.upper()], x_axis, y_axis)])
        except SyntaxError as error:
            plot = f"<h3> {str(error)} </h3>"
        return make_secure_response(render_template_string(plot))
        
    else:
        return make_secure_response(redirect(url_for("login")))

@flask_app.route("/calculate", methods=["GET", "POST"])
def calculate():
    if "username" in session:
        if request.method == "POST":
            return do_calculate()
        else:
            options = [
                ad_hoc.CalculateOption("census_tract", "=", default_value=None, hidden=False),
                ad_hoc.CalculateOption("loan_amount", "<", "1_000_000", hidden=True),
                ad_hoc.CalculateOption("property_value", "<", "1_000_000", hidden=True),
                ad_hoc.CalculateOption("income", "<", "100", hidden=True),
                ad_hoc.CalculateOption("interest_rate", "<", "90", hidden=True),
                ad_hoc.CalculateOption("loan_to_value_ratio", "<", "110", hidden=True), 
            ]
            return make_secure_response(render_template(
                "calculate.html",
                title="Calculate",
                year=datetime.now().year,
                message="",
                options=options,
             ))
    else:
        return make_secure_response(redirect(url_for("login")))

def do_calculate():
        x_axis = "income"
        y_axis = "loan_amount"
        
        user_income = ad_hoc.parse_numerical_expression(request.form.get("userIncome"))
        
        table_columns = []
        table_column = request.form.get("tableColumns0")
        table_column_index = 0
        while table_column is not None:
            table_columns.append(table_column)
            table_column_index += 1
            table_column = request.form.get(f"tableColumns{table_column_index}")
        where_condition = ad_hoc.get_where_condition(request, name_of_original_data_frame_variable)
        sql_query =  ad_hoc.SqlSelectQuery(table_columns, where_condition, None)
        try:
            df = ad_hoc.query_data_frame(sql_query, original_data_frame, abs_path_to_data_pickle)
            plot = plot_module.make_regression_plot(df, x_axis, y_axis, user_income)
            #TEST !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            #plot_module.estimate_overall_accuracy(df, x_axis, y_axis, "census_tract", [
            #"04001970502", "04003001100", "04005000100", "04007000301", "04009961100", "04011960300", 
            #"04012020501", "04013050702", "04015950500", "04017964202", "04019002400",
            #"04021000204", "04023966402", "04025000604", "04027011501"
            #])
        except SyntaxError as error:
            plot =  f"<h3> {str(error)} </h3>"
        return make_secure_response(render_template_string(plot))

@flask_app.route("/logout")
def logout():
    session.pop("username", None)
    return make_secure_response(redirect(url_for("login")))

def make_secure_response(template):
    response = make_response(template)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

