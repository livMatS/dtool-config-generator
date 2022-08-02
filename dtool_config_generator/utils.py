from flask import current_app, redirect, url_for
from flask_login import current_user
from functools import wraps


def confirmation_required(func):
    """
    If you decorate a view with this, it will ensure that the current user has
    been confirmed before calling the actual view. (If they are not, it calls
    the :attr:`LoginManager.unauthorized` callback.) For
    example::
        @app.route('/post')
        @login_required
        @confirmation_required
        def post():
            pass
    If there are only certain times you need to require that your user is
    logged in, you can do so with::
        if not current_user.is_confirmed:
            return current_app.login_manager.unauthorized()
    ...which is essentially the code that this function adds to your views.
    It can be convenient to globally turn off requiring confirmation when unit
    testing. To enable this, if the application configuration variable
    `CONFIRMATION_DISABLED` is set to `True`, this decorator will be ignored.
    :param func: The view function to decorate.
    :type func: function
    """

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_app.config.get("CONFIRMATION_DISABLED"):
            pass
        elif not current_user.is_confirmed:
            return redirect(url_for('auth.unconfirmed'))

        # flask 1.x compatibility
        # current_app.ensure_sync is only available in Flask >= 2.0
        if callable(getattr(current_app, "ensure_sync", None)):
            return current_app.ensure_sync(func)(*args, **kwargs)
        return func(*args, **kwargs)

    return decorated_view


def admin_required(func):
    """
    :param func: The view function to decorate.
    :type func: function
    """

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_app.config.get("ADMIN_DISABLED"):
            pass
        elif not current_user.is_admin:
            return current_app.login_manager.unauthorized()

        # flask 1.x compatibility
        # current_app.ensure_sync is only available in Flask >= 2.0
        if callable(getattr(current_app, "ensure_sync", None)):
            return current_app.ensure_sync(func)(*args, **kwargs)
        return func(*args, **kwargs)

    return decorated_view