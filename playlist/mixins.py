
from playlist.models import Playlist
from django.core.exceptions import PermissionDenied


class UserRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        usr = Playlist.objects.get(id=self.get_object().pk)
        if usr.writer_id == self.request.user.pk:
            return super(UserRequiredMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied()
