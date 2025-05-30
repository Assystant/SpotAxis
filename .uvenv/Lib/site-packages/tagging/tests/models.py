from django.db import models

from tagging.fields import TagField


class Perch(models.Model):
    size = models.IntegerField()
    smelly = models.BooleanField(default=True)


class Parrot(models.Model):
    state = models.CharField(max_length=50)
    perch = models.ForeignKey(Perch, null=True,
                              on_delete=models.CASCADE)

    def __str__(self):
        return self.state

    class Meta:
        ordering = ['state']


class Link(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Article(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class FormTest(models.Model):
    tags = TagField('Test', help_text='Test')


class FormTestNull(models.Model):
    tags = TagField(null=True)


class FormMultipleFieldTest(models.Model):
    tagging_field = TagField('Test', help_text='Test')
    name = models.CharField(max_length=50)
