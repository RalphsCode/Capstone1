"""Location of the WTForms"""

from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length

class AddressForm(FlaskForm):
    address = StringField("Event Location", validators=[Length(max=50),InputRequired()])
    date = DateField("Date of Event", format='%Y-%m-%d', validators=[InputRequired()])
    search_years = SelectField('Select how far back to search', choices=[
        (3, '3 Years - fastest'),
        (5, '5 Years'),
        (7, '7 Years'),
        (10, '10 Years - most accurate, but slowest')
        ])

class UserForm(FlaskForm):
    username = StringField("Username:", validators=[Length(max=50),InputRequired()])

    password = PasswordField("Password:", validators=[Length(max=50),InputRequired()])
    
    submit_button_register = SubmitField('Register')
    submit_button_login = SubmitField('Login')