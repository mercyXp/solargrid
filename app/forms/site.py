from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class SiteForm(FlaskForm):
    customer_id = SelectField("Customer", coerce=int, validators=[DataRequired()])
    site_name = StringField("Site Name", validators=[DataRequired(), Length(max=100)])
    address = TextAreaField("Address", validators=[DataRequired(), Length(max=255)])
    city = StringField("City", validators=[DataRequired(), Length(max=50)])
    province = SelectField(
        "Province",
        choices=[
            ("Central", "Central"),
            ("Copperbelt", "Copperbelt"),
            ("Eastern", "Eastern"),
            ("Luapula", "Luapula"),
            ("Lusaka", "Lusaka"),
            ("Muchinga", "Muchinga"),
            ("Northern", "Northern"),
            ("North-Western", "North-Western"),
            ("Southern", "Southern"),
            ("Western", "Western"),
        ],
        validators=[DataRequired()],
    )
    postal_code = StringField("Postal Code", validators=[Optional(), Length(max=10)])
    latitude = DecimalField("Latitude", validators=[Optional()], places=7)
    longitude = DecimalField("Longitude", validators=[Optional()], places=7)
    site_type = SelectField(
        "Site Type",
        choices=[
            ("Household", "Household"),
            ("School", "School"),
            ("Farm", "Farm"),
            ("Business", "Business"),
            ("Government", "Government"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Save Site")
