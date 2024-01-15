from typing import Callable

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


class UnderConstructionMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        return render(request, "core/siteuc.html")
