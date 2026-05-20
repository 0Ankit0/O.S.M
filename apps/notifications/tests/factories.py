import factory

from .. import models


class NotificationFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory("testsupport.factories.UserFactory")
    type = factory.Faker("pystr")
    issuer = factory.SubFactory("testsupport.factories.UserFactory")

    class Meta:
        model = models.Notification
