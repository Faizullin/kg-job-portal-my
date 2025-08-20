# views.py
import mimetypes
import os
from os.path import basename

from django.conf import settings
from django.http import HttpResponse, Http404
from django.views.static import serve
from protected_media.utils import server_header

from lms.apps.core.utils.crud_base.views import BaseApiView


class ProtectedMediaLoadView(BaseApiView):
    def get(self, request, path, server="django", as_download=False):
        file_path = os.path.join(settings.PROTECTED_MEDIA_ROOT, path)
        if not os.path.exists(file_path):
            raise Http404("File not found")

        if server != "django":
            mimetype, encoding = mimetypes.guess_type(file_path)
            response = HttpResponse()
            response["Content-Type"] = mimetype or "application/octet-stream"
            if encoding:
                response["Content-Encoding"] = encoding

            if as_download:
                response["Content-Disposition"] = (
                    f"attachment; filename={basename(file_path)}"
                )

            response[server_header(server)] = os.path.join(
                settings.PROTECTED_MEDIA_LOCATION_PREFIX, path
            ).encode("utf8")
        else:
            response = serve(
                request,
                path,
                document_root=settings.PROTECTED_MEDIA_ROOT,
                show_indexes=False,
            )

        return response
