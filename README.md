# traimaocv
Using matplotlib in django project
You will need to define env variables dj_secret_key, db_user and db_passwd

with django 4 you have to change
/lib/python3.10/site-packages/bokeh/server/django/routing.py
line 27
    from django.urls import path

line 107
    def get_http_urlpatterns(self) -> List[URLPattern]:
        return self._http_urlpatterns + [path(r"", AsgiHandler)]

    def get_websocket_urlpatterns(self) -> List[URLPattern]:
        return self._websocket_urlpatterns

    def _add_new_routing(self, routing: Routing) -> None:
        kwargs = dict(app_context=routing.app_context)


lib/python3.10/site-packages/bokeh/server/django/apps.py
line 45
    name = 'bokeh.server.django'
    label = 'bokeh_server_django'


