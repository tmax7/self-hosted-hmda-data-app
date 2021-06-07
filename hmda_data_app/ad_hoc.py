import os.path
import json
from enum import Enum

class TableInfo:
    def __init__(self, table_name, column_names):
        self.table_name = table_name
        self.column_names = column_names

class SqlSelectQuery:
    def __init__(self, table_columns, where_condition, limit):
        self.table_columns = table_columns
        self.where_condition = where_condition
        self.limit = limit

class SqlUpdateQuery:
    def __init__(self, table_columns, set_expression, where_condition):
        self.table_columns = table_columns
        self.set_expression = set_expression
        self.where_condition = where_condition

def query_data_frame(sql_query, original_data_frame, file_path):
    # original_data_frame represents the data_frame which is stored in file_path
    # df represents a version of original_data_frame that will be returned
    try:
        if isinstance(sql_query, SqlSelectQuery):
            table_columns = sql_query.table_columns
            limit = sql_query.limit
            where_condition = sql_query.where_condition

            if where_condition != "":
                df = original_data_frame[eval(where_condition)]
            else:
                df = original_data_frame

            if limit is not None:
                df = df[table_columns].head(limit)
            else:
                df = df[table_columns]
        elif isinstance(sql_query, SqlUpdateQuery):
            table_columns = sql_query.table_columns
            set_expression = sql_query.set_expression
            arbitrary_limit = 100

            where_condition = sql_query.where_condition
            if where_condition != "":
                # Updates data_frame according to the expression
                original_data_frame.loc[eval(where_condition), table_columns] = parse_numerical_expression(set_expression)
                df = original_data_frame.loc[eval(where_condition), table_columns].head(arbitrary_limit)
            else:
                # Updates data_frame according to the expression
                original_data_frame.loc[:, table_columns] = set_expression
                df = original_data_frame.loc[:, table_columns].head(arbitrary_limit)
            #Saves to pickle file
            original_data_frame.to_pickle(file_path)
        return df #a dataframe
    except (SyntaxError, NameError) as e:
        raise SyntaxError("Error: at least one of the where conditions contains a syntax error." +
                          "\n" +
                          "If the value is a string it must be enclosed in quotes e.g. \"some string\"."
                          )

def parse_numerical_expression(expression):
    try:
       return int(expression)
    except ValueError:
        try:
            return float(expression)
        except ValueError:
            return expression

def get_where_condition(request, name_of_original_data_frame_variable):
    
    loop_limit = 200
    row_index = 0
    where_condition = ""
    while row_index < loop_limit:
        table_column_for_where_condition = request.form.get(f"tableColumns{row_index}")
        if table_column_for_where_condition is not None:
            relational_operator = request.form.get(f"relationalOperator{row_index}")
            right_operand =  parse_numerical_expression(request.form.get(f"rightOperand{row_index}"))
            logical_operator = request.form.get(f"logicalOperator{row_index}")
            #IMPORTANT: IF YOU CHANGE THE VARIABLE NAME OF VARIABLE original_data_frame IN routes.py THIS WILL NOT WORK !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
            where_condition = where_condition + f"({name_of_original_data_frame_variable}[\"{table_column_for_where_condition}\"] {relational_operator} {right_operand}) {logical_operator} "
        row_index += 1

    if where_condition != "":
        where_condition = where_condition.replace("AND", "&").replace("OR", "|").replace(" = ", " == ")[0:-3]

    return where_condition


class CalculateOption:
    def __init__(self, column_name, relational_operator, default_value, hidden):
        self.column_name = column_name
        self.relational_operator = relational_operator
        self.default_value = default_value
        self.hidden = hidden

class PlotType(Enum):
    BAR = "bar"
    BOXPLOT = "boxplot"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
        
class PlotOption:
    def __init__(self, plot_type: PlotType, x_axis=None, y_axis=None):
        self.plot_type = plot_type
        self.x_axis = x_axis
        self.y_axis = y_axis

# PlotOption JSONEncoder
class PlotOptionEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, PlotOption):
                obj_as_dict = {
                    "__PlotOption__": True,
                    "plot_type": obj.plot_type.name,
                    "x_axis": obj.x_axis,
                    "y_axis": obj.y_axis,
                }
                return obj_as_dict
            else:
                return json.JSONEncoder.default(self, obj)

# object_hook function to decode a json serialized PlotOption
def as_PlotOption(dct):
    if "__PlotOption__" in dct:
        return PlotOption(PlotType[dct["plot_type"]], dct["x_axis"], dct["y_axis"])
    return dct