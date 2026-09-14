from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional


class CustomerForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=50)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=50)])
    company_name = StringField("Company Name", validators=[Optional(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=100)])
    phone = StringField("Phone", validators=[DataRequired(), Length(max=20)])
    address = TextAreaField("Address", validators=[DataRequired(), Length(max=255)])
    customer_type = SelectField(
        "Customer Type",
        choices=[("Individual", "Individual"), ("Business", "Business"), ("Government", "Government"), ("NGO", "NGO")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Save Customer")
