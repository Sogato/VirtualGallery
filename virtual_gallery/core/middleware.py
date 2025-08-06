from django.http import HttpResponse


class IgnoreDevToolsRequestMiddleware:
    """
    Middleware для игнорирования запросов от Chrome DevTools.

    Возвращает 204 No Content для пути '/.well-known/appspecific/com.chrome.devtools.json',
    чтобы избежать ошибок в консоли разработчика.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/.well-known/appspecific/com.chrome.devtools.json':
            return HttpResponse(status=204)  # No Content, без содержимого
        return self.get_response(request)
