from wtforms import Form, StringField, PasswordField, TextAreaField, validators


class LoginForm(Form):
    username = StringField("Username", validators=[validators.DataRequired()])
    password = PasswordField("Password", validators=[validators.DataRequired()])


class SignUpForm(Form):
    username = StringField("Username", validators=[validators.DataRequired()])
    email = StringField("E-Mail Address", validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField("Password", validators=[validators.DataRequired(),
                                                     validators.EqualTo(fieldname="password_confirm",
                                                                        message='Passwords must match')])
    password_confirm = PasswordField("Confirm Password", validators=[validators.DataRequired()])

