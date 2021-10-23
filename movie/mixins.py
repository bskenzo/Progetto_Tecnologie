from django.core.exceptions import PermissionDenied
from movie.models import Review


class AuthorRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        writer = Review.objects.get(id=self.get_object().pk)
        if writer.writer_id == self.request.user.pk or self.request.user.is_staff:
            return super(AuthorRequiredMixin, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied()
