
from hmda_data_app.ad_hoc import PlotType
import os.path
import base64
from io import BytesIO

import pandas as pd
from matplotlib.figure import Figure
from matplotlib import rcParams


import numpy as np


from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

import sklearn.cluster as cluster

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from sklearn import config_context

import time

class TooManyGroupsException(Exception):
    pass

GROUP_LIMIT_FOR_PLOTS = 20

def make_regression_plot(data_frame, x_axis, y_axis, user_point_x=None):
    df = data_frame[[x_axis, y_axis]].dropna()
    x_df = pd.DataFrame(df[x_axis])
    y_df = pd.DataFrame(df[y_axis])

    # Finds regression.
    is_error = False
    try:
        model = LinearRegression()
        
        # Splits data with random state set to an integer and shuffle to false for reproducible output across multiple function calls
        x_df_train, x_df_test, y_df_train, y_df_test = train_test_split(x_df, y_df, random_state=10, shuffle=False)
        model.fit(x_df_train, y_df_train)
        
        y_df_test_pred = model.predict(x_df_test)
        
        the_mean_squared_error = mean_squared_error(y_df_test, y_df_test_pred)
        the_variance_score = r2_score(y_df_test, y_df_test_pred)
        
        y_df_pred = model.predict(x_df)

    # When there is less than 2 samples then can't do regression:
    except (ValueError) as valueError:
        print(valueError)
        is_error = True
       
    # Creates figure
    fig = Figure()
    ax = fig.subplots()
    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)

    # Plots scatter
    ax.scatter(x_df, y_df)

    # Plots regression if there is enough data to do so
    if not is_error:
        ax.plot(x_df, y_df_pred, label="regression", color="red")

    # Creates data for html image tag
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")

    # user_point_x prediction
    if user_point_x and not is_error:
        user_point_x = [[user_point_x]]
        user_point_y_pred = model.predict(user_point_x)[0][0]
        return (f"<img src='data:image/png;base64,{data}'/>" +
                f"<h3>The recommended value is: ${user_point_y_pred}</h3>" +
                f"<h3>The mean squared error is: {the_mean_squared_error}</h3>" +
                f"<h3>The variance score is: {the_variance_score}</h3>")
    else: 
        return (f"<img src='data:image/png;base64,{data}'/>" + 
                f"<h3>There is not enough data with the given characteristics to create the regression</h3>")
            
def estimate_overall_accuracy(data_frame, x_axis, y_axis, column_name, values):
    model = LinearRegression()
    the_mean_squared_errors = []
    the_variance_scores = []

    for value in values:
        df = data_frame[data_frame[column_name] == value]
        df = data_frame[[x_axis, y_axis]].dropna()
        x_df = pd.DataFrame(df[x_axis])
        y_df = pd.DataFrame(df[y_axis])
        # Finds regression
        try:
            # Splits data with random state set to an integer and shuffle to false for reproducible output across multiple function calls
            x_df_train, x_df_test, y_df_train, y_df_test = train_test_split(x_df, y_df, random_state=10, shuffle=False)
            model.fit(x_df_train, y_df_train)
        
            y_df_test_pred = model.predict(x_df_test)
        
            the_mean_squared_errors.append(mean_squared_error(y_df_test, y_df_test_pred))
            the_variance_scores.append(r2_score(y_df_test, y_df_test_pred))

        # When there is less than 2 samples then can't do regression:
        except ValueError as e:
            print(e)
            pass
    if len(the_mean_squared_errors) != 0 and len(the_variance_scores) != 0:
        average_mean_squared_error = sum(the_mean_squared_errors) / len(the_mean_squared_errors)
        average_variance_score = sum(the_variance_scores) / len(the_variance_scores)
    else:
        average_mean_squared_error = "NA"
        average_variance_score = "NA"
    print(f"average mean squared error: {average_mean_squared_error} \n" +
          f"average variance score: {average_variance_score}")

def make_dashboard_plot(data_frame, plot_option):
    plot_type = plot_option.plot_type
    x_axis = plot_option.x_axis
    y_axis = plot_option.y_axis
    
    # Creates figure
    fig = Figure()
    ax = fig.subplots()
   
    too_many_groups = False
    is_error = False
    try:
        if plot_type == PlotType.BAR:
            df_bar = data_frame.groupby(x_axis).mean()
            # Checks that plot will not contain too many groups. 
            # This must be done to ensure a response time under 30 seconds.
            if len(df_bar.index) > GROUP_LIMIT_FOR_PLOTS:
                raise TooManyGroupsException()
            df_bar.plot.bar(y=y_axis, ax=ax, ylabel=f"mean {y_axis}", legend=False)

        elif plot_type == PlotType.BOXPLOT:
            df_boxplot = data_frame[[x_axis, y_axis]]
            df_boxplot = df_boxplot.groupby(x_axis, as_index=False)
            # Checks that plot will not contain to many groups. 
            # This must be done to ensure a response time under 30 seconds.
            if len(df_boxplot.groups) > GROUP_LIMIT_FOR_PLOTS:
                raise TooManyGroupsException
            df_boxplot.boxplot(column=y_axis, ax=ax, subplots=False, showfliers=False)

        elif plot_type == PlotType.LINE:
            data_frame.plot(x_axis, y_axis, ax=ax)

        elif plot_type == PlotType.SCATTER:
            # Drops NA values
            df_scatter = data_frame[[x_axis, y_axis]].dropna()
           
            x_df = pd.DataFrame(df_scatter[x_axis])
            y_df = pd.DataFrame(df_scatter[y_axis])
            try:
                # Calculates KMeans clusters 
                cluster_y_pred = cluster.KMeans(n_clusters=4).fit_predict(x_df, y_df)
              
                # Plots data points colored according to assigned cluster
                ax.scatter(x_df, y_df, c=cluster_y_pred)
                ax.set_xlabel(x_axis)
                ax.set_ylabel(y_axis)
               
            # When there is less than 2 samples then can't do cluster:
            except (TypeError, ValueError):
                df_scatter.plot.scatter(x_axis, y_axis, ax=ax)

        elif plot_type == PlotType.PIE:
            pie_df = data_frame.groupby(y_axis).size()
            # Checks that plot will not contain to many groups. 
            # This must be done to ensure a response time under 30 seconds.
            if len(pie_df.index) > GROUP_LIMIT_FOR_PLOTS:
                raise TooManyGroupsException
            pie_df.plot.pie(y=y_axis, ax=ax, title=y_axis, legend=True, autopct="%1.1f%%", labels=None, explode=[0.1 for i in range(len(pie_df.index))] )

    except TooManyGroupsException:
        too_many_groups = True
    except Exception as error:
        print(error)
        is_error = True
      
    # Creates data for html image tag
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    
    if too_many_groups:
        return f"<h2>The chosen plot takes too long to generate</h2>"
    elif not is_error:
        return f"<img src='data:image/png;base64,{data}'/>"
    else:
        return ("<h2>There was an error making this plot.</h2> \n" +
                "<h2>Please review column types and values to determine if the plot type can be made using the chosen x-axis and y-axis</h2>")

   
def make_PCA_plot(data_frame, columns):
    df = data_frame[columns].dropna()
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df)

    pca= PCA()
    X_pca = pca.fit_transform(scaled_data)

    # Creates figure
    fig = Figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(X_pca[:,0], X_pca[:,1], X_pca[:,2])
    

    # Creates data for html image tag
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")

    return f"<img src='data:image/png;base64,{data}'/>"

