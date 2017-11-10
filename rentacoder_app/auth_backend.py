from django.contrib.auth.backends import ModelBackend
from rentacoder_app.models import ProjectScore


class UserModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username, password, **kwargs)
        return user if user and not user.deleted else None


def processor(request):
    if request.user.is_authenticated():
        return {
            'authenticated': True,
            'user': request.user,
            'num_pending_scores': ProjectScore.get_num_pending_scores_for_user(request.user),
        }
    else:
        return {
            'authenticated': False
        }
