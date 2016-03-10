# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return unicode(self.name)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Author(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return unicode(self.name)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Book(models.Model):
    name = models.CharField(max_length=255)
    descn = models.TextField(blank=True)
    price = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    category = models.ForeignKey(Category, null=True, blank=True)
    authors = models.ManyToManyField(Author, blank=True)

    class Meta:
        ordering = ["name"]
        permissions = (
            ("sft_mgr_book", "manager book"),
        )

    def __unicode__(self):
        return unicode(self.name)

    def __str__(self):
        return self.name
