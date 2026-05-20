import factory
from django.contrib.auth import get_user_model


User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.LazyAttribute(lambda obj: obj.email)
    password = factory.PostGenerationMethodCall("set_password", "password123")

    class Meta:
        model = User

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", "password123")
        manager = cls._get_manager(model_class)
        return manager.create_user(password=password, **kwargs)
